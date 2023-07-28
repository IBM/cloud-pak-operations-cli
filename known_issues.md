---
nav_order: 5
---

## Known issues

### OpenShift CLI (macOS)

```shell
Unable to connect to the server: dial tcp: lookup … on …:53: no such host
```

- [GitHub issue](https://github.com/openshift/oc/issues/315)
- Workaround: Edit `/etc/hosts` and add IP address of OpenShift cluster

  - Example:

    ```
    9.AA.BBB.CC your.cluster.domain.com
    ```
