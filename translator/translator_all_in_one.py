# from importlib.metadata import metadata

import os
import re
import yaml
import uuid
from .utils.string_helpers import *
from .utils.yaml_helpers import *


def generate_deployments_services_k8s_manifest(input_yaml, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    #namespace
    app_namespace=input_yaml.get("ApplicationName")
    # SLAs
    global_SLAs={}
    if input_yaml.get("SLAs"):
        for SLAs_key, SLAs_value in input_yaml["SLAs"].items():
            formatted_key = f"global.sla.{SLAs_key[0].lower() + SLAs_key[1:]}"
            global_SLAs[formatted_key] = SLAs_value

    # Deployments and services yaml files for Microservices based on input IM
    for service in input_yaml.get("Microservices", []):
        ##### deployment yaml #####

        sla_annotations = {}
        metadata = {}
        metadata["namespace"] = app_namespace

        # ----> NOTE: Seems not used anymore (poulo)
        slas = service.get("MicroservicesSLAs", {})
        if slas:
            sla_annotations = {
                "sla.serviceAvailability": str(slas.get("ServiceAvailability", "N/A")),
                #"sla.maxResponseTime": f'"{slas.get("MaxResponseTime", "N/A")}"',
                "sla.maxResponseTime": str(slas.get("MaxResponseTime", "N/A")),
                "sla.dataThroughput": str(slas.get("DataThroughput", "N/A")),
            }


            metadata["name"] = service["MicroserviceName"]
            metadata["annotations"] = sla_annotations
        else:
            metadata["name"] = service["MicroserviceName"]

        if global_SLAs:
            metadata["annotations"] = {**metadata["annotations"], **global_SLAs}

        # Extract command if available
        #container_command = service.get("Command", [])

        # ----> NOTE: Seems not used anymore
        container_command = service.get("Command", [])
        if isinstance(container_command, str):  # Convert single string to list
            container_command = [container_command]


        deployment_manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": metadata,
            "spec": {
                # "replicas": int(service["ReplicaCount"]), # ----> NOTE: Seems ReplicaCount not be used anymore
                "replicas": 1,
                "selector": {"matchLabels": {"app": service["MicroserviceName"]}},
                "template": {
                    "metadata": {"labels": {"app": service["MicroserviceName"]}},
                    "spec": {

                        "serviceAccountName": service.get("ServiceAccountName", ""), # ----> NOTE: this seems to be generated only to `deployment_processor.yaml`

                        "volumes": [{
                            "name": volume["Name"],
                            "persistentVolumeClaim": {
                                "claimName": volume["VolumeSource"]["PersistentVolumeClaim"]["ClaimName"]}
                        } for volume in service.get("Volumes", []) if volume.get("Name")],



                        "initContainers": [{
                            "name": init["Name"],
                            "image": init["Image"],
                            "command": transform_command(init["Command"]),
                            "securityContext": {
                                "privileged": service.get("SecurityContext", {}).get("privileged", False)},
                            "volumeMounts": [{
                                "mountPath": mount["MountPath"],
                                "name": mount["Name"]
                            } for mount in init.get("volumeMounts", []) if mount.get("MountPath")]
                        } for init in service.get("InitContainers", []) if init.get("Name")],  # ----> NOTE: this seems not be present in any example

                        "containers": [{
                            "name": service["MicroserviceName"],
                            "image": service["Image"],
                            "securityContext": {
                                "privileged": service.get("SecurityContext", {}).get("Privileged", False)
                            },
                            "workingDir": service.get("WorkingDirectory", ""), #  ----> NOTE: `OSR` descriptor seems not containing any similar field but the some of the generated manifests are having `WorkingDirs`
                            "command": container_command if container_command else [],  # Add command if available
                            #"command": f'{container_command}' if container_command else None,  # Add command if available
                            "resources": {
                                "limits": { #  ----> NOTE: `OSR` descriptor seems not containing any similar field but some of the generated manifests are having `limits`
                                    "cpu": "{}m".format(int(float(re.search(r"[0-9.]+", service['ResourceRequirements']['Cpu']).group()) * 1000)), #CPU to millicores

                                    "memory": service["ResourceRequirements"]["Memory"]
                                    #"memory": f'"{service["ResourceRequirements"]["Memory"]}"'
                                }
                            },
                            "env": [{"name": env["Name"], "value": env["Value"]} for env in
                                    service.get("EnvironmentVariables", [])],
                            "ports": [{"containerPort": int(port["ContainerPort"])} for port in
                                      service.get("apiPort", [])], #  ----> NOTE: Ports is renamed to apiPort and its entries are in form "'1234:4567'" instead of "ContainerPort: 1234"
                        }],
                        
                        
                    }
                }
            }
        }
        #deployment_manifest = {key: value for key, value in deployment_manifest.items() if value is not None}

        # delete empty values
        for container in deployment_manifest["spec"]["template"]["spec"]["containers"]:
            if "env" in container and not container["env"]:
                del container["env"]
            if "workingDir" in container and not container["workingDir"]:
                del container["workingDir"]

            if "ports" in container and not container["ports"]:
                del container["ports"]

        save_yaml(deployment_manifest, os.path.join(output_dir, f"{service['MicroserviceName']}-deployment.yaml"))

        ##### service yaml #####
        if "Ports" in service:  # and service["ports"]:

            service_manifest = {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {"name": service["MicroserviceName"], "labels": {"app": service["MicroserviceName"]},"namespace": app_namespace},
                "spec": {
                    "ports": [{
                        "port": int(port["ContainerPort"]),
                        "targetPort": int(port["ContainerPort"]),
                        "protocol": "TCP",
                        "name": f"port-{port['ContainerPort']}"
                    } for port in service.get("Ports", [])], #  ----> NOTE: Ports is renamed to apiPort and its entries are in form "'1234:4567'" instead of "ContainerPort: 1234"
                    "selector": {"app": service["MicroserviceName"]}
                }
            }
            save_yaml(service_manifest, os.path.join(output_dir, f"{service['MicroserviceName']}-service.yaml"))

            # if "InitContiainers" in service:
            #     deployment_manifest["spec"]["template"]["spec"]["containers"][0]["command"] = service["command"]


