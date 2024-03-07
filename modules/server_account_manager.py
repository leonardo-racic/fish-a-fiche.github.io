# The first import module is only to guarantee a secure variable typing.
from __future__ import annotations
from account_module import Account
from json import loads as load_json, dumps as to_json
from flask import request
from terminal_log import inform
import hashlib


def get_hash(this_text: str) -> str:
    return hashlib.sha256(this_text.encode()).hexdigest()


def read_accounts_json() -> dict:
    with open("accounts.json", "r") as f:
        try:
            accounts_json: dict = load_json(f.read())["accounts"]
            accounts_dict: dict = {}
            for token, account_info in accounts_json.items():
                new_account: Account = Account(
                    account_info["username"],
                    account_info["password"],
                    account_info["profile_picture"],
                    account_info["description"],
                    token,
                )
                accounts_dict[token] = new_account
            return accounts_dict
        except Exception:
            with open("accounts.json", "w") as f:
                f.write("{\n    \"accounts\":{}\n}")
            return []
        
    


class ServerAccountManager:
    def __init__(self) -> None:
        self.accounts: dict = read_accounts_json()


    def get_all_accounts(self) -> list[Account]:
        return list(self.get_accounts_dict().values())
    

    def get_all_account_info(self) -> list[dict]:
        accounts: list[Account] = self.get_all_accounts()
        return [account.get_info() for account in accounts]


    def create_account(self, input_username: str, input_password: str, description: str = "", profile_picture: str = "") -> Account:
        new_account: Account = Account(input_username, get_hash(input_password), profile_picture, description)
        inform(f"{new_account} is being created")
        with open("accounts.json", "r") as f:
            json_data: dict = load_json(f.read())
        json_data["accounts"][new_account.get_id()] = new_account.get_info()
        with open("accounts.json", "w") as f:
            f.write(to_json(json_data, indent=4))
        self.accounts = read_accounts_json()
        inform(f"Account with id {new_account.get_id()} created successfully.")
        return new_account


    def get_account_by_token(self, token: str) -> Account:
        return self.get_accounts_dict().get(token, None)
    

    def delete_account(self, account: Account) -> None:
        self.get_accounts_dict().pop(account.get_id())
        with open("accounts.json", "r") as f:
            json_data: dict = load_json(f.read())["accounts"]
        json_data.pop(account.get_id())
        with open("accounts.json", "w") as f:
            f.write(to_json(json_data, indent=4))
        self.accounts = read_accounts_json()


    def get_accounts_dict(self) -> dict:
        self.accounts = read_accounts_json()
        return self.accounts
    

    def has_account(self, specific_account: Account) -> bool:
        r: bool = specific_account in self.get_all_accounts()
        return r
    

    def has_account_username(self, current_username: str) -> bool:
        for account_info in self.get_all_account_info():
            if account_info["username"] == current_username:
                return True
        return False
    

    def get_account_by_username(self, username: str) -> Account:
        for account_info in self.get_all_account_info():
            if account_info["username"] == username:
                return Account(
                    account_info["username"],
                    account_info["password"],
                    account_info["profile_picture"],
                    account_info["description"],
                    account_info["id"],
                )
        return None
    

    def get_account_info_by_username(self, username: str) -> dict:
        target_account: Account = self.get_account_by_username(username)
        if target_account is None:
            return {}
        return target_account.get_info()


    def is_login_valid(self, username: str, password: str) -> tuple[bool, bool, bool]:
        is_input_valid: bool = username != "" and password != ""
        if not is_input_valid:
            return (False, False, False)
         
        target_account: Account = self.get_account_by_username(username)
        account_exists: bool = target_account is not None
        password_hash: str = get_hash(password)
        password_correct: bool = target_account.check_password(password_hash) if account_exists else False
        return (is_input_valid, account_exists, password_correct)


    def is_sign_up_input_valid(self, username: str, password: str) -> bool:
        if not self.is_username_valid(username):
            return False
        elif password == "":
            return False
        return True
    

    def get_user_account_info(self) -> dict:
        user_account: Account = self.get_user_account()
        if user_account is None:
            return {}
        return user_account.get_info()


    def get_user_account(self) -> Account:
        account_token: str = request.cookies.get("account-token", "x")
        user_account: Account = self.get_account_by_token(account_token)
        return user_account
    

    def is_user_logged_in(self) -> bool:
        account_info: dict = self.get_user_account_info()
        return account_info != {}


    def is_username_valid(self, username: str, check_if_username_exists: bool = False) -> bool:
        if username == "":
            return False
        elif "/" in username:
            return False
        elif self.has_account_username(username) and check_if_username_exists:
            return False
        return True
    
    
    def modify_profile(self, new_image_input: str, description_input: str, username_input: str) -> None:
        account_info: dict = self.get_user_account_info()
        if account_info != {}:
            with open("accounts.json") as f:
                data: dict = load_json(f.read())["accounts"]
            for current_account_info in data.values():
                if current_account_info["username"] == account_info["username"]:
                    current_account_info["profile_picture"] = new_image_input
                    current_account_info["description"] = description_input
                    current_account_info["username"] = username_input
                    break
            with open("accounts.json", "w") as f:
                f.write(to_json({"accounts": data}, indent=4))
            self.accounts = read_accounts_json()



if __name__ == "__main__":
    s: ServerAccountManager = ServerAccountManager()
    s.create_account("User2332", "€uehfiuzhefoizef")
    