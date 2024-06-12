import json
from abc import ABC, abstractmethod
from datetime import datetime, timezone

class ContasIterador:
    def __init__(self, accounts):
        self.accounts = accounts
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        try:
            account = self.accounts[self._index]
            return f"""
            Agência: {account.agencia}
            Número: {account.number}
            Titular: {account.client.name}
            Saldo: R$ {account.saldo:.2f}
        """
        except IndexError:
            raise StopIteration
        finally:
            self._index += 1


class Client:
    def __init__(self, adress):        
        self.adress = adress
        self.accounts = []
        self.account_indice = 0
    
    def transacao(self, account, transacao):
        return transacao.registrar(account)

    def add_account(self, account):
        self.accounts.append(account)

class PessoaFisica(Client):
    def __init__(self, name, birthday, cpf, adress):
        super().__init__(adress)
        self.name = name
        self.birthday = birthday
        self.cpf = cpf

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: ('{self.name}', '{self.cpf}')>"

class Account(ABC):
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
            return False
        
        elif value > 0:
            self._saldo -= value
            return True

        else:
            print("Operação falhou! O valor informado é inválido.")
            return False
    
    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            return True
        else:
            print("Operação falhou! O valor informado é inválido.")
            return False
    
class ContaCorrente(Account):
    def __init__(self, number, client, limit=500, saque_limit=3):
        super().__init__(number, client)
        self.limit = limit
        self.saque_limit = saque_limit
    
    def sacar(self, value):
        saque_number = len([transacao for transacao in self.history.transacoes if transacao["tipo"] == Saque.__name__])
        
        excedeu_limite = value > self.limit
        excedeu_saques = saque_number >= self.saque_limit

        if excedeu_limite:
            print("Operação falhou! O valor do saque excede o limite.")
            return False

        elif excedeu_saques:
            print("Operação falhou! Número máximo de saques excedido.")
            return False

        return super().sacar(value)
    
    def __str__(self):
        return f"""
        Agência: {self.agencia}
        C/C: {self.number}
        Titular: {self.client.name}
        """
    
    def __repr__(self):
        return f"<{self.__class__.__name__}: ('{self.agencia}', '{self.number}', '{self.client.name}')>"
 
class History:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def add_transacao(self, transacao):        
        hoje = datetime.now().strftime("%d-%m-%Y")
        transacoes_hoje = [t for t in self._transacoes if t["data"].startswith(hoje)]
        
        if len(transacoes_hoje) >= 10:
            print("Operação falhou! Número máximo de transações diárias excedido.")
            return False
        
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.value,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )
        return True

    def gerar_relatorio(self, tipo_transacao=None):
        for transacao in self._transacoes:
            if tipo_transacao is None or transacao["tipo"].lower() == tipo_transacao.lower():
                yield transacao

class Transacao(ABC):
    @property    
    @abstractmethod
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
            return account.history.add_transacao(self)
        return False

class Deposito(Transacao):
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    def registrar(self, account):
        sucesso_transacao = account.depositar(self.value)

        if sucesso_transacao:
            return account.history.add_transacao(self)
        return False

def log_transacao(func):
    def envelope(*args, **kwargs):
        resultado = func(*args, **kwargs)
        print(f"{datetime.now()}: {func.__name__.upper()}")
        return resultado

    return envelope


def menu():
    menu = """
⥢-----------------------------------------⥤
    
    Selecione a opção desejada:

    [1] Depositar       [4] Nova Conta
    [2] Sacar           [5] Listar Contas
    [3] Extrato         [6] Novo Usuário

    [0] Sair

⥢-----------------------------------------⥤
    => """
    return input(menu)

def filter_user(cpf, users):
    usuarios_filtrados = [user for user in users if user.cpf == cpf]
    return usuarios_filtrados[0] if usuarios_filtrados else None

def recover_user_account(user):
    if not user.accounts:
        print("Cliente não possui conta! Crie uma conta para ter acesso!")
        return None
    
    return user.accounts[0]

def verificarValor(valor):
    try:
        valor_float = float(valor)
        if valor_float > 0:
            return valor_float
        else:
            raise ValueError            
    except ValueError:
        print("Operação falhou! O valor informado é inválido.")
        return None

