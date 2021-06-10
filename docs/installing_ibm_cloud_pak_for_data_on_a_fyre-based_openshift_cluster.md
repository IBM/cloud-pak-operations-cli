# Installing IBM Cloud Pak for Data on a FYRE-based OpenShift cluster

## Required Credentials

- [IBM Cloud Pak for Data entitlement key](https://myibm.ibm.com/products-services/containerlibrary)
- IBM GitHub API key

## Linux/macOS/Windows:

- Create FYRE cluster:

  ```bash
  dg fyre cluster create-for-db2-data-gate --alias {alias} --cluster-name {FYRE cluster name} --ssh-key "$(cat ~/.ssh/id_rsa.pub)"
  dg cluster use {alias}
  dg fyre cluster ssh
  ```

## Infrastructure node:

- Install packages:

  ```bash
  yum install --assumeyes git python38
  ```

- Install Data Gate CLI:

  ```bash
  pip3 install git+https://git@github.com/IBM/data-gate-cli.git
  ```

- Execute the following Data Gate CLI commands to install IBM Cloud Pak for Data, IBM Db2, IBM Db2 Warehouse, IBM Db2 Data Management Console, and IBM Db2 for z/OS Data Gate:

  ```
  dg adm download-dependencies
  dg adm store-credentials --ibm-cloud-pak-for-data-entitlement-key {IBM Cloud Pak for Data entitlement key}
  dg adm store-credentials --ibm-github-api-key {IBM GitHub API key}
  dg fyre cluster add --alias {alias} --cluster-name {FYRE cluster name} --password {kubeadmin password}
  dg cluster use {alias}
  dg fyre cluster install-nfs-storage-class
  dg cluster install-db2-data-gate-stack --accept-all-licenses --storage-class nfs-client
  ```
