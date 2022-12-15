import pytest
import uuid
from bank.fake_bank import FakeBankAPI
from atm.core.atm import ATM, ATM_STATUS
from atm.provider.bank_provider import BankAPIProvider, APIRequestFaildError

[card1_key, card2_key, account1_key] = key_list = [str(uuid.uuid1()) for i in range(3)]


@pytest.fixture
def atm():
    test_bank_api = FakeBankAPI()

    test_bank_api.card_data = {
        card1_key: {"name": "card1", "password": 1234},
        card2_key: {"name": "card2", "password": 4567},
    }
    account1_key = test_bank_api._generate_unique_key()
    test_bank_api.account_data = {
        account1_key: {
            "client_name": "tester1",
            "account_name": "account1",
            "linked_card": card1_key,
            "balance": 0,
        }
    }
    test_bank_api.deposit(account1_key, 1000)
    return ATM(bank_api_provider=BankAPIProvider(test_bank_api))


def test_atm_start(atm):
    atm.start()
    assert atm._status == ATM_STATUS.WAIT_FOR_CARD.value


def test_atm_insert_card(atm):
    atm.insert_card(card1_key)
    assert atm._status == ATM_STATUS.CARD_INSERTED.value
    return atm


def test_atm_insert_card_pin_number(atm):
    atm = test_atm_insert_card(atm)
    atm.insert_card_pin_number(1234)
    assert atm._status == ATM_STATUS.CARD_PASSWORD_VALIDATED.value
    return atm


def test_atm_insert_invalid_card_pin_number(atm):
    atm = test_atm_insert_card(atm)
    with pytest.raises(APIRequestFaildError):
        atm.insert_card_pin_number(4567)


def test_atm_insert_card_pin_with_invalid_pin(atm):
    atm = test_atm_insert_card_pin_number(atm)
    assert atm._status == ATM_STATUS.CARD_PASSWORD_VALIDATED.value
    return atm


def test_atm_get_account(atm):
    atm = test_atm_insert_card_pin_number(atm)
    assert atm._status == ATM_STATUS.CARD_PASSWORD_VALIDATED.value
    atm.get_account_list()
    assert len(atm._account_list) == 1
    assert atm._status == ATM_STATUS.ACCOUNT_LISTED.value
    return atm


def test_atm_select_account(atm):
    atm = test_atm_get_account(atm)
    atm.select_account(atm._account_list[0]["account_number"])
    atm._status == ATM_STATUS.ACCOUNT_SELECTED.value
    return atm


def test_atm_get_balance(atm):
    atm = test_atm_select_account(atm)
    assert 1000 == atm.get_balance()


def test_atm_deposit(atm):
    atm = test_atm_select_account(atm)
    assert 1000 == atm.get_balance()
    atm.deposit(1000)
    assert 2000 == atm.get_balance()


def test_atm_withdraw(atm):
    atm = test_atm_select_account(atm)
    atm.withdraw(1000)
    assert 0 == atm.get_balance()


def test_atm_withdraw_more_than_balance(atm):
    atm = test_atm_select_account(atm)
    with pytest.raises(APIRequestFaildError):
        atm.withdraw(2000)
