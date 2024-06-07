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

def depositar(saldo, valor, extrato, /):
    valor = verificarValor(valor)
    if valor is not None:
        saldo += valor
        extrato += f"   Depósito: R$ {valor:.2f}\n"
        print("⥢--- Depósito realizado com sucesso! ---⥤")
    return saldo, extrato

def sacar(*, saldo, valor, extrato, limite, numero_saques, limite_saques):
    valor = verificarValor(valor)
    if valor is not None:
        excedeu_saldo = valor > saldo
        excedeu_limite = valor > limite
        excedeu_saques = numero_saques >= limite_saques    

        if excedeu_saldo:
            print("Operação falhou! Você não tem saldo suficiente.")
        elif excedeu_limite:
            print("Operação falhou! O valor do saque excede o limite.")
        elif excedeu_saques:
            print("Operação falhou! Número máximo de saques excedido.")
        else:
            saldo -= valor
            extrato += f"   Saque: R$ {valor:.2f}\n"
            numero_saques += 1
            print("⥢--- Saque realizado com sucesso! ---⥤")        
    return saldo, extrato

def exibir_extrato(saldo, /, *, extrato):
    print(f"""                  
⥢============== EXTRATO ===============⥤
                  
{"Não foram realizadas movimentações.\n" if not extrato else extrato}
   Saldo: R$ {saldo:.2f}

⥢======================================⥤
    """)   

def create_user(user):
    cpf = input("Informe o CPF (somente número): ")
    usuario = filter_user(cpf, user)

    if usuario:
        print("Esse usuário já está registrado!")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    user.append({"nome": nome, "data_nascimento": data_nascimento, "cpf": cpf, "endereco": endereco})

    print("⥢--- Usuário criado com sucesso! ---⥤")


def filter_user(cpf, users):
    usuarios_filtrados = [user for user in users if user["cpf"] == cpf]
    return usuarios_filtrados[0] if usuarios_filtrados else None


def criar_conta(agencia, numero_conta, usuarios):
    cpf = input("Informe o CPF do usuário: ")
    usuario = filter_user(cpf, usuarios)

    if usuario:
        print("⥢--- Conta criada com sucesso! ---⥤")
        return {"agencia": agencia, "numero_conta": numero_conta, "usuario": usuario}

    print("Usuário não encontrado, registre-se primeiro!")


def listar_contas(contas):
    for conta in contas:
        lista = f"""

            Agência: {conta['agencia']}
            C/C: {conta['numero_conta']}
            Titular: {conta['usuario']['nome']}

        """
        print(" •"+ ("-=" * 19) + "-• ")
        print(lista)

def main():

    saldo = 0
    limite = 500
    extrato = ""
    numero_saques = 0
    LIMITE_SAQUES = 3
    AGENCIA= "0001"
    users = []
    contas = []

    while True:
        opcao = menu()

        match opcao:
            case "1":
                valor = input("Informe o valor do depósito: ")
                saldo, extrato = depositar(saldo, valor, extrato)
            
            case "2":
                valor = input("Informe o valor do saque: ")
                saldo, extrato = sacar(
                    saldo=saldo,
                    valor=valor,
                    extrato=extrato,
                    limite=limite,
                    numero_saques=numero_saques,
                    limite_saques=LIMITE_SAQUES,
                )               

            case "3":
                exibir_extrato(saldo, extrato=extrato)
            
            case "4":
                numero_conta = len(contas) + 1
                conta = criar_conta(AGENCIA, numero_conta, users)
                if conta:
                    contas.append(conta)

            case "5":
                listar_contas(contas)
                
            case "6":
                create_user(users)

            case "0":
                print("Operação finalizada!")
                break

            case _:
                print("Operação inválida, por favor selecione uma opção!")

main()