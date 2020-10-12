#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
易盾易盾反垃圾云服务音频离线结果获取接口python示例代码
接口文档: http://dun.163.com/api.html
python版本：python3.7
运行:
    1. 修改 SECRET_ID,SECRET_KEY,BUSINESS_ID 为对应申请到的值
    2. $ python audio_callback.py
"""
__author__ = 'yidun-dev'
__date__ = '2019/11/27'
__version__ = '0.2-dev'

import hashlib
import time
import random
import urllib.request as urlrequest
import urllib.parse as urlparse
import json
from gmssl import sm3, func


class AudioCallbackAPIDemo(object):
    """音频离线结果获取接口示例代码"""

    API_URL = "http://as.dun.163.com/v3/audio/callback/results"
    VERSION = "v3.2"  # 点播语音版本v3.2及以上二级细分类结构进行调整

    def __init__(self, secret_id, secret_key, business_id):
        """
        Args:
            secret_id (str) 产品密钥ID，产品标识
            secret_key (str) 产品私有密钥，服务端生成签名信息使用
            business_id (str) 业务ID，易盾根据产品业务特点分配
        """
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.business_id = business_id

    def gen_signature(self, params=None):
        """生成签名信息
        Args:
            params (object) 请求参数
        Returns:
            参数签名md5值
        """
        buff = ""
        for k in sorted(params.keys()):
            buff += str(k) + str(params[k])
        buff += self.secret_key
        if params["signatureMethod"] == "SM3":
            return sm3.sm3_hash(func.bytes_to_list(bytes(buff, encoding='utf8')))
        else:
            return hashlib.md5(buff.encode("utf8")).hexdigest()

    def check(self):
        """请求易盾接口
        Returns:
            请求结果，json格式
        """
        params = {}
        params["secretId"] = self.secret_id
        params["businessId"] = self.business_id
        params["version"] = self.VERSION
        params["timestamp"] = int(time.time() * 1000)
        params["nonce"] = int(random.random() * 100000000)
        # params["signatureMethod"] = "SM3"  # 签名方法，默认MD5，支持SM3
        params["signature"] = self.gen_signature(params)

        try:
            params = urlparse.urlencode(params).encode("utf8")
            request = urlrequest.Request(self.API_URL, params)
            content = urlrequest.urlopen(request, timeout=10).read()
            return json.loads(content)
        except Exception as ex:
            print("调用API接口失败:", str(ex))


if __name__ == "__main__":
    """示例代码入口"""
    SECRET_ID = "your_secret_id"  # 产品密钥ID，产品标识
    SECRET_KEY = "your_secret_key"  # 产品私有密钥，服务端生成签名信息使用，请严格保管，避免泄露
    BUSINESS_ID = "your_business_id"  # 业务ID，易盾根据产品业务特点分配
    api = AudioCallbackAPIDemo(SECRET_ID, SECRET_KEY, BUSINESS_ID)
    
    ret = api.check()

    code: int = ret["code"]
    msg: str = ret["msg"]
    if code == 200:
        resultArray: list = ret["antispam"]
        if resultArray is None or len(resultArray) == 0:
            print("暂时没有结果需要获取, 请稍后重试!")
        else:
            for result in resultArray:
                taskId: str = result["taskId"]
                asrStatus: int = result["asrStatus"]
                if asrStatus == 4:
                    asrResult: int = result["asrResult"]
                    print("检测失败: taskId=%s, asrResult=%s" % (taskId, asrResult))
                else:
                    action: int = result["action"]
                    labelArray: list = result["labels"]
                    if action == 0:
                        print("taskId=%s, 结果: 通过" % taskId)
                    elif action == 1 or action == 2:
                        for labelItem in labelArray:
                            label: int = labelItem["label"]
                            level: int = labelItem["level"]
                            # 注意二级细分类结构
                            subLabels: list = labelItem["subLabels"]
                            if subLabels is not None and len(subLabels) > 0:
                                for subLabelItem in subLabels:
                                    subLabel: str = subLabelItem["subLabel"]
                                    details: dict = subLabelItem["details"]
                                    hintArray: list = details["hint"]
                        print("taskId=%s, 结果: %s，证据信息如下: %s" % (taskId, "不确定" if action == 1 else "不通过", labelArray))
                    segments: list = result["segments"]
                    if segments is not None and len(segments) > 0:
                        for segment in segments:
                            startTime: int = segment["startTime"]
                            endTime: int = segment["endTime"]
                            content: str = segment["content"]
                            label: int = segment["label"]
                            level: int = segment["level"]
                            print("taskId=%s，开始时间：%s秒，结束时间：%s秒，内容：%s， label:%s, level:%s" %
                                  (taskId, startTime, endTime, content, label, level))

    else:
        print("ERROR: code=%s, msg=%s" % (ret["code"], ret["msg"]))
