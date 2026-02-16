# IM translator

## Prerequire

```bash
nano ./.env
```

```bash
REPOSITORY_URL="https://gitlab.server.eu/org/projects/ac3/translated-descriptors.git"
REPOSITORY_PASS="a repo token"
REPOSITORY_BRANCH="main"

MAESTRO_HOST="https://maestro.domain.eu"
HOST_KEYCLOAK="https://maestro-keycloak.domain.eu"
KEYCLOAK_USER="a user"
KEYCLOAK_PASS="a password"

CLIENT_SECRET="KEYCLOAK CLIENT SECRET"
REGISTRY_URL="oci://registry.domain.eu/projects/ac3/translated-descriptors"
CLEAN_REGISTRY_URL="registry.domain.eu"

REMOTE_TRANSLATOR_URL="https://maestro-translator.domain.net"

ACCESS_TOKEN_USER="a valid username"
ACCESS_TOKEN_PASSWORD="a valid access token"
```

## How to run the server

1) Download the project to your machine:

```bash
git clone https://github.com/AC3-Ubitech/IM-TMF-Translator.git
    # or
git clone git@github.com:AC3-Ubitech/IM-TMF-Translator.git
```

2) Make sure that you are in `Server` branch:

```bash
git fetch
git checkout Server
git pull
```

3) Run the docker container that is hosting the `im-traslator` service:

```bash
cd ./im-translator
docker compose up --build -d
```

4) **(Optional)** If you want to monitor the container's logs, please use:

```bash
docker logs -f im-translator-server
```

#

### Tip:
To restart the service and to monitor the logs, please use:

```bash
 docker compose down && docker compose up --build -d && docker logs -f im-translator-server
```

#

## How to test the service

### A. The `wizzard.sh` script:

```bash
cd /path/to/project/scripts
chmod +x ./wizzard.sh
./wizzard.sh
```

Type 1/2 for local or remote testing:

```bash
Choose service mode:
  1) Local
  2) Remote
Enter choice (1/2):
```

1. The Create a new ServiceOrder type:  **1**

```bash
────────────────────────────────────────────────────────────────────
            Current reference 'ServiceOrderId' is: 'N/A'            
────────────────────────────────────────────────────────────────────

Select an action:
  1) CREATE SERVICE ORDER
  2) GET SERVICE ORDER STATUS
  3) UPDATE SERVICE ORDER
  4) DELETE SERVICE ORDER
  5) EXIT
Enter choice (1/2/3/4/5): 1
```

Then a similar output should be printed:

```bash
CREATE SERVICE ORDER
{
  "message": "A new service order is being processed by Maestro.",
  "serviceOrderId": "094dc7ef-88f3-48d9-860d-5697341d3b7c"
}
The serviceOrder created successfully, the reference ServiceOrderId set to '094dc7ef-88f3-48d9-860d-5697341d3b7c'
```

2. To monitor the status of the order use menu option 2:

```bash
──────────────────────────────────────────────────────────────────────────────────────────────────────
            Current reference 'ServiceOrderId' is: '094dc7ef-88f3-48d9-860d-5697341d3b7c'            
──────────────────────────────────────────────────────────────────────────────────────────────────────

Select an action:
  1) CREATE SERVICE ORDER
  2) GET SERVICE ORDER STATUS
  3) UPDATE SERVICE ORDER
  4) DELETE SERVICE ORDER
  5) EXIT
Enter choice (1/2/3/4/5): 2
```

The result should be something similar to:

```bash
GET SERVICE ORDER STATUS
The JSON result body is:
{
  "deploymentDetails": [
    {
      "IP": "172.xx.yy.zz",
      "name": "a-6c4f5b64bc-6bpwj",
      "status": "Running"
    },
    {
      "IP": "",
      "name": "s-557b67649b-xxbnm",
      "status": "Running"
    },
    {
      "IP": "172.xx.yy.zz",
      "name": "d-5fc94b987b-75d74",
      "status": "Running"
    },
    {
      "IP": "172.xx.yy.zz",
      "name": "f-f597694b5-wz724",
      "status": "Running"
    },
    {
      "IP": "172.xx.yy.zz",
      "name": "g-7589bf8d4b-qm4sv",
      "status": "Running"
    },
    {
      "IP": "172.xx.yy.zz",
      "name": "h-79cf858949-qrx8k",
      "status": "Running"
    },
    {
      "IP": "172.xx.yy.zz",
      "name": "j-8494965bf-q8r5h",
      "status": "Running"
    },
    {
      "IP": "",
      "name": "k-5fbc6465c5-9rw2z",
      "status": "Running"
    },
    {
      "IP": "172.xx.yy.zz",
      "name": "l-549d9fc8fd-vq4xz",
      "status": "Running"
    },
    {
      "IP": "",
      "name": "z-9688d7f7c-452vs",
      "status": "Running"
    },
    {
      "IP": "172.xx.yy.zz",
      "name": "x-74987fcf88-d55rq",
      "status": "Running"
    }
  ],
  "description": "A service order for application service",
  "serviceOrderId": "094dc7ef-88f3-48d9-860d-5697341d3b7c",
  "state": "COMPLETED"
}

Do you want to re-run 'GET SERVICE ORDER STATUS'? (y/n):
```

