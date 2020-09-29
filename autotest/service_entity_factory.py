# -*- coding: utf-8 -*-
from .lib.service_helper import ServiceHelper


class EntityFactory(object):
    def __init__(self, cookies=None, concurrent_mode=False):
        self.service_helper = ServiceHelper()
        self.cookies = cookies
        self.concurrent_mode = concurrent_mode

    def get_entity(self, entity_cls, *args, **kwargs):
        if self.concurrent_mode:
            kwargs.update(service_helper=self.service_helper)
        if self.cookies:
            kwargs.update(cookies=self.cookies)
        try:
            entity = entity_cls(*args, **kwargs)
        except TypeError as e:
            original_message = "(original message: %s)" % e
            if self.concurrent_mode:
                error_message = "Add default arg 'service_helper=None' to %s's __init__ with concurrent mode\n" \
                                % entity_cls.__name__ + original_message
            else:
                error_message = entity_cls.__name__ + str(e)
            raise TypeError(error_message)
        return entity
