import tkinter as tk
from neo4j import GraphDatabase

class RedeSocialSimples:
    def __init__(self, uri, usuario, senha):
        self._driver = GraphDatabase.driver(uri, auth=(usuario, senha))

    def fechar(self):
        self._driver.close()

    def adicionar_pessoa(self, nome, idade, localizacao):
        with self._driver.session() as session:
            query = (
                "CREATE (p:Pessoa {nome: $nome, idade: $idade, localizacao: $localizacao}) "
                "RETURN id(p) as id, p"
            )
            result = session.run(query, nome=nome, idade=idade, localizacao=localizacao)
            for record in result:
                pessoa = record['p']
                print(f"ID: {record['id']}, Nome: {pessoa['nome']}, Idade: {pessoa['idade']}, Localização: {pessoa['localizacao']}")

    def listar_pessoas(self):
        with self._driver.session() as session:
            query = "MATCH (p:Pessoa) RETURN id(p) as id, p"
            result = session.run(query)
            print("\nListando Pessoas:")
            for record in result:
                pessoa = record['p']
                print(f"ID: {record['id']}, Nome: {pessoa['nome']}, Idade: {pessoa['idade']}, Localização: {pessoa['localizacao']}")

    def adicionar_amizade_por_id(self, pessoa_id1, pessoa_id2):
        with self._driver.session() as session:
            query = (
                "MATCH (p1:Pessoa), (p2:Pessoa) "
                "WHERE id(p1) = $pessoa_id1 AND id(p2) = $pessoa_id2 "
                "CREATE (p1)-[:AMIGO]->(p2)"
            )
            session.run(query, pessoa_id1=pessoa_id1, pessoa_id2=pessoa_id2)
            print("Amizade adicionada com sucesso!")

    def remover_pessoa_por_id(self, pessoa_id):
        with self._driver.session() as session:
            query = "MATCH (p) WHERE id(p) = $pessoa_id DETACH DELETE p"
            session.run(query, pessoa_id=pessoa_id)
            print("Pessoa removida com sucesso!")

    def listar_amigos_de_pessoa(self, pessoa_id):
        with self._driver.session() as session:
            query = (
                "MATCH (p1:Pessoa)-[:AMIGO]-(p2:Pessoa) "
                "WHERE id(p1) = $pessoa_id "
                "RETURN id(p2) as id, p2"
            )
            result = session.run(query, pessoa_id=pessoa_id)
            amigos = [record['p2'] for record in result]
            return amigos if amigos else None

    def remover_amizade(self, pessoa_id1, pessoa_id2):
        with self._driver.session() as session:
            query = (
                "MATCH (p1:Pessoa)-[rel:AMIGO]-(p2:Pessoa) "
                "WHERE id(p1) = $pessoa_id1 AND id(p2) = $pessoa_id2 "
                "DELETE rel"
            )
            session.run(query, pessoa_id1=pessoa_id1, pessoa_id2=pessoa_id2)
            print("Relação de amizade removida com sucesso!")

# Funções para interação com a interface gráfica
def adicionar_pessoa():
    nome = nome_entry.get()
    idade = int(idade_entry.get())
    localizacao = localizacao_entry.get()
    rede_social.adicionar_pessoa(nome, idade, localizacao)
    listar_pessoas()  # Atualiza a listagem após adicionar a pessoa

def listar_pessoas():
    lista_pessoas.delete(0, tk.END)  # Limpa a listbox antes de listar novamente
    with rede_social._driver.session() as session:
        query = "MATCH (p:Pessoa) RETURN id(p) as id, p"
        result = session.run(query)
        for record in result:
            pessoa = record['p']
            lista_pessoas.insert(tk.END, f"ID: {record['id']}, Nome: {pessoa['nome']}, Idade: {pessoa['idade']}, Localização: {pessoa['localizacao']}")

def adicionar_amizade():
    pessoa_id1 = int(amizade_id1_entry.get())
    pessoa_id2 = int(amizade_id2_entry.get())
    rede_social.adicionar_amizade_por_id(pessoa_id1, pessoa_id2)
    listar_pessoas()

def remover_pessoa():
    pessoa_id = int(remover_id_entry.get())
    rede_social.remover_pessoa_por_id(pessoa_id)
    listar_pessoas()

