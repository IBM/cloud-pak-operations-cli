#  Copyright 2022 IBM Corporation
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


from cpo.utils.error import CloudPakOperationsCLIException


class GetPodEntry:
    def __init__(self, name: str, readiness_actual: int, readiness_total: int, status: str, restarts: int, age: str):
        self.name = name
        self.readiness_actual = readiness_actual
        self.readiness_total = readiness_total
        self.status = status
        self.restarts = restarts
        self.age = age

    @classmethod
    def parse(cls, line: str):
        parts = line.split()

        if len(parts) != 5:
            raise CloudPakOperationsCLIException("Unable to split pod status line into 5 parts.")

        name = parts[0]

        ready = parts[1].split("/")
        if len(ready) != 2:
            raise CloudPakOperationsCLIException("Unable to split ready information into 2 parts")
        readiness_actual = int(ready[0])
        readiness_total = int(ready[1])

        status = parts[2]
        restarts = int(parts[3])
        age = parts[4]

        return GetPodEntry(name, readiness_actual, readiness_total, status, restarts, age)

    def is_ready(self):
        return self.readiness_actual == self.readiness_total

    def is_running(self):
        return self.status == "Running"
