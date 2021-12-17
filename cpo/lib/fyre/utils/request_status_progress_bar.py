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

from time import sleep
from typing import Callable

from tqdm import tqdm

from cpo.lib.fyre.data.request_status_data import RequestStatusData


def wait_for_request_completion(request_id: str, get_request_status_callback: Callable[[str], RequestStatusData]):
    """Waits for an FYRE/OCP+ API request to complete

    The status of a request is itself retrieved using the FYRE/OCP+ API.
    To visualize the progress, a progress bar is shown.

    Parameters
    ----------
    request_id
        request ID
    get_request_status_callback
        callback for getting the request status
    """

    request_progress_bar = tqdm(bar_format="{l_bar}{bar}| [{elapsed}]", total=100, unit="%")

    while True:
        request_status = get_request_status_callback(request_id).get_status()

        if request_status["status"] != "success":
            break

        request = request_status["request"]
        completion_percent = request["completion_percent"]
        n = completion_percent - request_progress_bar.n

        if n != 0:
            request_progress_bar.update(n)
        else:
            request_progress_bar.refresh()

        if completion_percent == 100:
            break

        sleep(1)

    request_progress_bar.close()