@log_transacao
def depositar(users):
    cpf = input("Informe o CPF do cliente: ")
    user = filter_user(cpf, users)

    if not user:
        print("Usuário não encontrado, registre-se primeiro!")
        return
    
    valor = verificarValor(input("Informe o valor do depósito: "))
    if valor is None:
        return

    transacao = Deposito(valor)
    conta = recover_user_account(user)
    if not conta:
        return

    if user.transacao(conta, transacao):
        print("⥢--- Depósito realizado com sucesso! ---⥤")

@log_transacao
def sacar(users):
    cpf = input("Informe o CPF do cliente: ")
    user = filter_user(cpf, users)

    if not user:
        print("Usuário não encontrado, registre-se primeiro!")
        return
    
    valor = verificarValor(input("Informe o valor do saque: "))
    if valor is None:
        return

    transacao = Saque(valor)
    conta = recover_user_account(user)
    if not conta:
        return

    if user.transacao(conta, transacao):
        print("⥢--- Saque realizado com sucesso! ---⥤")

@log_transacao
def exibir_extrato(clients):
    cpf = input("Informe o CPF do cliente: ")
    user = filter_user(cpf, clients)

    if not user:
        print("Usuário não encontrado, registre-se primeiro!")
        return

    conta = recover_user_account(user)
    if not conta:
        return

    extrato = ""
    transacoes = conta.history.transacoes

    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"{transacao['data']} - {transacao['tipo']}: R$ {transacao['valor']:.2f}\n"
    
    print(f"""                  
⥢============== EXTRATO ===============⥤
          
{extrato}

Saldo: R$ {conta.saldo:.2f}
⥢======================================⥤
""")

@log_transacao
def create_user(users):
    cpf = input("Informe o CPF (somente número): ")
    user = filter_user(cpf, users)

    if user:
        print("Esse usuário já está registrado!")
        return

    name = input("Informe o nome completo: ")
    birthday = input("Informe a data de nascimento (dd-mm-aaaa): ")
    adress = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    user = PessoaFisica(name=name, birthday=birthday, cpf=cpf, adress=adress)
    users.append(user)

    print("⥢--- Usuário criado com sucesso! ---⥤")

def save_data(clientes, contas, filepath='data.json'):
    data = {
        'clientes': [
            {
                'name': cliente.name,
                'birthday': cliente.birthday,
                'cpf': cliente.cpf,
                'adress': cliente.adress,
                'accounts': [
                    {
                        'number': conta.number,
                        'agencia': conta.agencia,
                        'saldo': conta.saldo,
                        'history': conta.history.transacoes,
                    }
                    for conta in cliente.accounts
                ]
            }
            for cliente in clientes
        ]
    }

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def load_data(filepath='data.json'):
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        clientes = []
        contas = []
        for cliente_data in data['clientes']:
            cliente = PessoaFisica(
                name=cliente_data['name'],
                birthday=cliente_data['birthday'],
                cpf=cliente_data['cpf'],
                adress=cliente_data['adress']
            )
            clientes.append(cliente)

            for conta_data in cliente_data['accounts']:
                conta = ContaCorrente(
                    number=conta_data['number'],
                    client=cliente
                )
                conta._saldo = conta_data['saldo']
                conta._history._transacoes = conta_data['history']
                cliente.accounts.append(conta)
                contas.append(conta)

        return clientes, contas
    except FileNotFoundError:
        return [], []

@log_transacao
def criar_conta(number_account, users, accounts):
    cpf = input("Informe o CPF do cliente: ")
    user = filter_user(cpf, users)

    if not user:
        print("Usuário não encontrado, registre-se primeiro!")
        return

    account = ContaCorrente.new_account(client=user, number=number_account)
    accounts.append(account)
    user.accounts.append(account)

    print("⥢--- Conta criada com sucesso! ---⥤")

def listar_contas(contas):
    for conta in contas:
        print(" •"+ ("-=" * 19) + "-• ")
        print(str(conta))

def main():
    clientes, contas = load_data()

    while True:
        opcao = menu()
        match opcao:
            case "1":
                depositar(clientes)        
            case "2":        
                sacar(clientes)
            case "3": 
                exibir_extrato(clientes)            
            case "4":         
                number_account = len(contas) + 1                
                criar_conta(number_account, clientes, contas)            
            case "5":         
                listar_contas(contas)
            case "6": 
                create_user(clientes)
            case "0":         
                print("Operação finalizada!")
                save_data(clientes, contas)
                break
            case _:
                print("Operação inválida, por favor selecione uma opção!")

main()
