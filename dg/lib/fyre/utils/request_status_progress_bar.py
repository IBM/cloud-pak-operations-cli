from time import sleep
from typing import Callable

from tqdm import tqdm

from dg.lib.fyre.data.request_status_data import RequestStatusData


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
