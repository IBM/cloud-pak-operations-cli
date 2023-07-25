# IBM Cloud Pak Operations CLI

<div align="center">
    <p>
        <a href="https://github.com/IBM/cloud-pak-operations-cli/blob/master/LICENSE"><img alt="GitHub license" src="https://img.shields.io/github/license/IBM/cloud-pak-operations-cli?style=for-the-badge"></a>
	    <a href="https://github.com/IBM/cloud-pak-operations-cli/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/IBM/cloud-pak-operations-cli?style=for-the-badge"></a>
        <a href="https://github.com/IBM/cloud-pak-operations-cli/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/IBM/cloud-pak-operations-cli?style=for-the-badge"></a>
        <a href="https://github.com/IBM/cloud-pak-operations-cli/actions?query=workflow%3A%22Python+Testing%22+branch%3Amaster"><img alt="GitHub Workflow Status (branch)" src="https://img.shields.io/github/actions/workflow/status/IBM/cloud-pak-operations-cli/python-package.yml?branch=master&style=for-the-badge"></a>
    </p>
</div>

The IBM Cloud Pak Operations CLI provides basic functionality to manage Red Hat OpenShift clusters and IBM Cloud Pak for Data on various cloud platforms on top of the OpenShift CLI (oc) and the [IBM Cloud Pak for Data CLI](https://github.com/IBM/cpd-cli) (cpd-cli).

## Installation & Configuration

### Installation

#### Python installation (3.10 or higher)

- macOS (requires [Homebrew](https://brew.sh)):

  ```shell
  brew install python
  ```

- Windows:

  - [Winget](https://github.com/microsoft/winget-cli):

    ```shell
    winget install --exact --id=Python.Python.3.11
    ```

  - [Chocolatey](https://chocolatey.org)

    ```shell
    choco install python
    ```

#### IBM Cloud Pak Operations CLI installation and update (latest release build)

<table>
<thead>
<tr>
<th>Action</th>
<th>Command</th>
</tr>
</thead>
<tbody>
<tr/>
<tr>
<td>Installation (provides <code>cpo</code> command)</td>
<td>

```shell
pip3 install cloud-pak-operations-cli
```

</td>
</tr>
<tr/>
<tr>
<td>Update</td>
<td>

```shell
pip3 install --upgrade cloud-pak-operations-cli
```

</td>
</tr>
</tbody>
</table>

#### IBM Cloud Pak Operations CLI installation and update (latest development code)

<table>
<thead>
<tr>
<th>Action</th>
<th>Command</th>
</tr>
</thead>
<tbody>
<tr/>
<tr>
<td>Installation (provides <code>cpo</code> command)</td>
<td>

```shell
pip3 install git+https://git@github.com/IBM/cloud-pak-operations-cli.git
```

</td>
</tr>
<tr/>
<tr>
<td>Update</td>
<td>

```shell
cpo adm update-dev
```

</td>
</tr>
</tbody>
</table>

### Configuration

#### Dependency download

- Downloads dependencies (IBM Cloud CLI, IBM Cloud Pak CLI, OpenShift CLI)

  ```shell
  cpo adm download-dependencies
  ```

#### Shell completion (Linux/macOS)

- Bash: Add the following code to `.bashrc`:

  ```shell
  . $(cpo adm get-shell-completion-script-location --shell bash)
  ```

- zsh: Add the following code to `.zshrc`:

  ```shell
  . $(cpo adm get-shell-completion-script-location --shell zsh)
  ```

## Running inside a Docker container

The latest version of the IBM Cloud Pak Operations CLI on the master branch can also be run inside a Docker container:

```shell
docker run -it quay.io/ibm/cloud-pak-operations-cli:latest bash
```

## Usage

### Cluster management

#### Registering a generic OpenShift cluster

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

#### Registering a Red Hat OpenShift on IBM Cloud cluster

- Log in to IBM Cloud:

  ```shell
  cpo ibmcloud login
  ```

- Register cluster:

  ```shell
  cpo ibmcloud oc cluster add --alias $ALIAS --cluster-name $CLUSTER_NAME
  ```

### Security management

- Obtain an OAuth access token for the current OpenShift cluster:

  ```shell
  cpo cluster get-cluster-access-token
  ```

- Manage the global pull secret:

  ```shell
  cpo cluster pull-secret
  ```

### Storage management

- Deploy Kubernetes NFS Subdir External Provisioner:

  ```shell
  cpo cluster install-nfs-storage-class
  ```

- Deploy OpenShift Data Foundation (Linux and macOS):

  ```shell
  cpo cluster install-odf-storage-classes
  ```

  Note: Currently, opinionated configuration values are used for deploying the `StorageCluster` custom resource (see [Ansible playbook](cpo/deps/playbooks/deploy_odf_playbook.yaml)).

## Development

- [Development Guide](docs/development_guide.md)

## Known issues

### OpenShift CLI (macOS)

```shell
Unable to connect to the server: dial tcp: lookup … on …:53: no such host
```

- [GitHub issue](https://github.com/openshift/oc/issues/315)
- Workaround: Edit `/etc/hosts` and add IP address of OpenShift cluster

  - Example:

    ```
    9.AA.BBB.CC your.cluster.domain.com
    ```