def generate_k8s_pv_pvc_manifests(input_yaml, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    app_namespace = input_yaml.get("ApplicationName")
    # Persistent Volume and PVC based on input IM
    for volume in input_yaml.get("Volumes_configuration", []):
        pv_manifest = {
            "apiVersion": "v1",
            "kind": "PersistentVolume",
            "metadata": {"name": volume["VolumeName"]},
            "spec": {
                "storageClassName": volume["StorageClass"],
                "capacity": {"storage": volume["Capacity"]},
                "accessModes": volume["AccessModes"],
                #"hostPath": {"path": f'"{volume["HostPath"]["Path"]}"'}
                "hostPath": {"path": volume["HostPath"]["Path"]}
            }
        }
        save_yaml(pv_manifest, os.path.join(output_dir, f"{volume['VolumeName']}-pv.yaml"))

        pvc_manifest = {
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {"name": volume["ClaimName"], "namespace": app_namespace},
            # "spec": {k[:1].lower() + k[1:]: v for k, v in volume["ClaimSpec"].items()} #first leter of each key to lowercase
            "spec": lowercase_keys(volume["ClaimSpec"])
        }
        save_yaml(pvc_manifest, os.path.join(output_dir, f"{volume['ClaimName']}-pvc.yaml"))


def generate_k8s_sa_rb_manifests(input_yaml, output_dir):
    # Security YAML files based on input IM
    os.makedirs(output_dir, exist_ok=True)
    app_namespace = input_yaml.get("ApplicationName")
    for security in input_yaml.get("Security_configuration", []):
        if security["Kind"] == "ServiceAccount":
            sa_manifest = {
                "apiVersion": security["ApiVersion"],
                "kind": "ServiceAccount",
                "metadata": {"name": security["Metadata"]["Name"], "namespace": app_namespace}
            }
            save_yaml(sa_manifest, os.path.join(output_dir, f"{security['Metadata']['Name']}-sa.yaml"))
        elif security["Kind"] == "RoleBinding":
            rb_manifest = {
                "apiVersion": security["ApiVersion"],
                "kind": "RoleBinding",
                "metadata": {"name": security["Metadata"]["Name"], "namespace": app_namespace},
                "roleRef": {"apiGroup": security["RoleRef"]["ApiGroup"], "kind": security["RoleRef"]["Kind"],
                            "name": security["RoleRef"]["Name"]},
                "subjects": [{"kind": sub["Kind"], "name": sub["Name"]} for sub in security["Subjects"]]

            }
            save_yaml(rb_manifest, os.path.join(output_dir, f"{security['Metadata']['Name']}-rb.yaml"))


def generate_namespace_k8s_manifest(input_yaml, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    #namespace
    app_namespace=input_yaml.get("ApplicationName")
    namespace_manifest = {
        "apiVersion": "v1",
        "kind": "Namespace",
        "metadata": {
            "name": app_namespace,
            "annotations":{
                "maestro.reference": str(uuid.uuid4())
            }
        }
    }

    save_yaml(namespace_manifest, os.path.join(output_dir, f"{app_namespace}-namespace.yaml"))


def generate_chart_yaml_k8s_manifest(output_dir):
    os.makedirs(output_dir, exist_ok=True)

    #namespace
    namespace_manifest = {
        "apiVersion": "v2",
        "name": "im-translator",
        "description": "A Helm chart for IM Translator",
        "type": "application",
        "version": "1.0.0",
        "appVersion": "1.0.0"
    }

    save_yaml(namespace_manifest, os.path.join(output_dir, "Chart.yaml"))


if __name__ == "__main__":
    #ac3_im_yaml = load_yaml("uc3-descriptor-orch.yml")
    ac3_im_yaml = load_yaml("../app_descriptors/uc3-descriptor-all-in-one.yml")
    generate_k8s_pv_pvc_manifests(ac3_im_yaml, "output_k8s_manifests/ templates")
    generate_k8s_sa_rb_manifests(ac3_im_yaml, "output_k8s_manifests/templates")
    generate_deployments_services_k8s_manifest(ac3_im_yaml, "output_k8s_manifests/templates")
    generate_namespace_k8s_manifest(ac3_im_yaml, "output_k8s_manifests/templates")
    generate_chart_yaml_k8s_manifest("output_k8s_manifests")

    print("Kubernetes manifests have been generated within 'output_k8s_manifests' directory")
