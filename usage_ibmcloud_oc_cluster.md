---
nav_order: 10
---

# Usage: Managing Red Hat OpenShift on IBM Cloud clusters

## Registering an existing Red Hat OpenShift on IBM Cloud cluster

### Syntax

```shell
cpo ibmcloud oc cluster add [OPTIONS]
```

### Parameters

```
  --alias TEXT                    Alias used to reference a cluster instead of
                                  its server URL
  --cluster-name TEXT             Name of the Red Hat OpenShift on IBM Cloud
                                  cluster to be registered  [required]
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --help                          Show this message and exit.
```

## Deleting a Red Hat OpenShift on IBM Cloud cluster

### Syntax

```shell
cpo ibmcloud oc cluster rm [OPTIONS]
```

### Parameters

```
  --cluster-name TEXT             Name of the Red Hat OpenShift on IBM Cloud
                                  cluster to be deleted  [required]
  --force                         Skip confirmation
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --help                          Show this message and exit.
```

## Listing Red Hat OpenShift on IBM Cloud clusters

### Syntax

```shell
cpo ibmcloud oc cluster ls [OPTIONS]
```

### Parameters

```
  --json                          Prints the command output in JSON format
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --help                          Show this message and exit.
```

## Logging in to a Red Hat OpenShift on IBM Cloud cluster

### Syntax

```shell
cpo ibmcloud oc cluster login [OPTIONS]
```

### Parameters

```
  --cluster-name TEXT             cluster name  [required]
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --help                          Show this message and exit.
```

## Displaying the status of a Red Hat OpenShift on IBM Cloud cluster

### Syntax

```shell
cpo ibmcloud oc cluster status [OPTIONS]
```

### Parameters

```
  --cluster-name TEXT             cluster name  [required]
  --json                          Prints the command output in JSON format
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --help                          Show this message and exit.
```
