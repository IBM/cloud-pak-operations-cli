#  Copyright 2020 IBM Corporation
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

from subprocess import CalledProcessError

import click

from dg.utils.thirdparty import execute_ibmcloud_command_with_check


@click.command()
@click.option(
    "--zone", required=True, help="Zone to delete deployments in (e.g. sjc03)"
)
def nuke_storage(zone: str):
    """Immediately cancel ALL classic file storage volumes on IBM Cloud in a given zone"""

    if click.confirm(
        click.style(
            f"Do you really wish to immediately cancel all classic file storage volumes in zone '{zone}'?",
            fg="red",
        )
    ):
        list_command = ["sl", "file", "volume-list"]
        volume_list_full = execute_ibmcloud_command_with_check(list_command)
        volumes_to_be_deleted = 0
        volume_ids_to_be_deleted = []

        click.echo()
        click.secho(
            f"The following volumes are marked for cancellation in zone '{zone}':",
            fg="white",
        )
        for line in volume_list_full.stdout.split("\n"):
            if zone in line:
                click.echo(line)
                volumes_to_be_deleted += 1
                volume_id = line.split(" ")[0]
                volume_ids_to_be_deleted.append(volume_id)

        click.echo("")
        if click.confirm(
            click.style(
                f"☠ You will immediately cancel {volumes_to_be_deleted} possible in-use volumes. Are you sure? ☠",
                fg="red",
                blink=True,
                bold=True,
            )
        ):
            volumes_deleted = 0

            for volume_id in volume_ids_to_be_deleted:
                try:
                    delete_command = [
                        "sl",
                        "file",
                        "volume-cancel",
                        volume_id,
                        "--immediate",
                        "-f",
                    ]
                    execute_ibmcloud_command_with_check(delete_command)

                    click.echo(
                        f"File volume {volume_id} has been marked for immediate cancellation"
                    )
                    volumes_deleted += 1
                except CalledProcessError as exception:
                    if "No billing item is found to cancel" in exception.stderr:
                        click.echo(
                            f"No billing item found for volume ID {volume_id}. This volume has most likely already "
                            f"been canceled."
                        )
                    else:
                        click.echo(
                            f"An error occurred during cancellation of volume id {volume_id}:"
                        )
                        click.echo(exception.stderr)

            click.secho(
                f"In total, {volumes_deleted} volumes have been marked for cancellation.",
                fg="white",
            )
    else:
        click.echo("Aborting.")
