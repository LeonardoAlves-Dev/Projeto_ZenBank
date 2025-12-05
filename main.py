import customtkinter as ctk
from tkinter import messagebox
import json
import os
import random


# ==========================================
# 🧱 PARTE 1: BACKEND (Lógica Melhorada)
# ==========================================

class Conta:
    def __init__(self, nome, cpf, senha, saldo=0.0, historico=None):
        self.nome = nome
        self.cpf = cpf
        self.senha = senha
        self.saldo = saldo
        self.numero_conta = random.randint(1000, 9999)
        self.historico = historico if historico is not None else []
        self.tipo = 'Conta'

    def registrar_historico(self, operacao, valor):
        transacao = {"operacao": operacao, "valor": valor}
        self.historico.append(transacao)

    def depositar(self, valor):
        if valor > 0:
            self.saldo += valor
            self.registrar_historico("Depósito 💰", valor)
            return True
        return False

    def sacar(self, valor):
        if valor > 0 and self.saldo >= valor:
            self.saldo -= valor
            self.registrar_historico("Saque 💸", -valor)
            return True
        return False

    def transferir(self, valor, conta_destino):
        # Tenta sacar da origem. Se der certo, deposita no destino.
        if self.sacar(valor):
            conta_destino.depositar(valor)
            # Ajusta o histórico para ficar mais claro
            self.historico[-1]["operacao"] = f"Transf. Enviada 📤"
            conta_destino.historico[-1]["operacao"] = f"Transf. Recebida 📥 ({self.nome})"
            return True
        return False

    def to_dict(self):
        return {
            "tipo": self.tipo, "nome": self.nome, "cpf": self.cpf,
            "senha": self.senha, "saldo": self.saldo, "historico": self.historico,
            "extra": getattr(self, "cheque_especial", 0)
        }


class ContaCorrente(Conta):
    def __init__(self, nome, cpf, senha, saldo=0.0, historico=None, cheque_especial=500):
        super().__init__(nome, cpf, senha, saldo, historico)
        self.cheque_especial = cheque_especial
        self.tipo = 'Corrente'

    def sacar(self, valor):
        saldo_total = self.saldo + self.cheque_especial
        if valor > 0 and saldo_total >= valor:
            self.saldo -= valor
            self.registrar_historico("Saque (CC) 💳", -valor)
            return True
        return False


class ContaPoupanca(Conta):
    def __init__(self, nome, cpf, senha, saldo=0.0, historico=None):
        super().__init__(nome, cpf, senha, saldo, historico)
        self.tipo = 'Poupanca'

    def render(self):
        rendimento = self.saldo * 0.05
        self.saldo += rendimento
        self.registrar_historico("Rendimento 📈", rendimento)
        return True


class BancoController:
    def __init__(self):
        self.contas = []
        self.arquivo_db = "banco_dados.json"
        self.carregar_dados()

    def salvar_dados(self):
        lista = [c.to_dict() for c in self.contas]
        with open(self.arquivo_db, 'w') as f:
            json.dump(lista, f, indent=4)

    def carregar_dados(self):
        if not os.path.exists(self.arquivo_db): return
        try:
            with open(self.arquivo_db, 'r') as f:
                dados = json.load(f)
                for d in dados:
                    if d['tipo'] == 'Corrente':
                        c = ContaCorrente(d['nome'], d['cpf'], d['senha'], d['saldo'], d['historico'], d['extra'])
                    else:
                        c = ContaPoupanca(d['nome'], d['cpf'], d['senha'], d['saldo'], d['historico'])
                    self.contas.append(c)
        except:
            pass

    def buscar_conta(self, cpf):
        for c in self.contas:
            if c.cpf == cpf: return c
        return None

    def realizar_transferencia(self, conta_origem, cpf_destino, valor):
        conta_dest = self.buscar_conta(cpf_destino)
        if not conta_dest:
            return False, "Conta destino não encontrada."

        if conta_origem.cpf == cpf_destino:
            return False, "Não pode transferir para si mesmo."

        if conta_origem.transferir(valor, conta_dest):
            self.salvar_dados()
            return True, "Transferência realizada!"
        else:
            return False, "Saldo insuficiente."

    def criar_conta_nova(self, nome, cpf, senha, tipo):
        if self.buscar_conta(cpf): return False
        if tipo == '1':
            nova = ContaCorrente(nome, cpf, senha)
        else:
            nova = ContaPoupanca(nome, cpf, senha)
        self.contas.append(nova)
        self.salvar_dados()
        return True


# ==========================================
# 🎨 PARTE 2: FRONTEND V4 (Navegação Fluida)
# ==========================================