If the result is not similar and the `state` is `"PENDING"`, you can press `'y'` in order to re-run the status check in a non-exhausting way.

Otherwise you can press `'n'` to return to the main menu:

```bash
Do you want to re-run 'GET SERVICE ORDER STATUS'? (y/n): n

The service order status has been retrieved.

──────────────────────────────────────────────────────────────────────────────────────────────────────
            Current reference 'ServiceOrderId' is: '094dc7ef-88f3-48d9-860d-5697341d3b7c'            
──────────────────────────────────────────────────────────────────────────────────────────────────────

Select an action:
  1) CREATE SERVICE ORDER
  2) GET SERVICE ORDER STATUS
  3) UPDATE SERVICE ORDER
  4) DELETE SERVICE ORDER
  5) EXIT
Enter choice (1/2/3/4/5):
```

3. Update the service order:

Open a new terminal and:
```bash
#2nd terminal
cd /path/to/project/kubeconfigs
```

Check the k8s `svc`s of the deployed service:

```bash
#2nd terminal
watch kubectl get svc -n application --kubeconfig ./cluster-config.yaml
```

The result should be:

```bash
NAME  TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)                                        AGE
a     ClusterIP   172.xx.yy.zz  <none>        9191/TCP,9192/TCP,9292/TCP,9293/TCP,9393/TCP   6d1h
s     ClusterIP   172.xx.yy.zz  <none>        8200/TCP                                       6d1h
d     ClusterIP   172.xx.yy.zz  <none>        5000/TCP                                       14m
f     ClusterIP   172.xx.yy.zz  <none>        9090/TCP                                       14m
g     ClusterIP   172.xx.yy.zz  <none>        5672/TCP,15672/TCP                             27h
h     ClusterIP   172.xx.yy.zz  <none>        6379/TCP                                       27h
j     ClusterIP   172.xx.yy.zz  <none>        8080/TCP,9090/TCP                              27h
k     ClusterIP   172.xx.yy.zz  <none>        8080/TCP                                       27h
```

Please notice the ports: `8080`.

Now return to the `main terminal` and press: `'3'`:

```bash
──────────────────────────────────────────────────────────────────────────────────────────────────────
            Current reference 'ServiceOrderId' is: '094dc7ef-88f3-48d9-860d-5697341d3b7c'            
──────────────────────────────────────────────────────────────────────────────────────────────────────


Select an action:
  1) CREATE SERVICE ORDER
  2) GET SERVICE ORDER STATUS
  3) UPDATE SERVICE ORDER
  4) DELETE SERVICE ORDER
  5) EXIT
Enter choice (1/2/3/4/5): 3
```

```bash
UPDATING SERVICE ORDER
{
  "status": "OK"
}
The serviceOrder updated successfully

──────────────────────────────────────────────────────────────────────────────────────────────────────
            Current reference 'ServiceOrderId' is: '094dc7ef-88f3-48d9-860d-5697341d3b7c'            
──────────────────────────────────────────────────────────────────────────────────────────────────────

Select an action:
  1) CREATE SERVICE ORDER
  2) GET SERVICE ORDER STATUS
  3) UPDATE SERVICE ORDER
  4) DELETE SERVICE ORDER
  5) EXIT
Enter choice (1/2/3/4/5):
```

Notice that all `8080` ports on `2nd terminal` terminal are now `8081`

4. Delete the ServiceOrder and/or exit:

Press `'4'` to delete the serviceOrder and undeploy the previous deployed app (from step 1):

