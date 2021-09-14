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

The Db2 Data Gate CLI allows the user-friendly installation of IBM Cloud Pak for Data 3.5.0/4.0.x, Db2 (Warehouse), the IBM Db2 Data Management Console, and IBM Db2 for z/OS Data Gate on OpenShift clusters. It also allows the one-click deployment of a Red Hat OpenShift on IBM Cloud cluster including the installation of IBM Cloud Pak for Data, Db2 Warehouse, and IBM Db2 for z/OS Data Gate as software.

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

TBA [September 2021]

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

### Installation of IBM Cloud Pak for Data 3.5.0/4.0.x, IBM Db2, IBM Db2 Warehouse, IBM Db2 Data Management Console, and IBM Db2 for z/OS Data Gate

- Register cluster:

  ```bash
  dg cluster add --alias *ALIAS* --server *SERVER* --username *USERNAME* --password *PASSWORD*
  ```

- Use cluster:

  ```bash
  dg cluster use *ALIAS*
  ```

- Store your [IBM Cloud Pak for Data entitlement key](https://myibm.ibm.com/products-services/containerlibrary):

  ```bash
  dg adm store-credentials --ibm-cloud-pak-for-data-entitlement-key *IBM_CLOUD_PAK_FOR_DATA_ENTITLEMENT_KEY*
  ```

- Install IBM Cloud Pak for Data, IBM Db2, IBM Db2 Warehouse, IBM Db2 Data Management Console, and IBM Db2 for z/OS Data Gate:

| Version | Command                                                                                                                                                                                                                                                                                                                         |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 3.5.0   | <code>dg cpd3 install-db2-data-gate-stack --storage-class _STORAGE_CLASS_</code>                                                                                                                                                                                                                                                |
| 4.0.x   | <code>dg cpd4 --accept-license --force --license _[ENTERPRISE\|STANDARD]_ install --storage-class _STORAGE_CLASS_</code><br /><code>dg cpd4 service install-db2-data-gate-stack --accept-all-licenses --db2-license _[ADVANCED\|COMMUNITY\|STANDARD]_ --license _[ENTERPRISE\|STANDARD]_ --storage-class _STORAGE_CLASS_</code> |

### Installation of IBM Cloud Pak for Data 3.5.0, Db2 Warehouse, and IBM Db2 for z/OS Data Gate as software on IBM Cloud

- Log in to IBM Cloud:

  ```bash
  dg ibmcloud login
  ```

- Install IBM Cloud Pak for Data, IBM Db2 Warehouse, and IBM Db2 for z/OS Data Gate:

| Action                        | Command                                                                                                 |
| ----------------------------- | ------------------------------------------------------------------------------------------------------- |
| Inst. w/ an existing cluster  | <code>dg ibmcloud oc cluster install --cluster-name _CLUSTER_NAME_</code>                               |
| Inst. w/o an existing cluster | <code>dg ibmcloud oc cluster create --alias _ALIAS_ --cluster-name _CLUSTER_NAME_ --full-install</code> |

### IBM-internal

- [Installing IBM Cloud Pak for Data on a FYRE-based OpenShift cluster](docs/installing_ibm_cloud_pak_for_data_on_a_fyre-based_openshift_cluster.md)

## Development

- [Development Guide](docs/development_guide.md)

## Known issues

### OpenShift Client CLI (macOS)

```bash
Unable to connect to the server: dial tcp: lookup *OPENSHIFT_CLUSTER* on *DNS_NAME_SERVER*:53: no such host
```

- [GitHub issue](https://github.com/openshift/oc/issues/315)
- Workaround: Edit `/etc/hosts` and add IP address of OpenShift cluster

  - Example:

    ```
    9.AA.BBB.CC your.cluster.domain.com
    ```
