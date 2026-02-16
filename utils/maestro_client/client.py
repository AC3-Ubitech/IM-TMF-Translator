import os
import requests
from . import models
from typing import Optional


class MaestroTranslatorClient:

    def __init__(self):

        self.host                                       = os.environ["MAESTRO_HOST"]
        self.host_keycloak                              = os.environ["HOST_KEYCLOAK"]
        self.session                                    = requests.Session()
        self.access_token : Optional[requests.Session]  = None

    def get_access_token_keycloak(self) -> requests.Response:

        url = f"{self.host_keycloak}/realms/tmf/protocol/openid-connect/token"
        payload = {
            "client_id": "tmf-api",
            "client_secret": os.environ["CLIENT_SECRET"],
            "grant_type": "password",
            "username": os.environ["KEYCLOAK_USER"],
            "password": os.environ["KEYCLOAK_PASS"],
        }
 
        headers = {
          'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = self.session.post(url, data=payload, headers=headers)
        response.raise_for_status()

        token_data = response.json()
        self.access_token = token_data.get("access_token")
        if not self.access_token:
            raise ValueError("Failed to retrieve access_token from Keycloak response.")

        # Update the session headers for future authenticated requests
        self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})

        return response

    def create_service_order(self, applicationName, version) -> str:

        if self.access_token is None:
            raise PermissionError(
                "Access token not available. Please call 'get_access_token_keycloak' first."
            )

        url = f"{self.host}/tmf-api/serviceOrdering/v4/serviceOrder"
        payload_model = models.produce_service_order_payload(applicationName, version)

        headers = {
          'Content-Type': 'application/json'
        }

        response = self.session.post(url, json=payload_model, headers=headers)
        if response.status_code < 200 or response.status_code >= 300:
            raise ConnectionError({response.status_code: response.json()["message"]})

        return response.json()["id"]

    def get_service_order(self, service_order_id: str, as_get_response : bool = True) -> dict:

        url = f"{self.host}/tmf-api/serviceOrdering/v4/serviceOrder/{service_order_id}"

        response = self.session.get(url)
        if response.status_code < 200 or response.status_code >= 300:
            raise ConnectionError({response.status_code: response.json()["message"]})

        if as_get_response:
            return models.produce_response_get_service_order_by_id(response.json())
        return response.json()

    def delete_service_order(self, service_order_id: str):

        url = f"{self.host}/tmf-api/serviceOrdering/v4/serviceOrder/{service_order_id}"

        response = self.session.delete(url)
        if response.status_code < 200 or response.status_code >= 300:
            print(f"    ---------> Error during deleting '{response.status_code}'.", flush=True)
            raise ConnectionError({response.status_code: response.json()})

    def get_service_inventory_item(self, service_id: str) -> dict:

        url = f"{self.host}/tmf-api/serviceInventory/v4/service/{service_id}"

        response = self.session.get(url)
        if response.status_code < 200 or response.status_code >= 300:
            raise ConnectionError({response.status_code: response.json()["message"]})

        return response.json()

    def patch_service_inventory_item(self, service_id: str, service_order_item: dict):

        url = f"{self.host}/tmf-api/serviceInventory/v4/service/{service_id}"

        response = self.session.patch(url, json=service_order_item)
        if response.status_code < 200 or response.status_code >= 300:
            raise ConnectionError({response.status_code: response.json()["message"]})