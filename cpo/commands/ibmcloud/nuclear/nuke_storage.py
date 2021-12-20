#  Copyright 2020, 2021 IBM Corporation
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

import logging

from subprocess import CalledProcessError

import click

from cpo.lib.ibmcloud import execute_ibmcloud_command
from cpo.utils.logging import loglevel_command

logger = logging.getLogger(__name__)


@loglevel_command()
@click.option("--zone", help="Zone to delete deployments in (e.g. sjc03)", required=True)
def nuke_storage(zone: str):
    """Immediately cancel ALL classic file storage volumes on IBM Cloud in a given zone"""

    if click.confirm(
        click.style(
            f"Do you really wish to immediately cancel all classic file storage volumes in zone '{zone}'?",
            bold=True,
            fg="red",
        )
    ):
        list_command = ["sl", "file", "volume-list"]
        volume_list_full = execute_ibmcloud_command(list_command, capture_output=True)
        volumes_to_be_deleted = 0
        volume_ids_to_be_deleted = []

        click.echo()
        click.secho(
            f"The following volumes are marked for cancellation in zone '{zone}':",
            bold=True,
        )
        for line in volume_list_full.stdout.split("\n"):
            if zone in line:
                click.echo(line)
                volumes_to_be_deleted += 1
                volume_id = line.split(" ")[0]
                volume_ids_to_be_deleted.append(volume_id)

        click.echo()
        if click.confirm(
            click.style(
                f"☠ You will immediately cancel {volumes_to_be_deleted} possible in-use volumes. Are you sure? ☠",
                blink=True,
                bold=True,
                fg="red",
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
                    execute_ibmcloud_command(delete_command)

                    logging.info(f"File volume {volume_id} has been marked for immediate cancellation")
                    volumes_deleted += 1
                except CalledProcessError as exception:
                    if "No billing item is found to cancel" in exception.stderr:
                        logging.warning(
                            f"No billing item found for volume ID {volume_id}. This volume has most likely already "
                            f"been canceled."
                        )
                    else:
                        logging.warning(
                            f"An error occurred while canceling volume ID {volume_id} – error details:\n"
                            f"{exception.stderr}"
                        )

            logging.info(
                f"In total, {volumes_deleted} volumes have been marked for cancellation.",
                bold=True,
            )
    else:
        click.echo("Aborting.")
