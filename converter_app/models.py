import json
import logging
import os
import pathlib
import tarfile
import tempfile
import uuid
from collections import defaultdict

from pathlib import Path

import magic
from flask import current_app
from werkzeug.datastructures import FileStorage

from converter_app.utils import check_uuid

logger = logging.getLogger(__name__)


class Profile:
    """
    Profile objects wraps profile JSON

    Attributes:
        data        [dict] contains {identifiers:..., tables: [...]}
        client_id   [str] id of the user
        id          [str] id of the profile and file name
        errors      [collections.defaultdict] contains all errors if profile is not correct
    """

    def __init__(self, profile_data, client_id, profile_id=None):
        self.data = profile_data
        self.client_id = client_id
        self.id = profile_id
        self.errors = defaultdict(list)

    def clean(self):
        """
        Checks if a profile is correct. see the error
        :return: [bool] if profile is validatable
        """
        self.errors.clear()

        self._clean_id()
        self._clean_identifiers()
        self._clean_tables()

        return not self.errors

    def _clean_id(self):
        """
        Checks if the profile ID is valid
        """
        if self.id is None and 'id' in self.data:
            profile_id = self.data['id']
            if check_uuid(profile_id):
                existing_profile = Profile.retrieve(self.client_id, self.data['id'])
                if existing_profile:
                    self.errors['id'].append('A profile with this ID already exists.')
            else:
                self.errors['id'].append('id is not a valid UUID4.')

    def _clean_identifiers(self):
        """
        Checks if the identifiers is valid
        """
        if 'identifiers' in self.data:
            if isinstance(self.data['identifiers'], list):
                pass
            else:
                self.errors['identifiers'].append('identifiers has to be a list.')
        else:
            self.errors['identifiers'].append('identifiers have to be provided.')

    def _clean_tables(self):
        """
        Checks if the tables is valid
        """

        if 'tables' in self.data:
            if isinstance(self.data['tables'], list):
                for table in self.data['tables']:
                    if 'table' in table:
                        if isinstance(table['table'], dict):
                            pass
                        else:
                            self.errors['tables'].append('table.table has to be an object.')
                    else:
                        self.errors['table'].append('table.table has to be provided.')

                    if 'header' in table:
                        if isinstance(table['header'], dict):
                            pass
                        else:
                            self.errors['tables'].append('table.header field has to be an object.')
                    else:
                        self.errors['header'].append('table.header has to be provided.')
            else:
                self.errors['tables'].append('tables have to be provided.')

    def save(self):
        """
        Saves a profile under $PROFILES_DIR/$client_id/$id.json
        """
        profiles_path = Path(current_app.config['PROFILES_DIR']).joinpath(self.client_id)
        profiles_path.mkdir(parents=True, exist_ok=True)

        if self.id is None:
            if 'id' in self.data:
                self.id = self.data['id']
            else:
                # create a uuid for new profiles
                self.id = str(uuid.uuid4())

        file_path = profiles_path.joinpath(self.id).with_suffix('.json')
        with open(file_path, 'w', encoding='utf8') as fp:
            json.dump(self.data, fp, sort_keys=True, indent=4)

    def delete(self):
        """
        deletes the profile file
        """
        profiles_path = Path(current_app.config['PROFILES_DIR']).joinpath(self.client_id)

        file_path = profiles_path.joinpath(self.id).with_suffix('.json')
        if file_path.is_file():
            file_path.unlink()

    @property
    def as_dict(self):
        """
        :return: Profile data as dict
        """
        return {
            'id': self.id,
            **self.data
        }

    @classmethod
    def load(cls, file_path: pathlib.PurePath):
        """
        Profile factory loads profile
        :param file_path: $PROFILES_DIR/$client_id/$id.json
        :return: new Profile object
        """
        profile_data = json.loads(file_path.read_text())

        # ensure compatibility with older isRegex flag
        for identifier in profile_data.get('identifiers', []):
            if 'match' not in identifier:
                if 'isRegex' in identifier:
                    identifier['match'] = ('regex' if identifier['isRegex'] else 'exact')
                    del identifier['isRegex']
                else:
                    identifier['match'] = 'exact'

        return profile_data

    @classmethod
    def list(cls, client_id):
        """
        List all profiles of one user/client
        :param client_id: [str] Username
        :return:
        """
        profiles_path = Path(current_app.config['PROFILES_DIR']).joinpath(client_id)

        if profiles_path.exists():
            for file_path in sorted(Path.iterdir(profiles_path)):
                profile_id = str(file_path.with_suffix('').name)
                profile_data = cls.load(file_path)
                yield cls(profile_data, client_id, profile_id)

        return []

    @classmethod
    def retrieve(cls, client_id, profile_id):
        """
        Profile factory loads profile
        :param client_id: [str] Username
        :param profile_id: [str] profile id (uuid)
        :return:
        """
        profiles_path = Path(current_app.config['PROFILES_DIR']).joinpath(client_id)

        # make sure that its really a uuid, this should prevent file system traversal
        if check_uuid(profile_id):
            file_path = profiles_path.joinpath(profile_id).with_suffix('.json')
            if file_path.is_file():
                profile_data = cls.load(file_path)
                return cls(profile_data, client_id, profile_id)

        return False


