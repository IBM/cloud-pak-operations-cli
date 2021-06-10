import pathlib
import urllib.parse

from typing import Final

import dg.lib.fyre.utils.network
import dg.utils.download
import dg.utils.network
import dg.utils.process
import dg.utils.ssh

SET_UP_OC4_URL: Final[str] = "https://github.ibm.com/api/v3/repos/PrivateCloud/cpd-fyre-cluster/contents/set_up_oc4.sh"


def download_nfs_storage_class_installation_script(ibm_github_api_key: str) -> pathlib.Path:
    """Downloads the NFS storage class installation script

    Parameters
    ----------
    ibm_github_api_key
        IBM GitHub API key

    Returns
    -------
    pathlib.Path
        path of the NFS storage class installation script
    """

    nfs_storage_class_installation_script_path = dg.utils.download.download_file(
        urllib.parse.urlsplit(SET_UP_OC4_URL),
        auth=("", ibm_github_api_key),
        headers={"Accept": "application/vnd.github.v3.raw"},
    )

    return nfs_storage_class_installation_script_path


def install_nfs_storage_class(ibm_github_api_key: str):
    """Installs the NFS storage class

    Parameters
    ----------
    ibm_github_api_key
        IBM GitHub API key
    """

    local_ipv4_addresses = dg.utils.network.get_local_ipv4_addresses()
    private_ip_address_of_infrastructure_node = dg.lib.fyre.utils.network.get_private_ip_address_of_infrastructure_node(
        local_ipv4_addresses
    )

    nfs_storage_class_installation_script_path = download_nfs_storage_class_installation_script(ibm_github_api_key)

    dg.utils.process.execute_command(pathlib.Path("chmod"), ["a+x", str(nfs_storage_class_installation_script_path)])
    dg.utils.process.execute_command(
        nfs_storage_class_installation_script_path,
        [str(private_ip_address_of_infrastructure_node)],
    )


async def install_nfs_storage_class_on_remote_host(
    infrastructure_node_hostname: str, ibm_github_api_key: str, oc_login_command_for_remote_host: str
):
    """Installs the NFS storage class on a remote host

    Parameters
    ----------
    infrastructure_node_hostname
        infrastructure node hostname
    ibm_github_api_key
        IBM GitHub API key
    oc_login_command_for_remote_host
        oc login command for logging in to OpenShift on the remote host
    """

    nfs_storage_class_installation_script_path = download_nfs_storage_class_installation_script(ibm_github_api_key)

    async with dg.utils.ssh.RemoteClient(infrastructure_node_hostname) as remoteClient:
        await remoteClient.connect()
        await remoteClient.execute(oc_login_command_for_remote_host)

        hostname_result = await remoteClient.execute("hostname --all-ip-addresses", print_output=False)
        private_ip_address_of_infrastructure_node = (
            dg.lib.fyre.utils.network.get_private_ip_address_of_infrastructure_node(
                dg.utils.network.parse_hostname_result(hostname_result)
            )
        )

        await remoteClient.upload(nfs_storage_class_installation_script_path)
        await remoteClient.execute("chmod a+x " + nfs_storage_class_installation_script_path.name)
        await remoteClient.execute(
            "./"
            + nfs_storage_class_installation_script_path.name
            + " "
            + str(private_ip_address_of_infrastructure_node)
        )
