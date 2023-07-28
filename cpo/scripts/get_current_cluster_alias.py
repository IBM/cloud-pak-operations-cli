#  Copyright 2023 IBM Corporation
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

from cpo.config.cluster_credentials_manager import cluster_credentials_manager


def get_current_cluster_alias():
    clusters_file_contents = cluster_credentials_manager.get_clusters_file_contents()

    if (
        (clusters_file_contents is not None)
        and ("current_cluster" in clusters_file_contents)
        and ((current_cluster := clusters_file_contents["current_cluster"]) != "")
    ):
        assert "clusters" in clusters_file_contents

        for server, cluster_data in clusters_file_contents["clusters"].items():
            if server == current_cluster:
                if "alias" in cluster_data:
                    print(cluster_data["alias"])
                else:
                    print(server)

                break
