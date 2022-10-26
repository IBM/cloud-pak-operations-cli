#  Copyright 2021, 2022 IBM Corporation
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

from time import sleep

import click

from cpo.utils.error import CloudPakOperationsCLIException

logger = logging.getLogger(__name__)


def wait_for(timeout, interval, action_name, predicate, *args, **kwargs):
    time_passed = 0

    while time_passed < timeout:
        time_passed_output = f"Time spent / timeout ({str(time_passed).rjust(4, ' ')}s / {str(timeout).rjust(4, ' ')}s)"

        if predicate(*args, **kwargs):
            if time_passed != 0:
                click.echo(time_passed_output)

            logger.info(f"{action_name} finished successfully.")

            break

        click.echo(f"{time_passed_output}\r", nl=False)
        sleep(interval)
        time_passed += interval
    else:
        raise CloudPakOperationsCLIException(f"{action_name} timed out.")
