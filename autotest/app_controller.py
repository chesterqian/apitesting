# coding: utf-8
from robot.api.deco import keyword
from autotest.ios_handle import IosHandler
from autotest.basic_controller import BasicController
from autotest.utility import Utility
from robot.api import logger
import time
from autotest.lib.util import take_screen_shot
from autotest.ios_handle import IosHandler

APP_ACCESS_ALLOW_BUTTON = "//*[@text='始终允许' or @text='allow' or @text='允许']"


class AppController(BasicController):
    util = Utility()
    started = False
    session_id = None

    def handle_security_prompt(self):
        while True:
            try:
                button = self.web_driver.find_element_by_xpath(APP_ACCESS_ALLOW_BUTTON)
                if button:
                    button.click()
            except Exception as e:
                break

    @keyword('Set Environemt Args')
    def android_set_environment_args(self, log_path, dict_para, popup_keywords, input_keywords):

        self.log_path = log_path
        self.app_path = dict_para.pop("app")
        self.platform_name = dict_para.pop("platformName")

        # 解决弹出框的问题
        adb = AdbHandler(dict_para["udid"], input_keywords["com.coloros.safecenter:id/et_login_passwd_edit"])
        # adb.restart_adb()
        installed = adb.is_package_installed(dict_para["appPackage"])
        # if not self.started:
        if installed:
            adb.uninstall_apk(dict_para["appPackage"])
        adb.install_apk_autoconfirm(self.app_path, popup_keywords, input_keywords)
        adb.close()

        self.web_driver = self.open_app(app_path=self.app_path, platform_name=self.platform_name,
                                        full_reset='false', **dict_para)
        self.web_driver.log_path = log_path
        self.session_id = self.web_driver.session_id
        time.sleep(5)
        self.handle_security_prompt()
        self.started = True
        return self.web_driver

    @keyword('Set Environemt Args')
    def ios_set_environment_args(self, log_path, dict_para):

        self.log_path = log_path
        self.app_path = dict_para.pop("app")
        self.platform_name = dict_para.pop("platformName")

        ios_handle = IosHandler(dict_para['udid'])
        time.sleep(5)
        ios_handle.install_ipa(self.app_path)

        self.web_driver = self.open_app(app_path=self.app_path, platform_name=self.platform_name,
                                        full_reset='false', **dict_para)

        self.web_driver.log_path = log_path

        self.session_id = self.web_driver.session_id
        self.handle_security_prompt()
        self.started = True
        return self.web_driver
