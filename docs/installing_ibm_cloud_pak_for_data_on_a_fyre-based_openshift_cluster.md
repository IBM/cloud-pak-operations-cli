# Installing IBM Cloud Pak for Data on a FYRE-based OpenShift cluster

## Required Credentials

- [IBM Cloud Pak for Data entitlement key](https://myibm.ibm.com/products-services/containerlibrary)

## Linux/macOS/Windows:

- Create a new OCP+ cluster for IBM Db2 Data Gate on IBM Cloud Pak for Data:

  ```shell
  dg fyre cluster create-for-db2-data-gate --alias $ALIAS --cluster-name $FYRE_CLUSTER_NAME --ssh-key "$(cat ~/.ssh/id_rsa.pub)"
  ```

- Set the current registered OpenShift cluster:

  ```shell
  dg cluster use $ALIAS
  ```

- Install NFS storage class:

  ```shell
  dg fyre cluster install-nfs-storage-class
  ```

## IBM Cloud Pak for Data 3.5.0

- Log in to infrastructure node:

  ```shell
  dg fyre cluster ssh --disable-strict-host-key-checking
  ```

- Install packages:

  ```shell
  yum install --assumeyes git python38
  ```

- Install Db2 Data Gate CLI:

  ```shell
  pip3 install git+https://git@github.com/IBM/data-gate-cli.git
  ```

- Execute the following Db2 Data Gate CLI commands to install IBM Cloud Pak for Data, IBM Db2, IBM Db2 Warehouse, IBM Db2 Data Management Console, and IBM Db2 for z/OS Data Gate:

  - Download dependencies:

    ```shell
    dg adm download-dependencies
    ```

  - Store credentials in a configuration file:

    ```shell
    dg adm store-credentials --ibm-cloud-pak-for-data-entitlement-key $IBM_CLOUD_PAK_FOR_DATA_ENTITLEMENT_KEY
    ```

  - Register the created OCP+ cluster:

    ```shell
    dg fyre cluster add --alias $ALIAS --cluster-name $FYRE_CLUSTER_NAME --password $KUBEADMIN_PASSWORD
    ```

  - Set the current registered OpenShift cluster:

    ```shell
    dg cluster use $ALIAS
    ```

  - Install IBM Cloud Pak for Data, IBM Db2, IBM Db2 Warehouse, IBM Db2 Data Management Console, and IBM Db2 for z/OS Data Gate:

    ```shell
    dg cpd3 install-db2-data-gate-stack --accept-all-licenses --storage-class managed-nfs-storage
    ```

## IBM Cloud Pak for Data 4.0.x

- Execute the following Db2 Data Gate CLI commands to install IBM Cloud Pak for Data, IBM Db2, IBM Db2 Warehouse, IBM Db2 Data Management Console, and IBM Db2 for z/OS Data Gate:

  - Store credentials in a configuration file:

    ```shell
    dg adm store-credentials --ibm-cloud-pak-for-data-entitlement-key $IBM_CLOUD_PAK_FOR_DATA_ENTITLEMENT_KEY
    ```

  - Install IBM Cloud Pak for Data:

    ```shell
    dg cpd4 install --accept-license --force --license (ENTERPRISE|STANDARD) --storage-class managed-nfs-storage
    ```

  - Install IBM Db2, IBM Db2 Warehouse, IBM Db2 Data Management Console, and IBM Db2 for z/OS Data Gate:

    ```shell
    dg cpd4 service install-db2-data-gate-stack --accept-all-licenses --db2-license (ADVANCED|COMMUNITY|STANDARD) --license (ENTERPRISE|STANDARD) --storage-class managed-nfs-storage
    ```
