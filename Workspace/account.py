"""A tiny double-entry-ish bank account."""


class InsufficientFunds(Exception):
    pass


class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance
        self.history = []

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.balance += amount
        self.history.append(("deposit", amount))

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount > self.balance:
            raise InsufficientFunds("insufficient funds")
        self.balance -= amount
        self.history.append(("withdraw", amount))

    def transfer(self, other, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.withdraw(amount)
        other.deposit(amount)
        self.history.append(("transfer", amount, other.owner))
        other.history.append(("received", amount, self.owner))
