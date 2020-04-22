import logging

from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.sms.v20190711 import sms_client, models

from .Base import BaseSmsBackend
from utils.data import format_mobile_no
from common.apis import get_tencent_cloud_credential

SMS_APP_ID = "1400306007"
SMS_APP_KEY = "f9c1dff071e58eb64d6e81faecae792f"
SIGNATURE = "骑行小帽"
TEMPLATES = {
    "REGISTER_VERIFY": "519961"
}

logger = logging.getLogger(__name__)


class TencentSmsBackend(BaseSmsBackend):

    def __init__(self):
        super().__init__()
        cred = get_tencent_cloud_credential()
        http_profile = HttpProfile()
        http_profile.endpoint = "sms.tencentcloudapi.com"
        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile
        self._client = sms_client.SmsClient(cred, "ap-guangzhou", client_profile)

    def send(self, content, target):
        mobile_no = format_mobile_no(target)
        template_id = TEMPLATES.get(target('template_id'))
        params = '{"PhoneNumberSet":["%s"],"TemplateID":"%s","Sign":"%s","TemplateParamSet":["%s"],"SmsSdkAppid":"%s"}'\
                 % (mobile_no, template_id, SIGNATURE, content, SMS_APP_ID)
        try:
            req = models.SendSmsRequest()
            req.from_json_string(params)
            resp = self._client.SendSms(req)
            result = resp.to_json_string()
            logger.info(result)
            return result

        except TencentCloudSDKException as err:
            logger.error(err)
