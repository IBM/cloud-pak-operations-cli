# Db2 Data Gate CLI (dg)

![Banner](./resources/banner.svg)

<div align="center">
    <p>
        <a href="https://github.com/IBM/data-gate-cli/blob/master/LICENSE"><img alt="GitHub license" src="https://img.shields.io/github/license/IBM/data-gate-cli?style=for-the-badge"></a>
	    <a href="https://github.com/IBM/data-gate-cli/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/IBM/data-gate-cli?style=for-the-badge"></a>
        <a href="https://github.com/IBM/data-gate-cli/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/IBM/data-gate-cli?style=for-the-badge"></a>
        <a href="https://twitter.com/intent/tweet?text=Wow:&url=https%3A%2F%2Fgithub.com%2FIBM%2Fdata-gate-cli"><img alt="Twitter URL" src="https://img.shields.io/twitter/url?color=blue&style=for-the-badge&url=https%3A%2F%2Fgithub.com%2FIBM%2Fdata-gate-cli"></a>
        <a href="https://github.com/IBM/data-gate-cli/actions?query=workflow%3A%22Python+Testing%22+branch%3Amaster"><img alt="GitHub Workflow Status (branch)" src="https://img.shields.io/github/workflow/status/IBM/data-gate-cli/Python%20Testing/master?label=Python%20Testing&style=for-the-badge"></a>
    </p>
</div>

The Db2 Data Gate CLI allows the user-friendly installation of IBM Cloud Pak for Data, Db2 (Warehouse), and IBM Db2 for z/OS Data Gate on OpenShift clusters. It also allows the one-click deployment of a Red Hat OpenShift on IBM Cloud cluster including the installation of IBM Cloud Pak for Data, Db2 Warehouse, and IBM Db2 for z/OS Data Gate as software.

For IBM-internal users, the Db2 Data Gate CLI additionally supports managing OpenShift clusters on FYRE.

## Installation & Configuration

### Installation

#### Python installation (3.8 or higher)

- macOS (requires [Homebrew](https://brew.sh/)):

  ```bash
  brew install python
  ```

- Windows (requires [Chocolatey](https://chocolatey.org/)):

  ```bash
  choco install python
  ```

#### Db2 Data Gate CLI installation and update (latest release build)

| Operation    | Command                                              |
| ------------ | ---------------------------------------------------- |
| Installation | `pip3 install data-gate-cli` (provides `dg` command) |
| Update       | `pip3 install --upgrade data-gate-cli`               |

#### Db2 Data Gate CLI installation and update (latest development code)

| Operation    | Command                                                                                 |
| ------------ | --------------------------------------------------------------------------------------- |
| Installation | `pip3 install git+https://git@github.com/IBM/data-gate-cli.git` (provides `dg` command) |
| Update       | `dg adm update-dev`                                                                     |

### Configuration

#### Dependency download

- Downloads dependencies (IBM Cloud CLI, IBM Cloud Terraform provider, OpenShift CLI, Terraform CLI)

  ```bash
  dg adm download-dependencies
  ```

#### Shell completion (Linux/macOS)

- Bash: Add the following code to `.bashrc`:

  ```bash
  . $(pip3 show dg | sed -En 's/Location: (.*)/\1/p')/dg/deps/autocomplete/dg-autocomplete-bash.sh
  ```

- zsh: Add the following code to `.zshrc`:

  ```bash
  . $(pip3 show dg | sed -En 's/Location: (.*)/\1/p')/dg/deps/autocomplete/dg-autocomplete-zsh.sh
  ```

## Running inside a Docker container

The latest version of the Db2 Data Gate CLI on the master branch can also be run inside a Docker container:

```bash
docker run -it quay.io/ibm/data-gate-cli:latest bash
```

## Usage

### Installation of IBM Cloud Pak for Data, IBM Db2, IBM Db2 Warehouse, IBM Db2 Data Management Console, and IBM Db2 for z/OS Data Gate

- Register cluster:

  ```bash
  dg cluster add --alias {alias} --server {server} --username {username} --password {password}
  ```

- Use cluster:

  ```bash
  dg cluster use {alias}
  ```

- Store your [IBM Cloud Pak for Data entitlement key](https://myibm.ibm.com/products-services/containerlibrary):

  ```bash
  dg adm store-credentials --ibm-cloud-pak-for-data-entitlement-key {ibm-cloud-pak-for-data-entitlement-key}
  ```

- Install IBM Cloud Pak for Data, IBM Db2, IBM Db2 Warehouse, IBM Db2 Data Management Console, and IBM Db2 for z/OS Data Gate:

  ```bash
  dg cluster install-db2-data-gate-stack --storage-class {storage class}
  ```

### Installation of IBM Cloud Pak for Data, Db2 Warehouse, and IBM Db2 for z/OS Data Gate as software on IBM Cloud

- Log in to IBM Cloud:

  ```bash
  dg ibmcloud login
  ```

- Install IBM Cloud Pak for Data, IBM Db2 Warehouse, and IBM Db2 for z/OS Data Gate:

| Action                                   | Command                                                                                      |
| ---------------------------------------- | -------------------------------------------------------------------------------------------- |
| Installation with an existing cluster    | `dg ibmcloud oc cluster install --cluster-name {cluster name}`                               |
| Installation without an existing cluster | `dg ibmcloud oc cluster create --alias {alias} --cluster-name {cluster name} --full-install` |

### IBM-internal

- [Installing IBM Cloud Pak for Data on a FYRE-based OpenShift cluster](docs/installing_ibm_cloud_pak_for_data_on_a_fyre-based_openshift_cluster.md)

## Development

- [Development Guide](docs/development_guide.md)

## Known issues

### OpenShift Client CLI (macOS)

```
Unable to connect to the server: dial tcp: lookup {OpenShift cluster} on {DNS name server}:53: no such host
```

- [GitHub issue](https://github.com/openshift/oc/issues/315)
- Workaround: Edit `/etc/hosts` and add IP address of OpenShift cluster

  - Example:

    ```
    9.AA.BBB.CC your.cluster.domain.com
    ```
