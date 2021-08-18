# Installing IBM Cloud Pak for Data on a FYRE-based OpenShift cluster

## Required Credentials

- [IBM Cloud Pak for Data entitlement key](https://myibm.ibm.com/products-services/containerlibrary)

## Linux/macOS/Windows:

- Create FYRE cluster:

  ```bash
  dg fyre cluster create-for-db2-data-gate --alias *ALIAS* --cluster-name *FYRE_CLUSTER_NAME* --ssh-key "$(cat ~/.ssh/id_rsa.pub)"
  dg cluster use *ALIAS*
  dg fyre cluster install-nfs-storage-class
  ```

## IBM Cloud Pak for Data 3.5.0

- Log in to infrastructure node:

  ```bash
  dg fyre cluster ssh --disable-strict-host-key-checking
  ```

- Install packages:

  ```bash
  yum install --assumeyes git python38
  ```

- Install Data Gate CLI:

  ```bash
  pip3 install git+https://git@github.com/IBM/data-gate-cli.git
  ```

- Execute the following Data Gate CLI commands to install IBM Cloud Pak for Data, IBM Db2, IBM Db2 Warehouse, IBM Db2 Data Management Console, and IBM Db2 for z/OS Data Gate:

  ```bash
  dg adm download-dependencies
  dg adm store-credentials --ibm-cloud-pak-for-data-entitlement-key *IBM_CLOUD_PAK_FOR_DATA_ENTITLEMENT_KEY*
  dg fyre cluster add --alias *ALIAS* --cluster-name *FYRE_CLUSTER_NAME* --password *KUBEADMIN_PASSWORD*
  dg cluster use *ALIAS*
  dg cluster install-db2-data-gate-stack --accept-all-licenses --storage-class managed-nfs-storage
  ```

## IBM Cloud Pak for Data 4.0.0

- Execute the following Data Gate CLI commands to install IBM Cloud Pak for Data, IBM Db2, IBM Db2 Warehouse, IBM Db2 Data Management Console, and IBM Db2 for z/OS Data Gate:

  ```bash
  dg adm store-credentials --ibm-cloud-pak-for-data-entitlement-key *IBM_CLOUD_PAK_FOR_DATA_ENTITLEMENT_KEY*
  dg cpd4 install --storage-class managed-nfs-storage
  dg cpd4 service install --service-name db2oltp --license *(ADVANCED|COMMUNITY|STANDARD)*
  dg cpd4 service install --service-name db2wh --license *(ENTERPRISE|STANDARD)*
  dg cpd4 service install --service-name dmc --license *(ENTERPRISE|STANDARD)*
  dg cpd4 service install --service-name datagate --license *(ENTERPRISE|STANDARD)*
  ```
