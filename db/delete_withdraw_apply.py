import dataset


class WithdrawApply():
    def __init__(self, user, pw, host, port, db):
        self._user = user
        self._pw = pw
        self._host = host
        self._port = port
        self._db = db

        self.connection = dataset.connect(
            f"mysql://{self._user}:{self._pw}@{self._host}:{self._port}/{self._db}")

    def deletion(self, uid=None):

        withdraw_apply_table = self.connection["withdraw_apply"]

        is_exist = withdraw_apply_table.find_one(uid=uid)

        if uid and is_exist:

            result = withdraw_apply_table.delete(uid=uid)

        elif not uid:

            raise Exception("Danagerous Operation!")

        else:

            return "Success"

        return "Success" if result else "Failed"


if __name__ == "__main__":

    wa = WithdrawApply("alice", "alice-secret", "10.132.0.6", 32781, "alicedb")

    print(wa.deletion(213111))