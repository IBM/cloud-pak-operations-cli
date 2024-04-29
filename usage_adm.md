---
nav_order: 2
---

# Usage: Administering the CLI

## Downloading dependencies

This commands explicitly downloads the latest version of all dependencies and stores them in `~/.cpo/bin`.

### Syntax

```shell
cpo adm download-dependencies [OPTIONS]
```

### Parameters

```
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --help                          Show this message and exit.
```

## Getting the location of the shell completion script

This commands supports enabling shell completion as descibed [here](/installation.html#shell-completion-linuxmacos).

### Syntax

```shell
cpo adm get-shell-completion-script-location [OPTIONS]
```

### Parameters

```
  --shell [bash|zsh]              Shell name  [required]
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --help                          Show this message and exit.
```

## Setting configuration option

### Syntax

```shell
cpo adm set-config-option [OPTIONS]
```

### Parameters

```
  --key TEXT                      Key name which should be set  [required]
  --value TEXT                    Value to which key should be set  [required]
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --help                          Show this message and exit.
```

## Storing credentials

This commands stores Artifactory credentials (IBM-internal functionality) and the IBM Cloud Pak for Data entitlement key.

### Syntax

```shell
cpo adm store-credentials [OPTIONS]
```

### Parameters

```
  --artifactory-password TEXT     Artifactory password
  --artifactory-username TEXT     Artifactory username
  --ibm-cloud-pak-for-data-entitlement-key TEXT
                                  IBM Cloud Pak for Data entitlement key (see
                                  https://myibm.ibm.com/products-
                                  services/containerlibrary)
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --help                          Show this message and exit.
```

## Updating the CLI to the latest development code

This command installs the latest development code from GitHub. It is not possible to update a release version to the latest development code.

### Syntax

```shell
cpo adm update-dev [OPTIONS]
```

### Parameters

```
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --help                          Show this message and exit.
```
