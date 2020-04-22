import abc

from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.http import HttpRequest
from rest_framework.request import Request

from entry.settings import MEDIA_ROOT, MEDIA_PATH_TEMP
from utils.data import guid
from utils.date import get_10
import os
import logging

logger = logging.getLogger(__name__)

STORAGE_TYPE_UNKNOWN = 0
STORAGE_TYPE_LOCAL_FILE = 1
STORAGE_TYPE_COS = 2

STORAGE_TYPE_LIST = ((STORAGE_TYPE_UNKNOWN, 'Unknown'),
                     (STORAGE_TYPE_LOCAL_FILE, 'Local File'),
                     (STORAGE_TYPE_COS, 'Tencent COS'))


class FileStorage(metaclass=abc.ABCMeta):

    STORAGE_TYPE = STORAGE_TYPE_LOCAL_FILE

    @classmethod
    def save(cls, file_data, to_path, to_name=None, org_name=None, use_date_directory=False):
        if isinstance(file_data, (Request, HttpRequest)):
            return cls._save_upload_file(file_data, to_path, to_name, use_date_directory)
        else:
            return cls._save(file_data, to_path, to_name, org_name, use_date_directory)

    @classmethod
    @abc.abstractmethod
    def _save(cls, file_data, to_path, to_name=None, org_name=None, use_date_directory=False):
        """
        save file data with storage
        :param file_data:
        :param args:
        :param kwargs:
        :return: saved success
        """
        pass

    @classmethod
    def delete(cls, file):
        cls._delete(file)

    @classmethod
    def delete_related(cls, file):
        cls._delete_related(file)

    @classmethod
    @abc.abstractmethod
    def _delete(cls, file):
        """
        delete file in storage
        :return: delete success
        """
        pass

    @classmethod
    @abc.abstractmethod
    def _delete_related(cls, file):
        """
        delete file in storage
        :return: delete success
        """
        pass

    @classmethod
    @abc.abstractmethod
    def _save_upload_file(cls, request, to_path, to_name, use_date_directory):
        pass

    @staticmethod
    @abc.abstractmethod
    def get_relative_path(path):
        pass

    @staticmethod
    @abc.abstractmethod
    def get_abspath_path(path):
        pass


class LocalFile(FileStorage):

    STORAGE_TYPE = STORAGE_TYPE_LOCAL_FILE

    @classmethod
    def _save(cls, file_data, to_path, to_name=None, org_name=None, use_date_directory=False):
        file_extension = org_name.split('.')[-1] if org_name else ''
        file_extension = '.' + file_extension if file_extension[0] != '.' else file_extension
        to_path = cls.get_abspath_path(to_path)
        if not os.path.isdir(to_path):
            logger.debug('Invalid path %s for save file' % to_path)
            return None
        destination = (cls._make_dirs_by_date(to_path) if use_date_directory else to_path) + '/' + \
                      (to_name if to_name else guid()) + file_extension
        destination = destination.replace('//', '/')
        if isinstance(file_data, InMemoryUploadedFile) or isinstance(file_data, TemporaryUploadedFile):
            with open(destination, 'wb+') as file_obj:
                for chunk in file_data.chunks():
                    file_obj.write(chunk)
                file_obj.close()

            logger.info('File %s has been saved!' % destination)
            return cls.get_relative_path(destination)
        else:
            return None

    @classmethod
    def _save_upload_file(cls, request, to_path, to_name=None, use_date_directory=False):
        """
        save uploaded file to storage with a media file object
        :param request: request
        :return: media file object
        """
        file_data = request.FILES['file']
        if file_data is None:
            return None

        return cls._save(file_data, to_path, to_name, file_data.name, use_date_directory)

    @classmethod
    def _delete(cls, file):
        file = cls.get_abspath_path(file)
        try:
            os.remove(file)
            logger.info('file %s has been deleted' % file)
        except FileNotFoundError as err:
            logger.warning('unable delete file %s! %s' % (file, err))

    @classmethod
    def _delete_related(cls, file):
        file = cls.get_abspath_path(file)
        path, full_name, name, ext = cls.split_file(file)
        for root, dirs, files in os.walk(path):
            for f in files:
                if os.path.splitext(f)[0].startswith(name):
                    os.remove(path + '/' + f)

    @staticmethod
    def _make_dirs_by_date(root_path):
        """
        create subdirectory tree by current date
        @:param: parent folder
        """
        if not root_path:
            return None

        root_path = root_path.replace("\\", '/')
        root_path = root_path.rstrip("/")

        sub_directory_str = '/' + get_10().replace('-', '/')

        directory = root_path + sub_directory_str
        try:
            os.makedirs(directory, exist_ok=True)
            return directory
        except OSError as why:
            logger.error("failed create folder %s, %s" % (directory, why))
            return None

    @staticmethod
    def get_relative_path(abspath, sub_path=MEDIA_ROOT):
        return abspath.replace(sub_path, '', 1)

    @staticmethod
    def get_abspath_path(relative_path):
        if not os.path.isdir(relative_path) and not os.path.isfile(relative_path):
            return MEDIA_ROOT + relative_path
        else:
            return relative_path

    @staticmethod
    def split_file(file):
        path, full_name = os.path.split(file)
        name, ext = os.path.splitext(full_name)
        return path, full_name, name, ext

    @classmethod
    def is_image(cls, file):
        return file.split('.')[-1].lower() in ['jpg', 'gif', 'png']

    @classmethod
    def is_video(cls, file):
        return file.split('.')[-1].lower() == 'mp4'

    @staticmethod
    def is_valid_file(file, for_write=False):
        if not os.access(file, os.R_OK):
            return False
        if for_write:
            if os.access(file, os.W_OK):
                return True
            else:
                return False
        return True


