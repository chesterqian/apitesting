# -*- coding:utf-8 -*-
import time
from functools import wraps
from selenium.common.exceptions import TimeoutException
from autotest.global_config import Global


def wait_for_page_to_load(func):
    """
    It needs time for browser to render the full page
    so that the performing action on page elements
    should be held over until the page is loaded completely
    within endurable time.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        page = args[0]
        time_sleep = Global.PageTimeout.RETRY_INTERVAL
        retry = 0

        def load_page_status():
            def _hasattr(_page, _condition):
                try:
                    return hasattr(_page, _condition)
                except TypeError:
                    return False

            conditions = [getattr(page, condition) for condition
                          in Global.PageLoadingConditons.conditions if
                          _hasattr(page, condition)]
            values = []
            condition_counts = 0
            for condition in conditions:
                if condition:
                    if page.element_exists_new(condition,
                                               Global.PageTimeout.LOADING_CONDITION_IGNORE):
                        try:
                            values.append(
                                getattr(page.get_element_new(condition),
                                        'is_displayed')())
                            condition_counts += 1
                        except TimeoutException:
                            pass

            value = [v for v in values if v]

            if value:
                status_for_is_loaded = False
            else:
                status_for_is_loaded = True

            setattr(page, 'is_assumed_fully_loaded', status_for_is_loaded)

            return status_for_is_loaded

        try:
            while not (load_page_status()):
                time.sleep(time_sleep)
                retry += 1
                print("Retry times #%s after %s seconds..." % (
                    retry, time_sleep))
                if retry > 10:
                    raise Exception(
                        "Timeout when page loading for %s!" % func.__name__)
        except AttributeError:
            pass

        return func(*args, **kwargs)

    return wrapper


def reset_page_load_status(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        page = args[0]
        page.is_assumed_fully_loaded = False

        return func(*args, **kwargs)

    return wrapper


def retry_on_exception(retry_times, exception_type):
    """
    Retry the decorated function for zero to maximal retry_times when exception_type occurs.
    Will raise exception when exceeding the maximal retry_times.
    """

    def deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_retry_times = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except exception_type:
                    current_retry_times += 1
                    if current_retry_times > retry_times:
                        raise

        return wrapper

    return deco


def check_page_afterwards(func):
    """
    检查页面是否跳转正确
    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(page_obj, *args, **kwargs):
        page = func(page_obj, *args, **kwargs)
        page.check_destination_page(page)

        return page

    return wrapper


def return_page_afterwards(func):
    @wraps(func)
    def wrapper(from_page, *args, **kwargs):
        func(from_page, *args, **kwargs)
        ui_flow = from_page.ui_flow
        activity_map_return_page = from_page.activity_map_return_page
        return_page_name = activity_map_return_page[func.__name__]
        return_page = ui_flow[return_page_name]
        # return_page.check_destination_page(return_page)

        return return_page

    return wrapper


def dec_handle_guide_swipe_before(SWIPE_START_CONDITION, SWIPE_STOP_CONDITION):
    def oper(func):
        @wraps(func)
        def wrapper(page_obj, *args, **kwargs):
            if page_obj.element_exists_new(SWIPE_START_CONDITION, timeout=15):
                page_obj.handle_swipe_operation(SWIPE_START_CONDITION,
                                                SWIPE_STOP_CONDITION)
                page_obj.perform_actions(SWIPE_STOP_CONDITION)

            return func(page_obj, *args, **kwargs)

        return wrapper

    return oper


def dec_login_afterwards(PHONE_NUMBER, LOGIN_PHONE_NUMBER, PASSWORD, LOGIN_PASSWORD, LOGIN_BUTTON):
    """
     自动登录
    :param func:
    :return:
    """

    def oper(func):
        @wraps(func)
        def wrapper(page_obj, *args, **kwargs):
            next_page_obj = func(page_obj, *args, **kwargs)

            if page_obj.element_exists_new(PHONE_NUMBER, timeout=30):
                page_obj.perform_actions(PHONE_NUMBER, LOGIN_PHONE_NUMBER, PASSWORD, LOGIN_PASSWORD, LOGIN_BUTTON)

            return next_page_obj

        return wrapper

    return oper


def dec_cancel_gesture_afterwards(CANCEL_GESTURE_BOTTUN):
    def oper(func):
        @wraps(func)
        def wrapper(page_obj, *args, **kwargs):
            next_page_obj = func(page_obj, *args, **kwargs)

            if page_obj.element_exists_new(CANCEL_GESTURE_BOTTUN, timeout=10):
                page_obj.perform_actions(CANCEL_GESTURE_BOTTUN)

            return next_page_obj

        return wrapper

    return oper


def dec_back_afterwards(BACK_BUTTON):
    """
    返回按钮
    :param func:
    :return:
    """

    def oper(func):
        @wraps(func)
        def wrapper(page_obj, *args, **kwargs):
            next_page_obj = func(page_obj, *args, **kwargs)

            if page_obj.element_exists_new(BACK_BUTTON, timeout=3):
                page_obj.perform_actions(BACK_BUTTON)

            return next_page_obj

        return wrapper

    return oper


def dec_cancel_prompt_afterwards(CANCEL_PROMPT):
    def oper(func):
        @wraps(func)
        def wrapper(page_obj, *args, **kwargs):
            next_page_obj = func(page_obj, *args, **kwargs)

            if page_obj.element_exists_new(CANCEL_PROMPT, timeout=15):
                page_obj.perform_actions(CANCEL_PROMPT)

            return next_page_obj

        return wrapper

    return oper


def dec_handle_dialog_close(DIALOG_CLOSE):
    def oper(func):
        @wraps(func)
        def wrapper(page_obj, *args, **kwargs):
            if page_obj.element_exists_new(DIALOG_CLOSE, timeout=3):
                page_obj.perform_actions(DIALOG_CLOSE)

            return func(page_obj, *args, **kwargs)

        return wrapper

    return oper


def dec_handle_dialog_close_afterword(DIALOG_CLOSE):
    def oper(func):
        @wraps(func)
        def wrapper(page_obj, *args, **kwargs):
            if page_obj.element_exists_new(DIALOG_CLOSE, timeout=3):
                page_obj.perform_actions(DIALOG_CLOSE)

            return func(page_obj, *args, **kwargs)

        return wrapper

    return oper
