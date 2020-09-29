import time


class LoopWait:
    """
    Loop execute a function until expected values appear or time-out occurs

    example:
        entity, is_find = LoopWait(5, 1).setfunc(self.main_service_entity.post_new_task, title=title, done=done)\
                .expects(False, status = 'Created', done = 'False'}

        entity, is_find = LoopWait().setfunc(self.main_service_entity.post_new_task, title=title, done=done)\
                .expect("status", "Created")
    """

    def __init__(self, total_time=5, interval_time=0.5):
        self._total_time = total_time
        self._interval_time = interval_time
        self._func, self._args, self._kwargs = None, None, None

    def setfunc(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs
        return self

    def expect(self, field, value):
        flag = False

        if self._func is None:
            raise Exception("please set up the execution function first!")

        entity = self._func(*self._args, **self._kwargs)

        for t in range(self._total_time):
            if not hasattr(entity, field):
                raise Exception("No such attribute %s" % field)

            if getattr(entity, field) == value:
                flag = True
                break

            time.sleep(self._interval_time)
            entity = self._func(*self._args, **self._kwargs)

        return entity, flag

    def expects(self, is_and=True, **kwargs):
        """
        multiple expectation conditions
        :param is_and:  whether or not the relationship of multiple condititons is 'and'
        :param kwargs:
        :return:
        """
        if self._func is None:
            raise Exception("please set up the execution function first!")

        entity = self._func(*self._args, **self._kwargs)
        flag = None

        for t in range(self._total_time):
            # depending on the relationship, set different default values
            flag = True if is_and else False
            for k, v in kwargs.items():
                if not hasattr(entity, k):
                    raise Exception("No such attribute %s" % k)

                if is_and and getattr(entity, k) != v:
                    flag = False
                    break
                elif not is_and and getattr(entity, k) == v:
                    flag = True
                    break

            if flag:
                break

            time.sleep(self._interval_time)
            entity = self._func(*self._args, **self._kwargs)

        return entity, flag
