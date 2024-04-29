---
nav_order: 7
---

# Usage: Installing storage-related OpenShift resources

## Installing Kubernetes NFS Subdir External Provisioner

### Syntax

```shell
cpo cluster storage install-nfs-storage-class [OPTIONS]
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
  --nfs-server TEXT               NFS server  [required]
  --nfs-path TEXT                 NFS path  [default: /var/nfs]
  --project TEXT                  Project used to install the Kubernetes NFS
                                  Subdir External Provisioner  [default:
                                  default]
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --help                          Show this message and exit.
```

## Installing Red Hat OpenShift Data Foundation (ODF)

### Syntax

```shell
cpo cluster storage install-odf-storage-classes [OPTIONS]
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

> Currently, opinionated configuration values are used for deploying the `StorageCluster` custom resource (see [Ansible playbook](https://github.com/IBM/cloud-pak-operations-cli/blob/master/cpo/deps/playbooks/deploy_odf_playbook.yaml)).