class File:
    """
    Wraps File file stream object
    """

    def __init__(self, file):
        self._features = {}
        self.fp = file

        # read the file
        self.content = file.read()
        file.seek(0)

        self.mime_type = magic.Magic(mime=True).from_buffer(self.content)
        self.suffix = Path(file.filename).suffix

        if self.suffix in ['.pdf']:
            self.encoding = 'binary'
        else:
            self.encoding = magic.Magic(mime_encoding=True).from_buffer(self.content)

        # decode file string
        self.string = self.content.decode(self.encoding, errors='ignore') if self.encoding != 'binary' else None

    @property
    def content_type(self):
        """
        :return: The content type of the file
        """
        return self.fp.content_type

    @property
    def name(self):
        """
        :return: The origin file name
        """
        return os.path.basename(self.fp.filename)

    @property
    def file_path(self):
        """
        This is only required for subfiles of a tar archive file
        :return: The origin file path
        """
        return os.path.dirname(self.fp.filename)

    def features(self, name):
        """
        features are extensions information of the file. For example PDF content or csv_dialect
        :param name: Name or Key of the feature
        :return:
        """
        res = self._features.get(name)
        if res is None:
            raise AttributeError(f"{name} is no feature of this file ({self.name})!")
        return res

    def set_features(self, name, feature_content):
        """
        features are extensions information of the file. For example PDF content or csv_dialect
        :param name: Name or Key of the feature
        :param feature_content: Feature content
        """
        self._features[name] = feature_content

    @property
    def is_tar_archive(self) -> bool:
        """
        Checks if the file is a tar archive
        :return: True if the file is a tar archive
        """
        return self.name.endswith(".gz") or self.name.endswith(".xz") or self.name.endswith(".tar")


def extract_tar_archive(file: File, temp_dir: str) -> list[File]:
    """
    If the file is a tar archive, this function extracts it and returns a list of all files
    :param file: Input file from the client
    :return: A list of all files extracted
    """
    if not file.is_tar_archive:
        return []
    file_list = []
    with tempfile.NamedTemporaryFile(delete=True) as temp_archive:
        try:
            # Save the contents of FileStorage to the temporary file
            file.fp.save(temp_archive.name)
            if file.name.endswith(".gz"):
                mode = "r:gz"
            elif file.name.endswith(".xz"):
                mode = "r:xz"
            elif file.name.endswith(".tar"):
                mode = "r:"
            else:
                return []
            with tarfile.open(temp_archive.name, mode) as tar:
                tar.extractall(temp_dir)
                tar.close()
        except ValueError:
            return []

        for root, _, files in os.walk(temp_dir, topdown=False):
            for name in files:
                path_file_name = os.path.join(root, name)
                content_type = magic.Magic(mime=True).from_file(path_file_name)
                f = open(path_file_name, 'rb')
                fs = FileStorage(stream=f, filename=path_file_name,
                                 content_type=content_type)
                file_list.append(File(fs))

    return file_list
