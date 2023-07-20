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

import os
import pathlib
import re as regex
import tarfile
import zipfile

from typing import Any, Callable

import cpo.utils.file

MemberIdentificationFunc = Callable[[str, cpo.utils.file.FileType], bool]
PostExtractionFunc = Callable[[pathlib.Path], None]


def execute_post_extraction_func_if_exists(extracted_file_path: pathlib.Path, **kwargs: Any):
    """Calls an optional function to perform post-extraction actions

    Parameters
    ----------
    extracted_file_path
        path of the extracted file
    **kwargs
        postExtractionFunc: PostExtractionFunc
            function called for each extracted file to perform
            post-extraction actions
    """

    if "postExtractionFunc" in kwargs:
        kwargs["postExtractionFunc"](extracted_file_path)


def extract_archive(archive_path: pathlib.Path, target_directory_path: pathlib.Path, **kwargs: Any):
    """Extracts a tar.gz, tgz, or zip archive

    Parameters
    ----------
    archive_path
        path of the archive to be extracted
    target_directory_path
        path of the directory the archive shall be extracted to
    **kwargs
        directoryPathToStartExtraction: str
            path of a directory indicating that only files and directories whose
            path starts with this path shall be extracted
        ignoreDirectoryStructure: bool
            flag indicating whether the directory structure within the archive shall
            be ignored (i.e., files are extracted to the target directory without
            creating subdirectories)
        memberIdentificationFunc: MemberIdentificationFunc
            function called for each file within the archive to determine whether
            the file shall be extracted
        postExtractionFunc: PostExtractionFunc
            function called for each extracted file to perform
            post-extraction actions
    """

    if (archive_path.suffixes == [".tar", ".gz"]) or (archive_path.suffix == ".tgz"):
        extract_tgz_archive(archive_path, target_directory_path, **kwargs)
    elif archive_path.suffix == ".zip":
        extract_zip_archive(archive_path, target_directory_path, **kwargs)


def extract_tgz_archive(archive_path: pathlib.Path, target_directory_path: pathlib.Path, **kwargs: Any):
    """Extracts a tar.gz or tgz archive

    Parameters
    ----------
    archive_path
        path of the archive to be extracted
    target_directory_path
        path of the directory the archive shall be extracted to
    **kwargs
        directoryPathToStartExtraction: str
            path of a directory indicating that only files and directories whose
            path starts with this path shall be extracted
        ignoreDirectoryStructure: bool
            flag indicating whether the directory structure within the archive shall
            be ignored (i.e., files are extracted to the target directory without
            creating subdirectories)
        memberIdentificationFunc: MemberIdentificationFunc
            function called for each file within the archive to determine whether
            the file shall be extracted
        postExtractionFunc: PostExtractionFunc
            function called for each extracted file to perform
            post-extraction actions
    """

    with tarfile.open(archive_path) as tar_file:
        for member in tar_file:
            if is_member_to_be_extracted(member.name, member.isdir(), **kwargs):
                if "directoryPathToStartExtraction" in kwargs:
                    directory_path_to_start_extraction = kwargs["directoryPathToStartExtraction"]
                    search_result = regex.search(f"({directory_path_to_start_extraction}/).*", member.name)

                    if search_result is None:
                        continue

                    member.name = member.name.removeprefix(search_result.group(1))

                if is_directory_structure_to_be_ignored(**kwargs):
                    member.name = os.path.basename(member.name)

                tar_file.extract(member, target_directory_path)
                execute_post_extraction_func_if_exists(target_directory_path / member.name, **kwargs)


def extract_zip_archive(archive_path: pathlib.Path, target_directory_path: pathlib.Path, **kwargs: Any):
    """Extracts a zip archive

    Parameters
    ----------
    archive_path
        path of the archive to be extracted
    target_directory_path
        path of the directory the archive shall be extracted to
    **kwargs
        directoryPathToStartExtraction: str
            path of a directory indicating that only files and directories whose
            path starts with this path shall be extracted
        ignoreDirectoryStructure: bool
            flag indicating whether the directory structure within the archive shall
            be ignored (i.e., files are extracted to the target directory without
            creating subdirectories)
        memberIdentificationFunc: MemberIdentificationFunc
            function called for each file within the archive to determine whether
            the file shall be extracted
        postExtractionFunc: PostExtractionFunc
            function called for each extracted file to perform
            post-extraction actions
    """

    with zipfile.ZipFile(archive_path) as zip_file:
        for member in zip_file.infolist():
            if is_member_to_be_extracted(member.filename, member.is_dir(), **kwargs):
                if is_directory_structure_to_be_ignored(**kwargs):
                    member.filename = os.path.basename(member.filename)

                zip_file.extract(member, str(target_directory_path))
                execute_post_extraction_func_if_exists(target_directory_path / member.filename, **kwargs)


def is_directory_structure_to_be_ignored(**kwargs: Any) -> bool:
    """Returns whether the directory structure within an archive shall be
       ignored

    Parameters
    ----------
    **kwargs
        ignoreDirectoryStructure: bool
            flag indicating whether the directory structure within the archive shall
            be ignored (i.e., files are extracted to the target directory without
            creating subdirectories)

    Returns
    -------
    bool
        true, if the directory structure within an archive shall be ignored
    """

    return ("ignoreDirectoryStructure" in kwargs) and (kwargs["ignoreDirectoryStructure"])


def is_member_to_be_extracted(member_name: str, is_dir: bool, **kwargs: Any) -> bool:
    """Returns whether the given member within an archive shall be extracted

    Parameters
    ----------
    member_name
        name of the member within an archive
    is_dir flag
        indicating whether the member is a directory
    **kwargs
        memberIdentificationFunc: MemberIdentificationFunc
            function called for each file within the archive to determine whether
            the file shall be extracted

    Returns
    -------
    bool
        true, if the given file within an archive shall be extracted
    """

    return ("memberIdentificationFunc" not in kwargs) or (
        ("memberIdentificationFunc" in kwargs)
        and kwargs["memberIdentificationFunc"](
            member_name,
            cpo.utils.file.FileType.Directory if is_dir else cpo.utils.file.FileType.RegularFile,
        )
    )
