# -*- coding:utf-8 -*-
import re
import time
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import InvalidElementStateException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from autotest.exception import PageExceptionType
from autotest.global_config import Global
from autotest.lib.selenium_page import SeleniumPage
from robot.api import logger
from autotest.lib.util import take_screen_shot

TIMEOUT_FOR_GET_ELEMENT = Global.PageTimeout.ELEMENT_FINDING


class TagMapOperation(object):
    # define operations on web elements depends on the type of html tag
    tag_map_function = {
        'a': 'handle_click_operation',
        'select': 'handle_select_operation',
        'input': 'handle_input_operation',
        'textarea': 'handle_textarea_operation',
        'div': 'handle_click_operation',
        'span': 'handle_click_operation',
        'li': 'handle_click_operation',
        'drag': 'handle_drag_drop_operation',
        'button': 'handle_click_operation',
        'img': 'handle_click_operation',
        'ul': 'handle_click_operation',
        'label': 'handle_input_operation',
        'click': 'handle_click_operation',
        'swipestart': 'handle_swipe_operation_new',
        'android.widget.ImageButton': 'handle_click_operation',
        'android.widget.EditText': 'handle_input_operation',
        'android.widget.Button': 'handle_click_operation',
        'android.widget.TextView': 'handle_click_operation',
        'android.widget.RadioButton': 'handle_click_operation',
        'android.widget.ImageView': 'handle_click_operation',
        'android.view.View': 'handle_click_operation',
        'android.widget.RelativeLayout': 'handle_click_operation',
        'XCUIElementTypeTextField': 'handle_input_operation',
        'XCUIElementTypeButton': 'handle_click_operation',
        'XCUIElementTypeSecureTextField': 'handle_input_operation',
        'XCUIElementTypeCell': 'handle_click_operation',
        'XCUIElementTypeStaticText': 'handle_click_operation',
        'XCUIElementTypeOther': 'handle_click_operation',
        'UIAButton': 'handle_click_operation',
        'UIATextField': 'handle_input_operation',
        'UIASecureTextField': 'handle_input_operation',
        'UIATableCell': 'handle_click_operation'
    }


class _PageElementControl(object):
    _exceptions = (WebDriverException, ElementNotVisibleException,
                   StaleElementReferenceException, InvalidElementStateException)

    def __init__(self, page_object, page_function_name, *args, **kwargs):
        self._page_object = page_object
        self._page_function_name = page_function_name
        self._function_args, self._function_kwargs = (args, kwargs)
        self._page_element = getattr(self._page_object, self._page_function_name)(
            *self._function_args, **self._function_kwargs)
        self._page_element_value = None
        self._error_message = 'The current element is in a unreachable state to be operated on!'
        self._retry_stale = 0

    def __getattr__(self, attribute):

        def get_element_state():
            if self._retry_stale > Global.RetryTimes.MAX:
                raise Exception(self._error_message)

            exception_occurred = False
            time.sleep(Global.PageOperationInterval.MIN)

            try:
                self._page_element_value = getattr(self._page_element, attribute)
                try:
                    if callable(self._page_element_value):
                        if None not in (attribute_args, attribute_kwargs):
                            self._page_element_value = \
                                self._page_element_value(
                                    *attribute_args, **attribute_kwargs)
                except NameError:
                    pass
                return exception_occurred
            except self._exceptions as  e:
                exception_occurred = True
                self._error_message = e
                self._retry_stale += 1
                print('retry # %s' % self._retry_stale)
                return exception_occurred

        def get_element_attribute_value():
            self._retry_stale = 0

            while get_element_state():
                self._page_element = getattr(self._page_object, self._page_function_name)(
                    *self._function_args, **self._function_kwargs)

            return self._page_element_value

        value = get_element_attribute_value()

        if callable(value):
            def wrapper(*args, **kwargs):
                global attribute_args, attribute_kwargs
                attribute_args, attribute_kwargs = args, kwargs
                exception_occurred = True

                while exception_occurred:
                    try:
                        value = get_element_attribute_value()
                    except self._exceptions:
                        continue
                    finally:
                        attribute_args, attribute_kwargs = (None, None)
                    exception_occurred = False
                return value

            return wrapper
        else:
            return value

    def __getitem__(self, idx):
        if isinstance(self._page_element, list):
            return self._page_element[idx]
        else:
            raise TypeError('not support slicing this way!')


