from tencentcloud.common import credential
from entry.settings import ACCESS_KEYS


def get_tencent_cloud_credential():
    return credential.Credential(ACCESS_KEYS['TENCENT_CLOUD']['SECRET_ID'], ACCESS_KEYS['TENCENT_CLOUD']['SECRET_KEY'])
