# IBM Cloud Pak Operations CLI: Development Guide

## Setting up the development environment

- Clone the IBM Cloud Pak Operations CLI GitHub repository:

  ```shell
  git clone https://github.com/IBM/cloud-pak-operations-cli
  ```

- Execute the following commands to create a [virtual environment](https://virtualenv.pypa.io/en/latest/) within the directory the GitHub repository was cloned into:

  - Linux/macOS:

    ```shell
    pip3 install virtualenv
    virtualenv .venv
    . .venv/bin/activate
    pip3 install black flake8
    pip3 install --editable .
    ```

  - Windows:

    ```shell
    pip3 install virtualenv
    virtualenv .venv
    .venv/Scripts/activate
    pip3 install black flake8
    pip3 install --editable .
    ```

## Extending the IBM Cloud Pak Operations CLI

The IBM Cloud Pak Operations CLI is based on the [Click package](https://palletsprojects.com/p/click/).

### Registering a new Click command

To register a new Click command, add the Python module containing the command to the `commands` directory or one of its subdirectories.

### Registering a new Click group

To register a new Click group (e.g., `click-group-name`), add a Python package (i.e., a directory containing a file named `__init__.py`) to the `commands` directory or one of its subdirectories (e.g., `click_group_name`). For each Python package below the `commands` directory, a new Click group (i.e., an instance of [LazyLoadingMultiCommand](cpo/lib/click/lazy_loading_multi_command.py)) is implictly created.

## Writing an IBM Cloud Pak Operations CLI plug-in

The IBM Cloud Pak Operations CLI is extensible via plug-ins, which are regular distribution packages managed by `pip`.

To add Click commands or command groups to a built-in command group, CLI plug-ins (i.e., distribution packages) must export packages by specifying one or more entry points within the `cloud_pak_operations_cli_plugins` group in their configuration file.

To specify the built-in command group, the `__doc__` attribute of the `__init__.py` module of an entry point package must be set to the path of the built-in command group in the command hierarchy. Nested built-in command groups must be separated by slashes. If the `__doc__` attribute is not set, Click commands or command groups are added to the root command group.

### Examples

1. Package structure

```
package_1
| __init__.py (__doc__ = "")
| … (modules and subpackages)

package_2
| __init__.py (__doc__ = "adm/config")
| … (modules and subpackages)
```

2. setup.cfg:

```
[options.entry_points]
cloud_pak_operations_cli_plugins =
    entry_point_1 = package_1
    entry_point_2 = package_2
```

## Running unit tests

Unit tests are based on the `unittest` package and contained in the `tests.test` package. Execute the following command to execute all unit tests within your virtual environment:

```shell
python -m unittest discover tests.test
```

## Profiling using FunctionTrace (Linux/macOS)

Use [FunctionTrace](https://functiontrace.com/) to profile an IBM Cloud Pak Operations CLI command as follows:

- [Install Rust and Cargo](https://doc.rust-lang.org/cargo/getting-started/installation.html#install-rust-and-cargo)

- Install the FunctionTrace server:

  ```shell
  cargo install functiontrace-server
  ```

- Install the Python client in your virtual environment:

  ```shell
  pip3 install functiontrace
  ```

- Execute the following command to profile an IBM Cloud Pak Operations CLI command:

  ```shell
  python3 -m functiontrace $(which cpo) $COMMAND
  ```

- After having executed the CLI command, the FunctionTrace server prints the location of the profiling data file:

  ```shell
  [FunctionTrace] Wrote profile data to …
  ```

- Use [Firefox Profiler](https://profiler.firefox.com/) to analyze the profiling data file.

## Correcting copyright headers

Execute the following command to automatically correct copyright headers of source code files:

- Install required packages:

  ```shell
  pip3 install dulwich
  ```

- Execute the `update-copyright-headers` command:

  ```shell
  python3 -m scripts.scripts update-copyright-headers $REPO_PATH
  ```

## Testing the release of a new version using semantic versioning

- Create a new branch, commit the code leading to a new release, and tag the commit with a semantic version:

  ```shell
  git tag v$MAJOR.$MINOR.$PATCH
  ```

- Push the branch and the tag:

  ```shell
  git push --atomic origin $BRANCH_NAME v$MAJOR.$MINOR.$PATCH
  ```

- Delete the tag:

  ```shell
  git tag --delete v$MAJOR.$MINOR.$PATCH
  ```

- Delete the remote tag:

  ```shell
  git push --delete origin v$MAJOR.$MINOR.$PATCH
  ```

After having pushed the branch and the tag, the following actions are performed:

- A Python distribution is built using the tagged version as the package version.
- The Python distribution is published to [TestPyPI](https://test.pypi.org/).

To install a specific IBM Cloud Pak Operations CLI version from TestPyPI, execute the following command:

```shell
pip3 install --extra-index-url https://pypi.org/simple --index-url https://test.pypi.org/simple/ cloud-pak-operations-cli==$VERSION
```

If you are satisfied with the result and would like to publish the Python distribution to [PyPI](https://pypi.org/), continue as follows:

- Create a pull request based on the created branch
- Merge the reviewed pull request

## Releasing a new version using semantic versioning

- On the master branch, tag the latest commit with a semantic version:

  ```shell
  git tag v$MAJOR.$MINOR.$PATCH
  ```

- Push the tag:

  ```shell
  git push origin v$MAJOR.$MINOR.$PATCH
  ```

After having pushed the tag, the following actions are performed:

- A Python distribution is built using the tagged version as the package version.
- The Python distribution is published to [PyPI](https://pypi.org/).
- A Docker image containing the installed Python distribution is built and pushed to Quay.
- A GitHub release draft is created, which must be manually published.

## Adding support for a new IBM Cloud Pak for Data 4.0.x release

To add support for a new IBM Cloud Pak for Data 4.0.x release, perform the following steps:

- Update the `_IBM_CLOUD_PAK_FOR_DATA_VERSION` class variable of the [CloudPakForDataManager](cpo/lib/cloud_pak_for_data/cpd_4_0_0/cpd_manager.py) class
- Update [cpd-custom-resources.json](/cpo/deps/config/cpd-custom-resources.json) according to the [IBM Cloud Pak for Data 4.0 documentation](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.0?topic=integrations-services) (check custom resources for changes)
- Update [cpd-operand-requests.json](/cpo/deps/config/cpd-operand-requests.json) according to the [IBM Cloud Pak for Data 4.0 documentation](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.0?topic=tasks-creating-operator-subscriptions#preinstall-operator-subscriptions__svc-subcriptions) (check subscriptions for changes)
- Update [cpd-subscriptions.json](/cpo/deps/config/cpd-subscriptions.json) according to the [IBM Cloud Pak for Data 4.0 documentation](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.0?topic=tasks-creating-operator-subscriptions#preinstall-operator-subscriptions__svc-subcriptions) (check subscriptions for changes)

## References

- [Coding Guidelines](coding_guidelines.md)
