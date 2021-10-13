# Db2 Data Gate CLI (dg)

<div align="center">
    <p>
        <a href="https://github.com/IBM/data-gate-cli/blob/master/LICENSE"><img alt="GitHub license" src="https://img.shields.io/github/license/IBM/data-gate-cli?style=for-the-badge"></a>
	    <a href="https://github.com/IBM/data-gate-cli/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/IBM/data-gate-cli?style=for-the-badge"></a>
        <a href="https://github.com/IBM/data-gate-cli/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/IBM/data-gate-cli?style=for-the-badge"></a>
        <a href="https://twitter.com/intent/tweet?text=Wow:&url=https%3A%2F%2Fgithub.com%2FIBM%2Fdata-gate-cli"><img alt="Twitter URL" src="https://img.shields.io/twitter/url?color=blue&style=for-the-badge&url=https%3A%2F%2Fgithub.com%2FIBM%2Fdata-gate-cli"></a>
        <a href="https://github.com/IBM/data-gate-cli/actions?query=workflow%3A%22Python+Testing%22+branch%3Amaster"><img alt="GitHub Workflow Status (branch)" src="https://img.shields.io/github/workflow/status/IBM/data-gate-cli/Python%20Testing/master?label=Python%20Testing&style=for-the-badge"></a>
    </p>
</div>

The Db2 Data Gate CLI allows the user-friendly installation of IBM Cloud Pak for Data 3.5.0/4.0.x, Db2 (Warehouse), the IBM Db2 Data Management Console, and IBM Db2 for z/OS Data Gate on OpenShift clusters. It also allows the one-click deployment of a Red Hat OpenShift on IBM Cloud cluster including the installation of Cloud Pak for Data, Db2 Warehouse, and Db2 for z/OS Data Gate as software.

For IBM-internal users, the Db2 Data Gate CLI additionally supports managing OpenShift clusters on FYRE.

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

#### Db2 Data Gate CLI installation and update (latest release build)

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
<td>Installation (provides <code>dg</code> command)</td>
<td>

```shell
pip3 install data-gate-cli
```

</td>
</tr>
<tr/>
<tr>
<td>Update</td>
<td>

```shell
pip3 install --upgrade data-gate-cli
```

</td>
</tr>
</tbody>
</table>

#### Db2 Data Gate CLI installation and update (latest development code)

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
<td>Installation (provides <code>dg</code> command)</td>
<td>

```shell
pip3 install git+https://git@github.com/IBM/data-gate-cli.git
```

</td>
</tr>
<tr/>
<tr>
<td>Update</td>
<td>

```shell
dg adm update-dev
```

</td>
</tr>
</tbody>
</table>

### Configuration

#### Dependency download

- Downloads dependencies (IBM Cloud CLI, IBM Cloud Terraform provider, OpenShift CLI, Terraform CLI)

  ```shell
  dg adm download-dependencies
  ```

#### Shell completion (Linux/macOS)

- Bash: Add the following code to `.bashrc`:

  ```shell
  . $(dg adm get-shell-completion-script-location --shell bash)
  ```

- zsh: Add the following code to `.zshrc`:

  ```shell
  . $(dg adm get-shell-completion-script-location --shell zsh)
  ```

## Running inside a Docker container

The latest version of the Db2 Data Gate CLI on the master branch can also be run inside a Docker container:

```shell
docker run -it quay.io/ibm/data-gate-cli:latest bash
```

## Usage

### Installation of IBM Cloud Pak for Data 3.5.0/4.0.x, IBM Db2, IBM Db2 Warehouse, IBM Db2 Data Management Console, and IBM Db2 for z/OS Data Gate

- Register cluster:

  ```shell
  dg cluster add --alias $ALIAS --server $SERVER --username $USERNAME --password $PASSWORD
  ```

- Use cluster:

  ```shell
  dg cluster use $ALIAS
  ```

- Store your [IBM Cloud Pak for Data entitlement key](https://myibm.ibm.com/products-services/containerlibrary):

  ```shell
  dg adm store-credentials \
      --ibm-cloud-pak-for-data-entitlement-key $IBM_CLOUD_PAK_FOR_DATA_ENTITLEMENT_KEY
  ```

- Install IBM Cloud Pak for Data, IBM Db2, IBM Db2 Warehouse, IBM Db2 Data Management Console, and IBM Db2 for z/OS Data Gate:

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
dg cpd3 install-db2-data-gate-stack --storage-class $STORAGE_CLASS
```

</td>
</tr>
<tr/>
<tr>
<td rowspan="3">4.0.x</td>
<td>

```shell
dg cpd4 install \
    --accept-license \
    --force \
    --license (ENTERPRISE|STANDARD) \
    --storage-class $STORAGE_CLASS
```

</td>
<tr/>
<tr>
<td>

```shell
dg cpd4 service install-db2-data-gate-stack \
    --accept-all-licenses \
    --db2-license (ADVANCED|COMMUNITY|STANDARD) \
    --license (ENTERPRISE|STANDARD) \
    --storage-class $STORAGE_CLASS
```

</td>
</tr>
</tr>
</tbody>
</table>

### Installation of IBM Cloud Pak for Data 3.5.0, Db2 Warehouse, and IBM Db2 for z/OS Data Gate as software on IBM Cloud

- Log in to IBM Cloud:

  ```shell
  dg ibmcloud login
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
dg ibmcloud oc cluster install --cluster-name $CLUSTER_NAME
```

</td>
</tr>
<tr/>
<tr>
<td>Installation without an existing cluster</td>
<td>

```shell
dg ibmcloud oc cluster create \
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
  dg adm config set --key fyre_commands --value true

- [Installing IBM Cloud Pak for Data on a FYRE-based OpenShift cluster](docs/installing_ibm_cloud_pak_for_data_on_a_fyre-based_openshift_cluster.md)

## Development

- [Development Guide](docs/development_guide.md)

## Known issues

### OpenShift Client CLI (macOS)

```shell
Unable to connect to the server: dial tcp: lookup … on …:53: no such host
```

- [GitHub issue](https://github.com/openshift/oc/issues/315)
- Workaround: Edit `/etc/hosts` and add IP address of OpenShift cluster

  - Example:

    ```
    9.AA.BBB.CC your.cluster.domain.com
    ```
