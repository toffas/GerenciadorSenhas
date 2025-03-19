import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import re
import random
from cryptography.fernet import Fernet

#NÃO A NECESSIDADE DO CODIGO "functions1.py" para rodar esse codigo, somente precisa instalar o "tkinter"!

def carregar_ou_gerar_chave():
    try:
        with open("secret.key", "rb") as key_file:
            key = key_file.read()
    except FileNotFoundError:
        key = Fernet.generate_key()
        with open("secret.key", "wb") as key_file:
            key_file.write(key)
    return key

key = carregar_ou_gerar_chave()
fernet = Fernet(key)

def criptografar_senha(senha):
    return fernet.encrypt(senha.encode()).decode()

def descriptografar_senha(senha_criptografada):
    return fernet.decrypt(senha_criptografada.encode()).decode()

def criar_tabela():
    conexao = sqlite3.connect("logins.db")
    cursor = conexao.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    
    conexao.commit()
    conexao.close()

def buscar_usuario(login):
    conexao = sqlite3.connect("logins.db")
    cursor = conexao.cursor()
    
    cursor.execute("SELECT * FROM usuarios WHERE login = ?", (login,))
    usuario = cursor.fetchone()
    
    conexao.close()
    if usuario:
        return (usuario[0], usuario[1], descriptografar_senha(usuario[2]))
    return None

def atualizar_senha(login, nova_senha):
    conexao = sqlite3.connect("logins.db")
    cursor = conexao.cursor()
    
    nova_senha_criptografada = criptografar_senha(nova_senha)
    cursor.execute("UPDATE usuarios SET password = ? WHERE login = ?", (nova_senha_criptografada, login))
    
    conexao.commit()
    conexao.close()

def inserir_usuario(login, senha):
    conexao = sqlite3.connect("logins.db")
    cursor = conexao.cursor()
    
    senha_criptografada = criptografar_senha(senha)
    cursor.execute("INSERT INTO usuarios (login, password) VALUES (?, ?)", (login, senha_criptografada))
    
    conexao.commit()
    conexao.close()

def listar_usuarios():
    conexao = sqlite3.connect("logins.db")
    cursor = conexao.cursor()
    
    cursor.execute("SELECT login, password FROM usuarios")
    usuarios = cursor.fetchall()
    
    conexao.close()
    return [(login, descriptografar_senha(senha)) for login, senha in usuarios]

def remover_login_especifico(login):
    conexao = sqlite3.connect("logins.db")
    cursor = conexao.cursor()
    
    cursor.execute("DELETE FROM usuarios WHERE login = ?", (login,))
    
    conexao.commit()
    conexao.close()

def listar_logins():
    conexao = sqlite3.connect("logins.db")
    cursor = conexao.cursor()
    
    cursor.execute("SELECT login FROM usuarios")
    logins = cursor.fetchall()
    
    conexao.close()
    return [login[0] for login in logins]

def gerar_senha(lenpass):
    caracteres = "AabBCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz1234567890!#$%&'()*+,-./:;<=>?@[]^_`{|}~"
    return "".join(random.choice(caracteres) for _ in range(lenpass))

def check_password_strength(password):
    min_password_length = 8
    base_score = 0
    score = 0

    num = {
        "Excess": 0,
        "Upper": 0,
        "Numbers": 0,
        "Symbols": 0
    }

    bonus = {
        "Excess": 3,
        "Upper": 4,
        "Numbers": 5,
        "Symbols": 5,
        "Combo": 0,
        "FlatLower": 0,
        "FlatNumber": 0
    }

    if len(password) >= min_password_length:
        base_score = 50
        
        for char in password:
            if char.isupper():
                num["Upper"] += 1
            elif char.isdigit():
                num["Numbers"] += 1
            elif re.match(r"[!@#$%^&*?_~]", char):
                num["Symbols"] += 1
        
        num["Excess"] = len(password) - min_password_length

        if num["Upper"] and num["Numbers"] and num["Symbols"]:
            bonus["Combo"] = 25
        elif (num["Upper"] and num["Numbers"]) or (num["Upper"] and num["Symbols"]) or (num["Numbers"] and num["Symbols"]):
            bonus["Combo"] = 15

        if re.match(r"^[a-z]+$", password):
            bonus["FlatLower"] = -15

        if re.match(r"^[0-9]+$", password):
            bonus["FlatNumber"] = -35

        score = (base_score + (num["Excess"] * bonus["Excess"]) +
                 (num["Upper"] * bonus["Upper"]) + (num["Numbers"] * bonus["Numbers"]) +
                 (num["Symbols"] * bonus["Symbols"]) + bonus["Combo"] +
                 bonus["FlatLower"] + bonus["FlatNumber"])
    
    return evaluate_strength(score)

