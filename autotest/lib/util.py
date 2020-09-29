# -*- coding:utf8 -*-
import datetime
import time
import re

from robot.api import logger


def take_screen_shot(driver, path):
    time.sleep(1)
    file_name = str(str(time.time()).replace('.', ''))
    file_fullname = path + "\\" + file_name + '.png'
    driver.get_screenshot_as_file(file_fullname)
    logger.info('<a href="%s"><img src="%s" width="%s"></a>'
                % (file_fullname, file_fullname, '300'), html=True)
    return file_fullname


def format_str(orign_str, size=13):
    if not size:
        return orign_str
    elif size >= len(orign_str):
        return orign_str.ljust(size, "0")
    else:
        return orign_str[0:size]


def get_time_stamp(size=13, **kwargs):
    """
    :param size:
    :param kwargs: 同timedelta参数 {days=?,seconds=?,microseconds=?,milliseconds=?,minutes=?,hours=?,weeks=?}
    :return:类似1543740088362

    example:
        stamp = get_time_stamp(size=13, days=-1)
        stamp = get_time_stamp(size=17, days=10, hours=20))
    """
    if kwargs:
        dt = datetime.datetime.now() + datetime.timedelta(**kwargs)
        stamp = str(dt.timestamp()).replace(".", "")
    else:
        stamp = str(time.time()).replace(".", "")

    return format_str(stamp, size)


def get_time_str(size=13, **kwargs):
    """
    基本同get_time_stamp
    :return:类似2018121316412
    """
    if kwargs:
        time_str = str(datetime.datetime.now() + datetime.timedelta(**kwargs))
    else:
        time_str = str(datetime.datetime.now())

    time_str = re.sub(r'[.\- :]', '', time_str)

    return format_str(time_str, size)
