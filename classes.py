from abc import ABC, abstractmethod
from datetime import datetime

class Client:
    def __init__(self, adress):        
        self.adress = adress
        self.accounts = []
    
    def transacao(self, account, transacao):
        transacao.registrar(account)

    def add_account(self, account):
        self.accounts.append(account)

class PessoaFisica(Client):
    def __init__(self, name, birthday, cpf, adress):
        super().__init__(adress)
        self.name = name
        self.birthday = birthday
        self.cpf = cpf

class Account:
    def __init__(self, number, client):
        self._saldo = 0
        self._number = number
        self._agencia = '0001'
        self._client = client
        self._history = History()
    
    @classmethod
    def new_account(cls, client, number):
        return cls(number, client)
    
    @property
    def saldo(self):
        return self._saldo
    
    @property
    def number(self):
        return self._number
    
    @property
    def agencia(self):
        return self._agencia

    @property
    def client(self):
        return self._client
    
    @property
    def history(self):
        return self._history
    
    def sacar(self, value):
        saldo = self.saldo
        excedeu_saldo = value > saldo    

        if excedeu_saldo:
            print("Operação falhou! Você não tem saldo suficiente.")
        
        elif value > 0:
            self._saldo -= value
            print("⥢--- Saque realizado com sucesso! ---⥤")
            return True

        else:
            print("Operação falhou! O valor informado é inválido.")

        return False
    
    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("⥢--- Depósito realizado com sucesso! ---⥤")
        else:
            print("Operação falhou! O valor informado é inválido.")
            return False

        return True
    
class ContaCorrente(Account):
    def __init__(self, number, client, limit=500, saque_limit=3):
        super().__init__(number, client)
        self.limit = limit
        self.saque_limit = saque_limit
    
    def sacar(self, value):
        saque_number = len( [transacao for transacao in self.history.transacoes if transacao["tipo"] == Saque.__name__])
        
        excedeu_limite = value > self.limit
        excedeu_saques = saque_number >= self.saque_limit

        if excedeu_limite:
            print("Operação falhou! O valor do saque excede o limite.")

        elif excedeu_saques:
            print("Operação falhou! Número máximo de saques excedido.")

        else:
            return super().sacar(value)

        return False
    
    def __str__(self):
        return f"""
            Agência: {self.agencia}
            C/C: {self.number}
            Titular: {self.client.name}
        """
    
class History:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def add_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.value,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%s"),
            }
        )

class Transacao(ABC):
    @property    
    def value(self):
        pass

    @abstractmethod
    def registrar(self, account):
        pass

class Saque(Transacao):
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    def registrar(self, account):
        sucesso_transacao = account.sacar(self.value)

        if sucesso_transacao:
            account.history.add_transacao(self)

class Deposito(Transacao):
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    def registrar(self, account):
        sucesso_transacao = account.depositar(self.value)

        if sucesso_transacao:
            account.history.add_transacao(self)