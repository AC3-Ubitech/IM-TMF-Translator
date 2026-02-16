import os
import uuid
import datetime
import traceback

from pathlib import Path
from flask import request, jsonify
from utils.maestro_client import models

import yaml
from kubernetes import client, config
from flask import Flask, jsonify, request

from utils.helm import helm
from translator import template_translator as translator
from utils.maestro_client import MaestroTranslatorClient

# from translator import translator_all_in_one as translator

maestro_client = MaestroTranslatorClient()

app = Flask(__name__)
map_ns_to_so_ids : dict[str, str]= {}

@app.route('/health', methods=['GET'])
def healthcheck():
    return jsonify(status='healthy'), 200

@app.route('/uc3/deployments', methods=['POST'])
def deploy_app():
    # Ensure a file is uploaded
    if 'file' not in request.files:
        return jsonify({"error": "No descriptor in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No descriptor file selected"}), 400

    # Generate filename
    try:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d--%H:%M:%S')
        random_hash = uuid.uuid4().hex
        filename = f"{timestamp}_{random_hash}.yaml"
        save_path = os.path.join('/app/incoming-descriptors/deploy/', filename)

        file.save(save_path)
        file.seek(0)
        print("------> Descriptor saved at : ", save_path, flush=True)
    except Exception as e:
        traceback.print_exc()
        print("------> ACTUAL ERROR: ", str(e), flush=True)
        return jsonify({"translator_error": "filed to reach cache"}), 400

    try:
        ac3_im_yaml = yaml.safe_load(file.read().decode('utf-8'))
        application_name, version = translator.run(ac3_im_yaml, Path("./output_k8s_manifests").resolve())
    except Exception as e:
        traceback.print_exc()
        return jsonify({"translator_error": str(e)}), 400

    try:
        helm.helm_package_and_push(
            application_name,
            version,
            chart_path= str(Path("./output_k8s_manifests").resolve())
        )
    except Exception as e:
        return jsonify({"helm_error": str(e)}), 400

    try:
        maestro_client.get_access_token_keycloak()
        service_order_id = maestro_client.create_service_order(application_name, version)

        map_ns_to_so_ids[service_order_id] = application_name
        return jsonify({
            "message": "A new service order is being processed by Maestro.",
            "serviceOrderId": service_order_id
        }), 201

    except Exception as e:
        return jsonify({"client_error": e.args[0]}), 400

@app.route('/uc3/deployments/<string:id>', methods=['GET'])
def get_app_details(id: str):

    if not id in map_ns_to_so_ids:
        return jsonify({
            "client_error": f"the serviceOrderId '{id}' cannot be matched to any previously created namespace"
        }), 404

    name_space = map_ns_to_so_ids[id]

    res = None
    try:
        maestro_client.get_access_token_keycloak()
        res = maestro_client.get_service_order(id)
    except Exception as e:
        return jsonify({"client_error": e.args[0]}), 400

    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()

        if res["state"] == "COMPLETED": #"PARTIAL"
            services = v1.list_namespaced_service(namespace=name_space).items
            pods = v1.list_namespaced_pod(namespace=name_space).items

            for pod in pods:
                pod_labels = pod.metadata.labels or {}
                matched_ip = ""

                for svc in services:
                    selector = svc.spec.selector

                    if not selector:
                        continue

                    if all(pod_labels.get(k) == v for k, v in selector.items()):
                        matched_ip = svc.spec.cluster_ip
                        break

                res["deploymentDetails"].append({
                    "name": pod.metadata.name,
                    "IP": matched_ip,
                    "status": pod.status.phase
                })

        return jsonify(res), 201

    except Exception:
        return jsonify({"kubernetes_client": "An error occurred during k8s connection"}), 400

@app.route('/uc3/deployments/<string:id>', methods=['DELETE'])
def delete_app(id: str):

    res = None
    try:
        maestro_client.get_access_token_keycloak()
        res = maestro_client.get_service_order(id, False)
    except Exception as e:
        return jsonify({"client_error": e.args[0]}), 400

    service_item_id = ""
    for order_item in res["serviceOrderItem"]:
        if order_item["service"]["name"] == "service-spec-end-user-cfs-ocm":
            service_item_id = order_item["service"]["id"]
            break

    if service_item_id == "":
        return jsonify({404: f"Service order with id '{id}', has no valid 'OCM' order item"}), 404

    try:
        service_item_body = maestro_client.get_service_inventory_item(service_item_id)

        service_item_body["state"] = "TERMINATED"
        maestro_client.patch_service_inventory_item(service_item_id, service_item_body)

        maestro_client.delete_service_order(id)
    except Exception as e:
        return jsonify({"client_error": e.args[0]}), 400

    if id in map_ns_to_so_ids:
        del map_ns_to_so_ids[id]
        print(f"    the serviceOrderId '{id}' is been cleaned from cache", flush=True)

    return jsonify({"status": 'OK'}), 200

