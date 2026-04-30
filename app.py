import sqlite3

# --- BANCO DE DADOS ---
def iniciar_db():
    with sqlite3.connect('vendas.db') as conn:
        cursor = conn.cursor()
        # Tabela de Clientes/Usuários
        cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            usuario TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )''')
        # Tabela de Produtos
        cursor.execute('''CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            estoque INTEGER NOT NULL
        )''')
        # Tabela de Vendas
        cursor.execute('''CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            produto_id INTEGER,
            quantidade INTEGER,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id),
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )''')
        # Criar Admin Padrão
        try:
            cursor.execute("INSERT INTO clientes (nome, usuario, senha) VALUES (?, ?, ?)", 
                           ('Administrador', 'admin', 'admin123'))
        except sqlite3.IntegrityError:
            pass
        conn.commit()

# --- FUNÇÕES DE APOIO ---
def cadastrar_usuario(nome_tela):
    print(f"\n--- {nome_tela} ---")
    nome = input("Nome Completo: ")
    user = input("Usuário: ")
    senha = input("Senha: ")
    try:
        with sqlite3.connect('vendas.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO clientes (nome, usuario, senha) VALUES (?, ?, ?)", (nome, user, senha))
            conn.commit()
            print(f"✅ Usuário {nome} cadastrado!")
    except sqlite3.IntegrityError:
        print("❌ Erro: Usuário já existe.")

def listar_estoque():
    print("\n--- ESTOQUE ATUAL ---")
    with sqlite3.connect('vendas.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM produtos")
        prods = cursor.fetchall()
        print(f"{'ID':<4} | {'Produto':<20} | {'Preço':<10} | {'Qtd':<5}")
        for p in prods:
            print(f"{p[0]:<4} | {p[1]:<20} | R${p[2]:<8.2f} | {p[3]:<5}")
    return prods

# --- FUNÇÕES DO ADMIN ---
def cadastrar_produto():
    nome = input("Nome do Produto: ")
    preco = float(input("Preço: "))
    qtd = int(input("Quantidade inicial: "))
    with sqlite3.connect('vendas.db') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)", (nome, preco, qtd))
        conn.commit()
    print(f"✅ Produto {nome} cadastrado!")

def repor_estoque():
    listar_estoque()
    id_p = int(input("\nID do produto para repor: "))
    qtd = int(input("Quantidade a adicionar: "))
    with sqlite3.connect('vendas.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE produtos SET estoque = estoque + ? WHERE id = ?", (qtd, id_p))
        conn.commit()
    print("✅ Estoque atualizado!")

def ver_historico():
    print("\n--- HISTÓRICO DE VENDAS ---")
    with sqlite3.connect('vendas.db') as conn:
        cursor = conn.cursor()
        query = """SELECT v.id, c.nome, p.nome, v.quantidade 
                   FROM vendas v 
                   JOIN clientes c ON v.cliente_id = c.id 
                   JOIN produtos p ON v.produto_id = p.id"""
        cursor.execute(query)
        for v in cursor.fetchall():
            print(f"Venda ID: {v[0]} | Cliente: {v[1]} | Produto: {v[2]} | Qtd: {v[3]}")

# --- FUNÇÕES DO CLIENTE ---
def realizar_venda(id_cliente, nome_cliente):
    listar_estoque()
    id_p = int(input("\nID do produto que deseja: "))
    qtd = int(input("Quantidade: "))
    with sqlite3.connect('vendas.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nome, estoque FROM produtos WHERE id = ?", (id_p,))
        p = cursor.fetchone()
        if p and p[1] >= qtd:
            cursor.execute("UPDATE produtos SET estoque = estoque - ? WHERE id = ?", (qtd, id_p))
            cursor.execute("INSERT INTO vendas (cliente_id, produto_id, quantidade) VALUES (?, ?, ?)", (id_cliente, id_p, qtd))
            conn.commit()
            print(f"\n💰 VENDA REALIZADA!")
            print(f"Cliente: {nome_cliente} | comprou {qtd}x {p[0]}")
        else:
            print("❌ Estoque insuficiente ou produto inválido.")

# --- MENUS ---
def menu_admin(user):
    while True:
        print(f"\n--- PAINEL ADMIN ({user[1]}) ---")
        print("1. Cadastrar Cliente")
        print("2. Cadastrar Produto")
        print("3. Repor Estoque")
        print("4. Ver Histórico de Vendas")
        print("5. Ver Estoque")
        print("0. Sair")
        op = input("Escolha: ")
        if op == '1': cadastrar_usuario("CADASTRO PELO ADMIN")
        elif op == '2': cadastrar_produto()
        elif op == '3': repor_estoque()
        elif op == '4': ver_historico()
        elif op == '5': listar_estoque()
        elif op == '0': break

def menu_cliente(user):
    while True:
        print(f"\n--- ÁREA DO CLIENTE ({user[1]}) ---")
        print("1. Ver Estoque")
        print("2. Comprar Produto")
        print("0. Sair")
        op = input("Escolha: ")
        if op == '1': listar_estoque()
        elif op == '2': realizar_venda(user[0], user[1])
        elif op == '0': break

def main():
    iniciar_db()
    while True:
        print("\n=== SISTEMA DE VENDAS ===")
        print("1. Login")
        print("2. Fazer Cadastro (Novo Cliente)")
        print("0. Sair")
        op = input("Escolha: ")
        
        if op == '1':
            u = input("Usuário: ")
            s = input("Senha: ")
            with sqlite3.connect('vendas.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nome, usuario FROM clientes WHERE usuario=? AND senha=?", (u, s))
                user = cursor.fetchone()
            if user:
                if user[2] == 'admin': menu_admin(user)
                else: menu_cliente(user)
            else: print("❌ Login incorreto.")
        elif op == '2':
            cadastrar_usuario("AUTO-CADASTRO CLIENTE")
        elif op == '0': break

if __name__ == "__main__":
    main()