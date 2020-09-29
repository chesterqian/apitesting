# coding: utf-8
'''
Created on Feb 21, 2013

@author: Chester.Qian
'''

import time

from appium import webdriver as app_driver
from selenium.webdriver.chrome.webdriver import WebDriver as C_WebDriver
from selenium.webdriver.firefox.webdriver import WebDriver as F_WebDriver
from selenium.webdriver.ie.webdriver import WebDriver as I_WebDriver
from selenium.webdriver.phantomjs.webdriver import WebDriver as P_WebDriver
from selenium.webdriver.common.keys import Keys
from autotest.global_config import Global
from autotest.utility import Utility
from selenium.webdriver.chrome.options import Options
from selenium import webdriver



class MyChromeWebDriver(C_WebDriver):
    set_time_out_for_element = 0

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument("disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        super(MyChromeWebDriver, self).__init__(options=chrome_options)


    def get(self, *args):
        super(C_WebDriver, self).get(*args)

    def find_element_by_xpath(self, *args):
        return super(C_WebDriver, self).find_element_by_xpath(*args)

    def find_elements_by_tag_name(self, *args):
        return super(C_WebDriver, self).find_elements_by_tag_name(*args)


class MyFireFoxWebDriver(F_WebDriver):
    set_time_out_for_element = 0

    def get(self, *args):
        super(F_WebDriver, self).get(*args)
        print("sleeping after get (firefox)")
        time.sleep(5)

    def find_element_by_xpath(self, *args):
        if not self.set_time_out_for_element:
            self.set_time_out_for_element += 1
            self.implicitly_wait(10)
        return super(F_WebDriver, self).find_element_by_xpath(*args)

    def find_elements_by_tag_name(self, *args):
        self.implicitly_wait(1)
        return super(F_WebDriver, self).find_elements_by_tag_name(*args)


class IEElementWrapper:
    """
    包装IE WebElement,重写click方法，解决部分IE版本click不生效问题
    """

    def __init__(self, driver, xpath, element):
        self.driver = driver
        self.xpath = xpath
        self.wrapper = element

    def click(self):
        if self.wrapper:
            self.wrapper.send_keys(Keys.ENTER)
            js = "var result = document.evaluate(\"%s\", document.documentElement, null, \
            XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;\
            if(result!=null) {result.focus();result.click();}" % self.xpath
            self.driver.execute_script(js)

    def __getattr__(self, item):
        return getattr(self.wrapper, item)


class MyIEWebDriver(I_WebDriver):
    set_time_out_for_element = 0

    def get(self, *args):
        super(I_WebDriver, self).get(*args)

    def find_element_by_xpath(self, *args):
        element = super(I_WebDriver, self).find_element_by_xpath(*args)
        return IEElementWrapper(self, args[0], element)

    def find_elements_by_tag_name(self, *args):
        return super(I_WebDriver, self).find_elements_by_tag_name(*args)


class MyPhantomjsDriver(P_WebDriver):
    set_time_out_for_element = 0

    def get(self, *args):
        super(P_WebDriver, self).get(*args)

    def find_element_by_xpath(self, *args):
        return super(P_WebDriver, self).find_element_by_xpath(*args)

    def find_elements_by_tag_name(self, *args):
        return super(P_WebDriver, self).find_elements_by_tag_name(*args)


class AndroidDriverWrapper:
    def __init__(self, driver):
        self.wrapper = driver

    def find_element_by_xpath(self, *args):
        element = self.wrapper.find_element_by_xpath(*args)
        return AndroidElementWrapper(element)

    def __getattr__(self, item):
        return getattr(self.wrapper, item)


class AndroidElementWrapper:
    def __init__(self, element):
        self.wrapper = element

    # tag_name部分版本不支持，统一成classname
    @property
    def tag_name(self):
        return self.wrapper.get_attribute("className")

    def __getattr__(self, item):
        return getattr(self.wrapper, item)


class BasicController:
    page_assertion_obj = None
    _main_window_handle = None
    _current_window_handle = None

    def __init__(self):
        self.web_driver = None
        self.current_page_obj = None
        self.desired_caps = dict()

    def open_web_driver(self, browser, url, user_name, password, log_path):
        browser_dict = {'chrome': MyChromeWebDriver,
                        'firefox': MyFireFoxWebDriver,
                        'ie': MyIEWebDriver,
                        'phantomjs': MyPhantomjsDriver}
        self.web_driver = browser_dict[browser]()
        self.web_driver.user_name = user_name
        self.web_driver.password = password
        self.web_driver.log_path = log_path
        self.web_driver.get(url)
        self.web_driver.maximize_window()
        self._main_window_handle = self.web_driver.current_window_handle
        self._current_window_handle = self.web_driver.current_window_handle
        return self.web_driver


    def open_android_app(self, app_path, full_reset=False, **kwargs):
        util = Utility()
        self.desired_caps = dict()
        self.desired_caps['fullReset'] = full_reset
        self.desired_caps['automationName'] = "UIAutomator2"
        self.desired_caps['autoGrantPermissions'] = True
        self.desired_caps["noReset"] = "True"
        self.desired_caps['newCommandTimeout'] = 0
        self.desired_caps['noReset'] = True
        self.desired_caps['noSign'] = True
        self.desired_caps['autoAcceptAlerts'] = True
        self.desired_caps.update(kwargs)
        self.desired_caps['app'] = app_path
        self.desired_caps['platformName'] = 'android'
        self.web_driver = app_driver.Remote(kwargs["appium_url"], self.desired_caps)
        return AndroidDriverWrapper(self.web_driver)

    def open_ios_app(self, app_path, full_reset='false', **kwargs):
        util = Utility()
        self.desired_caps = dict()
        self.desired_caps = kwargs
        self.desired_caps['platformName'] = 'ios'
        # 在已安装软件的情况下，这两句话先注释掉
        # self.desired_caps['app'] = app_path
        # self.desired_caps['bundleId'] = bundle_id

        if not kwargs["bundleId"]:
            self.desired_caps['app'] = util.intersection_of_path(app_path)
        else:
            self.desired_caps['bundleId'] = kwargs["bundleId"]

        self.web_driver = app_driver.Remote(kwargs["appium_url"], self.desired_caps)
        return self.web_driver

    def open_app(self, app_path, platform_name, *args, **kwargs):
        name_map_func = {'android': self.open_android_app,
                         'ios': self.open_ios_app
                         }
        func = name_map_func[platform_name]
        return func(app_path, *args, **kwargs)

    def switch_window_by_title(self, title):
        '''
        This method is on purpose of handle one driver with multiple windows/tabs.
        The switching identifier is @title text. If fail to switch by title, web 
        driver would stay on the focus page.
        '''
        for handle in self.web_driver.window_handles:
            self.web_driver.switch_to_window(handle)
            if str(self.web_driver.title) == title:
                self._current_window_handle = self.web_driver.current_window_handle
                break
            else:
                self._current_window_handle = None

        if not self._current_window_handle:
            self.web_driver.switch_to_default_content()
            self._current_window_handle = self.web_driver.current_window_handle

    def switch_to_main_window(self):
        self.web_driver.switch_to_window(self._main_window_handle)
        self._current_window_handle = self._main_window_handle

    def go_back(self):
        self.web_driver.back()

    def close_web_driver(self):
        '''
        Release the opened web driver, in the meanwhile, the browser would be closed.
        '''
        self.web_driver.quit()

    def close_window(self):
        '''
        Close the current window of browser which is controlled by current web driver.
        '''
        self.web_driver.close()

    def status_should_be(self, expected_msg):
        status_msg = self.current_page_obj.status_msg
        actual_msg = status_msg.msg
        details = status_msg.details
        if not actual_msg == expected_msg:
            raise AssertionError("expected_msg to be '%s' but was '%s(details is%s)'"
                                 % (expected_msg, actual_msg, details))

    def wait_for_element_to_be_displayed(self, xpath, timeout=Global.PageTimeout.CHECK_STATUS):
        return self.current_page_obj.wait_for_element_attribute_as_specific_value(xpath, \
                                                                                  timeout=timeout)

    def wait_for_element_as_specific_attribute_value(self, xpath, \
                                                     attr_name, attr_value, timeout=Global.PageTimeout.CHECK_STATUS):
        return self.current_page_obj.wait_for_element_attribute_as_specific_value(xpath, \
                                                                                  attribute_name=attr_name,
                                                                                  attribute_value=attr_value,
                                                                                  timeout=timeout)
