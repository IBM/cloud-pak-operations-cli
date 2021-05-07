# Data Gate CLI (dg)

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

## Installation & Update

1. Install Python 3.8 or higher

- macOS (requires [Homebrew](https://brew.sh/)):

```bash
brew install python
```

- Windows (requires [Chocolatey](https://chocolatey.org/)):

```bash
choco install python
```

2. Install Data Gate CLI Python package (provides `dg` command)

```bash
pip3 install git+ssh://git@github.com/IBM/data-gate-cli.git
```

Execute the following command to update the Data Gate CLI to the latest version:

```bash
dg adm update
```

## Shell completion (Linux/macOS)

- Bash: Add the following code to `.bashrc`:

```bash
. $(pip3 show dg | sed -En 's/Location: (.*)/\1/p')/dg/deps/autocomplete/dg-autocomplete-bash.sh
```

- zsh: Add the following code to `.zshrc`:

```bash
. $(pip3 show dg | sed -En 's/Location: (.*)/\1/p')/dg/deps/autocomplete/dg-autocomplete-zsh.sh
```

## Running inside a Docker container

The latest version of the Data Gate CLI on the master branch can also be run inside a Docker container:

```bash
docker run -it quay.io/ibm/data-gate-cli:latest bash
```

## Development

### Recommended Visual Studio Code plug-ins

- [Pylance](https://github.com/microsoft/pylance-release) (static type checking)

### Cloning the Data Gate CLI GitHub repository

```bash
git clone git@github.com:IBM/data-gate-cli.git
```

### Creating a virtual environment

Execute the following commands to create a [virtual environment](https://virtualenv.pypa.io/en/latest/) within the directory the Data Gate CLI GitHub repository was cloned into.

- Linux/macOS:

```bash
pip3 install virtualenv
virtualenv .venv
. .venv/bin/activate
pip3 install black flake8 isort
pip3 install --editable .
```

- Windows:

```bash
pip3 install virtualenv
virtualenv .venv
.venv/Scripts/activate
pip3 install black flake8 isort
pip3 install --editable .
```

### Set environment variable

- Linux/macOS:

```
export DG_VENV_PYTHON_PATH=.venv/bin/python
```

- Windows:

```
DG_VENV_PYTHON_PATH=.venv\\Scripts\\python.exe
```

### Extending the Data Gate CLI

The Data Gate CLI is based on the [Click package](https://palletsprojects.com/p/click/).

#### Registering a new Click command

To register a new Click command, add the Python module containing the command to the `commands` directory or one of its subdirectories.

#### Registering a new Click group

To register a new Click group, add a Python package (i.e., a directory containing a file named `__init__.py`) to the `commands` directory or one of its subdirectories. Furthermore, add the following code to `__init__.py` to automatically register Click commands within Python modules contained in the package:

```python
import sys

import click

from dg.lib.click.lazy_loading_multi_command import (
    create_click_multi_command_class,
)


@click.command(cls=create_click_multi_command_class(sys.modules[__name__]))
def {Click group name}():
    pass
```

#### Running unit tests

Unit tests are based on the `unittest` package and contained in the `test` package. Execute the following command to execute all unit tests within your virtual environment:

```bash
python -m unittest discover test
```

#### References

- [Coding Guidelines](docs/coding_guidelines.md)

## Known issues

### macOS

```
Unable to connect to the server: dial tcp: lookup {OpenShift cluster} on {DNS name server}:53: no such host
```

- [GitHub issue](https://github.com/openshift/oc/issues/315)
- Workaround: Edit `/etc/hosts` and add IP address of OpenShift cluster
- Example:

```
9.AA.BBB.CC your.cluster.domain.com
```

## IBM-internal

- [Installing IBM Cloud Pak for Data on a FYRE-based OpenShift cluster](docs/installing_ibm_cloud_pak_for_data_on_a_fyre-based_openshift_cluster.md)
