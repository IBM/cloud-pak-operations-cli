---
nav_order: 1
---

# Installation & Configuration

## Installation

### Python installation (3.10 or higher)

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

### Installation and update (latest release build)

- Installation (provides <code>cpo</code> command):

  ```shell
  pip3 install cloud-pak-operations-cli
  ```

- Update:

  ```shell
  pip3 install --upgrade cloud-pak-operations-cli
  ```

### Installation and update (latest development code)

- Installation (provides <code>cpo</code> command):

  ```shell
  pip3 install git+https://git@github.com/IBM/cloud-pak-operations-cli.git
  ```

- Update:

  ```shell
  cpo adm update-dev
  ```

## Configuration

### Dependency download

- Downloads dependencies (IBM Cloud CLI, IBM Cloud Pak CLI, OpenShift CLI)

  ```shell
  cpo adm download-dependencies
  ```

### Shell completion (Linux/macOS)

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
docker run --interactive --tty quay.io/ibm/cloud-pak-operations-cli:latest bash
```
