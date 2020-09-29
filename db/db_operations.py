from config.config_handler import config_handler
from db.delete_withdraw_apply import WithdrawApply
from db.update_loan_status import LoanStatus


def clean_db_for_eloan_regression():
    wa = WithdrawApply(**config_handler.aliceDB)
    wa.deletion(213111)
    ls = LoanStatus(**config_handler.creditLoanDB)
    ls.update_status(3, uid="213111", product_id="ELOAN_SALARY")


if __name__ == "__main__":
    clean_db_for_eloan_regression()