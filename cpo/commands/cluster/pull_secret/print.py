#  Copyright 2024 IBM Corporation
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

import base64

import click

from pydantic import BaseModel

from cpo.utils.logging import loglevel_command


class RegistryCredentials(BaseModel):
    auth: str
    email: str
    password: str
    username: str


class DockerConfigJSON(BaseModel):
    auths: dict[str, RegistryCredentials]


@loglevel_command()
@click.option("--registry-location", help="Container registry location", required=True)
@click.option("--registry-location-username", help="Container registry username", required=True)
@click.option("--registry-location-password", help="Container registry password", required=True)
@click.option("--registry-location-email", default="", help="Container registry e-mail", show_default=True)
@click.option("--encode-base64", is_flag=True)
@click.pass_context
def print(
    ctx: click.Context,
    registry_location: str,
    registry_location_username: str,
    registry_location_password: str,
    registry_location_email: str,
    encode_base64: bool,
):
    """Print dockerconfigjson secret based on the given credentials"""

    docker_config_json = DockerConfigJSON(
        auths={
            registry_location: RegistryCredentials(
                auth=base64.standard_b64encode(
                    f"{registry_location_username}:{registry_location_password}".encode()
                ).decode("utf-8"),
                email=registry_location_email,
                password=registry_location_password,
                username=registry_location_username,
            )
        }
    )

    docker_config_json_str = docker_config_json.model_dump_json()

    if encode_base64:
        click.echo(base64.standard_b64encode(docker_config_json_str.encode()).decode("utf-8"))
    else:
        click.echo(docker_config_json_str)
