import base64
from datetime import datetime, timezone

cluster_metadata = "YXBpVmVyc2lvbjogc2NoZWR1bGluZy5wMmNvZGUuZXUvdjFhbHBoYTEKa2luZDogUDJDb2RlU2NoZWR1bGluZ01hbmlmZXN0Cm1ldGFkYXRhOgogIGxhYmVsczoKICAgIGFwcC5rdWJlcm5ldGVzLmlvL25hbWU6IHAyY29kZS1zY2hlZHVsZXIKICAgIGFwcC5rdWJlcm5ldGVzLmlvL21hbmFnZWQtYnk6IGt1c3RvbWl6ZQogIG5hbWU6IHRyYW5zbGF0ZWQtYXBwCiAgbmFtZXNwYWNlOiBwMmNvZGUtc2NoZWR1bGVyLXN5c3RlbQpzcGVjOgogIGdsb2JhbEFubm90YXRpb25zOgogICAgLSAicDJjb2RlLnRhcmdldC5tYW5hZ2VkQ2x1c3RlclNldD1hYzMiCiAgICAtICJwMmNvZGUudGFyZ2V0LmNsdXN0ZXI9Y2x1c3Rlci00Igo="

def get_base64_cluster_metadata() -> str:
    return cluster_metadata

def get_readable_cluster_metadata() -> str:
    return base64.b64decode(cluster_metadata).decode("utf-8")

def set_readable_cluster_metadata(yaml_txt : str):
    global cluster_metadata
    cluster_metadata = base64.b64encode(yaml_txt.encode("utf-8")).decode("utf-8")