class PageObject(object):
    """
    All page object should inherit from.

    It encapsulates and extends basic web driver operations.
    """

    web_driver = None
    _is_assumed_fully_loaded = False
    _page_identifier = None
    _current_url = None
    _is_app = None
    previous_element_xpath = None
    previous_arguments_for_xpath = None
    current_element = None
    current_xpath_on_error = None
    fetch_from_element = False
    fetch_from_element_value = []
    is_current_element_not_displayed = False
    may_contain_scroll_bar = False
    sleep_seconds = 0
    retry = 0
    ignore_time_sleep = False
    page_exception_class = None
    page_exception = None
    destination_url = None

    REG_ACTION_PARAMETER_PATTERN = r"(drop-|swipestop-)"
    REG_OPERATOR_MATCH_PATTERN = r"(drag|hover|input|click|swipestart)-"
    REG_LOCATION_LAZY_INITIAL_PATTERN = r"lazy_inital-"
    REG_MULTI_LOCATION_QUREY_INDEX_PATTERN = r"\[\d+\]$"

    SPECIAL_OPERATOR_MATCH_PATTERN = ('drag', 'swipestart')

    def __init__(self, web_driver):
        self.web_driver = web_driver
        self.utils = SeleniumPage(self.web_driver, WebDriverWait)

    def __getattr__(self, attribute):
        if hasattr(self.web_driver, attribute):
            return getattr(self.web_driver, attribute)
        else:
            raise TypeError("no attribute named '%s' for %s !" %
                            (attribute, self.__class__.__name__))

    @property
    def page_identifier(self):
        return self._page_identifier

    @property
    def current_url(self):
        self._current_url = self.web_driver.current_url
        return self._current_url

    @property
    def is_assumed_fully_loaded(self):
        try:
            self.get_page_loading_status()
        except Exception:
            pass
        finally:
            return self._is_assumed_fully_loaded

    @is_assumed_fully_loaded.setter
    def is_assumed_fully_loaded(self, value):
        self._is_assumed_fully_loaded = value

    @property
    def is_app(self):
        if not self._is_app:
            _is_app = [i for i in ('udid', 'deviceUDID')
                       if i in self.desired_capabilities]
            r = _is_app and True or False
            self._is_app = r

        return self._is_app

    def get_tag_name(self, html_tag, operator_tag):
        return operator_tag or html_tag

    def _build_parameters(self, perform_args=None,
                          current_perform_args_idx=None, pre_location=None):
        location = None
        offset_index = False
        operator_tag = None
        action_parameter_tag = None
        query_func_name = None
        strategy_map_func_name = {
            '//': 'find_element_by_xpath',
            'accId_': 'find_element_by_accessibility_id',
            'accIds_': 'find_elements_by_accessibility_id',
            'predicate_': 'find_element_by_ios_predicate'
        }

        parameters = (location, query_func_name,
                      operator_tag, action_parameter_tag,
                      offset_index, pre_location)

        def _build(_location=None, _query_func_name=None,
                   _operator_tag=None, _action_parameter_tag=None,
                   _offset_index=False, pre_location=None):
            location_strategy = None
            build_from = None
            arguments_for_location = None
            next_item_action_parameter_tag = None
            lazy_initial_tag = None
            multi_location_index = None

            if pre_location:
                _location = pre_location
            elif perform_args and current_perform_args_idx is not None:
                build_from = 'perform_actions'

                next_item_idx = current_perform_args_idx + 1
                _location = perform_args[current_perform_args_idx]

            reg_xpath_pattern = r"^//"
            reg_accid_pattern = r"^(accIds_|accId_)"
            reg_predicate_pattern = r"^predicate_"

            current_location_pattern = None
            current_location_pattern_match = None

            for p in (reg_xpath_pattern, reg_accid_pattern, reg_predicate_pattern):
                current_location_pattern_match = re.search(p, _location)

                if current_location_pattern_match:
                    current_location_pattern = p

                    break

            if current_location_pattern_match:
                location_strategy = current_location_pattern_match.group()

                try:
                    # get multi elemtent index
                    query_index_match = re.search(self.REG_MULTI_LOCATION_QUREY_INDEX_PATTERN, _location)
                    if query_index_match:
                        _tmp_idx = query_index_match.group()
                        multi_location_index = int(re.search(r"\d+", _tmp_idx).group())

                        _location = re.sub(self.REG_MULTI_LOCATION_QUREY_INDEX_PATTERN, '', _location)
                except AttributeError:
                    pass

            if not location_strategy:
                return

            # remove tag from real location
            # retrive strategy_tag, operator_tag
            matches = [current_location_pattern_match,
                       re.search(self.REG_OPERATOR_MATCH_PATTERN, _location),
                       re.search(self.REG_ACTION_PARAMETER_PATTERN, _location),
                       re.search(self.REG_LOCATION_LAZY_INITIAL_PATTERN, _location)]

            tags = []

            for match in matches:
                tag = None

                if match:
                    if current_location_pattern != reg_xpath_pattern:
                        _location = re.sub(match.group(), '', _location)

                    tag = match.group().split('-')[0]

                tags.append(tag)

            if tags:
                strategy_tag, _operator_tag, \
                _action_parameter_tag, lazy_initial_tag = tags

                _query_func_name = strategy_map_func_name[location_strategy]

            if build_from == 'perform_actions':
                # decide if location string contains '%s' and build complete location
                if re.search(r"%s", _location):
                    _location = _location % perform_args[next_item_idx]
                    _offset_index = True

                try:
                    next_item = perform_args[next_item_idx]
                    next_item_parameters = _build(pre_location=next_item)

                    if next_item_parameters:
                        next_item_action_parameter_tag = next_item_parameters[3]

                        if next_item_action_parameter_tag:
                            arguments_for_location = next_item_parameters
                        else:
                            arguments_for_location = ()

                    else:
                        arguments_for_location = (next_item,)

                except IndexError:
                    arguments_for_location = ()

            if _operator_tag in self.SPECIAL_OPERATOR_MATCH_PATTERN \
                    and not next_item_action_parameter_tag:
                raise Exception('need location for action parameter!')

            _parameters = (_location, _query_func_name,
                           _operator_tag, _action_parameter_tag,
                           lazy_initial_tag, _offset_index,
                           arguments_for_location, multi_location_index)

            return _parameters

        parameters = _build(*parameters)

        return parameters

    def get_page_loading_status(self):
        raise Exception("Should be implemented")

    def set_sleep_seconds(self, seconds):
        self.sleep_seconds = seconds

    def reset_sleep_seconds(self):
        self.sleep_seconds = 0

    def switch_iframe_by_reference(self, iframe_reference):
        """
        reference can be index or name
        """
        self.web_driver.switch_to_frame(iframe_reference)

    def get_element_new(self, location, query_func_name=None,
                        timeout=TIMEOUT_FOR_GET_ELEMENT):
        # both get element and get elements are supported using ios accId strategy
        # for get element, the location should start with 'accId'
        # for get elements, the location should start with 'accIds'
        if not query_func_name:
            parameters = self._build_parameters(pre_location=location)
            location, query_func_name = parameters[0:2]

        find_element_expression = lambda x: getattr(x, query_func_name)(location)

        try:
            log_info = "finding element %s within %s seconds..." % (location, timeout)
            logger.info(log_info, False, True)
            element = WebDriverWait(self.web_driver, timeout).until(find_element_expression)
        except TimeoutException:
            error_message = "element not found, location is '%s for %s page'" \
                            % (location, self.__class__.__name__)

            if self.page_exception_class:
                if self.page_exception_class.exception_type == \
                        PageExceptionType.ELEMENT_NOT_EXIST:
                    if not self.page_exception:
                        self.page_exception = \
                            self.page_exception_class(self)
                    else:
                        self.page_exception.add_error_message(error_message)

                    raise self.page_exception

            raise TimeoutException(error_message)

        return element

    def get_elements(self, xpath, match=None, timeout=TIMEOUT_FOR_GET_ELEMENT):
        if match:
            xpath = re.sub(match.group(), '', xpath)

        find_elements_expression = lambda x: x.find_elements_by_xpath(xpath)

        log_info = "finding element %s within %s seconds..." % (xpath, timeout)
        logger.info(log_info, False, True)
        elements = WebDriverWait(self.web_driver, timeout).until(find_elements_expression)
        return elements

    # To check whether the provided xpath is an existing element on the page
    def element_exists_new(self, pre_location, timeout=TIMEOUT_FOR_GET_ELEMENT):
        parameters = self._build_parameters(pre_location=pre_location)
        location, query_func_name = parameters[0:2]

        try:
            self.get_element_new(location, query_func_name, timeout)
        except Exception:
            return False

        return True

    def get_element_attribute_value_by_name(self, xpath, attribute_name):
        element = self.get_element(xpath)
        value = element.get_attribute(attribute_name)

        return value

    def is_enabled_element(self, xpath):
        element = self.get_element(xpath)
        is_readonly = ('readonly' == element.get_attribute('readonly'))
        is_enabled = element.is_enabled()

        return not is_readonly or is_enabled

    def get_element_text(self, xpath):
        element = self.get_element_new(xpath)
        text = element.text
        if text == "":
            "This branch is handling to get inner text of invisible elements"
            return self.web_driver.execute_script("""
                return jQuery(arguments[0]).contents().filter(function() {
                    return this.nodeType == Node.TEXT_NODE;
                }).text();
            """, element)
        else:
            return text

    def go_to_by_url(self, link_xpath):
        link = self.web_driver.find_element_by_xpath(link_xpath)
        link_url = link.get_attribute("href")
        self.web_driver.get(link_url)

        return self.function_pass

    def go_to_by_link(self):
        self.current_exception_type = '1'
        self.current_element.click()
        return self.function_pass

    def check_destination_page(self, page):
        identifier = page.page_identifier
        if not identifier:
            raise Exception("no page identifier found!")

        retry = 0

        while not self.element_exists_new(identifier,
                                          Global.PageTimeout.QUICK_IGNORE):
            retry += 1
            print("Retry time #%s for checking existence of element %s" \
                  % (retry, identifier))
            if retry > Global.RetryTimes.MIN:
                if self.page_exception_class:
                    if self.page_exception_class.exception_type == \
                            PageExceptionType.PAGE_NAVIGATION_ERROR:
                        self.page_exception = \
                            self.page_exception_class(self, page)
                        raise self.page_exception
                raise Exception('check destination page %s error!' % page)

    # @xpath is a XPATH formatted string
    # @kwargs keys of it include timeout, attribute_name, attribute_value
    # @timeout is to set maximum wait time as default
    # @attribute_name, @attribute_value will ignore checking if no key there
    def wait_for_element_attribute_as_specific_value(self, xpath, **kwargs):
        """
        This method can be used for checking page identifier before execute checkpoints
        or perform actions.
        """

        def check_display():
            is_element_displayed = element.is_displayed()
            if attribute_name is False:
                return is_element_displayed
            else:
                return is_element_displayed and \
                       element.get_attribute(attribute_name).find(attribute_value) >= 0

        element = self.get_element(xpath, Global.PageTimeout.QUICK_IGNORE)
        time_sleep = Global.PageTimeout.RETRY_INTERVAL
        # If timeout value is not specified, it shall use check status time as default
        timeout = kwargs.get('timeout') and kwargs['timeout'] or Global.PageTimeout.CHECK_STATUS
        attribute_name = kwargs.get('attribute_name') and kwargs['attribute_name']
        attribute_value = kwargs.get('attribute_value') and kwargs['attribute_value']
        retry = timeout / time_sleep
        counter = 1

        while not check_display():
            time.sleep(time_sleep)
            print("Retry times #%s after %s seconds..." % (counter, time_sleep))
            counter += 1
            if counter > retry:
                if attribute_name is False:
                    raise Exception("Timeout to wait for ['%s'] displayed." % xpath)
                else:
                    raise Exception("Timeout to wait until ['%s'] has attribute ['%s'] as ['%s']." \
                                    % (xpath, attribute_name, attribute_value))

        return True

    def handle_click_operation(self):
        element = self.current_element
        element.click()

    def handle_select_operation(self, option):
        select = self.current_element
        self.utils.select_option(select, option)

    def handle_input_operation(self, *arg):
        _input = self.current_element
        if not self.is_app:
            type_value = _input.get_attribute('type')

            if type_value in ('text', 'password', 'file'):
                if self.fetch_from_element:
                    self.append_element_value(_input)
                else:
                    _input.clear()
                    _input.send_keys(arg)
            elif type_value in ('checkbox', 'button', 'submit'):
                _input.click()
        else:
            _input.clear()
            # only workround when using ios9.3 with appium1.5.3
            platform_name = self.desired_capabilities['platformName']
            platform_version = self.desired_capabilities['platformVersion']
            c1 = platform_name == 'iOS'
            c2 = platform_version == '9.3'

            if c1 and c2:
                _input.set_value(arg)

                return

            _input.send_keys(arg)

            try:
                self.hide_keyboard()
            except WebDriverException:
                pass

    def handle_textarea_operation(self, *arg):
        text_area = self.current_element
        if self.fetch_from_element:
            self.append_element_value(text_area)
        else:
            text_area.clear()
            text_area.send_keys(arg)

    def handle_drag_drop_operation(self, to_element):
        action_chains = ActionChains(self.web_driver)
        action_chains.drag_and_drop(self.current_element, to_element).perform()

    def click_element_by_specified_proportion(self, xpath, x_proportion=0.5,
                                              y_proportion=0.5):
        """
        Move the mouse by an offset of the specified element.
           Offsets are relative to the top-left corner of the element.
        proportion must be >=0 and <= 1.
        :Args:
         - xpath: The element path to move to.
         - x_proportion: proportion of X offset to move to.
         - y_proportion: proportion of Y offset to move to.
        """
        element = self.get_element(xpath)
        element_size = element.size
        xoffset = int(x_proportion * element_size["width"])
        yoffset = int(y_proportion * element_size["height"])
        action_chains = ActionChains(self.web_driver)
        action_chains.move_to_element_with_offset(element, xoffset, yoffset).click().perform()

    def handle_swipe_operation(self, start_condition, stop_condition, direction=0):
        # mobile only
        # direction: 0 :from left to right
        # direction: 1: from down to up
        # stop_condition: stop operation when element xpath as condition occurs
        if self.element_exists_new(stop_condition, timeout=1.5):
            return

        counter = 0
        while not self.element_exists_new(start_condition):
            if counter > 1:
                counter = 0
                break
            counter += 1

            continue

        window_size = self.get_window_size()
        width, height = window_size['width'], window_size['height']

        if direction == 0:
            args = (width / 1.2, height / 2, width / 18, height / 2, 1000)
        elif direction == 1:
            args = (width / 2, height / 1.2, width / 2, height / 4, 1000)

        while self.web_driver.swipe(*args):
            if counter > 15:
                raise Exception('can not complete swiption!')
            if self.element_exists_new(stop_condition, timeout=1):
                break

            counter += 1

    def handle_swipe_operation_new(self, stop_condition, direction=0):
        # mobile only
        # direction: 0 :from left to right
        # direction: 1: from down to up
        # stop_condition: stop operation when element xpath as condition occurs
        if self.element_exists_new(stop_condition, timeout=1.5):
            return
        counter = 0
        window_size = self.get_window_size()
        width, height = window_size['width'], window_size['height']

        if direction == 0:
            args = (width / 1.2, height / 2, width / 18, height / 2, 1000)
        elif direction == 1:
            args = (width / 2, height / 1.2, width / 2, height / 4, 1000)

        while self.web_driver.swipe(*args):
            if counter > 40:
                raise Exception('can not complete swiption!')
            if self.element_exists_new(stop_condition, timeout=1):
                break

            counter += 1

    def append_element_value(self, element):
        value = None
        attr = None

        if element.get_attribute('type') == 'text':
            attr = 'get_attribute'
            value = 'value'
        elif element.get_attribute('type') == 'textarea':
            attr = 'text'
            value = None

        if value:
            data = getattr(element, attr)(value)
        else:
            data = getattr(element, attr)
        self.fetch_from_element_value.append(data)

    def perform_actions(self, *args, **kwargs):
        """
        Argument parsing and perform operations
        on web elements depends on the arg type.

        keyword arguments for perform_actions includes:
        A 'timeout':used for setting timeout value
            when waiting for element to be processed.
        B 'interval':used for controlling the interval of operation
            between the current element and next element
            to improve the stability
        C 'pause_step':used for interrupting action after certain step

        Type of argument chains:
        A (location, parameter_for_former_location, ...)
        B (location, location, ...)
        C (location, location_as_parameter_for_former_location, ...)

        Example:
        def login(self, user_name,
                    password, domain_name_tag, sleep=0):
            self._go_to_login_page(domain_name_tag)

            self.perform_actions(LOGIN_USER_NAME_XPATH, user_name,
                                LOGIN_PASSWORD_XPATH, password, LOGIN_SUBMIT_BUTTON_XPATH)
        """
        location_count = 0
        current_step = 0
        timeout = 'timeout' in kwargs and kwargs['timeout'] or TIMEOUT_FOR_GET_ELEMENT
        interval = 'interval' in kwargs and kwargs['interval'] or None
        pause_step = 'pause_step' in kwargs and kwargs['pause_step'] or None

        def get_next_item_index(args):  # retrieve the index of next object from arg list
            return args.index(args[i], i) + 1

        if self.is_current_element_not_displayed:
            self.is_current_element_not_displayed = False
            self.reset_sleep_seconds()

        # prepare for arguments
        for i in range(len(args)):
            operator_tag = None

            if args[i]:
                next_item_idx = get_next_item_index(args)
                parameters = self._build_parameters(args, i)

                # decide if arg is a location expression
                if parameters:
                    location, query_func_name, operator_tag, \
                    action_parameter_tag, lazy_initial_tag, \
                    offset_index, arguments_for_location, \
                    multi_location_index = parameters

                    self.current_element = _PageElementControl(self, 'get_element_new',
                                                               *(location, query_func_name),
                                                               **{'timeout': timeout})

                    if multi_location_index is not None:
                        self.current_element = self.current_element[multi_location_index]

                    location_count += 1
                    current_step += 1

                    if offset_index:
                        next_item_idx += 1

                    if not self.current_element.is_displayed():
                        print("the element %s is not displayed" % location)
                        # CONSIDERED LIABLE TO CHANGE WITHOUT WARNING.
                        # Use this to discover where on the screen an element is so that we can click it.
                        # This method should cause the element to be scrolled into view.
                        # Returns the top left hand corner location on the screen,
                        # or None if the element is not visible
                        can_be_scrolled_into_view = self.may_contain_scroll_bar and \
                                                    self.current_element.location_once_scrolled_into_view
                        if not can_be_scrolled_into_view:
                            if self.ignore_time_sleep:
                                self.ignore_time_sleep = False
                            else:
                                self.is_current_element_not_displayed = True
                                self.set_sleep_seconds(Global.PageTimeout.STABILITY_INTERVAL)

                    if operator_tag in self.SPECIAL_OPERATOR_MATCH_PATTERN:
                        next_item_location, next_item_query_func_name = arguments_for_location[0:2]
                        next_item_lazy_initial_tag = arguments_for_location[4]

                        if not next_item_lazy_initial_tag:
                            arguments_for_location = (_PageElementControl(self, 'get_element_new',
                                                                          *(next_item_location,
                                                                            next_item_query_func_name),
                                                                          **{'timeout': timeout}),)
                        else:
                            arguments_for_location = (next_item_location,)
                else:
                    # if arg is not a location expression,continue
                    continue
            else:
                continue

            # retrieve tag name of web element
            tag_name = self.get_tag_name(self.current_element.tag_name, operator_tag)

            # ready to execute actions
            if interval:
                time.sleep(interval)

            mapped_function_name = TagMapOperation.tag_map_function[tag_name]
            log_info = 'performing %s on %s' % (mapped_function_name, location)
            logger.info(log_info, False, True)
            getattr(self, mapped_function_name)(*arguments_for_location)
            take_screen_shot(self.web_driver, self.web_driver.log_path)

            if pause_step and (pause_step == current_step):
                break
        if self.fetch_from_element:
            self.fetch_from_element = False

            return self.fetch_from_element_value

        if not location_count:
            raise Exception("Argument error!(no location found)")