def evaluate_strength(score):
    if score == 0:
        return "Digite a Senha"
    elif score < 50:
        return "fraca!"
    elif 50 <= score < 75:
        return "média!"
    elif 75 <= score < 100:
        return "forte!"
    else: 
        return "segura!"

def adicionar_atualizar_login():
    login = entry_login.get()
    tamanho_senha = entry_tamanho_senha.get()

    if not tamanho_senha.isdigit():
        messagebox.showerror("Erro", "O tamanho da senha deve ser um número inteiro!")
        return

    tamanho_senha = int(tamanho_senha)
    nova_senha = gerar_senha(tamanho_senha)

    usuario = buscar_usuario(login)
    if usuario:
        atualizar_senha(login, nova_senha)
        messagebox.showinfo("Sucesso", f"Login: {login} e nova senha: {nova_senha} atualizados no banco de dados.")
    else:
        inserir_usuario(login, nova_senha)
        messagebox.showinfo("Sucesso", f"Login: {login} e senha: {nova_senha} salvos no banco de dados.")

def remover_login():
    login = entry_login_remover.get()

    if not login:
        messagebox.showerror("Erro", "Digite um login para remover!")
        return

    remover_login_especifico(login)
    messagebox.showinfo("Sucesso", f"Login: {login} removido com sucesso.")

def listar_logins_interface():
    logins = listar_usuarios()
    if logins:
        lista_logins = "\n".join([f"Login: {login} | Senha: {senha}" for login, senha in logins])
        messagebox.showinfo("Logins Salvos", lista_logins)
    else:
        messagebox.showinfo("Logins Salvos", "Nenhum login salvo.")

def verificar_forca_senha():
    senha = entry_senha_verificar.get()
    forca = check_password_strength(senha)
    messagebox.showinfo("Força da Senha", f"A senha é {forca}")

root = tk.Tk()
root.title("Gerenciador de Logins")
root.geometry("400x500")

frame_principal = ttk.Frame(root)
frame_principal.pack(expand=True, fill="both", padx=20, pady=20)

frame_adicionar = ttk.LabelFrame(frame_principal, text="Adicionar/Atualizar Login")
frame_adicionar.pack(pady=10, fill="x")

label_login = ttk.Label(frame_adicionar, text="Login:")
label_login.grid(row=0, column=0, padx=5, pady=5)

entry_login = ttk.Entry(frame_adicionar)
entry_login.grid(row=0, column=1, padx=5, pady=5)

label_tamanho_senha = ttk.Label(frame_adicionar, text="Tamanho da Senha:")
label_tamanho_senha.grid(row=1, column=0, padx=5, pady=5)

entry_tamanho_senha = ttk.Entry(frame_adicionar)
entry_tamanho_senha.grid(row=1, column=1, padx=5, pady=5)

botao_adicionar = ttk.Button(frame_adicionar, text="Adicionar/Atualizar", command=adicionar_atualizar_login)
botao_adicionar.grid(row=2, column=0, columnspan=2, pady=10)

frame_remover = ttk.LabelFrame(frame_principal, text="Remover Login")
frame_remover.pack(pady=10, fill="x")

label_login_remover = ttk.Label(frame_remover, text="Login:")
label_login_remover.grid(row=0, column=0, padx=5, pady=5)

entry_login_remover = ttk.Entry(frame_remover)
entry_login_remover.grid(row=0, column=1, padx=5, pady=5)

botao_remover = ttk.Button(frame_remover, text="Remover", command=remover_login)
botao_remover.grid(row=1, column=0, columnspan=2, pady=10)


frame_listar = ttk.LabelFrame(frame_principal, text="Listar Logins")
frame_listar.pack(pady=10, fill="x")

botao_listar = ttk.Button(frame_listar, text="Listar Logins Salvos", command=listar_logins_interface)
botao_listar.pack(pady=10)


frame_verificar = ttk.LabelFrame(frame_principal, text="Verificar Força da Senha")
frame_verificar.pack(pady=10, fill="x")

label_senha_verificar = ttk.Label(frame_verificar, text="Senha:")
label_senha_verificar.grid(row=0, column=0, padx=5, pady=5)

entry_senha_verificar = ttk.Entry(frame_verificar, show="*")
entry_senha_verificar.grid(row=0, column=1, padx=5, pady=5)

botao_verificar = ttk.Button(frame_verificar, text="Verificar Força", command=verificar_forca_senha)
botao_verificar.grid(row=1, column=0, columnspan=2, pady=10)

root.mainloop()
