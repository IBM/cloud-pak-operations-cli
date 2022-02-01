# Installing IBM Cloud Pak for Data on a FYRE-based OpenShift cluster

## Required Credentials

- [IBM Cloud Pak for Data entitlement key](https://myibm.ibm.com/products-services/containerlibrary)

## Linux/macOS/Windows:

- Create a new OCP+ cluster for IBM Db2 Data Gate on IBM Cloud Pak for Data:

  ```shell
  cpo fyre cluster create --alias $ALIAS --cluster-name $FYRE_CLUSTER_NAME --ocp-version 4.8 --ssh-key "$(cat ~/.ssh/id_rsa.pub)" --worker-node-num-cpus 16 --worker-node-ram-size 64
  ```

- Set the current registered OpenShift cluster:

  ```shell
  cpo cluster use $ALIAS
  ```

- Install NFS storage class:

  ```shell
  cpo fyre cluster install-nfs-storage-class
  ```

## IBM Cloud Pak for Data 4.0.x

- Execute the following IBM Cloud Pak Operations CLI commands to install IBM Cloud Pak for Data:

  - Store credentials in a configuration file:

    ```shell
    cpo adm store-credentials --ibm-cloud-pak-for-data-entitlement-key $IBM_CLOUD_PAK_FOR_DATA_ENTITLEMENT_KEY
    ```

  - Install IBM Cloud Pak for Data:

    ```shell
    cpo cpd4 install --accept-license --force --license (ENTERPRISE|STANDARD) --storage-class managed-nfs-storage
    ```

## IBM Cloud Pak for Data 3.5.0

- Log in to infrastructure node:

  ```shell
  cpo fyre cluster ssh --disable-strict-host-key-checking
  ```

- Install packages:

  ```shell
  yum install --assumeyes git python38
  ```

- Install IBM Cloud Pak Operations CLI:

  ```shell
  pip3 install cloud-pak-operations-cli
  ```

- Execute the following IBM Cloud Pak Operations CLI commands to install IBM Cloud Pak for Data:

  - Download dependencies:

    ```shell
    cpo adm download-dependencies
    ```

  - Store credentials in a configuration file:

    ```shell
    cpo adm store-credentials --ibm-cloud-pak-for-data-entitlement-key $IBM_CLOUD_PAK_FOR_DATA_ENTITLEMENT_KEY
    ```

  - Register the created OCP+ cluster:

    ```shell
    cpo fyre cluster add --alias $ALIAS --cluster-name $FYRE_CLUSTER_NAME --password $KUBEADMIN_PASSWORD
    ```

  - Set the current registered OpenShift cluster:

    ```shell
    cpo cluster use $ALIAS
    ```

  - Install IBM Cloud Pak for Data:

    ```shell
    cpo cpd3 install --accept-all-licenses --storage-class managed-nfs-storage
    ```
