class Lancamento:
    """
    Representa um lançamento financeiro.
    """

    def __init__(self, id, data, tipo, categoria, descricao, valor):
        self.id = id
        self.data = data
        self.tipo = tipo
        self.categoria = categoria
        self.descricao = descricao
        self.valor = valor