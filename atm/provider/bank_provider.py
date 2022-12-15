class APIRequestFaildError(Exception):
    def __init__(self, msg="reuest failed", *args, **kwargs) -> None:
        super().__init__(msg, *args, **kwargs)


class ResponseHandler:
    def is_success_res(self, res: dict):
        return res["status"] >= 200 and res["status"] <= 300

    def get_data_from_res(self, res: dict):
        return res["data"]

    def get_err_messages(self, res: dict):
        return res.get("message", "No Error Message Provided")


class BankAPIProvider:
    # Response handler will handler api's response
    # handler could be dependent to api

    def __init__(
        self,
        api: any,
        version: int = 1,
    ) -> None:
        self.version = version
        self.res_handler = ResponseHandler()
        self.api = api

    def _reqeust(self, params: dict, api_to_request):
        res = api_to_request(**params)
        if self.res_handler.is_success_res(res):
            return self.res_handler.get_data_from_res(res)
        raise APIRequestFaildError(self.res_handler.get_err_messages(res))

    def request_card_validation(self, card_id: str, password: int):
        api_to_req = self.api.validate_card_password
        return self._reqeust(
            {"card_id": card_id, "card_password": password}, api_to_req
        )

    def request_account_list(self, card_id: str, password: int):
        api_to_req = self.api.find_accounts_by_cards
        return self._reqeust(
            {"card_id": card_id, "card_password": password}, api_to_req
        )

    def request_deposit(self, account_id: str, money: int):
        api_to_req = self.api.deposit
        params = {"account_id": account_id, "money": money}
        return self._reqeust(params, api_to_req)

    def request_withdraw(self, account_id: str, money: int):
        api_to_req = self.api.withdraw
        params = {"account_id": account_id, "money": money}
        return self._reqeust(params, api_to_req)

    def request_get_balance(self, account_id: str):
        api_to_req = self.api.get_balance
        params = {"account_id": account_id}
        return self._reqeust(params, api_to_req)["balance"]
