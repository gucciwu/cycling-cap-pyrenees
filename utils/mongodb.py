import json
import logging

from pymongo import MongoClient
from entry.settings import DATABASES
from utils.data import guid, JSONEncoder
from utils.date import get_25

logger = logging.getLogger(__name__)


class DB:
    PYRENEES_GUID_KEY = '_db_pyr_guid'

    def __init__(self, connect_str=None, db_settings_key=None):
        if connect_str is None:
            if db_settings_key is None:
                connect_str = self._get_connect_string(DATABASES['mongodb'])
                db_name = DATABASES['mongodb']['NAME']
            else:
                connect_str = self._get_connect_string(DATABASES[db_settings_key])
                db_name = DATABASES[db_settings_key]['NAME']
        else:
            db_name = connect_str.split('?')[0].split('/'[-1])

        self.client = MongoClient(connect_str)
        self.db = self.client[db_name]

    @staticmethod
    def _get_connect_string(host_config):
        user_name = host_config.get('USER', None)
        password = host_config.get('PASSWORD', None)
        if password and user_name:
            return 'mongodb://%s:%s@%s:%s/%s' % (user_name,
                                                 password,
                                                 host_config['HOST'],
                                                 host_config['PORT'],
                                                 host_config['NAME'],)
        else:
            return 'mongodb://%s:%s/%s' % (host_config['HOST'], host_config['PORT'], host_config['NAME'],)

    def insert(self, collection, data, by_user=None):
        if self.PYRENEES_GUID_KEY not in data:
            data.update({self.PYRENEES_GUID_KEY: guid()})
        self.touch(data, by_user)
        json_data = JSONEncoder().encode(data)
        self.db[collection].insert(json.loads(json_data))
        return data

    def insert_or_replace(self, collection, filter_data, data, by_user=None):
        """
        insert a new document if no document found with filter data,
        or delete the old one and insert a new one with original properties
        :param collection:
        :param filter_data:
        :param data:
        :param by_user:
        :return:
        """
        if filter_data is None:
            """
            for safety, just insert a new document when filter not provide
            """
            result = None
        else:
            if isinstance(filter_data, str):
                filter_data = {self.PYRENEES_GUID_KEY: filter_data}
            result = self.find_one(collection, filter_data)
        if result is not None:
            self.delete(collection, {self.PYRENEES_GUID_KEY: result[self.PYRENEES_GUID_KEY]})
            data.update({
                '_db_created_time': result['_db_created_time'],
                '_db_created_by': result['_db_created_by'],
                '_db_updated_time': get_25(),
                '_db_updated_by': by_user.username if by_user else None,
                '_db_deleted': result['_db_deleted'],
                '_db_owner': result['_db_owner'],
                self.PYRENEES_GUID_KEY: result[self.PYRENEES_GUID_KEY],
            })
            self.insert(collection, data, by_user)
            result = data
        else:
            result = self.insert(collection, data, by_user)
        return result

    def find_one(self, collection, filter_data=None):
        if filter_data is None:
            filter_data = {}
        if isinstance(filter_data, str):
            filter_data = {self.PYRENEES_GUID_KEY: filter_data}
        ret = self.db[collection].find_one(filter_data)
        tmp = JSONEncoder().encode(ret)
        return json.loads(tmp)

    def query(self, collection, filter_data=None, sort_data=None, limit=None):
        if filter_data is None:
            filter_data = {}
        if isinstance(filter_data, str):
            filter_data = {self.PYRENEES_GUID_KEY: filter_data}
        if sort_data is None:
            sort_data = [('_db_modified_time', -1)]
        if limit is None:
            limit = 0
        records = self.db[collection].find(filter_data).sort(sort_data).limit(limit)
        result = []
        for record in records:
            tmp = JSONEncoder().encode(record)
            result.append(json.dumps(tmp))
        return result

    def soft_delete(self, collection, filter_data):
        if isinstance(filter_data, str):
            filter_data = {self.PYRENEES_GUID_KEY: filter_data}
        self.db[collection].update(filter_data, {'_db_deleted', True})

    def delete(self, collection, filter_data):
        if isinstance(filter_data, str):
            filter_data = {self.PYRENEES_GUID_KEY: filter_data}
        self.db[collection].remove(filter_data)

    @staticmethod
    def touch(data, by_user=None):
        if '_db_created_time' not in data:
            data.update({'_db_created_time': get_25()})
        elif data['_db_created_time'] is None:
            data['_db_created_time'] = get_25()

        if '_db_created_by' not in data:
            data.update({'_db_created_by': by_user.username if by_user else None})
        elif data['_db_created_by'] is None:
            data['_db_created_by'] = by_user.username if by_user else None

        if '_db_updated_time' not in data:
            data.update({'_db_updated_time': get_25()})
        else:
            data['_db_updated_time'] = get_25()

        if '_db_updated_by' not in data:
            data.update({'_db_updated_by': by_user.username if by_user else None})
        else:
            data['_db_updated_by'] = by_user.username if by_user else None

        if '_db_deleted' not in data:
            data.update({'_db_deleted': False})

        if '_db_owner' not in data:
            data.update({'_db_owner': by_user.username if by_user else None})

        if '_db_created_time' not in data:
            data.update({'_db_created_time': get_25()})

    class Collections:
        MEDIA_PARSED_DATA = 'media_parsed'
        MEDIA_ANALYSIS_DATA = 'media_analysis'
        TIMELINE_NODE_DATA = 'timeline_nodes'


mongodb = DB()
