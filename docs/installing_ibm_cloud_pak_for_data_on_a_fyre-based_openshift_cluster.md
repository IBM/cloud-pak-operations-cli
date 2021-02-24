# Installing IBM Cloud Pak for Data on a FYRE-based OpenShift cluster

## Required Credentials

- [IBM Cloud Pak for Data entitlement key](https://myibm.ibm.com/products-services/containerlibrary)
- IBM GitHub API key
- Password for `kubeadmin` user of OpenShift cluster (see e-mail from fyre@us.ibm.com: "[FYRE] OpenShift cluster finished building")

## Linux/macOS/Windows:

To create a FYRE cluster using the following command, your FYRE memory quota must be greater than or equal to 220 GiB and may be adjusted by one of the owners of your FYRE product group.

- Create FYRE cluster:

  ```bash
  dg fyre cluster create --cluster-name {FYRE cluster name}
  dg fyre cluster copy-ssh-key --infrastructure-node-hostname {FYRE cluster name}-inf.fyre.ibm.com
  ssh root@{FYRE cluster name}-inf.fyre.ibm.com
  ```

## Infrastructure node:

- [Enable SSH access to GitHub](https://docs.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh)
- Compile and install Python 3.9:

  ```bash
  yum install gcc libffi-devel openssl-devel zlib-devel
  wget https://www.python.org/ftp/python/3.9.2/Python-3.9.2.tgz
  tar -xf Python-3.9.2.tgz
  cd Python-3.9.2
  ./configure
  make
  make install
  ```

- Install Data Gate CLI:

  ```bash
  pip3 install git+ssh://git@github.com/IBM/data-gate-cli.git
  ```

- Execute Data Gate CLI commands:

  ```
  dg adm download-dependencies
  dg fyre cluster add --alias {alias} --cluster-name {FYRE cluster name} --password {kubeadmin password}
  dg cluster use {alias}
  dg adm store-credentials --ibm-cloud-pak-for-data-entitlement-key {IBM Cloud Pak for Data entitlement key}
  dg adm store-credentials --ibm-github-api-key {IBM GitHub API key}
  dg fyre cluster install-nfs-storage-class
  dg cluster install-cloud-pak-for-data --storage-class nfs-client
  dg cluster install-assembly --assembly-name dmc --storage-class nfs-client
  dg cluster install-data-gate --storage-class nfs-client
  dg cluster install-db2 --db2-edition {[db2oltp|db2wh]} --storage-class nfs-client
  ```
