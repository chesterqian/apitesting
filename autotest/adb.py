# -*- coding: utf-8 -*-
import os
import re
import subprocess
import threading
import time
from time import sleep

from uiautomator import Device
import psutil

# import pwd

MONKEY_SHELL_FOR_XJB = "adb shell monkey -p com.shhxzq.xjb -v 50000 --monitor-native-crashes --throttle 2000 --pct-nav 20 --pct-majornav 25 > $HOME/jenkins_workspace/workspace/%s/monkey_test_result.txt"
MONKEY_SHELL_FOR_ZTB = "adb shell monkey -p com.shhxzq.ztb -v 50000 --monitor-native-crashes --throttle 2000 --pct-nav 20 --pct-majornav 25 > $HOME/jenkins_workspace/workspace/%s/monkey_test_result.txt"
CMD_TEST = "adb install -r %s"
CMD_INPUT_KEY = "adb -s %s shell input keyevent %s"
CMD_GET_ACTIVITY = 'adb -s %s shell dumpsys activity activities %s  | findstr "Intent"'
CMD_LAUNCH_APP = "adb -s %s shell am start -n %s"
CMD_INSTALLED = "adb -s %s shell pm list packages | findstr %s"
BUSINESS_TYPE_MAP_CMD = {'0': MONKEY_SHELL_FOR_XJB,
                         '1': MONKEY_SHELL_FOR_ZTB
                         }


class Adb(object):
    device = None
    dev_handle = None
    # 监控线程退出标记，业务（如安装）线程退出时置位
    exit_flag = False

    def __init__(self, _device):
        self.device = _device
        self.dev_handle = Device(self.device)

    def close(self):
        self.dev_handle.server.stop()
        self.restart_adb()
        sleep(2)

    def execute_monkey_test(business_type, log_output):
        # log_output:jenkins job name
        cmd = BUSINESS_TYPE_MAP_CMD[str(business_type)] % log_output
        subprocess.call(cmd, shell=True, executable='/bin/zsh', creationflags=subprocess.CREATE_NEW_CONSOLE)

        current_user_dir = pwd.getpwuid(os.geteuid()).pw_dir
        log_file_path = re.sub(r'>\s\$HOME', current_user_dir, (re.search(r'>.*', cmd).group()))

        return log_file_path

    def install_apk(self, path_to_apk):
        p = subprocess.Popen("adb -s %s install %s" % (self.device, path_to_apk), stdout=subprocess.PIPE, shell=True)
        data = p.stdout.read()
        s = str(data, encoding='utf-8')
        print('Installing apk: %s for device: %s,msg: %s' % (path_to_apk, self.device, s.replace("\r\n", ".")))

    def is_package_installed(self, package):
        p = subprocess.Popen(CMD_INSTALLED % (self.device, package), stdout=subprocess.PIPE, shell=True)
        data = p.stdout.read()
        s = str(data, encoding='utf-8')
        if package in s:
            return True
        else:
            return False

    def uninstall_apk(self, package):
        p = subprocess.Popen("adb -s %s uninstall %s" % (self.device, package), stdout=subprocess.PIPE, shell=True)
        data = p.stdout.read()
        s1 = str(data, encoding='utf-8')
        print('Uninstall apk: %s for device: %s, msg:%s.' % (package, self.device, s1.replace("\r\n", ".")))

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
        proc = psutil.Popen(CMD_GET_ACTIVITY % (self.device, package), shell=True, stdout=subprocess.PIPE,
                            creationflags=subprocess.CREATE_NEW_CONSOLE)
        info = proc.communicate()[0]
        proc.terminate()
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

    def auto_confirm(self, loop_count, element_keys):
        """
        循环查找关键元素，并点击
        :param loop_count:
        :param device_name:
        :param element_keys:元素关键字
        :return:
        """
        for i in range(loop_count):
            for key in element_keys:
                # 优先完全匹配；若匹配不上，再匹配已关键字开头
                element = self.dev_handle(text=key)
                if element.exists:
                    element.click()
                    break
                else:
                    element = self.dev_handle(textStartsWith=key)
                    if element.exists:
                        element.click()
                        break

                if self.exit_flag:
                    return

            sleep(1)

    def install_apk_autoconfirm(self, apk_path, element_keys):
        """
         起线程安装app，自动确认弹出框
        :param device_name:
        :param apk_path:
        :param element_keys:
        :return:
        """
        threads = []
        install = threading.Thread(target=self.install_apk, args=(apk_path,))
        confirm = threading.Thread(target=self.auto_confirm, args=(40, element_keys))
        threads.append(confirm)
        threads.append(install)
        for t in threads:
            # t.setDaemon(True)
            t.start()

        install.join()
        self.exit_flag = True
        confirm.join()


if __name__ == '__main__':
    # install_apk('/Users/linkinpark/jenkins_workspace/workspace/xjb_android_test/huaxin/ui_demo/apps/hxxjb-uat-latest.apk')
    device_id = 'A7Q0218301002953'
    package_name = "com.lianlian.finance"
    apk = 'D:\download\com.lianlian.finance_5.3.3_liqucn.com.apk'

    keys = (u'继续安装', u'我已充分了解', u'安装')

    # 真机测试的代码
    adb = Adb(device_id)
    adb.restart_adb()
    installed = adb.is_package_installed(package_name)
    if installed:
        adb.uninstall_apk(package_name)
    adb.install_apk_autoconfirm(apk, keys)
    adb.close()
