import uuid


class FakeBankAPI:
    # skip any non-critical validaition because this is fake abstracted bank
    # APIProvider Will Call FakeBankAPI's functions

    def __init__(self) -> None:
        self.account_data = dict()
        self.card_data = dict()

    def _generate_unique_key(
        self,
    ):
        return str(uuid.uuid1())

    def _is_valid_card_password(self, card_id: str, password: int):
        return self.card_data[card_id]["password"] == password

    def create_card(self, name: str, password: int):
        key = self._generate_unique_key()
        self.card_data[key] = {"name": name, "password": password}
        return self._return_201_response({"card_number": key, **self.card_data[key]})

    def _return_card_validation_fail_response(self):
        return {"message": "invalid card password", "status": 400}

    def _return_balance_is_empty_or_less_than_request_response(self):
        return {"message": "Balance is not enough", "status": 400}

    def _return_201_response(self, data: dict = {}):
        return {"data": data, "status": 201}

    def _return_200_response(self, data: dict = {}):
        return {"data": data, "status": 200}

    def create_account(
        self,
        client_name: str,
        account_name: str,
        linked_card_id: str,
        card_password: int,
    ):
        if not self._is_valid_card_password(linked_card_id, card_password):
            return self._return_card_validation_fail_response()
        else:
            key = self._generate_unique_key()
            self.account_data[key] = {
                "client_name": client_name,
                "account_name": account_name,
                "linked_card": linked_card_id,
                "balance": 0,
            }
            self._return_201_response({"account_number": key, **self.account_data[key]})

    def validate_card_password(self, card_id: str, card_password: int):
        if not self._is_valid_card_password(card_id, card_password):
            return self._return_card_validation_fail_response()
        else:
            return self._return_200_response()

    def find_accounts_by_cards(self, card_id, card_password):
        if not self._is_valid_card_password(card_id, card_password):
            return self._return_card_validation_fail_response()
        else:
            accounts = list(
                map(
                    lambda account_id: {
                        "account_number": account_id,
                        **self.account_data[account_id],
                    },
                    (
                        filter(
                            lambda account_id: self.account_data[account_id][
                                "linked_card"
                            ]
                            == card_id,
                            self.account_data.keys(),
                        )
                    ),
                )
            )
            return self._return_201_response({"accounts": accounts})

    def get_balance(self, account_id: str):
        balance = self.account_data[account_id]["balance"]
        return self._return_201_response({"balance": balance})

    def _update_account_balance(self, account_id: str, money: int):
        self.account_data[account_id]["balance"] += money

    def deposit(self, account_id: str, money: int):
        self._update_account_balance(account_id, money)
        return self._return_201_response()

    def withdraw(self, account_id: str, money: int):
        if self.account_data[account_id]["balance"] >= money:
            self._update_account_balance(account_id, -money)
            return self._return_201_response()
        else:
            return self._return_balance_is_empty_or_less_than_request_response()


bank_api = FakeBankAPI
