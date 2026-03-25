import sqlite3
from models import Lancamento


class BancoDados:
    """
    Responsável por toda a comunicação com o banco SQLite.
    """

    def __init__(self, nome_banco="gastos.db"):
        self.nome_banco = nome_banco
        self.criar_tabela()

    def conectar(self):
        return sqlite3.connect(self.nome_banco)

    def criar_tabela(self):
        conexao = self.conectar()
        cursor = conexao.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lancamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                tipo TEXT NOT NULL,
                categoria TEXT NOT NULL,
                descricao TEXT NOT NULL,
                valor REAL NOT NULL
            )
        """)

        conexao.commit()
        conexao.close()

    def salvar(self, lancamento):
        conexao = self.conectar()
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO lancamentos (data, tipo, categoria, descricao, valor)
            VALUES (?, ?, ?, ?, ?)
        """, (
            lancamento.data,
            lancamento.tipo,
            lancamento.categoria,
            lancamento.descricao,
            lancamento.valor
        ))

        conexao.commit()
        conexao.close()

    def listar(self):
        conexao = self.conectar()
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT id, data, tipo, categoria, descricao, valor
            FROM lancamentos
            ORDER BY id DESC
        """)

        dados = cursor.fetchall()
        conexao.close()

        return [Lancamento(*dado) for dado in dados]

    def buscar_por_id(self, id_lancamento):
        conexao = self.conectar()
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT id, data, tipo, categoria, descricao, valor
            FROM lancamentos
            WHERE id = ?
        """, (id_lancamento,))

        dado = cursor.fetchone()
        conexao.close()

        if dado:
            return Lancamento(*dado)
        return None

    def atualizar(self, lancamento):
        conexao = self.conectar()
        cursor = conexao.cursor()

        cursor.execute("""
            UPDATE lancamentos
            SET data = ?, tipo = ?, categoria = ?, descricao = ?, valor = ?
            WHERE id = ?
        """, (
            lancamento.data,
            lancamento.tipo,
            lancamento.categoria,
            lancamento.descricao,
            lancamento.valor,
            lancamento.id
        ))

        conexao.commit()
        conexao.close()

    def excluir(self, id_lancamento):
        conexao = self.conectar()
        cursor = conexao.cursor()

        cursor.execute("DELETE FROM lancamentos WHERE id = ?", (id_lancamento,))

        conexao.commit()
        conexao.close()