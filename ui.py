import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from models import Lancamento
from database import BancoDados
from service import LancamentoService

CATEGORIAS = [
    "Alimentação",
    "Transporte",
    "Moradia",
    "Lazer",
    "Saúde",
    "Educação",
    "Salário",
    "Outros"
]


class App:
    """
    Interface gráfica principal do sistema.
    """

    def __init__(self):
        self.db = BancoDados()
        self.service = LancamentoService()

        self.root = tk.Tk()
        self.root.title("Controle de Gastos")
        self.root.geometry("1320x820")
        self.root.configure(bg="#f4f6f8")

        self.id_em_edicao = None
        self.figura = None
        self.canvas_grafico = None
        self.ax = None

        self.todos_lancamentos = []
        self.lancamentos_visiveis = []

        self.configurar_estilo()
        self.criar_widgets()
        self.carregar_lancamentos()

    def configurar_estilo(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.configure("Treeview", font=("Arial", 10), rowheight=26)
        style.configure("TCombobox", padding=4)

    def criar_card(self, parent, bg="#ffffff"):
        return tk.Frame(parent, bg=bg, bd=1, relief="solid")

    def criar_widgets(self):
        frame_principal = tk.Frame(self.root, bg="#f4f6f8")
        frame_principal.pack(fill="both", expand=True, padx=12, pady=12)

        titulo = tk.Label(
            frame_principal,
            text="Controle de Gastos",
            font=("Arial", 20, "bold"),
            bg="#f4f6f8",
            fg="#1f2937"
        )
        titulo.pack(anchor="w", pady=(0, 10))

        frame_topo = self.criar_card(frame_principal)
        frame_topo.pack(fill="x", pady=(0, 10), ipadx=8, ipady=8)

        tk.Label(frame_topo, text="Data (dd/mm/aaaa)", bg="#ffffff").grid(row=0, column=0, sticky="w", padx=6, pady=(6, 0))
        self.entry_data = tk.Entry(frame_topo, width=15)
        self.entry_data.grid(row=1, column=0, padx=6, pady=6)

        tk.Label(frame_topo, text="Tipo", bg="#ffffff").grid(row=0, column=1, sticky="w", padx=6, pady=(6, 0))
        self.combo_tipo = ttk.Combobox(
            frame_topo,
            values=["Receita", "Despesa"],
            state="readonly",
            width=15
        )
        self.combo_tipo.grid(row=1, column=1, padx=6, pady=6)
        self.combo_tipo.set("Despesa")

        tk.Label(frame_topo, text="Categoria", bg="#ffffff").grid(row=0, column=2, sticky="w", padx=6, pady=(6, 0))
        self.combo_categoria = ttk.Combobox(
            frame_topo,
            values=CATEGORIAS,
            state="readonly",
            width=18
        )
        self.combo_categoria.grid(row=1, column=2, padx=6, pady=6)
        self.combo_categoria.set(CATEGORIAS[0])

        tk.Label(frame_topo, text="Descrição", bg="#ffffff").grid(row=0, column=3, sticky="w", padx=6, pady=(6, 0))
        self.entry_descricao = tk.Entry(frame_topo, width=30)
        self.entry_descricao.grid(row=1, column=3, padx=6, pady=6)

        tk.Label(frame_topo, text="Valor", bg="#ffffff").grid(row=0, column=4, sticky="w", padx=6, pady=(6, 0))
        self.entry_valor = tk.Entry(frame_topo, width=12)
        self.entry_valor.grid(row=1, column=4, padx=6, pady=6)

        tk.Button(
            frame_topo,
            text="Adicionar",
            width=12,
            bg="#2563eb",
            fg="white",
            command=self.adicionar_lancamento
        ).grid(row=1, column=5, padx=6, pady=6)

        tk.Button(
            frame_topo,
            text="Atualizar",
            width=12,
            bg="#059669",
            fg="white",
            command=self.atualizar_lancamento_interface
        ).grid(row=1, column=6, padx=6, pady=6)

        tk.Button(
            frame_topo,
            text="Limpar",
            width=12,
            bg="#6b7280",
            fg="white",
            command=self.limpar_campos
        ).grid(row=1, column=7, padx=6, pady=6)

        frame_resumos = tk.Frame(frame_principal, bg="#f4f6f8")
        frame_resumos.pack(fill="x", pady=(0, 10))

        self.card_receitas = self.criar_card(frame_resumos)
        self.card_receitas.pack(side="left", fill="x", expand=True, padx=(0, 6), ipadx=8, ipady=8)

        self.card_despesas = self.criar_card(frame_resumos)
        self.card_despesas.pack(side="left", fill="x", expand=True, padx=6, ipadx=8, ipady=8)

        self.card_saldo = self.criar_card(frame_resumos)
        self.card_saldo.pack(side="left", fill="x", expand=True, padx=6, ipadx=8, ipady=8)

        self.card_mes = self.criar_card(frame_resumos)
        self.card_mes.pack(side="left", fill="x", expand=True, padx=(6, 0), ipadx=8, ipady=8)

        self.label_receitas = tk.Label(self.card_receitas, text="Receitas\nR$ 0.00", font=("Arial", 12, "bold"), bg="#ffffff", fg="#065f46")
        self.label_receitas.pack(padx=10, pady=10)

        self.label_despesas = tk.Label(self.card_despesas, text="Despesas\nR$ 0.00", font=("Arial", 12, "bold"), bg="#ffffff", fg="#991b1b")
        self.label_despesas.pack(padx=10, pady=10)

        self.label_saldo = tk.Label(self.card_saldo, text="Saldo\nR$ 0.00", font=("Arial", 12, "bold"), bg="#ffffff", fg="#1d4ed8")
        self.label_saldo.pack(padx=10, pady=10)

        self.label_mes_atual = tk.Label(self.card_mes, text="Mês atual\nR$ 0.00", font=("Arial", 12, "bold"), bg="#ffffff", fg="#7c3aed")
        self.label_mes_atual.pack(padx=10, pady=10)

        frame_busca_filtro = self.criar_card(frame_principal)
        frame_busca_filtro.pack(fill="x", pady=(0, 10), ipadx=8, ipady=8)

        tk.Label(frame_busca_filtro, text="Buscar", bg="#ffffff").grid(row=0, column=0, sticky="w", padx=6, pady=(6, 0))
        self.entry_busca = tk.Entry(frame_busca_filtro, width=24)
        self.entry_busca.grid(row=1, column=0, padx=6, pady=6)

        tk.Button(
            frame_busca_filtro,
            text="Pesquisar",
            bg="#2563eb",
            fg="white",
            command=self.buscar_lancamentos_interface
        ).grid(row=1, column=1, padx=6, pady=6)

        tk.Button(
            frame_busca_filtro,
            text="Mostrar todos",
            bg="#6b7280",
            fg="white",
            command=self.carregar_lancamentos
        ).grid(row=1, column=2, padx=6, pady=6)

        tk.Label(frame_busca_filtro, text="Mês", bg="#ffffff").grid(row=0, column=3, sticky="w", padx=6, pady=(6, 0))
        self.entry_mes = tk.Entry(frame_busca_filtro, width=6)
        self.entry_mes.grid(row=1, column=3, padx=6, pady=6)

        tk.Label(frame_busca_filtro, text="Ano", bg="#ffffff").grid(row=0, column=4, sticky="w", padx=6, pady=(6, 0))
        self.entry_ano = tk.Entry(frame_busca_filtro, width=8)
        self.entry_ano.grid(row=1, column=4, padx=6, pady=6)

        tk.Label(frame_busca_filtro, text="Tipo", bg="#ffffff").grid(row=0, column=5, sticky="w", padx=6, pady=(6, 0))
        self.combo_filtro_tipo = ttk.Combobox(
            frame_busca_filtro,
            values=["Todos", "Receita", "Despesa"],
            state="readonly",
            width=12
        )
        self.combo_filtro_tipo.grid(row=1, column=5, padx=6, pady=6)
        self.combo_filtro_tipo.set("Todos")

        tk.Label(frame_busca_filtro, text="Categoria", bg="#ffffff").grid(row=0, column=6, sticky="w", padx=6, pady=(6, 0))
        self.combo_filtro_categoria = ttk.Combobox(
            frame_busca_filtro,
            values=["Todas"] + CATEGORIAS,
            state="readonly",
            width=16
        )
        self.combo_filtro_categoria.grid(row=1, column=6, padx=6, pady=6)
        self.combo_filtro_categoria.set("Todas")

        tk.Button(
            frame_busca_filtro,
            text="Aplicar filtros",
            bg="#059669",
            fg="white",
            command=self.aplicar_filtros
        ).grid(row=1, column=7, padx=6, pady=6)

        tk.Button(
            frame_busca_filtro,
            text="Limpar filtros",
            bg="#6b7280",
            fg="white",
            command=self.limpar_filtro
        ).grid(row=1, column=8, padx=6, pady=6)

        frame_principal_interno = tk.Frame(frame_principal, bg="#f4f6f8")
        frame_principal_interno.pack(fill="both", expand=True)

        frame_lista = self.criar_card(frame_principal_interno)
        frame_lista.pack(side="left", fill="both", expand=True, padx=(0, 6), ipadx=8, ipady=8)

        frame_botoes_lista = tk.Frame(frame_lista, bg="#ffffff")
        frame_botoes_lista.pack(fill="x", padx=8, pady=8)

        tk.Button(
            frame_botoes_lista,
            text="Carregar para editar",
            bg="#2563eb",
            fg="white",
            command=self.carregar_lancamento_para_edicao
        ).pack(side="left", padx=4)

        tk.Button(
            frame_botoes_lista,
            text="Excluir selecionado",
            bg="#dc2626",
            fg="white",
            command=self.excluir_lancamento_interface
        ).pack(side="left", padx=4)

        colunas = ("id", "data", "tipo", "categoria", "descricao", "valor")

        tabela_frame = tk.Frame(frame_lista, bg="#ffffff")
        tabela_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.tree = ttk.Treeview(tabela_frame, columns=colunas, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("data", text="Data")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("categoria", text="Categoria")
        self.tree.heading("descricao", text="Descrição")
        self.tree.heading("valor", text="Valor")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("data", width=100, anchor="center")
        self.tree.column("tipo", width=100, anchor="center")
        self.tree.column("categoria", width=130, anchor="center")
        self.tree.column("descricao", width=340, anchor="w")
        self.tree.column("valor", width=100, anchor="e")

        scrollbar = ttk.Scrollbar(tabela_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        frame_grafico = self.criar_card(frame_principal_interno)
        frame_grafico.pack(side="right", fill="both", expand=False, padx=(6, 0), ipadx=8, ipady=8)

        topo_grafico = tk.Frame(frame_grafico, bg="#ffffff")
        topo_grafico.pack(fill="x", padx=8, pady=8)

        tk.Label(topo_grafico, text="Tipo de gráfico", bg="#ffffff").pack(side="left", padx=(0, 6))

        self.combo_tipo_grafico = ttk.Combobox(
            topo_grafico,
            values=["Barras", "Pizza"],
            state="readonly",
            width=10
        )
        self.combo_tipo_grafico.pack(side="left")
        self.combo_tipo_grafico.set("Barras")

        tk.Button(
            topo_grafico,
            text="Atualizar gráfico",
            bg="#2563eb",
            fg="white",
            command=self.atualizar_grafico
        ).pack(side="left", padx=8)

        self.frame_grafico = tk.Frame(frame_grafico, bg="#ffffff", width=420)
        self.frame_grafico.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def preencher_tabela(self, lancamentos):
        self.tree.delete(*self.tree.get_children())

        for lancamento in lancamentos:
            self.tree.insert(
                "",
                "end",
                values=(
                    lancamento.id,
                    lancamento.data,
                    lancamento.tipo,
                    lancamento.categoria,
                    lancamento.descricao,
                    f"R$ {lancamento.valor:.2f}"
                )
            )

    def atualizar_indicadores(self):
        self.preencher_tabela(self.lancamentos_visiveis)
        self.atualizar_resumo()
        self.atualizar_grafico()

    def carregar_lancamentos(self):
        self.todos_lancamentos = self.db.listar()
        self.lancamentos_visiveis = self.todos_lancamentos.copy()
        self.atualizar_indicadores()

    def limpar_campos(self):
        self.id_em_edicao = None
        self.entry_data.delete(0, tk.END)
        self.combo_tipo.set("Despesa")
        self.combo_categoria.set(CATEGORIAS[0])
        self.entry_descricao.delete(0, tk.END)
        self.entry_valor.delete(0, tk.END)

    def limpar_filtro(self):
        self.entry_mes.delete(0, tk.END)
        self.entry_ano.delete(0, tk.END)
        self.combo_filtro_tipo.set("Todos")
        self.combo_filtro_categoria.set("Todas")
        self.entry_busca.delete(0, tk.END)
        self.carregar_lancamentos()

    def obter_dados_formulario(self):
        data = self.entry_data.get().strip()
        tipo = self.combo_tipo.get().strip()
        categoria = self.combo_categoria.get().strip()
        descricao = self.entry_descricao.get().strip()
        valor_texto = self.entry_valor.get().strip().replace(",", ".")

        if not data or not tipo or not categoria or not descricao or not valor_texto:
            messagebox.showwarning("Campos obrigatórios", "Preencha todos os campos.")
            return None

        if not self.service.validar_data(data):
            messagebox.showerror("Data inválida", "Use o formato dd/mm/aaaa.")
            return None

        try:
            valor = float(valor_texto)
        except ValueError:
            messagebox.showerror("Valor inválido", "Digite um valor numérico.")
            return None

        return data, tipo, categoria, descricao, valor

    def adicionar_lancamento(self):
        dados = self.obter_dados_formulario()
        if not dados:
            return

        data, tipo, categoria, descricao, valor = dados
        lancamento = Lancamento(None, data, tipo, categoria, descricao, valor)
        self.db.salvar(lancamento)

        self.carregar_lancamentos()
        self.limpar_campos()
        messagebox.showinfo("Sucesso", "Lançamento adicionado com sucesso!")

    def carregar_lancamento_para_edicao(self):
        item = self.tree.selection()

        if not item:
            messagebox.showwarning("Seleção", "Selecione um lançamento na tabela.")
            return

        valores = self.tree.item(item[0], "values")
        id_lancamento = int(valores[0])

        lancamento = self.db.buscar_por_id(id_lancamento)

        if not lancamento:
            messagebox.showerror("Erro", "Lançamento não encontrado.")
            return

        self.id_em_edicao = lancamento.id

        self.entry_data.delete(0, tk.END)
        self.entry_data.insert(0, lancamento.data)

        self.combo_tipo.set(lancamento.tipo)
        self.combo_categoria.set(lancamento.categoria)

        self.entry_descricao.delete(0, tk.END)
        self.entry_descricao.insert(0, lancamento.descricao)

        self.entry_valor.delete(0, tk.END)
        self.entry_valor.insert(0, f"{lancamento.valor:.2f}")

    def atualizar_lancamento_interface(self):
        if self.id_em_edicao is None:
            messagebox.showwarning("Edição", "Selecione um lançamento para editar primeiro.")
            return

        dados = self.obter_dados_formulario()
        if not dados:
            return

        data, tipo, categoria, descricao, valor = dados
        lancamento = Lancamento(self.id_em_edicao, data, tipo, categoria, descricao, valor)
        self.db.atualizar(lancamento)

        self.carregar_lancamentos()
        self.limpar_campos()
        messagebox.showinfo("Sucesso", "Lançamento atualizado com sucesso!")

    def excluir_lancamento_interface(self):
        item = self.tree.selection()

        if not item:
            messagebox.showwarning("Seleção", "Selecione um lançamento para excluir.")
            return

        valores = self.tree.item(item[0], "values")
        id_lancamento = int(valores[0])

        confirmar = messagebox.askyesno(
            "Confirmar exclusão",
            f"Deseja excluir o lançamento ID {id_lancamento}?"
        )

        if not confirmar:
            return

        self.db.excluir(id_lancamento)
        self.carregar_lancamentos()
        self.limpar_campos()
        messagebox.showinfo("Sucesso", "Lançamento excluído com sucesso!")

    def buscar_lancamentos_interface(self):
        self.aplicar_filtros()

    def aplicar_filtros(self):
        mes = self.entry_mes.get().strip()
        ano = self.entry_ano.get().strip()
        tipo = self.combo_filtro_tipo.get().strip()
        categoria = self.combo_filtro_categoria.get().strip()
        termo = self.entry_busca.get().strip()

        self.lancamentos_visiveis = self.service.filtrar_lancamentos(
            self.todos_lancamentos,
            mes=mes,
            ano=ano,
            tipo=tipo,
            categoria=categoria,
            termo=termo
        )

        self.atualizar_indicadores()

    def atualizar_resumo(self):
        total_receitas, total_despesas, saldo = self.service.calcular_resumo(self.lancamentos_visiveis)
        _, _, saldo_mes = self.service.calcular_total_mes_atual(self.todos_lancamentos)

        self.label_receitas.config(text=f"Receitas\nR$ {total_receitas:.2f}")
        self.label_despesas.config(text=f"Despesas\nR$ {total_despesas:.2f}")
        self.label_saldo.config(text=f"Saldo\nR$ {saldo:.2f}")
        self.label_mes_atual.config(text=f"Mês atual\nR$ {saldo_mes:.2f}")

    def atualizar_grafico(self):
        despesas = self.service.calcular_despesas_por_categoria(self.lancamentos_visiveis)

        if self.canvas_grafico is not None:
            self.canvas_grafico.get_tk_widget().destroy()

        self.figura, self.ax = plt.subplots(figsize=(4.8, 4.8))
        tipo_grafico = self.combo_tipo_grafico.get()

        if despesas:
            categorias = list(despesas.keys())
            valores = list(despesas.values())

            if tipo_grafico == "Pizza":
                self.ax.pie(valores, labels=categorias, autopct="%1.1f%%", startangle=90)
                self.ax.set_title("Participação das Despesas por Categoria")
            else:
                self.ax.bar(categorias, valores)
                self.ax.set_title("Despesas por Categoria")
                self.ax.set_xlabel("Categoria")
                self.ax.set_ylabel("Valor (R$)")
                self.ax.tick_params(axis="x", rotation=30)
        else:
            self.ax.text(
                0.5,
                0.5,
                "Sem despesas para exibir",
                ha="center",
                va="center",
                transform=self.ax.transAxes
            )
            self.ax.set_title("Despesas por Categoria")
            self.ax.set_xticks([])
            self.ax.set_yticks([])

        self.figura.tight_layout()

        self.canvas_grafico = FigureCanvasTkAgg(self.figura, master=self.frame_grafico)
        self.canvas_grafico.draw()
        self.canvas_grafico.get_tk_widget().pack(fill="both", expand=True)

    def run(self):
        self.root.mainloop()