def produce_service_order_payload(applicationName :str, version :str) -> dict:
    service_current_iso_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        # "id": str(uuid.uuid4()),
        "orderDate": service_current_iso_time,
        "completionDate": None,
        "expectedCompletionDate": "2026-11-15T16:30:53Z",
        "requestedCompletionDate": "2026-11-15T16:30:53Z",
        "requestedStartDate": service_current_iso_time,
        "startDate": service_current_iso_time,
        "@baseType": "BaseRootEntity",
        "state": "INITIAL",
        "@schemaLocation": None,
        "@type": "ServiceOrder",
        "href": None,
        "category": None,
        "description": f"A service order for {applicationName} service",
        "externalId": None,
        "notificationContact": None,
        "priority": None,
        "note": [],
        "serviceOrderItem": [
            {
                "@baseType": "BaseEntity",
                "@schemaLocation": None,
                "@type": None,
                "href": None,
                "action": "add",
                "orderItemRelationship": [],
                "state": "ACKNOWLEDGED",
                "service": {
                    "serviceSpecification": {
                        "@baseType": "BaseEntity",
                        "@schemaLocation": None,
                        "@type": None,
                        "href": None,
                        "name": "service-spec-end-user-cfs-ocm",
                        "version": "1.2.0",
                        "targetServiceSchema": None,
                        "@referredType": None,
                        "id": "e76d354c-36c9-485f-b75a-c7b9be689e4c"
                    },
                    "@baseType": "BaseEntity",
                    "@schemaLocation": None,
                    "@type": None,
                    "href": None,
                    "name": "service-spec-end-user-cfs-ocm",
                    "category": None,
                    "serviceType": None,
                    "place": [],
                    "relatedParty": [],
                    "serviceCharacteristic": [
                        {
                            "@baseType": "BaseRootEntity",
                            "@schemaLocation": None,
                            "@type": None,
                            "href": None,
                            "name": "Service name",
                            "valueType": "TEXT",
                            "value": {
                                "value": "Starlight App",
                                "alias": None
                            }
                        },
                        {
                            "@baseType": "BaseRootEntity",
                            "@schemaLocation": None,
                            "@type": None,
                            "href": None,
                            "name": "Service package manager",
                            "valueType": "ENUM",
                            "value": {
                                "value": "helm",
                                "alias": None
                            }
                        },
                        {
                            "@baseType": "BaseRootEntity",
                            "@schemaLocation": None,
                            "@type": None,
                            "href": None,
                            "name": "Base service registry/repository URL",
                            "valueType": "TEXT",
                            "value": {
                                "value": "oci://registry.ubitech.eu/nsit/eu-projects/ac3/translated-descriptors/",
                                "alias": None
                            }
                        },
                        {
                            "@baseType": "BaseRootEntity",
                            "@schemaLocation": None,
                            "@type": None,
                            "href": None,
                            "name": "Service artifact identifier in service registry/repository",
                            "valueType": "TEXT",
                            "value": {
                                "value": applicationName,
                                "alias": None
                            }
                        },
                        {
                            "@baseType": "BaseRootEntity",
                            "@schemaLocation": None,
                            "@type": None,
                            "href": None,
                            "name": "Service artifact version",
                            "valueType": "TEXT",
                            "value": {
                                "value": version,
                                "alias": None
                            }
                        },
                        {
                            "@baseType": "BaseRootEntity",
                            "@schemaLocation": None,
                            "@type": None,
                            "href": None,
                            "name": "Cluster Manager",
                            "valueType": "ENUM",
                            "value": {
                                "value": "ocm",
                                "alias": None
                            }
                        },
                        {
                            "@baseType": "BaseRootEntity",
                            "@schemaLocation": None,
                            "@type": None,
                            "href": None,
                            "name": "Cluster Metadata",
                            "valueType": "TEXT",
                            "value": {
                                "value": cluster_metadata,
                                "alias": None
                            }
                        }
                    ],
                    "state": "feasibilityChecked",
                    "supportingResource": [],
                    "serviceRelationship": [],
                    "supportingService": []
                },
                "appointment": None
            },
            {
                "@baseType": "BaseEntity",
                "@schemaLocation": None,
                "@type": None,
                "href": None,
                "action": "add",
                "orderItemRelationship": [],
                "state": "ACKNOWLEDGED",
                "service": {
                    "serviceSpecification": {
                        "@baseType": "BaseEntity",
                        "@schemaLocation": None,
                        "@type": None,
                        "href": None,
                        "name": "AC3-K8aaS-OCM:Openslice-athens",
                        "version": "1.2.0",
                        "targetServiceSchema": None,
                        "@referredType": None,
                        "id": "91559075-eacb-40e5-bdca-adf4c6174288"
                    },
                    "@baseType": "BaseEntity",
                    "@schemaLocation": None,
                    "@type": None,
                    "href": None,
                    "name": "AC3-K8aaS-OCM:Openslice-athens",
                    "category": None,
                    "serviceType": None,
                    "place": [],
                    "relatedParty": [],
                    "serviceCharacteristic": [
                        {
                            "@baseType": "BaseRootEntity",
                            "@schemaLocation": None,
                            "@type": None,
                            "href": None,
                            "name": "Number of worker nodes",
                            "valueType": "TEXT",
                            "value": {
                                "value": "1",
                                "alias": None
                            }
                        }
                    ],
                    "state": "feasibilityChecked",
                    "supportingResource": [],
                    "serviceRelationship": [],
                    "supportingService": []
                },
                "appointment": None
            }
        ],
        "orderRelationship": [],
        "relatedParty": [
            {
                "@baseType": "BaseRootEntity",
                "@schemaLocation": None,
                "@type": None,
                "href": None,
                "name": "UBITECH",
                "role": "REQUESTER",
                "@referredType": "SimpleUsername_Individual",
                "id": "2c034f2b-4ecc-44cc-9af3-6633aa96b217",
                "extendedInfo": None
            }
        ]
    }

def produce_response_get_service_order_by_id(res: dict) -> dict:
    return {
        "state": res["state"],
        "description": res["description"],
        "serviceOrderId": res["id"],
        "deploymentDetails": []
    }