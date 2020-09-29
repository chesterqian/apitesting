# -*- coding: utf-8 -*-
class Global:
    class Environment:
        pass

    class PageTimeout:
        URL_JUMPING = 3
        ELEMENT_FINDING = 30
        QUICK_IGNORE = 15
        LOADING_CONDITION_IGNORE = 1
        RETRY_INTERVAL = 3
        MEDIA_HOTPOINT_INTERVAL = 240
        CHECKPOINT_INTERVAL = 5
        STABILITY_INTERVAL = 5
        TECH_CHECK_IDENTIFY = 5
        DEEP_LINKING = 60
        CHECK_STATUS = 60

    class RetryTimes:
        MIN = 2
        MEDIUM = 5
        MAX = 25
        GET_JOB_STATUS = 30

    class WebElementStatus:
        REG_DISABLED = r'ets-disabled|ets-broken'
        REG_ACTIVE = r'ets-active'
        REG_LOCKED = r'ets-locked'
        REG_PASSED = r'ets-ui-acc-act-nav-passed|ets-passed'
        REG_EXPANDED = r'ets-expanded'
        REG_SELECT_MODE = r'ets-select-mode'

    class PageLoadingConditons:
        # where all loading conditions are defined
        conditions = (
            'loading_icon', 'loading_backdrop', 'asr_loading_icon', 'question_counter_icon')

    class PageOperationInterval:
        MIN = 0.25
        MEDIUM = 1.5
        MAX = 3

    class PageOperationTimeout:
        MIN = 1
        MEDIUM = 1.5

    class HeaderContentType:
        FORM = "application/x-www-form-urlencoded; charset=UTF-8"
        JSON = "application/json; charset=utf-8"
