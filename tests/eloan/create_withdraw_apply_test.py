import unittest
import os
from ddt import ddt, file_data, unpack
from autotest.exception import BadStatusCodeException
from autotest.meta_data_handler import BaseMetaDataHandler
from service_entities.eloan_entities.main_eloan_service import \
    MainEloanService
from db.db_operations import clean_db_for_eloan_regression

JPEG_FILE_PATH = "static/upsert_withdraw_apply.jpeg"
JPEG_FILE_PATH = os.path.join(os.path.dirname(__file__), JPEG_FILE_PATH)


def clean_withdraw_apply_from_db(func):
    def wrapper(*args, **kwargs):
        print("Prepare db data")
        clean_db_for_eloan_regression()
        print("Finish prepare db data")
        return func(*args, **kwargs)

    return wrapper


class TestOracle(BaseMetaDataHandler):
    pass


def assert_by_oracle(case, entity, test_oracle):
    error_msg = "key with error:{}"

    def prepare_assert_equal_args():
        args = (getattr(entity, attr), 
                        getattr(test_oracle, attr), 
                        error_msg.format(attr))
        return args

    def prepare_assert_is_not_none_args():
        args = (getattr(entity, attr), error_msg.format(attr))
        return args

    assertion_map_args_prepare = {
                "assertEqual": prepare_assert_equal_args,
                "assertIsNotNone": prepare_assert_is_not_none_args
                }

    for _assert in test_oracle.meta_data:
        with test_oracle.shift_context(_assert, getattr(test_oracle, _assert)): 
                for attr in test_oracle.meta_data:
                    assert_args = assertion_map_args_prepare[_assert]()

                    getattr(case, _assert)(*assert_args)


@ddt
class EloanCreateWithdrawApplyTest(unittest.TestCase):
    def setUp(self):
        clean_db_for_eloan_regression()
        self.main_service_entity = MainEloanService()
        # 获取token
        self.main_service_entity.post_token()
        self.assertIsNotNone(self.main_service_entity.token)
        # 登录获取uid
        self.main_service_entity.post_uid()

    @file_data('testdata/ddt_create_withdraw_apply_testdata_on_failure.json')
    @unpack
    def test_ddt_create_withdraw_apply_on_failure(self, loan_amount, test_oracle):
        entity = self.main_service_entity
        test_oracle = TestOracle(test_oracle)

        try:
            print("loanAmount={}".format(loan_amount))
            entity.upsert_withdraw_apply(loanAmount=loan_amount)
        except BadStatusCodeException:
            pass

        assert_by_oracle(self, entity, test_oracle)

    @file_data('testdata/ddt_create_withdraw_apply_testdata_on_success.json')
    @unpack
    def test_ddt_create_withdraw_apply_on_success(self, loan_amount, test_oracle):
        entity = self.main_service_entity
        test_oracle = TestOracle(test_oracle)

        try:
            print("loanAmount={}".format(loan_amount))
            entity.upsert_withdraw_apply(loanAmount=loan_amount)
        except BadStatusCodeException:
            pass

        assert_by_oracle(self, entity, test_oracle)

    def tearDown(self):
        clean_db_for_eloan_regression()
        print("Test case finished")


if __name__ == '__main__':
    unittest.main()
