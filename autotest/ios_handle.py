# -*- coding: utf-8 -*-
import os
import re
import subprocess
import threading
import time
from time import sleep
from uiautomator import Device

# 全局变量
EXIT_FLAG = False


class IosHandler(object):
    def __init__(self, _device):
        self.device_udid = _device
        # 监控线程退出标记，业务（如安装）线程退出时置位
        self.dev_handler = None

    def install_ipa(self, path_to_ipa):
        # 声明全局变量，如果在局部要对全局变量修改，需要在局部也要先声明该全局变量：
        global EXIT_FLAG
        p = subprocess.Popen("ideviceinstaller -o %s -i %s " % (self.device_udid, path_to_ipa), stdout=subprocess.PIPE,
                             shell=True)
        data = p.communicate()
        # p.terminate()
        s = str(data[0], encoding='utf-8')
        print('Installing ipa: %s for device: %s,msg: %s' % (path_to_ipa, self.device_udid, s.replace("\r", ".")))
        EXIT_FLAG = True

    # subprocess启动一个新的进程，通过shell来执行，如果希望从stdout和stderr获取数据，必须将stdout和stderr设置为PIPE
    def uninstall_ipa(self, appBundle_id):
        p = subprocess.Popen("ideviceinstaller -o %s -U %s" % (self.device_udid, appBundle_id), stdout=subprocess.PIPE,
                             shell=True)
        data = p.communicate()
        # p.terminate()
        s1 = str(data[0], encoding='utf-8')
        print('Uninstall ipa: %s for device: %s, msg:%s.' % (appBundle_id, self.device_udid, s1.replace("\r", " ")))


if __name__ == '__main__':
    device_id = 'c6a7f1d7b57b522518b04e2d01acfc493268ed17'
    appBundle_id = "com.homelink.p2p"
    ipa = '/homelink_p2p7.0.0.ipa'

    # 真机测试的代码
    ios_handle = IosHandler(device_id)
    time.sleep(5)
    # ios_handle.uninstall_ipa(appBundle_id)
    ios_handle.install_ipa(ipa)