def listar_amigos():
    pessoa_id = int(amigos_id_entry.get())
    amigos = rede_social.listar_amigos_de_pessoa(pessoa_id)
    if amigos:
        print(f"Amigos da Pessoa ID {pessoa_id}:")
        for amigo in amigos:
            print(f"ID: {amigo['id']}, Nome: {amigo['nome']}, Idade: {amigo['idade']}, Localização: {amigo['localizacao']}")
    else:
        print("Essa pessoa não possui amigos ou o ID da pessoa é inválido.")

def remover_amizade():
    pessoa_id1 = int(remover_amizade_id1_entry.get())
    pessoa_id2 = int(remover_amizade_id2_entry.get())
    rede_social.remover_amizade(pessoa_id1, pessoa_id2)
    listar_pessoas()

# Configurações de conexão ao banco de dados Neo4j
uri = "bolt://localhost:7687"  # Seu URI do banco de dados Neo4j
usuario = "neo4j"  # Seu usuário do Neo4j
senha = "12345678"  # Sua senha do Neo4j

# Instanciando a rede social
rede_social = RedeSocialSimples(uri, usuario, senha)

# Interface Gráfica
root = tk.Tk()
root.title("Rede Social")

# Widgets
label_nome = tk.Label(root, text="Nome:")
label_nome.grid(row=0, column=0)
nome_entry = tk.Entry(root)
nome_entry.grid(row=0, column=1)

label_idade = tk.Label(root, text="Idade:")
label_idade.grid(row=1, column=0)
idade_entry = tk.Entry(root)
idade_entry.grid(row=1, column=1)

label_localizacao = tk.Label(root, text="Localização:")
label_localizacao.grid(row=2, column=0)
localizacao_entry = tk.Entry(root)
localizacao_entry.grid(row=2, column=1)

adicionar_btn = tk.Button(root, text="Adicionar Pessoa", command=adicionar_pessoa)
adicionar_btn.grid(row=3, columnspan=2)

listar_btn = tk.Button(root, text="Listar Pessoas", command=listar_pessoas)
listar_btn.grid(row=4, columnspan=2)

# Adicionar amizade
amizade_id1_label = tk.Label(root, text="ID Pessoa 1:")
amizade_id1_label.grid(row=5, column=0)
amizade_id1_entry = tk.Entry(root)
amizade_id1_entry.grid(row=5, column=1)

amizade_id2_label = tk.Label(root, text="ID Pessoa 2:")
amizade_id2_label.grid(row=6, column=0)
amizade_id2_entry = tk.Entry(root)
amizade_id2_entry.grid(row=6, column=1)

adicionar_amizade_btn = tk.Button(root, text="Adicionar Amizade", command=adicionar_amizade)
adicionar_amizade_btn.grid(row=7, columnspan=2)

# Remover pessoa
remover_id_label = tk.Label(root, text="ID Pessoa a Remover:")
remover_id_label.grid(row=8, column=0)
remover_id_entry = tk.Entry(root)
remover_id_entry.grid(row=8, column=1)

remover_pessoa_btn = tk.Button(root, text="Remover Pessoa", command=remover_pessoa)
remover_pessoa_btn.grid(row=9, columnspan=2)

# Listar amigos
amigos_id_label = tk.Label(root, text="ID Pessoa para Listar Amigos:")
amigos_id_label.grid(row=10, column=0)
amigos_id_entry = tk.Entry(root)
amigos_id_entry.grid(row=10, column=1)

listar_amigos_btn = tk.Button(root, text="Listar Amigos", command=listar_amigos)
listar_amigos_btn.grid(row=11, columnspan=2)

# Remover amizade
remover_amizade_id1_label = tk.Label(root, text="ID Pessoa 1 para Remover Amizade:")
remover_amizade_id1_label.grid(row=12, column=0)
remover_amizade_id1_entry = tk.Entry(root)
remover_amizade_id1_entry.grid(row=12, column=1)

remover_amizade_id2_label = tk.Label(root, text="ID Pessoa 2 para Remover Amizade:")
remover_amizade_id2_label.grid(row=13, column=0)
remover_amizade_id2_entry = tk.Entry(root)
remover_amizade_id2_entry.grid(row=13, column=1)

remover_amizade_btn = tk.Button(root, text="Remover Amizade", command=remover_amizade)
remover_amizade_btn.grid(row=14, columnspan=2)

lista_pessoas = tk.Listbox(root)

lista_pessoas.grid(row=15, columnspan=2)

root.update()  # Atualiza a janela para obter o tamanho correto da tela

largura_tela = root.winfo_width()  # Obtém a largura da tela

lista_pessoas.config(width=80)  # Define a largura da Listbox de acordo com a largura da tela

root.mainloop()