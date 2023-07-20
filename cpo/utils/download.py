#  Copyright 2021, 2023 IBM Corporation
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

import io
import logging
import os
import pathlib
import re as regex
import tempfile
import urllib.parse

from typing import Any

import requests

from tqdm import tqdm

logger = logging.getLogger(__name__)


def download_file(url: urllib.parse.SplitResult, **kwargs: Any) -> pathlib.Path:
    """Downloads a file to the temporary directory of the current user

    If an argument for target_directory_path is passed, the file is
    downloaded to the specified directory.

    Parameters
    ----------
    url
        url of the file to be downloaded
    **kwargs
        auth
            passed to requests.get()
        headers
            passed to requests.get()
        target_directory_path
            path of the directory the file shall be downloaded to

    Returns
    -------
    pathlib.Path
        Path of the downloaded file
    """

    args: dict[str, Any] = {}

    if "auth" in kwargs:
        args["auth"] = kwargs["auth"]

    if "headers" in kwargs:
        args["headers"] = kwargs["headers"]

    args["stream"] = True

    response = requests.get(urllib.parse.urlunsplit(url), **args)
    response.raise_for_status()

    file_name: str

    if "Content-Disposition" in response.headers:
        content_disposition = response.headers["Content-Disposition"]
        search_result = regex.search('filename="?([^;"]+)"?', content_disposition)
        file_name = (
            search_result.group(1)
            if search_result is not None
            else os.path.basename(urllib.parse.urlsplit(response.url).path)
        )
    else:
        file_name = os.path.basename(urllib.parse.urlsplit(response.url).path)

    logger.info(f"Downloading: {response.url} [{file_name}]")

    content_length = (
        int(str(response.headers.get("Content-Length"))) if response.headers.get("Content-Length") is not None else 0
    )

    download_progress_bar = tqdm(total=content_length, unit="B", unit_scale=True)
    path = (
        pathlib.Path(kwargs["target_directory_path"] if "target_directory_path" in kwargs else tempfile.gettempdir())
        / file_name
    )

    with open(path, "wb") as file:
        for chunk in response.iter_content(chunk_size=1048576):  # 1 MiB
            file.write(chunk)
            download_progress_bar.update(len(chunk))

    download_progress_bar.close()

    return path


def download_file_into_buffer(url: urllib.parse.SplitResult, output_stream: io.BufferedIOBase, **kwargs: Any) -> str:
    """Downloads a file and writes its content into the given output
    stream.

    Parameters
    ----------
    url
        url of the file to be downloaded
    output_stream
        output stream the content of the downloaded file is written to
    **kwargs
        silent: bool
            flag indicating whether output to stdout shall be suppressed
    """

    response = requests.get(urllib.parse.urlunsplit(url), stream=True)
    response.raise_for_status()

    file_name: str

    if "Content-Disposition" in response.headers:
        content_disposition = response.headers["Content-Disposition"]
        search_result = regex.search('filename="?([^;"]+)"?', content_disposition)
        file_name = (
            search_result.group(1)
            if search_result is not None
            else os.path.basename(urllib.parse.urlsplit(response.url).path)
        )
    else:
        file_name = os.path.basename(urllib.parse.urlsplit(response.url).path)

    if ("silent" not in kwargs) or not kwargs["silent"]:
        logger.info(f"Downloading: {response.url} [{file_name}]")

    content_length = (
        int(str(response.headers.get("Content-Length"))) if response.headers.get("Content-Length") is not None else 0
    )

    if ("silent" in kwargs) and kwargs["silent"]:
        for chunk in response.iter_content(chunk_size=1048576):  # 1 MiB
            output_stream.write(chunk)
    else:
        download_progress_bar = tqdm(total=content_length, unit="B", unit_scale=True)

        for chunk in response.iter_content(chunk_size=1048576):  # 1 MiB
            output_stream.write(chunk)
            download_progress_bar.update(len(chunk))

        download_progress_bar.close()

    return file_name
