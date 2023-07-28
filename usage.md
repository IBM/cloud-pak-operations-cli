---
nav_order: 2
---

# Usage

## Cluster management

### Registering a generic OpenShift cluster

- Register cluster:

  ```shell
  cpo cluster add --alias $ALIAS --server $SERVER --username $USERNAME --password $PASSWORD
  ```

- Use cluster:

  ```shell
  cpo cluster use $ALIAS
  ```

- Use cluster and log in using the OpenShift CLI:

  ```shell
  cpo cluster use $ALIAS --login
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

## Security management

- Obtain an OAuth access token for the current OpenShift cluster:

  ```shell
  cpo cluster get-cluster-access-token
  ```

- Manage the global pull secret:

  ```shell
  cpo cluster pull-secret
  ```

## Storage management

- Deploy Kubernetes NFS Subdir External Provisioner:

  ```shell
  cpo cluster install-nfs-storage-class
  ```

- Deploy OpenShift Data Foundation (Linux and macOS):

  ```shell
  cpo cluster install-odf-storage-classes
  ```

  Note: Currently, opinionated configuration values are used for deploying the `StorageCluster` custom resource (see [Ansible playbook](https://github.com/IBM/cloud-pak-operations-cli/blob/master/cpo/deps/playbooks/deploy_odf_playbook.yaml)).
