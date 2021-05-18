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

from typing import TypedDict


class RequestData(TypedDict):
    complete: str
    completion_percent: int
    failed: str
    in_progress: str
    job_count: str
    last_status_time: str
    last_status: str
    pending: str
    request_id: str
    task_count: str


class OCPRequestGetResponse(TypedDict):
    request: RequestData
    status: str
