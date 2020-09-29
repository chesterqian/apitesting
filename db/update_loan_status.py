import dataset



class LoanStatus():
    def __init__(self, user, pw, host, port, db):
        self._user = user
        self._pw = pw
        self._host = host
        self._port = port
        self._db = db

        self.connection = dataset.connect(
            f"mysql://{self._user}:{self._pw}@{self._host}:{self._port}/{self._db}"
        )

    def update_status(self, status, **condition):

        credit_loan_table = self.connection["loan"]

        condition_key = list(condition.keys())

        condition.update({"loan_lifecycle_status": status})

        data = condition

        if condition_key:

            result = credit_loan_table.update(data, condition_key)

        else:

            raise Exception("Danagerous Operation!")

        return "Success" if result else "Failed"


if __name__ == "__main__":

    ls = LoanStatus("credit_loan", "oqj7K_ReZdBq1", "172.29.10.50", 3308,
                    "credit_loan")

    print(
        ls.update_status(3, **{
            "uid": "213111",
            "product_id": "ELOAN_SALARY"
        }))
