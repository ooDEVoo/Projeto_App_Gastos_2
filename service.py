from datetime import datetime


class LancamentoService:
    """
    Contém regras de negócio, filtros e cálculos.
    """

    def validar_data(self, data):
        try:
            datetime.strptime(data, "%d/%m/%Y")
            return True
        except ValueError:
            return False

    def filtrar_lancamentos(self, lancamentos, mes="", ano="", tipo="Todos", categoria="Todas", termo=""):
        resultados = []

        termo = termo.lower().strip()

        for lancamento in lancamentos:
            passou = True

            if mes or ano:
                partes = lancamento.data.split("/")
                if len(partes) != 3:
                    continue

                _, mes_lanc, ano_lanc = partes

                if mes and mes_lanc != mes:
                    passou = False
                if ano and ano_lanc != ano:
                    passou = False

            if tipo != "Todos" and lancamento.tipo != tipo:
                passou = False

            if categoria != "Todas" and lancamento.categoria != categoria:
                passou = False

            if termo:
                texto = (
                    f"{lancamento.data} "
                    f"{lancamento.tipo} "
                    f"{lancamento.categoria} "
                    f"{lancamento.descricao} "
                    f"{lancamento.valor}"
                ).lower()

                if termo not in texto:
                    passou = False

            if passou:
                resultados.append(lancamento)

        return resultados

    def calcular_resumo(self, lancamentos):
        receitas = sum(l.valor for l in lancamentos if l.tipo == "Receita")
        despesas = sum(l.valor for l in lancamentos if l.tipo == "Despesa")
        saldo = receitas - despesas
        return receitas, despesas, saldo

    def calcular_despesas_por_categoria(self, lancamentos):
        totais = {}

        for lancamento in lancamentos:
            if lancamento.tipo == "Despesa":
                totais[lancamento.categoria] = totais.get(lancamento.categoria, 0) + lancamento.valor

        return totais

    def calcular_total_mes_atual(self, lancamentos):
        hoje = datetime.now()
        mes_atual = hoje.strftime("%m")
        ano_atual = hoje.strftime("%Y")

        lancamentos_mes = self.filtrar_lancamentos(
            lancamentos,
            mes=mes_atual,
            ano=ano_atual
        )

        return self.calcular_resumo(lancamentos_mes)