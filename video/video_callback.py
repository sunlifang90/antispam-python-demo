#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
易盾反垃圾云服务视频点播离线结果获取接口python示例代码
接口文档: http://dun.163.com/api.html
python版本：python3.7
运行:
    1. 修改 SECRET_ID,SECRET_KEY,BUSINESS_ID 为对应申请到的值
    2. $ python video_callback.py
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


class VideoCallbackAPIDemo(object):
    """视频点播离线结果获取接口示例代码"""

    API_URL = "http://as.dun.163.com/v3/video/callback/results"
    VERSION = "v3.1"

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
            params = urlparse.urlencode(params).encode()
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
    api = VideoCallbackAPIDemo(SECRET_ID, SECRET_KEY, BUSINESS_ID)
    
    ret = api.check()

    code: int = ret["code"]
    msg: str = ret["msg"]
    if code == 200:
        resultArray: list = ret["result"]
        if len(resultArray) == 0:
            print("暂无回调数据")
        else:
            for result in resultArray:
                status: int = result["status"]
                if status != 0:  # 异常，异常码定义见官网文档
                    print("视频异常, status: %s" % status)
                    continue
                taskId: str = result["taskId"]
                callback: str = result["callback"]
                videoLevel: str = result["level"]
                if videoLevel == 0:
                    print("视频正常, taskId: %s, callback: %s" % (taskId, callback))
                elif videoLevel == 1 or videoLevel == 2:
                    evidenceArray: list = result["evidences"]
                    for evidence in evidenceArray:
                        beginTime: int = evidence["beginTime"]
                        endTime: int = evidence["endTime"]
                        type: int = evidence["type"]
                        url: str = evidence["url"]
                        labelArray: list = evidence["labels"]
                        for labelItem in labelArray:
                            label: int = labelItem["label"]
                            level: int = labelItem["level"]
                            rate: float = labelItem["rate"]
                        print("taskId: %s, %s, callback: %s, 证据信息: %s, 证据分类: %s" %
                              (taskId, "不确定" if videoLevel == 1 else "确定", callback, evidence, labelArray))
    else:
        print("ERROR: code=%s, msg=%s" % (ret["code"], ret["msg"]))
