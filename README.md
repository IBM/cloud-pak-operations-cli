# IBM Cloud Pak Operations CLI

<div align="center">
    <p>
        <a href="https://github.com/IBM/cloud-pak-operations-cli/blob/master/LICENSE"><img alt="GitHub license" src="https://img.shields.io/github/license/IBM/cloud-pak-operations-cli?style=for-the-badge"></a>
	    <a href="https://github.com/IBM/cloud-pak-operations-cli/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/IBM/cloud-pak-operations-cli?style=for-the-badge"></a>
        <a href="https://github.com/IBM/cloud-pak-operations-cli/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/IBM/cloud-pak-operations-cli?style=for-the-badge"></a>
        <a href="https://twitter.com/intent/tweet?text=Wow:&url=https%3A%2F%2Fgithub.com%2FIBM%2Fcloud-pak-operations-cli"><img alt="Twitter URL" src="https://img.shields.io/twitter/url?color=blue&style=for-the-badge&url=https%3A%2F%2Fgithub.com%2FIBM%2Fcloud-pak-operations-cli"></a>
        <a href="https://github.com/IBM/cloud-pak-operations-cli/actions?query=workflow%3A%22Python+Testing%22+branch%3Amaster"><img alt="GitHub Workflow Status (branch)" src="https://img.shields.io/github/workflow/status/IBM/cloud-pak-operations-cli/Python%20Testing/master?label=Python%20Testing&style=for-the-badge"></a>
    </p>
</div>

The IBM Cloud Pak Operations CLI allows the user-friendly installation of IBM Cloud Pak for Data 3.5.0/4.0.x and IBM Cloud Pak for Data services on OpenShift clusters. It also allows the one-click deployment of a Red Hat OpenShift on IBM Cloud cluster including the installation of IBM Cloud Pak for Data 3.5.0 as software.

For IBM-internal users, the IBM Cloud Pak Operations CLI additionally supports managing OpenShift clusters on FYRE.

## Installation & Configuration

### Installation

#### Python installation (3.8 or higher)

- macOS (requires [Homebrew](https://brew.sh/)):

  ```shell
  brew install python
  ```

- Windows (requires [Chocolatey](https://chocolatey.org/)):

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

- Downloads dependencies (IBM Cloud CLI, IBM Cloud Terraform provider, OpenShift CLI, Terraform CLI)

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

### Installation of IBM Cloud Pak for Data 3.5.0/4.0.x, IBM Db2, IBM Db2 Warehouse, IBM Db2 Data Management Console, and IBM Db2 for z/OS Data Gate

- Register cluster:

  ```shell
  cpo cluster add --alias $ALIAS --server $SERVER --username $USERNAME --password $PASSWORD
  ```

- Use cluster:

  ```shell
  cpo cluster use $ALIAS
  ```

- Store your [IBM Cloud Pak for Data entitlement key](https://myibm.ibm.com/products-services/containerlibrary):

  ```shell
  cpo adm store-credentials \
      --ibm-cloud-pak-for-data-entitlement-key $IBM_CLOUD_PAK_FOR_DATA_ENTITLEMENT_KEY
  ```

- Install IBM Cloud Pak for Data:

<table>
<thead>
<tr>
<th>Version</th>
<th>Command</th>
</tr>
</thead>
<tbody>
<tr/>
<tr>
<td>3.5.0</td>
<td>

```shell
cpo cpd3 install --storage-class $STORAGE_CLASS
```

</td>
</tr>
<tr/>
<tr>
<td>4.0.x</td>
<td>

```shell
cpo cpd4 install \
    --accept-license \
    --force \
    --license (ENTERPRISE|STANDARD) \
    --storage-class $STORAGE_CLASS
```

</td>
</tr>
</tbody>
</table>

### Installation of IBM Cloud Pak for Data 3.5.0, Db2 Warehouse, and IBM Db2 for z/OS Data Gate as software on IBM Cloud

- Log in to IBM Cloud:

  ```shell
  cpo ibmcloud login
  ```

- Install IBM Cloud Pak for Data, IBM Db2 Warehouse, and IBM Db2 for z/OS Data Gate:

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
<td>Installation with an existing cluster</td>
<td>

```shell
cpo ibmcloud oc cluster install --cluster-name $CLUSTER_NAME
```

</td>
</tr>
<tr/>
<tr>
<td>Installation without an existing cluster</td>
<td>

```shell
cpo ibmcloud oc cluster create \
    --alias $ALIAS \
    --cluster-name $CLUSTER_NAME \
    --full-install
```

</td>
</tr>
</tbody>
</table>

### IBM-internal

- Enable FYRE-specific commands:

  ```shell
  cpo adm config set --key fyre_commands --value true
  ```

- [Installing IBM Cloud Pak for Data on a FYRE-based OpenShift cluster](docs/installing_ibm_cloud_pak_for_data_on_a_fyre-based_openshift_cluster.md)

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
