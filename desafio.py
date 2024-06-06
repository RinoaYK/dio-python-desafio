menu = """
⥢--------------------------------⥤
    
    Selecione a opção desejada:

    [1] Depositar
    [2] Sacar
    [3] Extrato
    [0] Sair

⥢--------------------------------⥤
=> """

saldo = 0
limite = 500
extrato = ""
numero_saques = 0
LIMITE_SAQUES = 3

while True:
    opcao = input(menu)

    match opcao:
        case "1":
            valor = input("Informe o valor do depósito: ")
            try:
                valor = float(valor)
                if valor > 0:
                    saldo += valor
                    extrato += f"Depósito: R$ {valor:.2f}\n"
                else:
                    raise ValueError
            except ValueError:
                print("Operação falhou! O valor informado é inválido.")

        case "2":
            valor = input("Informe o valor do saque: ")
            try:
                valor = float(valor)

                excedeu_saldo = valor > saldo
                excedeu_limite = valor > limite
                excedeu_saques = numero_saques >= LIMITE_SAQUES

                if excedeu_saldo:
                    print("Operação falhou! Você não tem saldo suficiente.")
                elif excedeu_limite:
                    print("Operação falhou! O valor do saque excede o limite.")
                elif excedeu_saques:
                    print("Operação falhou! Número máximo de saques excedido.")
                elif valor > 0:
                    saldo -= valor
                    extrato += f"Saque: R$ {valor:.2f}\n"
                    numero_saques += 1
                else:
                    raise ValueError
            except ValueError:
                print("Operação falhou! O valor informado é inválido.")

        case "3":
            print(f"""                  
⥢============== EXTRATO ===============⥤
                  
{"Não foram realizadas movimentações.\n" if not extrato else extrato}
Saldo: R$ {saldo:.2f}

⥢======================================⥤
            """)            

        case "0":
            print("Operação finalizada!")
            break

        case _:
            print("Operação inválida, por favor selecione uma opção!")
