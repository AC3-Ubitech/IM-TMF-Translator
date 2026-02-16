import os
import yaml
import uuid
import shutil
from typing import Tuple
from pathlib import Path
from string import Template

def load_yaml(file_path): # load yaml file
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def save_yaml(data, file_path): #save yaml file
    with open(file_path, 'w') as file:
        file.write(data)


TEMPLATE_DIR = "app_descriptors/templates"

def generate_deployments_services_k8s_manifest(input_yaml, output_dir):
    #namespace
    app_namespace=input_yaml.get("ApplicationName")

    # Deployments and services yaml files for Microservices based on input IM
    for svc in input_yaml.get("Microservices", []):

        data={}
        data["ApplicationName"] = app_namespace

        if "apiPort" in svc:
            for idx, port in enumerate(svc["apiPort"], start=1):
                data[f"ApiPort{idx}"]=port.split(":")[0]

        if "SecurityContext" in svc:
            data["SecurityContextPrivileged"] = str(svc["SecurityContext"]["privileged"]).lower()

        if "Volumes" in svc and "Volume Source" in svc["Volumes"][0]:
            data["PersistentVolumeClaimName"] = svc["Volumes"][0]["Volume Source"]["Persistent Volume Claim"]["Claim Name"]

        if "VolumeMounts" in svc:
            data["VolumeMountPath"] = svc["VolumeMounts"][0]["MountPath"]

        svc_name = svc["MicroserviceName"]
        print(f"Rendering Deployment manifests for microservice: {svc_name}")
        tpl_path = f"{TEMPLATE_DIR}/deployment-{svc_name}.yaml"

        with open(tpl_path) as f:
            tpl_content = f.read()

        deployment_manifest = Template(tpl_content).safe_substitute({**data, **svc})

        save_yaml(deployment_manifest, os.path.join(output_dir, f"templates/deployment-{svc['MicroserviceName']}.yaml"))

        if "EnvironmentVariables" in svc:
            if "SCALING_VAR" in svc["EnvironmentVariables"] and "SCALING_THRESHOLD" in svc["EnvironmentVariables"]:
                scaling_var = svc["EnvironmentVariables"]["SCALING_VAR"]
                scaling_threshold = svc["EnvironmentVariables"]["SCALING_THRESHOLD"]
                generate_hpa_manifest(svc_name, app_namespace, scaling_var, scaling_threshold, output_dir)

def generate_k8s_pv_pvc_manifests(input_yaml, output_dir):
    app_namespace = input_yaml.get("ApplicationName")

    # with open(f"{TEMPLATE_DIR}/volume.yaml") as f:
    #     tpl_volume = f.read()

    with open(f"{TEMPLATE_DIR}/volumeclaim.yaml") as f:
        tpl_volume_claim = f.read()

    for volume in input_yaml.get("VolumesConfiguration", []):

        # volume_name = volume["VolumeName"]
        claim_name  = volume["ClaimName"]
        claim_spec_storage = volume["ClaimSpec"]["Storage Class Name"]

        print(f"Rendering VolumeClaim manifests for volume: {claim_name}")

        # volume_manifest       = Template(tpl_volume).safe_substitute({"ApplicationName": app_namespace,**volume})
        volume_claim_manifest = Template(tpl_volume_claim).safe_substitute({"ApplicationName": app_namespace, "ClaimSpecStorage": claim_spec_storage, **volume})

        # save_yaml(volume_manifest, os.path.join(output_dir, f"templates/volume-{volume_name}.yaml"))
        save_yaml(volume_claim_manifest, os.path.join(output_dir, f"templates/volume-claim-{claim_name}.yaml"))