```bash
──────────────────────────────────────────────────────────────────────────────────────────────────────
            Current reference 'ServiceOrderId' is: '094dc7ef-88f3-48d9-860d-5697341d3b7c'            
──────────────────────────────────────────────────────────────────────────────────────────────────────

Select an action:
  1) CREATE SERVICE ORDER
  2) GET SERVICE ORDER STATUS
  3) UPDATE SERVICE ORDER
  4) DELETE SERVICE ORDER
  5) EXIT
Enter choice (1/2/3/4/5): 4

DELETE SERVICE ORDER
The JSON result body is:
{
  "status": "OK"
}
```

To exit the wizzard press `'5'`:

```bash
────────────────────────────────────────────────────────────────────
            Current reference 'ServiceOrderId' is: 'N/A'            
────────────────────────────────────────────────────────────────────

Select an action:
  1) CREATE SERVICE ORDER
  2) GET SERVICE ORDER STATUS
  3) UPDATE SERVICE ORDER
  4) DELETE SERVICE ORDER
  5) EXIT
Enter choice (1/2/3/4/5): 5

Exiting
```

### A. The manual way:

```bash
cd /apt/to/project/app_descriptors
```

1. Create a `serviceOrder`:

```bash
 curl -X POST -F "file=@uc3_descriptor.yaml" https://im-tmf-translator.domain.eu/uc3/deployments
```

```bash
{
  "message": "A new service order is being processed by Maestro.",
  "serviceOrderId": "8fc16e24-7f60-4389-a7b7-23fd3cb79790" # <-- copy this
}
```

2. Get Status:

```bash
curl -X GET https://im-tmf-translator.domain.eu/uc3/deployments/<service-order-id-from-create>
```

```bash
{
  "deploymentDetails": [
    {
      "IP": "172.xx.yy.zz",
      "name": "a-6c4f5b64bc-vnpf2",
      "status": "Running"
    },
    {
      "IP": "",
      "name": "experiment-tool-557b67649b-xxbnm",
      "status": "Running"
    },
    {
      "IP": "172.xx.yy.zz",
      "name": "s-5fc94b987b-75q88",
      "status": "Running"
    },
    {
      "IP": "172.xx.yy.zz",
      "name": "d-f597694b5-57rt8",
      "status": "Running"
    },
    {
      "IP": "172.xx.yy.zz",
      "name": "f-7589bf8d4b-xnh8t",
      "status": "Running"
    },
    {
      "IP": "172.xx.yy.zz",
      "name": "g-79cf858949-965cq",
      "status": "Running"
    },
    {
      "IP": "172.xx.yy.zz",
      "name": "h-8494965bf-zdvkd",
      "status": "Running"
    },
    {
      "IP": "",
      "name": "transfer-5fbc6465c5-wkrz7",
      "status": "Running"
    },
    {
      "IP": "172.xx.yy.zz",
      "name": "uc3-frontend-549d9fc8fd-llck7",
      "status": "Running"
    },
    {
      "IP": "",
      "name": "ucm-processor-deployment-9688d7f7c-fzks2",
      "status": "Pending"
    },
    {
      "IP": "172.xx.yy.zz",
      "name": "ucm-producer-deployment-74987fcf88-hlnjw",
      "status": "Running"
    }
  ],
  "description": "A service order for application service",
  "serviceOrderId": "8fc16e24-7f60-4389-a7b7-23fd3cb79790",
  "state": "COMPLETED"
}
```

3. Update the ServiceOrder:

```bash
curl -X PATCH -F "file=@updated_uc3_descriptor.yaml" https://im-tmf-translator.domain.eu/uc3/deployments/<service-order-id-from-create>
```

```bash
{
  "status": "OK"
}
```

4. Delete the ServiceOrder:

```bash
 curl -X DELETE https://im-tmf-translator.domain.eu/uc3/deployments/<service-order-id-from-create>
```

```bash
{
  "status": "OK"
}
```

> Notice: instead of `https://im-tmf-translator.domain.eu` you can use `http://127.0.0.1:5000` to test the local environment.


## References:

The latest valid inputs for `im-translator` service can be fount on [here](./app_descriptors/uc3_descriptor.yaml). There is also a version that differs slightly in terms of data (not schema) under [this link](./app_descriptors/updated_uc3_descriptor.yaml). The second one can be used to perform an update to an already deployed service.