class CosStorage(FileStorage):
    STORAGE_TYPE = STORAGE_TYPE_COS
    SPLITTER = '@'

    @staticmethod
    def get_relative_path(path):
        pass

    @staticmethod
    def get_abspath_path(path):
        pass

    @classmethod
    def _save_upload_file(cls, request, bucket, to_name, use_date_directory):
        file_data = request.FILES['file']
        if file_data is None:
            return None

        return cls._save(file_data, bucket, to_name, file_data.name, use_date_directory)

    @classmethod
    def _save(cls, file_data, bucket, to_name=None, org_name=None, use_date_directory=False):
        if isinstance(file_data, str):
            file_path = LocalFile.get_abspath_path(file_data)
        else:
            file_path = LocalFile.save(file_data, MEDIA_PATH_TEMP, to_name, org_name)
        path, full_name, name, ext = LocalFile.split_file(file_path)

        if cls.upload_cos(bucket, file_path):
            return '%s%s%s' % (full_name, cls.SPLITTER, bucket)
        else:
            return None

    @staticmethod
    def upload_cos(bucket, file, delete_after_success=False):
        file = LocalFile.get_abspath_path(file)
        uploaded = TencentClient.cos_upload_object(bucket, file)
        if uploaded and delete_after_success:
            LocalFile.delete(file)
        return uploaded

    @classmethod
    def _delete(cls, file):
        bucket, file_name = cls.split_path(file)
        return cls.cos_delete_file(bucket, file_name)

    @classmethod
    def _delete_related(cls, file):
        bucket, file_name = cls.split_path(file)
        prefix = file_name.split('.')[0]
        # get list
        file_list = TencentClient.cos_query_objects(bucket, prefix)
        return TencentClient.cos_delete_objects(bucket, file_list)

    @classmethod
    def upload_cos_related(cls, file, delete_after_success=False):
        file_path = LocalFile.get_abspath_path(file)
        path, full_name, name, ext = LocalFile.split_file(file_path)
        uploaded = False
        for root, dirs, files in os.walk(path):
            for f in files:
                arr = os.path.splitext(f)
                if arr[0].startswith(name):
                    if f == full_name and ext.lower() != '.mp4':
                        uploaded = TencentClient.cos_upload_object(MEDIA['COS_ORIGINAL_BUCKET'], path + '/' + f)
                    elif arr[1] == '.geojson':
                        uploaded = TencentClient.cos_upload_object(GEOJSON['COS_BUCKET'], path + '/' + f)
                    else:
                        uploaded = TencentClient.cos_upload_object(MEDIA['COS_BUCKET'], path + '/' + f)
                    if uploaded and delete_after_success:
                        LocalFile.delete(path + '/' + f)
        if uploaded:
            return '%s%s%s' % (full_name, cls.SPLITTER, MEDIA['COS_BUCKET'])
        else:
            return None

    @classmethod
    def cos_delete_file(cls, bucket, file):
        return TencentClient.cos_delete_objects(bucket, file)

    @classmethod
    def split_path(cls, file):
        """
        split file to bucket and filename
        :param file:
        :return:
        """
        arr = file.split('@')
        return arr[1], arr[0]