def generate_k8s_sa_rb_manifests(input_yaml, output_dir):
    app_namespace = input_yaml.get("ApplicationName")

    with open(f"{TEMPLATE_DIR}/service-account.yaml") as f:
        tpl_service_account = f.read()
    service_account_manifest = Template(tpl_service_account).safe_substitute({"ApplicationName": app_namespace})
    save_yaml(service_account_manifest, os.path.join(output_dir, f"templates/service-account.yaml"))

    for security in input_yaml.get("SecurityConfiguration", []):
        role_bind_name  = security["RoleBindingName"]
        print(
            f"Rendering Service Account & Role Binding manifests for role bind name: {role_bind_name}"
        )

        with open(f"{TEMPLATE_DIR}/role-bind-{role_bind_name}.yaml") as f:
            tpl_role_binding = f.read()

        role_binding_manifest    = Template(tpl_role_binding).safe_substitute({"ApplicationName": app_namespace, **security})
        save_yaml(role_binding_manifest, os.path.join(output_dir, f"templates/role-bind-{role_bind_name}.yaml"))

def generate_namespace_k8s_manifest(input_yaml, output_dir):

    app_namespace = input_yaml.get("ApplicationName")

    with open(f"{TEMPLATE_DIR}/namespace.yaml") as f:
        tpl_name_space = f.read()
        
    print("Rendering Namespace manifests")

    volume_manifest = Template(tpl_name_space).safe_substitute({"ApplicationName": app_namespace, "uuid": str(uuid.uuid4())})

    save_yaml(volume_manifest, os.path.join(output_dir, f"templates/namespace.yaml"))

def generate_chart_yaml_k8s_manifest(output_dir):
    shutil.copyfile(f"{TEMPLATE_DIR}/Chart.yaml", f"{output_dir}/Chart.yaml")

def generate_asset_manifest(input_yaml, output_dir):
    app_namespace = input_yaml.get("ApplicationName")
    version = input_yaml.get("Version")

    for manifest_template in ["service-monitor-metrics", "Chart"]: #, "horizontal-pod-autoscaler"]:
        with open(f"{TEMPLATE_DIR}/{manifest_template}.yaml") as f:
            tpl_asset = f.read()

        print(f"Rendering Asset manifests for: {manifest_template}.yaml")

        asset_manifest = Template(tpl_asset).safe_substitute({"ApplicationName": app_namespace, "Version": version})
        
        if manifest_template == "Chart":
            save_yaml(asset_manifest, os.path.join(output_dir, f"{manifest_template}.yaml"))
        else:
            save_yaml(asset_manifest, os.path.join(output_dir, f"templates/{manifest_template}.yaml"))

def generate_hpa_manifest(microservice_name :str, app_namespace :str, scaling_var: str, scaling_threshold: str, output_dir :str):
    with open(f"{TEMPLATE_DIR}/horizontal-pod-autoscaler.yaml") as f:
        tpl_asset = f.read()

    print(f"Rendering HPA manifests for: horizontal-pod-autoscaler.yaml")

    asset_manifest = Template(tpl_asset).safe_substitute({"ApplicationName": app_namespace, "ScalingThreshold":scaling_threshold, "ScalingVar": scaling_var})
    save_yaml(asset_manifest, os.path.join(output_dir, f"templates/{microservice_name}-{app_namespace}-hpa.yaml"))

def run(
        ac3_im_yaml = "../app_descriptors/OSR_app_descriptor_uc3.yaml",
        output_dir = "../output_k8s_manifests"
    ) -> Tuple[str, str]:

    if Path(f"{output_dir}/templates").exists():
        shutil.rmtree(f"{output_dir}/templates")
    os.makedirs(f"{output_dir}/templates", exist_ok=True)

    generate_k8s_pv_pvc_manifests(ac3_im_yaml, output_dir)
    generate_k8s_sa_rb_manifests(ac3_im_yaml, output_dir)
    generate_namespace_k8s_manifest(ac3_im_yaml, output_dir)
    generate_deployments_services_k8s_manifest(ac3_im_yaml, output_dir)
    generate_asset_manifest(ac3_im_yaml, output_dir)

    # generate_chart_yaml_k8s_manifest("../output_k8s_manifests")

    print("Kubernetes manifests have been generated within 'output_k8s_manifests' directory")

    return ac3_im_yaml.get("ApplicationName"), ac3_im_yaml.get("Version")

if __name__ == "__main__":
    run()
