---
nav_order: 7
---

# Usage: Managing the global pull secret

## Storing registry credentials in the global pull secret

### Syntax

```shell
cpo cluster pull-secret set [OPTIONS]
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
  --registry-location TEXT        Container registry location  [required]
  --registry-location-username TEXT
                                  Container registry username  [required]
  --registry-location-password TEXT
                                  Container registry password  [required]
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --help                          Show this message and exit.
```

## Removing registry credentials from the global pull secret

### Syntax

```shell
cpo cluster pull-secret rm [OPTIONS]
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
  --registry-location TEXT        Container registry location  [required]
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --help                          Show this message and exit.
```

## Listing registry credentials stored in the global pull secret

### Syntax

```shell
cpo cluster pull-secret ls [OPTIONS]
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
  --json                          Prints the command output in JSON format
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --help                          Show this message and exit.
```
