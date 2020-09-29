import time
import unittest
import os
from ddt import ddt, file_data, unpack
from autotest.exception import BadStatusCodeException
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


@ddt
class EloanRegressionTest(unittest.TestCase):
    def setUp(self):
        self.main_service_entity = MainEloanService()
        # 获取token
        self.main_service_entity.post_token()
        self.assertIsNotNone(self.main_service_entity.token)
        # 登录获取uid
        self.main_service_entity.post_uid()

    @clean_withdraw_apply_from_db
    def test_positive_flow(self):
        entity = self.main_service_entity
        # 申请额度
        # entity.apply_credit_limit(product_id="ELOAN_SALARY")

        # 创建/更新借款申请
        print("do upsert_withdraw_apply")
        entity.upsert_withdraw_apply(loan_type="ELOAN_SALARY")
        print("finish upsert_withdraw_apply")
        
        self.assertIsNotNone(entity.id)
        self.assertEqual(entity.uid, "213111")
        self.assertEqual(entity.productId, "ELOAN_SALARY")
        self.assertEqual(entity.applyStatus, "CREATED")
        self.assertEqual(entity.loanAmount, 6000)
        self.assertEqual(entity.loanMaturity, {
            "code": "MONTH_6",
            "name": "6个月",
            "term": 6
        })
        self.assertEqual(entity.loanPurpose, "DAILY_CONSUMPTION")
        self.assertEqual(entity.receiveAccount, {
            "uid": "213111",
            "accountType": None,
            "accountName": None,
            "accountNo": "6217003810048135570",
            "bankCode": None,
            "bankName": "建设银行",
            "accountTelephone": None,
            "bankAddress": None,
            "bankUnionNo": None
        })
        self.assertEqual(entity.repaymentMethod, "AVERAGE_CAPITAL_PLUS_INTEREST")

        product_id = entity.productId
        loan_amount = entity.loanAmount
        loan_maturity = entity.loanMaturity_code
        loan_purpose = entity.loanPurpose
        uid = entity.uid

        # 获取apply id
        apply_id = entity.id

        # 上传文件
        print("do upload_file")
        entity.upload_file(1, apply_id, JPEG_FILE_PATH, file_type="LOAN_PURPOSE_CERTIFICATION")
        print("finish upload_file")

        self.assertEqual(entity.code, "200")
        self.assertEqual(entity.msg, "上传成功！")
        self.assertIsNotNone(entity.fileId)

        # 资金路由
        print("do standard_fund_examine")
        entity.standard_fund_examine(apply_id=apply_id)
        print("finish standard_fund_examine")

        self.assertEqual(entity.applyId, apply_id)
        self.assertIsNotNone(entity.financeOrderNo)
        self.assertIsNotNone(entity.fundLoanNo)
        self.assertEqual(entity.examStatus, "ACCEPT")

        # 最近一笔借款
        while entity.loanProgressStatus != "ACCOUNT_SUCCESS":
            entity.get_latest_withdraw_apply(loan_type="ELOAN_SALARY")
            time.sleep(1)

        self.assertEqual(entity.uid, uid)
        self.assertEqual(entity.productId, product_id)
        self.assertIsNotNone(entity.withdrawApplyId)
        self.assertEqual(entity.loanProgressStatus, "ACCOUNT_SUCCESS")
        self.assertEqual(entity.loanAmount, loan_amount)
        self.assertEqual(entity.loanMaturity, loan_maturity)
        self.assertEqual(entity.loanPurpose, loan_purpose)

        # 风控/签约
        entity.submit_withdraw_apply(apply_id=apply_id)
        self.assertEqual(entity.applyStatus, "SUBMITTED")
        self.assertEqual(entity.applyId, apply_id)
        self.assertEqual(entity.loanAmount, loan_amount)

        # 风控/签约后再次查询借款状态
        while entity.loanProgressStatus != "APPROVED":
            try:
                entity.get_latest_withdraw_apply(loan_type="ELOAN_SALARY")
            except BadStatusCodeException:
                pass
            time.sleep(1)

        # 信贷额度/credit-limit
        print("get get_credit_limit")
        entity.get_credit_limit(productId="ELOAN_SALARY")
        print("get get_credit_limit")
        self.assertEqual(entity.json_content, {
                                                "uid": uid,
                                                "limit": 10000.00,
                                                "available": 10000.00,
                                                "used": 0.00,
                                                "serviceFeeRate": 0.0065,
                                                "annualizedRate": 0.0780,
                                                "status": "NORMAL",
                                                "expiryDate": 1561362557650,
                                                "maxLoanLimit": 6
                                            })

    def tearDown(self):
        clean_db_for_eloan_regression()
        print("Test case finished")


if __name__ == '__main__':
    unittest.main()
