from autotest import EntityFactory
from util import intersection_of_path
from service_entities.eloan_entities.post_uus_user_auth_entity import \
    PostUusUserAuthEntity
from service_entities.eloan_entities.post_credit_login_entity import \
    PostCreditLoginEntity
from service_entities.eloan_entities.get_credit_limit_entity import \
    GetCreditLimitEntity
from service_entities.eloan_entities.get_withdraw_apply_eloan_salary_latest_loan_entity import \
    GetWithdrawApplyEloanSalaryLatestLoanEntity
from service_entities.eloan_entities.post_credit_limit_apply_entity import \
    PostCreditLimitApplyEntity
from service_entities.eloan_entities.post_withdraw_apply_eloan_salary_create_or_update_entity import \
    PostWithdrawApplyEloanSalaryCreateOrUpdateEntity
from service_entities.eloan_entities.post_withdraw_apply_submit_entity import \
    PostWithdrawApplySubmitEntity
from service_entities.eloan_entities.post_withdraw_apply_standard_fund_examine_entity import \
    PostWithdrawApplyStandardFundExamineEntity
from service_entities.eloan_entities.post_withdraw_apply_upload_file_entity import \
    PostWithdrawApplyUploadFileEntity


class MainEloanService(object):
    def __init__(self, concurrent_mode=False):
        self._entity_factory = EntityFactory(
            concurrent_mode=concurrent_mode)
        self._current_entity = None
        self._token = None
        self._common_headers = {}

    @property
    def common_headers(self):
        return self._common_headers

    @property
    def token(self):
        return self._token

    def __getattr__(self, attr):
        return getattr(self._current_entity, attr)

    def post_token(self, **kwargs):
        entity = self._entity_factory.get_entity(PostUusUserAuthEntity)
        self._current_entity = entity

        entity.send_request(**kwargs)
        self._token = entity.content["access_token"]
        self._common_headers["X-BK-UUSSSO-Token"] = self._token
        return self._token

    def post_uid(self, **kwargs):
        entity = self._entity_factory.get_entity(PostCreditLoginEntity,
                                                 **{
                                                     "request_headers": self.common_headers
                                                     })
        self._current_entity = entity

        entity.send_request(**kwargs)
        self._common_headers["X-UID"] = entity.data_uid

    def apply_credit_limit(self, product_id="ELOAN_SALARY"):
        entity = self._entity_factory.get_entity(PostCreditLimitApplyEntity,
                                                 **{
                                                     "productId": product_id,
                                                     "request_headers": self.common_headers
                                                 })
        self._current_entity = entity

        entity.send_request()

    def get_credit_limit(self, **kwargs):
        # kwargs:productId=ELOAN_SALARY
        entity = self._entity_factory.get_entity(GetCreditLimitEntity,
                                                 **{
                                                     "request_headers": self.common_headers
                                                     })
        self._current_entity = entity

        entity.send_request(**kwargs)

    def get_latest_withdraw_apply(self, loan_type="ELOAN_SALARY"):
        entity = self._entity_factory.get_entity(
            GetWithdrawApplyEloanSalaryLatestLoanEntity,
            **{
                "request_headers": self.common_headers,
                "loan_type": loan_type
            }
        )
        self._current_entity = entity

        entity.send_request()

    def upsert_withdraw_apply(self, loan_type="ELOAN_SALARY", **kwargs):
        # kwargs: 
        # loanAmount=6000,
        # loanMaturity="MONTH_6",
        # loanPurpose="DAILY_CONSUMPTION"
        entity = self._entity_factory.get_entity(
            PostWithdrawApplyEloanSalaryCreateOrUpdateEntity,
            **{
                "request_headers": self.common_headers,
                "loan_type": loan_type
            }
        )
        self._current_entity = entity

        entity.send_request(**kwargs)

    def standard_fund_examine(self, apply_id):
        entity = self._entity_factory.get_entity(
            PostWithdrawApplyStandardFundExamineEntity,
            **{
                "request_headers": self.common_headers,
                "apply_id": apply_id
            }
        )
        self._current_entity = entity

        entity.send_request()

    def submit_withdraw_apply(self, apply_id):
        entity = self._entity_factory.get_entity(
            PostWithdrawApplySubmitEntity,
            **{
                "request_headers": self.common_headers,
                "apply_id": apply_id
            }
        )
        self._current_entity = entity

        entity.send_request()

    def upload_file(self, file_name, apply_id, jpeg_file_path,
                    file_type="LOAN_PURPOSE_CERTIFICATION"):
        file_path = jpeg_file_path

        with open(file_path, 'rb')as f:
            files = {"file": (f.name.split('/')[-1], f, "image/jpeg")}

            entity = self._entity_factory.get_entity(
                PostWithdrawApplyUploadFileEntity,
               **{
                    "request_headers": self.common_headers,
                    "apply_id": apply_id,
                    "file_type": file_type,
                    "file_name": file_name,
                    "files": files
                }
                )
            self._current_entity = entity

            entity.send_request()


if __name__ == '__main__':
    main_entity = MainEloanService()
    main_entity.post_token()
    main_entity.post_uid()
    # main_entity.apply_credit_limit()
    # main_entity.get_credit_limit(productId="ELOAN_SALARY")
    # main_entity.get_latest_withdraw_apply()
    # main_entity.upsert_withdraw_apply(loanAmount=6000)
    # main_entity.standard_fund_examine(87)
    # main_entity.submit_withdraw_apply(87)
    relative_path = "test-eloan/tests/service_entities_unit_test/static/ddt_upsert_withdraw_apply.jpeg"
    main_entity.upload_file(1, 1, relative_path)
