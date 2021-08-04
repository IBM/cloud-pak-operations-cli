# Development Guide

## Setting up the development environment

- Clone the Db2 Data Gate CLI GitHub repository:

  ```bash
  git clone https://github.com/IBM/data-gate-cli.git
  ```

- Execute the following commands to create a [virtual environment](https://virtualenv.pypa.io/en/latest/) within the directory the Db2 Data Gate CLI GitHub repository was cloned into:

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

## Extending the Db2 Data Gate CLI

The Db2 Data Gate CLI is based on the [Click package](https://palletsprojects.com/p/click/).

### Registering a new Click command

To register a new Click command, add the Python module containing the command to the `commands` directory or one of its subdirectories.

### Registering a new Click group

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

## Running unit tests

Unit tests are based on the `unittest` package and contained in the `tests.test` package. Execute the following command to execute all unit tests within your virtual environment:

```bash
python -m unittest discover tests.test
```

## Releasing a new version using semantic versioning

- Create a new branch, commit the code leading to a new release, and tag the commit with a semantic version:

  ```bash
  git tag v{major}.{minor}.{patch}
  ```

- Push the branch and the tag:

  ```bash
  git push --atomic origin {branch name} v{major}.{minor}.{patch}
  ```

- Create a pull request based on the created branch
- Merge the reviewed pull request

After having pushed the branch and the tag, the following actions are performed:

- A Python distribution is built using the tagged version as the package version.
- The Python distribution is published to [TestPyPI](https://test.pypi.org/).

After having merged the pull request, the following actions are performed:

- A Python distribution is built using the tagged version as the package version.
- The Python distribution is published to [PyPI](https://pypi.org/).
- A Docker image containing the installed Python distribution is built and pushed to Quay.
- A GitHub release draft is created, which must be manually published.

To install a Db2 Data Gate CLI version from TestPyPI, execute the following command:

```bash
pip3 install --extra-index-url https://pypi.org/simple --index-url https://test.pypi.org/simple/ data-gate-cli=={version}
```

## References

- [Coding Guidelines](docs/coding_guidelines.md)
