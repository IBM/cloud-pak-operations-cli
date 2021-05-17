# Installing IBM Cloud Pak for Data on a FYRE-based OpenShift cluster

## Required Credentials

- [IBM Cloud Pak for Data entitlement key](https://myibm.ibm.com/products-services/containerlibrary)
- IBM GitHub API key

## Linux/macOS/Windows:

- Create FYRE cluster:

  ```bash
  dg fyre cluster create-for-db2-data-gate --cluster-name {FYRE cluster name}
  dg fyre cluster add --alias {alias} --cluster-name {FYRE cluster name} --password {kubeadmin password}
  dg cluster use {alias}
  dg fyre cluster copy-ssh-key
  dg fyre cluster ssh
  ```

## Infrastructure node:

- [Enable SSH access to GitHub](https://docs.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh)
- Compile and install Python 3.8 or higher:

  ```bash
  yum install gcc git libffi-devel make openssl-devel zlib-devel
  export PYTHON_VERSION="3.{minor version}.{patch version}"
  wget "https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz"
  tar -xf "Python-$PYTHON_VERSION.tgz"
  cd "Python-$PYTHON_VERSION"
  ./configure
  make
  make install
  ```

- Install Data Gate CLI:

  ```bash
  pip3 install git+ssh://git@github.com/IBM/data-gate-cli.git
  ```

- Execute the following Data Gate CLI commands to install IBM Cloud Pak for Data, IBM Db2, IBM Db2 Warehouse, IBM Db2 Data Management Console, and IBM Db2 for z/OS Data Gate:

  ```
  dg adm download-dependencies
  dg adm store-credentials --ibm-cloud-pak-for-data-entitlement-key {IBM Cloud Pak for Data entitlement key}
  dg adm store-credentials --ibm-github-api-key {IBM GitHub API key}
  dg fyre cluster add --alias {alias} --cluster-name {FYRE cluster name} --password {kubeadmin password}
  dg cluster use {alias}
  dg fyre cluster install-nfs-storage-class
  dg cluster install-db2-data-gate-stack --storage-class nfs-client
  ```
