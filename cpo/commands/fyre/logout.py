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

import cpo.config
import cpo.lib.click

from cpo.utils.logging import loglevel_command


@loglevel_command()
def logout():
    """Log out from FYRE"""

    credentials_to_be_stored = {"fyre_api_key": "", "fyre_api_user_name": ""}

    cpo.config.configuration_manager.store_credentials(credentials_to_be_stored)
