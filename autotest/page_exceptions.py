'''
Created on Aug 8, 2013

@author: Chester.Qian
'''
ERROR_MESSAGE_DESTINATION_PAGE_NAVIGATION = "Error occurred when going to page %s"
ERROR_MESSAGE_QUESTION_NAVIGATION = "Error occurred when going to question number which is %s"
ERROR_MESSAGE_ACTIVITY_NAVIGATION = "Error occurred when going to activity page whose id is %s"
ERROR_MESSAGE_COURSE_NAVIGATION = "Error occurred when going to course page"
ERROR_MESSAGE_NOT_SHOWN = "element not shown on the page, xpath:%s"


class ExceptionType:
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


class BasicActivityPageException(BasicPageException):

    def __init__(self, page_object):
        '''
        Some activities(e.g.MatchingActivityPage,TypingActivityPage)
        have a feature that it randomly and selectively shows questions and answer element
        on page object from raw content which means if the expected element didn't show on
        the page then the page should raise its own type of exception to handle such circumstances
        as a kind of work around for testablily issues.
        '''
        super(BasicActivityPageException, self).__init__(page_object)

        activity = self.page_object.activity
        self.number_of_questions_from_content = len(activity.questions)
        self.number_of_questions_in_runtime = activity.filtered_question_number

        self.length_difference = abs(cmp(self.number_of_questions_from_content, \
                                         self.number_of_questions_in_runtime))

    def handle_exception(self):
        # handle business level exception
        error_message = ERROR_MESSAGE_NOT_SHOWN % \
                        self.page_object.current_xpath_on_error

        if self.length_difference == 0:
            self.add_error_message(error_message)
            raise NotImplementedError

        self.number_of_questions_from_content -= 1
        if self.number_of_questions_from_content < \
                self.number_of_questions_in_runtime:
            self.add_error_message(error_message)
            raise NotImplementedError

        pass
