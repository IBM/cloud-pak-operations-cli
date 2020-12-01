# `Data Gate CLI (dg)`
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

1. Install Python

- macOS (requires [Homebrew](https://brew.sh/)):

```bash
brew install python@3.9
brew link python@3.9 --force
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
pip3 install --editable .
```

- Windows:

```bash
pip3 install virtualenv
virtualenv .venv
.venv/Scripts/activate
pip3 install flake8
pip3 install --editable .
```

### Set environment variable

- Linux/macOS:

```
export DG_VENV_PYTHON_PATH=.venv/bin/python3
```

- Windows:

```
DG_VENV_PYTHON_PATH=.venv/Scripts/python3
```

### Extending the Data Gate CLI

The Data Gate CLI is based on the [Click package](https://palletsprojects.com/p/click/).

#### Registering a new Click command

To register a new Click command, add the Python module containing the command to the `commands` directory or one of its subdirectories.

#### Registering a new Click group

To register a new Click group, add a Python package (i.e., a directory containing a file named `__init__.py`) to the `commands` directory or one of its subdirectories. Furthermore, add the following code to `__init__.py` to automatically register Click commands within Python modules contained in the package:

```python
import click
import pathlib

import dg.utils.click as dgclick


def get_click_multi_command_class() -> type[click.Command]:
    return dgclick.create_click_multi_command_class(
        dgclick.import_packages_and_modules(__name__, pathlib.Path(__file__).parent)
    )


@click.command(cls=get_click_multi_command_class())
def {Click group name}():
    pass
```

#### Docstring Syntax

[numpydoc docstring guide](https://numpydoc.readthedocs.io/en/latest/format.html)

#### Running unit tests

Unit tests are based on the `unittest` package and contained in the `test` package. Execute the following command to execute all unit tests within your virtual environment:

```bash
python -m unittest discover test
```

## Known issues

### macOS

```
Unable to connect to the server: dial tcp: lookup {OpenShift cluster} on {DNS name server}:53: no such host
```

- [GitHub issue](https://github.com/openshift/oc/issues/315)
- Workaround: Edit `/etc/hosts` and add IP address of OpenShift cluster
- Example: 9.AA.BBB.CC your.cluster.domain.com

## IBM-internal

### Compiling and installing Python 3.9 on FYRE infrastructure nodes

```
yum install gcc libffi-devel openssl-devel zlib-devel
wget https://www.python.org/ftp/python/3.9.0/Python-3.9.0.tgz
tar -xf Python-3.9.0.tgz
cd Python-3.9.0
./configure
make
make install
```