class AppBancario(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração da Janela
        self.title("Senai Bank V4")
        self.geometry("400x650")
        self.centralizar_janela(400, 650)

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("green")

        self.banco = BancoController()
        self.conta_logada = None

        # Container principal (onde as telas mudam)
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        self.mostrar_tela_login()

    def centralizar_janela(self, largura, altura):
        # Lógica matemática para achar o centro da tela
        tela_largura = self.winfo_screenwidth()
        tela_altura = self.winfo_screenheight()
        pos_x = (tela_largura // 2) - (largura // 2)
        pos_y = (tela_altura // 2) - (altura // 2)
        self.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

    def limpar_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # --- TELA: LOGIN ---
    def mostrar_tela_login(self):
        self.limpar_container()

        frame = ctk.CTkFrame(self.container, fg_color="transparent")
        frame.pack(pady=80)

        ctk.CTkLabel(frame, text="🔒", font=("Arial", 60)).pack(pady=10)
        ctk.CTkLabel(frame, text="Senai Bank", font=("Arial", 24, "bold")).pack(pady=5)

        self.entry_cpf = ctk.CTkEntry(frame, placeholder_text="CPF", width=250)
        self.entry_cpf.pack(pady=10)

        self.entry_senha = ctk.CTkEntry(frame, placeholder_text="Senha", show="*", width=250)
        self.entry_senha.pack(pady=10)

        ctk.CTkButton(frame, text="Acessar", width=250, command=self.fazer_login).pack(pady=20)
        ctk.CTkButton(frame, text="Criar Conta", width=250, fg_color="transparent", border_width=1,
                      command=self.mostrar_tela_cadastro).pack()

    def fazer_login(self):
        cpf = self.entry_cpf.get()
        senha = self.entry_senha.get()
        conta = self.banco.buscar_conta(cpf)
        if conta and conta.senha == senha:
            self.conta_logada = conta
            self.mostrar_dashboard()
        else:
            messagebox.showerror("Erro", "Login inválido.")

    # --- TELA: CADASTRO ---
    def mostrar_tela_cadastro(self):
        self.limpar_container()
        frame = ctk.CTkFrame(self.container, fg_color="transparent")
        frame.pack(pady=50)

        ctk.CTkLabel(frame, text="Nova Conta ✨", font=("Arial", 22, "bold")).pack(pady=20)

        entry_nome = ctk.CTkEntry(frame, placeholder_text="Nome Completo", width=250)
        entry_nome.pack(pady=5)
        entry_cpf = ctk.CTkEntry(frame, placeholder_text="CPF", width=250)
        entry_cpf.pack(pady=5)
        entry_senha = ctk.CTkEntry(frame, placeholder_text="Senha (4 digitos)", width=250)
        entry_senha.pack(pady=5)

        tipo_var = ctk.StringVar(value="1")
        ctk.CTkSwitch(frame, text="Conta Poupança?", variable=tipo_var, onvalue="2", offvalue="1").pack(pady=15)

        def confirmar():
            if self.banco.criar_conta_nova(entry_nome.get(), entry_cpf.get(), entry_senha.get(), tipo_var.get()):
                messagebox.showinfo("Sucesso", "Conta criada!")
                self.mostrar_tela_login()
            else:
                messagebox.showerror("Erro", "CPF já existe.")

        ctk.CTkButton(frame, text="Confirmar", width=250, command=confirmar).pack(pady=20)
        ctk.CTkButton(frame, text="Voltar", width=250, fg_color="gray", command=self.mostrar_tela_login).pack()

    # --- TELA: DASHBOARD (Principal) ---
    def mostrar_dashboard(self):
        self.limpar_container()

        # Cabeçalho
        topo = ctk.CTkFrame(self.container, fg_color="#1e1e1e", corner_radius=0)
        topo.pack(fill="x", ipady=20)

        ctk.CTkLabel(topo, text=f"Olá, {self.conta_logada.nome.split()[0]} 👋", font=("Arial", 16)).pack()
        self.lbl_saldo = ctk.CTkLabel(topo, text=f"R$ {self.conta_logada.saldo:.2f}", font=("Arial", 36, "bold"),
                                      text_color="#2CC985")
        self.lbl_saldo.pack(pady=5)
        ctk.CTkLabel(topo, text="Saldo Disponível", font=("Arial", 12)).pack()

        # Área de Botões (Grid)
        grid = ctk.CTkFrame(self.container, fg_color="transparent")
        grid.pack(pady=30)

        # Função auxiliar para criar botões quadrados bonitos
        def criar_botao_menu(texto, icone, comando, linha, coluna):
            btn = ctk.CTkButton(grid, text=f"{icone}\n{texto}", width=100, height=80,
                                font=("Arial", 14), fg_color="#2b2b2b", hover_color="#3a3a3a",
                                command=comando)
            btn.grid(row=linha, column=coluna, padx=10, pady=10)

        criar_botao_menu("Pix", "💠", lambda: self.mostrar_tela_transacao("Transferência"), 0, 0)
        criar_botao_menu("Pagar", "📄", lambda: self.mostrar_tela_transacao("Pagamento"), 0, 1)
        criar_botao_menu("Depositar", "💰", lambda: self.mostrar_tela_transacao("Depósito"), 1, 0)
        criar_botao_menu("Sacar", "💸", lambda: self.mostrar_tela_transacao("Saque"), 1, 1)
        criar_botao_menu("Extrato", "📜", self.mostrar_extrato, 2, 0)
        criar_botao_menu("Ajuda", "❓", self.mostrar_ajuda, 2, 1)

        ctk.CTkButton(self.container, text="Sair da Conta", fg_color="#c0392b", width=200,
                      command=self.mostrar_tela_login).pack(side="bottom", pady=30)

    # --- TELA GENÉRICA: TRANSAÇÕES (Depósito, Saque, Transferência) ---
    def mostrar_tela_transacao(self, tipo_transacao):
        self.limpar_container()

        ctk.CTkLabel(self.container, text=f"{tipo_transacao}", font=("Arial", 22, "bold")).pack(pady=30)

        # Se for transferência, precisa de mais campos
        entry_destino = None
        combo_tipo = None

        if tipo_transacao == "Transferência":
            ctk.CTkLabel(self.container, text="Tipo de Transferência").pack()
            combo_tipo = ctk.CTkComboBox(self.container, values=["Pix", "TED", "DOC"], width=250)
            combo_tipo.pack(pady=5)

            entry_destino = ctk.CTkEntry(self.container, placeholder_text="Chave Pix ou CPF Destino", width=250)
            entry_destino.pack(pady=10)

        entry_valor = ctk.CTkEntry(self.container, placeholder_text="Valor (R$)", width=250)
        entry_valor.pack(pady=10)

        def confirmar():
            try:
                valor = float(entry_valor.get())
                sucesso = False
                msg = ""

                if tipo_transacao == "Depósito":
                    sucesso = self.conta_logada.depositar(valor)
                    msg = "Depósito realizado!"
                elif tipo_transacao == "Saque":
                    sucesso = self.conta_logada.sacar(valor)
                    msg = "Saque realizado!" if sucesso else "Saldo insuficiente."
                elif tipo_transacao == "Pagamento":
                    sucesso = self.conta_logada.sacar(valor)
                    self.conta_logada.registrar_historico("Pagamento Boleto 📄", -valor)
                    msg = "Conta Paga!" if sucesso else "Saldo insuficiente."
                elif tipo_transacao == "Transferência":
                    sucesso, msg = self.banco.realizar_transferencia(self.conta_logada, entry_destino.get(), valor)

                if sucesso:
                    self.banco.salvar_dados()
                    messagebox.showinfo("Sucesso", msg)
                    self.mostrar_dashboard()
                else:
                    messagebox.showerror("Erro", msg)
            except ValueError:
                messagebox.showerror("Erro", "Digite um valor numérico válido.")

        ctk.CTkButton(self.container, text="Confirmar", width=250, command=confirmar).pack(pady=20)
        ctk.CTkButton(self.container, text="Cancelar", fg_color="gray", width=250,
                      command=self.mostrar_dashboard).pack()

    # --- TELA: EXTRATO ---
    def mostrar_extrato(self):
        self.limpar_container()
        ctk.CTkLabel(self.container, text="Extrato", font=("Arial", 22, "bold")).pack(pady=20)

        scroll_frame = ctk.CTkScrollableFrame(self.container, width=350, height=400)
        scroll_frame.pack()

        if not self.conta_logada.historico:
            ctk.CTkLabel(scroll_frame, text="Nenhuma movimentação.").pack(pady=20)

        for item in reversed(self.conta_logada.historico):  # Mostra do mais recente pro antigo
            cor = "#2CC985" if item['valor'] > 0 else "#E74C3C"
            card = ctk.CTkFrame(scroll_frame, fg_color="#2b2b2b")
            card.pack(fill="x", pady=5, padx=5)

            ctk.CTkLabel(card, text=item['operacao'], font=("Arial", 14, "bold")).pack(side="left", padx=10, pady=10)
            ctk.CTkLabel(card, text=f"R$ {item['valor']:.2f}", text_color=cor, font=("Arial", 14, "bold")).pack(
                side="right", padx=10)

        ctk.CTkButton(self.container, text="Voltar", width=250, fg_color="gray", command=self.mostrar_dashboard).pack(
            pady=20)

    # --- TELA: AJUDA ---
    def mostrar_ajuda(self):
        self.limpar_container()
        ctk.CTkLabel(self.container, text="Central de Ajuda ❓", font=("Arial", 22, "bold")).pack(pady=20)

        texto_ajuda = """
        Dúvidas Frequentes:

        1. Como faço Pix?
           Vá em Transferência > Selecione Pix > Digite o CPF.

        2. Qual meu limite?
           Contas Corrente têm R$500 de cheque especial.

        3. Rendimento Poupança
           Rende 5% a cada simulação.

        Contato: suporte@senaibank.com
        """
        ctk.CTkLabel(self.container, text=texto_ajuda, justify="left").pack(pady=20)
        ctk.CTkButton(self.container, text="Voltar", width=250, command=self.mostrar_dashboard).pack()


if __name__ == "__main__":
    app = AppBancario()
    app.mainloop()