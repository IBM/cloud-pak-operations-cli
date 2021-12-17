#  Copyright 2021 IBM Corporation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import pathlib

from typing import Final, List

import cpo.lib.openshift.oc
import cpo.utils.process
import cpo.utils.ssh

STORAGE_PATH: Final[str] = "/var/home/core/data"


def init_node_for_db2(node: str, db2_edition: str, use_host_path_storage: bool):
    """Initializes a worker node before creating a Db2 instance

    Parameters
    ----------
    node
        hostname of the worker node to be initialized
    db2_edition
        Db2 edition
    use_host_path_storage
        flag indicating whether hostpath storage shall be used
    """

    cpo.lib.openshift.oc.execute_oc_command(_get_oc_adm_taint_node_command(node, db2_edition))
    cpo.lib.openshift.oc.execute_oc_command(_get_oc_label_node_command(node, db2_edition))
    cpo.utils.process.execute_command(pathlib.Path("ssh"), _get_ssh_setsebool_container_manage_cgroup_command(node))

    if use_host_path_storage:
        label_storage_path(node)


async def init_node_for_db2_from_remote_host(
    infrastructure_node_hostname: str,
    node: str,
    db2_edition: str,
    use_host_path_storage: bool,
    oc_login_command_for_remote_host: str,
):
    """Initializes a worker node from a remote host before creating a Db2
    instance

    Parameters
    ----------
    infrastructure_node_hostname
        infrastructure node hostname
    node
        hostname of the worker node to be initialized
    db2_edition
        Db2 edition
    use_host_path_storage
        flag indicating whether hostpath storage shall be used
    oc_login_command_for_remote_host
        oc login command for logging in to OpenShift on the remote host
    """

    async with cpo.utils.ssh.RemoteClient(infrastructure_node_hostname) as remoteClient:
        await remoteClient.connect()
        await remoteClient.execute(oc_login_command_for_remote_host)
        await remoteClient.execute("oc " + " ".join(_get_oc_adm_taint_node_command(node, db2_edition)))
        await remoteClient.execute("oc " + " ".join(_get_oc_label_node_command(node, db2_edition)))
        await remoteClient.execute("ssh " + " ".join(_get_ssh_setsebool_container_manage_cgroup_command(node)))

        if use_host_path_storage:
            await label_storage_path_from_remote_host(remoteClient, node)


def label_storage_path(node: str):
    """Labels the storage path on the given node

    See https://www.ibm.com/support/producthub/icpdata/docs/content/SSQNUZ_latest/svc-db2/hostpath-selinux-aese.html

    Parameters
    ----------
    node
        node on which the storage path shall be labeled
    """

    cpo.utils.process.execute_command(pathlib.Path("ssh"), _get_ssh_mkdir_storage_path_command(node))
    cpo.utils.process.execute_command(pathlib.Path("ssh"), _get_ssh_chmod_storage_path_command(node))
    cpo.utils.process.execute_command(pathlib.Path("ssh"), _get_ssh_semanage_storage_path_command(node))
    cpo.utils.process.execute_command(pathlib.Path("ssh"), _get_ssh_restorecon_storage_path_command(node))


async def label_storage_path_from_remote_host(remote_client: cpo.utils.ssh.RemoteClient, node: str):
    """Labels the storage path on the given node from a remote host

    See https://www.ibm.com/support/producthub/icpdata/docs/content/SSQNUZ_latest/svc-db2/hostpath-selinux-aese.html

    Parameters
    ----------
    remote_client
        SSH client
    node
        node on which the storage path shall be labeled
    """

    await remote_client.execute("ssh " + _join_args(_get_ssh_mkdir_storage_path_command(node)))
    await remote_client.execute("ssh " + _join_args(_get_ssh_chmod_storage_path_command(node)))
    await remote_client.execute("ssh " + _join_args(_get_ssh_semanage_storage_path_command(node)))
    await remote_client.execute("ssh " + _join_args(_get_ssh_restorecon_storage_path_command(node)))


def _get_oc_adm_taint_node_command(node: str, db2_edition: str) -> List[str]:
    return [
        "adm",
        "taint",
        "node",
        node,
        f"icp4data=database-{db2_edition}:NoSchedule",
    ]


def _get_oc_label_node_command(node: str, db2_edition: str) -> List[str]:
    return ["label", "node", node, f"icp4data=database-{db2_edition}"]


def _get_ssh_mkdir_storage_path_command(node: str) -> List[str]:
    return [f"core@{node}", "mkdir", "--parents", STORAGE_PATH]


def _get_ssh_chmod_storage_path_command(node: str) -> List[str]:
    return [f"core@{node}", "chmod", "777", STORAGE_PATH]


def _get_ssh_restorecon_storage_path_command(node: str) -> List[str]:
    return [f"core@{node}", "sudo", "restorecon", "-Rv", STORAGE_PATH]


def _get_ssh_semanage_storage_path_command(node: str) -> List[str]:
    return [
        f"core@{node}",
        f'sudo semanage fcontext --add --type container_file_t "{STORAGE_PATH}(/.*)?"',
    ]


def _get_ssh_setsebool_container_manage_cgroup_command(node: str) -> List[str]:
    return [
        f"core@{node}",
        "sudo",
        "setsebool",
        "-P",
        "container_manage_cgroup",
        "true",
    ]


def _join_args(args: List[str]) -> str:
    args_copy = args.copy()

    for i in range(len(args_copy)):
        if " " in args[i]:
            if "'" in args[i]:
                args_copy[i] = args_copy[i].replace("'", "\\'")

            args_copy[i] = f"'{args[i]}'"

    return " ".join(args_copy)
