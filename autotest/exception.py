# -*- coding: utf-8 -*-
ERROR_MESSAGE_DESTINATION_PAGE_NAVIGATION = "Error occurred when going to page %s"
ERROR_MESSAGE_QUESTION_NAVIGATION = "Error occurred when going to question number which is %s"
ERROR_MESSAGE_ACTIVITY_NAVIGATION = "Error occurred when going to activity page whose id is %s"
ERROR_MESSAGE_COURSE_NAVIGATION = "Error occurred when going to course page"
ERROR_MESSAGE_NOT_SHOWN = "element not shown on the page, xpath:%s"


class PageExceptionType:
    ELEMENT_NOT_EXIST = 1
    PAGE_NAVIGATION_ERROR = 2
    QUESTION_NAVIGATION_ERROR = 3


class BasicPageException(Exception):
    # types of exception:
    # 1.element exists exception
    # 2.page navigation exception
    exception_type = None

    def __init__(self, page_object):
        self.page_object = page_object
        self.error_message = None

    def __str__(self):
        exception_msg = "Message: %s " % repr(self.error_message)
        return exception_msg

    def add_error_message(self, error_message):
        self.error_message = error_message

    def handle_exception(self):
        raise NotImplementedError("Should be implemented")

        
class MetaDataException(Exception):
    pass


class BadStatusCodeException(Exception):
    def __init__(self, error_msg, response):
        self.entity = None
        self.message = error_msg
        self.response = response

        super(BadStatusCodeException, self).__init__(error_msg)

    def __str__(self):
        return self.message