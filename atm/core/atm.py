from enum import Enum


class ATM_STATUS(Enum):
    WAIT_FOR_API_RES = 0
    WAIT = 1
    WAIT_FOR_CARD = 2
    CARD_INSERTED = 3
    CARD_PASSWORD_VALIDATED = 4
    ACCOUNT_LISTED = 4
    ACCOUNT_SELECTED = 5
    BALANCE_SHOWED = 6
    DEPOSIT_DONE = 7
    WITHDRAW_DONE = 8


class ATM:
    # ATM must not be dependent on the provider
    # It will raise APIRequestFaildError wit error message when any request failed
    # TODO: Showing the error message to user is required features
    def __init__(
        self, bank_api_provider: any, location: str = "somewhere", rot_number: int = 0
    ) -> None:
        self._bank_api = bank_api_provider
        self.location = location
        self.rot_number = rot_number
        self.phase = None
        self._card_id = None
        self._card_password = None
        self._selected_account_id = None
        self._account_list = []
        self._status = None

    def _update_status(self, status: ATM_STATUS):
        self._status = status.value

    def start(self):
        self._update_status(ATM_STATUS.WAIT_FOR_CARD)

    def insert_card(self, card_id: str = "0000"):
        self._card_id = card_id
        self._update_status(ATM_STATUS.CARD_INSERTED)

    def insert_card_pin_number(self, pin: int):
        self._card_password = pin
        self._update_status(ATM_STATUS.WAIT_FOR_API_RES)
        return self._request_card_password_validation()

    def _request_card_password_validation(self):
        self._bank_api.request_card_validation(self._card_id, self._card_password)
        self._update_status(ATM_STATUS.CARD_PASSWORD_VALIDATED)
        return True

    def get_account_list(self):
        return self._request_account_list()

    def _request_account_list(self):
        self._account_list = self._bank_api.request_account_list(
            self._card_id, self._card_password
        )["accounts"]
        self._update_status(ATM_STATUS.ACCOUNT_LISTED)

    def select_account(self, account_id: str):
        self._selected_account_id = account_id
        self._update_status(ATM_STATUS.ACCOUNT_SELECTED)
        return True

    def _request_balance(self):
        return self._bank_api.request_get_balance(self._selected_account_id)

    def _req_withdraw(self, money: int):
        return self._bank_api.request_withdraw(self._selected_account_id, money)

    def _req_deposit(self, money: int):
        return self._bank_api.request_deposit(self._selected_account_id, money)

    def get_balance(self):
        self._update_status(ATM_STATUS.WAIT_FOR_API_RES)
        balance = self._request_balance()
        self._update_status(ATM_STATUS.BALANCE_SHOWED)
        return balance

    def withdraw(self, money: int):
        self._update_status(ATM_STATUS.WAIT_FOR_API_RES)
        is_sucess = self._req_withdraw(money)
        self._update_status(ATM_STATUS.WITHDRAW_DONE)
        return is_sucess

    def deposit(self, money: int):
        self._update_status(ATM_STATUS.WAIT_FOR_API_RES)
        is_sucess = self._req_deposit(money)
        self._update_status(ATM_STATUS.WITHDRAW_DONE)
        return is_sucess
