---
nav_order: 3
---

# Usage: Administering IBM-internal CLI plug-ins

## Listing available IBM-internal CLI plug-ins

### Syntax

```shell
cpo adm ibm-internal-plugin ls [OPTIONS]
```

### Parameters

```
  --artifactory-username TEXT     Artifactory username (IBM e-mail address)
                                  [required]
  --artifactory-password TEXT     Artifactory identity token (Artifactory
                                  website → 'Edit Profile' → 'Identity
                                  Tokens')  [required]
  --repository-url TEXT
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --help                          Show this message and exit.
```

## Installing IBM-internal CLI plug-ins

### Syntax

```shell
cpo adm ibm-internal-plugin install [OPTIONS] [DISTRIBUTION_PACKAGE_NAMES]...
```

### Parameters

```
  --artifactory-username TEXT     Artifactory username (IBM e-mail address)
                                  [required]
  --artifactory-password TEXT     Artifactory identity token (Artifactory
                                  website → 'Edit Profile' → 'Identity
                                  Tokens')  [required]
  --repository-url TEXT
  --user                          Install to user site-packages directory
  --version TEXT                  Plug-in version
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --help                          Show this message and exit.
```

## Upgrading IBM-internal CLI plug-ins

### Syntax

```shell
cpo adm ibm-internal-plugin upgrade-plugins [OPTIONS]
```

### Parameters

```
  --artifactory-username TEXT     Artifactory username (IBM e-mail address)
                                  [required]
  --artifactory-password TEXT     Artifactory identity token (Artifactory
                                  website → 'Edit Profile' → 'Identity
                                  Tokens')  [required]
  --repository-url TEXT
  --user                          Install to user site-packages directory
  --loglevel [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Log level
  --help                          Show this message and exit.
```
