---
nav_order: 4
---

# Usage: Managing clusters

## Registering an existing Red Hat OpenShift cluster

### Syntax

```shell
cpo cluster add [OPTIONS]
```

This command registers an existing Red Hat OpenShift cluster. The provided data is stored in `~/.cpo/clusters.json`.

### Parameters

```
  --aws-access-key TEXT           AWS access key  [required]
  --aws-secret-key TEXT           AWS secret key  [required]
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --help                          Show this message and exit.
```

## Editing metadata of a registered OpenShift cluster

### Syntax

```shell
cpo cluster edit [OPTIONS] ALIAS_OR_SERVER
```

### Parameters

```
  --alias TEXT                    Alias used to reference a cluster instead of
                                  its server URL
  --username TEXT                 OpenShift username
  --password TEXT                 OpenShift password
  --insecure-skip-tls-verify / --no-insecure-skip-tls-verify
                                  Disables or enables checking the server's
                                  certificate for validity
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --help                          Show this message and exit.
```

## Removing a registered OpenShift cluster

### Syntax

```shell
cpo cluster rm [OPTIONS] ALIAS_OR_SERVER
```

### Parameters

```
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --help                          Show this message and exit.
```

## Listing registered OpenShift clusters

### Syntax

```shell
cpo cluster ls [OPTIONS]
```

### Parameters

```
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --help                          Show this message and exit.
```

> A star in the first column of the output indicates the current cluster.

## Setting the current registered OpenShift cluster

### Syntax

```shell
cpo cluster use [OPTIONS] ALIAS_OR_SERVER
```

### Parameters

```
  --login                         Log in to the current OpenShift cluster
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --help                          Show this message and exit.
```

> When setting a cluster as the current cluster, it is automatically used by commands that operate on a cluster (unless another cluster is explicitly specified).

## Getting the current registered OpenShift cluster

### Syntax

```shell
cpo cluster current [OPTIONS]
```

### Parameters

```
  --print-alias                   Print the alias used to reference a cluster
                                  instead of its server URL
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --help                          Show this message and exit.
```

> To include the alias (or server if no alias was defined) of the current cluster in your prompt, you should run the following faster command: `cpo-get-current-cluster-alias`

## Resetting the current registered OpenShift cluster

### Syntax

```shell
cpo cluster reset-current-cluster [OPTIONS]
```

### Parameters

```
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --help                          Show this message and exit.
```

### Registering a Red Hat OpenShift on IBM Cloud cluster

- Log in to IBM Cloud:

  ```shell
  cpo ibmcloud login
  ```

- Register cluster:

  ```shell
  cpo ibmcloud oc cluster add --alias $ALIAS --cluster-name $CLUSTER_NAME
  ```

## Logging in to the current OpenShift cluster

This command depends on the OpenShift CLI and executes `oc login` using the given or stored cluster credentials. The OpenShift CLI executable is managed by the IBM Cloud Pak Operations CLI.

### Syntax

```shell
cpo cluster login [OPTIONS]
```

### Parameters

```
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --help                          Show this message and exit.
```

## Obtaining an OAuth access token for an OpenShift cluster

### Syntax

```shell
cpo cluster get-cluster-access-token [OPTIONS]
```

### Parameters

```
  --server TEXT                   OpenShift server URL
  --username TEXT                 OpenShift cluster username
  --password TEXT                 OpenShift cluster password
  --print-login-command           Print oc login command instead of just the
                                  OAuth access token
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --help                          Show this message and exit.
```
