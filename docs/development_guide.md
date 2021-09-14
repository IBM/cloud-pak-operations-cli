# Development Guide

## Setting up the development environment

- Clone the Db2 Data Gate CLI GitHub repository:

  ```shell
  git clone https://github.com/IBM/data-gate-cli.git
  ```

- Execute the following commands to create a [virtual environment](https://virtualenv.pypa.io/en/latest/) within the directory the Db2 Data Gate CLI GitHub repository was cloned into:

  - Linux/macOS:

    ```shell
    pip3 install virtualenv
    virtualenv .venv
    . .venv/bin/activate
    pip3 install black flake8 isort
    pip3 install --editable .
    ```

  - Windows:

    ```shell
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

To register a new Click group (e.g., `click-group-name`), add a Python package (i.e., a directory containing a file named `__init__.py`) to the `commands` directory or one of its subdirectories (e.g., `click_group_name`). Furthermore, add the following code to `__init__.py` to automatically register Click commands within Python modules contained in the package:

```python
import sys

import click

from dg.lib.click.lazy_loading_multi_command import (
    create_click_multi_command_class,
)

@click.command(cls=create_click_multi_command_class(sys.modules[__name__]))
def click_group_name():
    pass
```

## Running unit tests

Unit tests are based on the `unittest` package and contained in the `tests.test` package. Execute the following command to execute all unit tests within your virtual environment:

```shell
python -m unittest discover tests.test
```

## Profiling using FunctionTrace (Linux/macOS)

Use [FunctionTrace](https://functiontrace.com/) to profile a Db2 Data Gate CLI command as follows:

- [Install Rust and Cargo](https://doc.rust-lang.org/cargo/getting-started/installation.html#install-rust-and-cargo)

- Install the FunctionTrace server:

  ```shell
  cargo install functiontrace-server
  ```

- Install the Python client in your virtual environment:

  ```shell
  pip3 install functiontrace
  ```

- Execute the following command to profile a Db2 Data Gate CLI command:

  ```shell
  python3 -m functiontrace $(which dg) $COMMAND
  ```

- After having executed the Db2 Data Gate CLI, the FunctionTrace server prints the location of the profiling data file:

  ```shell
  [FunctionTrace] Wrote profile data to …
  ```

- Use [Firefox Profiler](https://profiler.firefox.com/) to analyze the profiling data file.

## Releasing a new version using semantic versioning

- Create a new branch, commit the code leading to a new release, and tag the commit with a semantic version:

  ```shell
  git tag v$MAJOR.$MINOR.$PATCH
  ```

- Push the branch and the tag:

  ```shell
  git push --atomic origin $BRANCH_NAME v$MAJOR.$MINOR.$PATCH
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

```shell
pip3 install --extra-index-url https://pypi.org/simple --index-url https://test.pypi.org/simple/ data-gate-cli==$VERSION
```

## References

- [Coding Guidelines](coding_guidelines.md)