@app.route('/uc3/deployments/dummy/<string:id>', methods=['DELETE'])
def delete_semi_manually_app(id: str):

    if not id in map_ns_to_so_ids:
        return jsonify({
            "client_error": f"the serviceOrderId '{id}' cannot be matched to any previously created namespace"
        }), 404
    
    name_space = map_ns_to_so_ids[id]

    config.load_kube_config(config_file="/root/.kube/hub-config")
    api = client.CustomObjectsApi()

    try:
        scheduling_manifests = api.list_namespaced_custom_object(
            group="scheduling.p2code.eu",
            version="v1alpha1",
            namespace="p2code-scheduler-system",
            plural="p2codeschedulingmanifests"
        )

        scheduling_manifest_name = ""
        for scheduling_manifest in scheduling_manifests["items"]:
            current_scheduling_manifest_name = scheduling_manifest["metadata"]["name"]

            for spec_manifest in scheduling_manifest["spec"]["manifests"]:
                if spec_manifest["kind"] == "Deployment":
                    if spec_manifest["metadata"]["namespace"] == name_space:
                        scheduling_manifest_name = current_scheduling_manifest_name
                        break

        if scheduling_manifest_name == "":
            return jsonify({"client_error": f"Scheduling id that matches the '{id}' and ns '{name_space}' not found."}), 404

        api.delete_namespaced_custom_object(
            group="scheduling.p2code.eu",
            version="v1alpha1",
            namespace="p2code-scheduler-system",
            plural="p2codeschedulingmanifests",
            name=scheduling_manifest_name,
            body=client.V1DeleteOptions()
        )

        maestro_client.delete_service_order(id)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"client_error": e.args[0]}), 400

    if id in map_ns_to_so_ids:
        del map_ns_to_so_ids[id]
        print(f"    the serviceOrderId '{id}' is been cleaned from cache", flush=True)

    return jsonify({"status": 'OK'}), 200

@app.route('/uc3/deployments/<string:id>', methods=['PATCH'])
def update_app(id: str):

     # Ensure a file is uploaded
    if 'file' not in request.files:
        return jsonify({"error": "No descriptor in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No descriptor file selected"}), 400

    try:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d--%H:%M:%S')
        random_hash = uuid.uuid4().hex
        filename = f"{timestamp}_{random_hash}.yaml"
        save_path = os.path.join('/app/incoming-descriptors/update/', filename)

        file.save(save_path)
        file.seek(0)
        print("------> Descriptor saved at : ", save_path, flush=True)
    except Exception as e:
        traceback.print_exc()
        print("------> ACTUAL ERROR: ", str(e), flush=True)
        return jsonify({"translator_error": "filed to reach cache"}), 400

    try:
        ac3_im_yaml = yaml.safe_load(file.read().decode('utf-8'))
        application_name, version = translator.run(ac3_im_yaml, Path("./output_k8s_manifests").resolve())
    except Exception as e:
        traceback.print_exc()
        return jsonify({"translator_error": str(e)}), 400

    try:
        helm.helm_package_and_push(
            application_name,
            version,
            chart_path= str(Path("./output_k8s_manifests").resolve())
        )
    except Exception as e:
        return jsonify({"helm_error": str(e)}), 400

    res = None
    try:
        maestro_client.get_access_token_keycloak()
        res = maestro_client.get_service_order(id, False)
    except Exception as e:
        return jsonify({"client_error": e.args}), 400

    service_item_id = ""
    for order_item in res["serviceOrderItem"]:
        if order_item["service"]["name"] == "service-spec-end-user-cfs-ocm":
            service_item_id = order_item["service"]["id"]
            break

    if service_item_id == "":
        return jsonify({404: f"Service order with id '{id}', has no valid 'OCM' order item"}), 404

    try:
        service_item_body = maestro_client.get_service_inventory_item(service_item_id)
    except Exception as e:
        return jsonify({"client_error": e.args[0]}), 400

    try:
        is_version_found= False

        for index, service_char in enumerate(service_item_body["serviceCharacteristic"]):            
            if service_char["name"]== "Service artifact version":            
                if service_char["value"]["value"] == version:
                    return jsonify(
                        {
                            400: f"The Version '{version}' specified in OSR is the same as the current deployed version."
                        }
                    ), 400
                service_item_body["serviceCharacteristic"][index]["value"]["value"] = version

                is_version_found = True
                break

        if not is_version_found:
            return jsonify(
                {
                    "client_error": "Version information not found in the maestro service inventory context."
                }
            ), 404

        maestro_client.patch_service_inventory_item(service_item_id, service_item_body)
    except Exception as e:
        return jsonify({"client_error": e.args[0]}), 400

    return jsonify({"status": 'OK'}), 200

@app.route('/cluster_metadata', methods=['GET'])
def get_cluster_metadata():
    return jsonify(cluster_metadata=models.get_readable_cluster_metadata()), 200

@app.route('/cluster_metadata', methods=['PATCH'])
def set_cluster_metadata():
    if 'file' not in request.files:
        return jsonify({"error": "No cluster_metadata in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No cluster_metadata file selected"}), 400

    try:
        models.set_readable_cluster_metadata(file.read().decode('utf-8'))
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400
    
    return jsonify(status="New cluster metadata has been set"), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
