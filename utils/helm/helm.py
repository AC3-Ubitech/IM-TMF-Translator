import os
import subprocess

def helm_package_and_push(
    application_name: str,
    version: str,
    chart_path: str = "."
) -> bool:

    registry_url = os.environ["REGISTRY_URL"]
    try:
        package_cmd = ["helm", "package", chart_path]
        subprocess.run(package_cmd, check=True)
        print("Helm chart packaged successfully.")

        push_cmd = ["helm", "push", f"{application_name}-{version}.tgz", registry_url]
        subprocess.run(push_cmd, check=True)
        print(f"Pushed {application_name}-{version}.tgz to {registry_url}")

        return True

    except Exception as e:
        print(f"Error during Helm packaging or push: {e}")
        return False
