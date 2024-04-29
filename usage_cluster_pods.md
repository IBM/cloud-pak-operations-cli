---
nav_order: 6
---

# Usage: Managing pods

## Deleting terminated pods

This command deletes completed (both succeeded and failed) pods.

### Syntax

```shell
cpo cluster pods delete-terminated-pods [OPTIONS]
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
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --help                          Show this message and exit.
```
