# -*- coding:utf-8 -*-
from selenium.common.exceptions import NoSuchElementException, \
    TimeoutException


class SeleniumPage(object):
    driver = None
    waiter = None

    def __init__(self, driver, waiter):
        self.web_driver = driver
        self.waiter = waiter

    def open_page(self, url):
        self.driver.get(url)

    def print_el(self, element):
        print('tag: ' + element.tag_name + ' id: ' + element.id + ' class: ' + element.get_attribute(
            'class') \
              + ' text: ' + element.text)

    def get_el(self, selector):
        if isinstance(selector, str):
            return self.driver.find_elements_by_xpath(selector)
        else:
            return selector

    def get_els(self, selector):
        if isinstance(selector, str):
            return self.driver.find_elements_by_xpath(selector)
        else:
            return selector

    def get_child_el(self, parent, selector):
        return parent.find_element_by_css_selector(selector)

    def get_child_els(self, parent, selector):
        return parent.find_elements_by_css_selector(selector)

    def is_el_present(self, selector):
        try:
            self.driver.find_element_by_css_selector(selector)
            return True
        except NoSuchElementException:
            return False

    def is_el_visible(self, selector):
        return self.get_el(selector).is_displayed()

    def click_button(self, selector):
        self.get_el(selector).click()

    def enter_text_field(self, selector, text):
        text_field = self.get_el(selector)
        text_field.clear()
        text_field.send_keys(text)

    def select_checkbox(self, selector, name, deselect=False):
        found_checkbox = False
        checkboxes = self.get_els(selector)
        for checkbox in checkboxes:
            if checkbox.get_attribute('name') == name:
                found_checkbox = True
                if not deselect and not checkbox.is_selected():
                    checkbox.click()
                if deselect and checkbox.is_selected():
                    checkbox.click()
        if not found_checkbox:
            raise Exception('Checkbox %s not found.' % name)

    def select_option(self, select, value):
        found_option = False
        options = select.find_elements_by_tag_name("option")
        for option in options:
            if option.get_attribute('value') == value:
                found_option = True
                option.click()
        if not found_option:
            raise Exception('Option %s not found' % value)

    def is_option_selected(self, selector, value):
        options = self.get_els(selector)
        for option in options:
            if option.is_selected() != (
                value == option.get_attribute('value')):
                return False
        return True

    def verify_inputs_checked(self, selector, checked):
        checkboxes = self.get_els(selector)
        for checkbox in checkboxes:
            name = checkbox.get_attribute('name')
            if checkbox.is_selected() != (name in checked):
                raise Exception(
                    "Input isn't checked as expected - %s" % name)

    def verify_option_selected(self, selector, value):
        if not self.is_option_selected(selector, value):
            raise Exception('Option isnt selected as expected')

    def verify_text_field(self, selector, text):
        text_field = self.get_el(selector)
        value = text_field.get_attribute('value')
        if value != text:
            raise Exception(
                'Text field contains %s, not %s' % (value, text))

    def verify_text_in_els(self, selector, text):
        els = self.get_els(selector)
        found_text = False
        for el in els:
            if text in el.text:
                found_text = True
        if not found_text:
            raise Exception("Didn't find text: %s" % text)

    def is_button_enabled(self, selector):
        return self.get_el(selector).get_attribute('disabled') == 'false'

    def check_title(self, title):
        return self.driver.title == title

    def wait_for(self, condition):
        self.waiter.until(lambda driver: condition())

    def wait_for_button(self, selector):
        try:
            self.waiter.until(
                lambda driver: self.is_button_enabled(selector))
        except TimeoutException:
            raise Exception('Never saw button %s enabled' % selector)

    def wait_for_el(self, selector):
        try:
            self.waiter.until(lambda driver: self.is_el_present(selector))
        except TimeoutException:
            raise Exception('Never saw element %s' % selector)

    def wait_for_title(self, title):
        try:
            self.waiter.until(lambda driver: self.check_title(title))
        except TimeoutException:
            raise Exception('Never saw title change to %s' % title)
