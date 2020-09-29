# -*- coding: utf-8 -*-
import os
import re
import subprocess
import threading
import time
from time import sleep
from uiautomator import Device

CMD_TEST = "adb install -r %s"
CMD_INPUT_KEY = "adb -s %s shell input keyevent %s"
CMD_GET_ACTIVITY = 'adb -s %s shell dumpsys activity activities %s  | findstr "Intent"'
CMD_LAUNCH_APP = "adb -s %s shell am start -n %s"
CMD_INSTALLED = "adb -s %s shell pm list packages | findstr %s"
EXIT_FLAG = False


class AdbHandler(object):
    def __init__(self, _device, _account):
        self.device = _device
        # 监控线程退出标记，业务（如安装）线程退出时置位
        self.dev_handler = None

    def close(self):
        self.dev_handler.server.stop()
        # self.restart_adb()
        # sleep(2)

    def install_apk(self, path_to_apk):
        global EXIT_FLAG
        p = subprocess.Popen("adb -s %s install -g %s" % (self.device, path_to_apk), stdout=subprocess.PIPE, shell=True)
        data = p.communicate()
        # p.terminate()
        s = str(data[0], encoding='utf-8')
        print('Installing apk: %s for device: %s,msg: %s' % (path_to_apk, self.device, s.replace("\r", ".")))
        EXIT_FLAG = True

    def is_package_installed(self, package):
        p = subprocess.Popen(CMD_INSTALLED % (self.device, package), stdout=subprocess.PIPE, shell=True)
        data = p.communicate()
        # p.terminate()
        s = str(data[0], encoding='utf-8')
        return package in s

    def uninstall_apk(self, package):
        p = subprocess.Popen("adb -s %s uninstall %s" % (self.device, package), stdout=subprocess.PIPE, shell=True)
        data = p.communicate()
        # p.terminate()
        s1 = str(data[0], encoding='utf-8')
        print('Uninstall apk: %s for device: %s, msg:%s.' % (package, self.device, s1.replace("\r", " ")))

    def back_to_home(self):
        subprocess.call(CMD_INPUT_KEY % (self.device, 'KEYCODE_HOME'), shell=True, stdout=subprocess.PIPE,
                        creationflags=subprocess.CREATE_NEW_CONSOLE)

    def restart_adb(self):
        try:
            subprocess.call("adb -s %s reconnect" % self.device)
            sleep(2)
        except Exception as e:
            print(e)

    def launch_app(self, package):
        # 获取切换前的活动的activity
        proc = subprocess.Popen(CMD_GET_ACTIVITY % (self.device, package), shell=True, stdout=subprocess.PIPE,
                                creationflags=subprocess.CREATE_NEW_CONSOLE)
        info = proc.communicate()[0]
        # proc.terminate()
        match_obj = re.match(r'.+?=(\S+/\S+).+', info, re.M | re.I)
        if match_obj:
            # 先切换到home
            self.back_to_home()
            activity = match_obj.group(1)
            # 再启动app
            subprocess.call(CMD_LAUNCH_APP % (self.device, activity), shell=True, stdout=subprocess.PIPE,
                            creationflags=subprocess.CREATE_NEW_CONSOLE)
            time.sleep(1)
        else:
            pass

    def auto_confirm(self, loop_count, click_keys, input_dict={}):
        """
        循环查找关键元素，并点击
        :param loop_count:
        :param device_name:
        :param click_keys:需要点击的元素关键字
        :param input_dict:key（需要查找的元素xpath） value（需要输入的内容）
        :return:
        """
        global EXIT_FLAG
        time.sleep(1)
        self.dev_handler = Device(self.device)
        for index in range(loop_count):
            bl_find = False
            for key in input_dict:
                element = self.dev_handler(resourceId=key, clickable=True)
                if element.exists:
                    bl_find = True
                    element.set_text(input_dict[key])

            for key in click_keys:
                # 优先完全匹配；若匹配不上，再匹配以关键字开头
                element = self.dev_handler(text=key, clickable=True)
                if element.exists:
                    bl_find = True
                    element.click()
                    break
                else:
                    element = self.dev_handler(textStartsWith=key, clickable=True)
                    if element.exists:
                        bl_find = True
                        element.click()
                        break

            # 都找不到，并且安装线程已退出，才退出；防止部分机型安装成功后还有一个确认窗口的问题
            if not bl_find and EXIT_FLAG:
                return

            time.sleep(1)

    def install_apk_autoconfirm(self, apk_path, click_keys, input_dict):
        """
         起线程安装app，自动确认弹出框
        :param device_name:
        :param apk_path:
        :param click_keys:可点击的元素关键字
        :param input_dict:需要输入的元素信息（元素xpath：需要输入的内容）
        :return:
        """
        threads = []
        install = threading.Thread(target=self.install_apk, args=(apk_path,))
        confirm = threading.Thread(target=self.auto_confirm, args=(80, click_keys, input_dict))
        threads.append(install)
        threads.append(confirm)
        for t in threads:
            t.start()

        install.join()
        confirm.join()


if __name__ == '__main__':
    # install_apk('/Users/linkinpark/jenkins_workspace/workspace/xjb_android_test/huaxin/ui_demo/apps/hxxjb-uat-latest.apk')
    device_id = 'A7Q0218301002953'
    package_name = "com.lianlian.finance"
    apk = 'D:\download\com.lianlian.finance_5.3.3_liqucn.com.apk'

    keys = ('继续安装', '我已充分了解', '安装', '完成')
    input = {}

    # 真机测试的代码
    adb = AdbHandler(device_id)
    adb.restart_adb()
    installed = adb.is_package_installed(package_name)
    if installed:
        adb.uninstall_apk(package_name)
    adb.install_apk_autoconfirm(apk, keys, input)
    adb.close()
