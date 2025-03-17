import functions1

functions1.criar_tabela()

while True:
    print("\n=== Gerenciador de Senhas ===")
    print("1 - Ver senhas salvas")
    print("2 - Adicionar ou editar login")
    print("3 - Remover um login específico")
    print("4 - Verificar força da senha")
    print("5 - Sair")

    opcao = input("Escolha uma opção: ")

    if opcao == "1":
        usuarios = functions1.listar_usuarios()
        if usuarios:
            print("\n=== Logins Salvos ===")
            for login, senha in usuarios:
                print(f" Login: {login} |  Senha: {senha}")
        else:
            print("\n Nenhum login salvo.")

    elif opcao == "2":
        login = input("\nDigite o login: ")

        while True:
            lenpass = input("Digite o tamanho da senha: ")
            if lenpass.isdigit():
                lenpass = int(lenpass)
                break
            else:
                print("Erro: Digite um número inteiro válido!")

        usuario = functions1.buscar_usuario(login)

        if usuario:
            nova_senha = functions1.gerar_senha(lenpass)
            functions1.atualizar_senha(login, nova_senha)
            print(f' Login: {login} e nova senha: {nova_senha} atualizados no banco de dados.')
        else:
            nova_senha = functions1.gerar_senha(lenpass)
            functions1.inserir_usuario(login, nova_senha)
            print(f' Login: {login} e senha: {nova_senha} salvos no banco de dados.')

    elif opcao == "3":
        logins = functions1.listar_logins()
        
        if logins: 
            print("\n=== Logins Salvos ===")
            for i, login in enumerate(logins, start=1):
                print(f"{i}. {login}")
        else:
            print("Nenhum login salvo!")
            continue
        
        try:
            escolha = int(input("\nDigite o número do login que deseja remover: ")) - 1
            if 0 <= escolha < len(logins):
                login = logins[escolha]
                confirmacao = input(f"Tem certeza que deseja remover o login '{login}'? (s/n): ").strip().lower()
                if confirmacao == "s":
                    functions1.remover_login_especifico(login)
                    print(f"O login '{login}' foi removido com sucesso!")
                else:
                    print("\nOperação cancelada.")
            else:
                print("\nNúmero inválido!")
        except ValueError:
            print("\nEntrada inválida! Digite um número.")

    elif opcao == "4":
        logins = functions1.listar_logins()

        if logins:
            print("\n=== Logins Salvos ===")
            for i, login in enumerate(logins, start=1): 
                    print(f"{i}. {login}")

        try: 
            escolha = int(input("\nDigite o número do login para testar a senha: ")) - 1
            
            if 0 <= escolha < len(logins):
                login = logins[escolha]
                usuario = functions1.buscar_usuario(login) 
                
                if usuario:  
                    senha = usuario[2]
                    forca = functions1.check_password_strength(senha)
                    print(f"A senha do login '{login}' é {forca}")
                else:
                    print("\nUsuário não encontrado!")

            else:
                print("\nNúmero inválido! Escolha um número da lista.")

        except ValueError:
            print("\nEntrada inválida! Digite um número.")

        
        #if usuario:
        #    senha = usuario[2]
        #    forca = functions1.check_password_strength(senha)
        #   print(f"A senha do login '{login}' é {forca}")
        #else:
        #    print("Login não encontrado.")
    
    elif opcao == "5":
        print("Exit")
        break

    else:
        print("Opção inválida! Escolha entre 1, 2, 3, 4 ou 5.")
