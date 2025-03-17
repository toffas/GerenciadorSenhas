import sqlite3
import re
import random
from cryptography.fernet import Fernet

# Gerar ou carregar a chave Fernet
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

# Funções de criptografia
def criptografar_senha(senha):
    return fernet.encrypt(senha.encode()).decode()

def descriptografar_senha(senha_criptografada):
    return fernet.decrypt(senha_criptografada.encode()).decode()

# Funções do banco de dados
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
