---
nav_order: 5
---

# Usage: Install various operators

## Installing the Node Feature Discovery Operator

This command installs the [Node Feature Discovery Operator](https://docs.openshift.com/container-platform/latest/hardware_enablement/psap-node-feature-discovery-operator.html)

### Syntax

```shell
cpo aws operator install-node-feature-discovery-operator [OPTIONS]
```

### Parameters

```
  --server TEXT                   OpenShift server URL
  --username TEXT                 OpenShift username
  --password TEXT                 OpenShift password
  --token TEXT                    OpenShift OAuth access token
  --insecure-skip-tls-verify      Skips checking the server's certificate for
                                  validity
  --use-cluster TEXT              Alias or server URL of a registered
                                  OpenShift cluster to be used
  --project TEXT                  OpenShift project  [default: openshift-nfd]
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --help                          Show this message and exit.
```

## Installing the NVIDIA GPU Operator

This command installs the [NVIDIA GPU Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/index.html).

### Syntax

```shell
cpo aws operator install-nvidia-gpu-operator [OPTIONS]
```

### Parameters

```
  --server TEXT                   OpenShift server URL
  --username TEXT                 OpenShift username
  --password TEXT                 OpenShift password
  --token TEXT                    OpenShift OAuth access token
  --insecure-skip-tls-verify      Skips checking the server's certificate for
                                  validity
  --use-cluster TEXT              Alias or server URL of a registered
                                  OpenShift cluster to be used
  --project TEXT                  OpenShift project  [default: nvidia-gpu-
                                  operator]
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --help                          Show this message and exit.
```
