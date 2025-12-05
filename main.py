import customtkinter as ctk
from tkinter import messagebox
import json
import os
import random


# ==========================================
# 🧱 PARTE 1: BACKEND (Lógica de Negócio)
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
# 🎨 PARTE 2: FRONTEND (CustomTkinter)
# ==========================================

class AppBancario(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuracao da Janela
        self.title("Senai Bank V1")
        self.geometry("400x600")
        ctk.set_appearance_mode("Dark")  # Modo Escuro
        ctk.set_default_color_theme("blue")

        # Inicia o Controlador (Banco de Dados)
        self.banco = BancoController()
        self.conta_logada = None

        # Carrega a Tela de Login
        self.tela_login()

    def limpar_tela(self):
        for widget in self.winfo_children():
            widget.destroy()

    # --- TELA 1: LOGIN ---
    def tela_login(self):
        self.limpar_tela()

        titulo = ctk.CTkLabel(self, text="🔒 Login SecureBank", font=("Arial", 24, "bold"))
        titulo.pack(pady=40)

        self.entry_cpf = ctk.CTkEntry(self, placeholder_text="Digite seu CPF")
        self.entry_cpf.pack(pady=10)

        self.entry_senha = ctk.CTkEntry(self, placeholder_text="Sua Senha", show="*")
        self.entry_senha.pack(pady=10)

        btn_entrar = ctk.CTkButton(self, text="Entrar", command=self.fazer_login)
        btn_entrar.pack(pady=20)

        btn_criar = ctk.CTkButton(self, text="Criar Nova Conta", fg_color="transparent", border_width=1,
                                  command=self.tela_cadastro)
        btn_criar.pack(pady=10)

    def fazer_login(self):
        cpf = self.entry_cpf.get()
        senha = self.entry_senha.get()

        conta = self.banco.buscar_conta(cpf)

        if conta and conta.senha == senha:
            self.conta_logada = conta
            self.tela_principal()
        else:
            messagebox.showerror("Erro", "CPF ou Senha inválidos!")

    # --- TELA 2: CADASTRO ---
    def tela_cadastro(self):
        self.limpar_tela()

        ctk.CTkLabel(self, text="Nova Conta ✨", font=("Arial", 20)).pack(pady=20)

        entry_nome = ctk.CTkEntry(self, placeholder_text="Nome Completo")
        entry_nome.pack(pady=5)

        entry_cpf_cad = ctk.CTkEntry(self, placeholder_text="CPF")
        entry_cpf_cad.pack(pady=5)

        entry_senha_cad = ctk.CTkEntry(self, placeholder_text="Senha (4 digitos)")
        entry_senha_cad.pack(pady=5)

        # Switch para tipo de conta
        self.tipo_var = ctk.StringVar(value="1")  # 1=Corrente
        chk = ctk.CTkSwitch(self, text="Conta Poupança?", variable=self.tipo_var, onvalue="2", offvalue="1")
        chk.pack(pady=10)

        def confirmar_cadastro():
            sucesso = self.banco.criar_conta_nova(entry_nome.get(), entry_cpf_cad.get(), entry_senha_cad.get(),
                                                  self.tipo_var.get())
            if sucesso:
                messagebox.showinfo("Sucesso", "Conta criada! Faça login.")
                self.tela_login()
            else:
                messagebox.showerror("Erro", "CPF já existe.")

        ctk.CTkButton(self, text="Confirmar", command=confirmar_cadastro).pack(pady=20)
        ctk.CTkButton(self, text="Voltar", fg_color="gray", command=self.tela_login).pack()

    # --- TELA 3: PRINCIPAL (DASHBOARD) ---
    def tela_principal(self):
        self.limpar_tela()

        # Cabeçalho
        frame_top = ctk.CTkFrame(self, fg_color="transparent")
        frame_top.pack(pady=20)

        ctk.CTkLabel(frame_top, text=f"Olá, {self.conta_logada.nome} 👋").pack()
        self.lbl_saldo = ctk.CTkLabel(frame_top, text=f"R$ {self.conta_logada.saldo:.2f}", font=("Arial", 32, "bold"),
                                      text_color="#2CC985")
        self.lbl_saldo.pack()

        # Botoes de Acao
        frame_botoes = ctk.CTkFrame(self)
        frame_botoes.pack(pady=20, padx=20, fill="both")

        ctk.CTkButton(frame_botoes, text="Depositar 💰", command=self.acao_depositar).pack(pady=10, fill="x", padx=20)
        ctk.CTkButton(frame_botoes, text="Sacar 💸", command=self.acao_sacar).pack(pady=10, fill="x", padx=20)
        ctk.CTkButton(frame_botoes, text="Extrato 📜", command=self.acao_extrato).pack(pady=10, fill="x", padx=20)

        ctk.CTkButton(self, text="Sair", fg_color="red", command=self.tela_login).pack(pady=20)

    # --- FUNCOES DOS BOTOES ---
    def acao_depositar(self):
        # Abre uma caixinha simples pedindo valor
        dialog = ctk.CTkInputDialog(text="Qual valor deseja depositar?", title="Depósito")
        valor_str = dialog.get_input()
        if valor_str:
            try:
                v = float(valor_str)
                if self.conta_logada.depositar(v):
                    self.banco.salvar_dados()
                    self.lbl_saldo.configure(text=f"R$ {self.conta_logada.saldo:.2f}")  # Atualiza tela
                    messagebox.showinfo("Sucesso", "Depósito realizado!")
            except:
                messagebox.showerror("Erro", "Valor inválido")

    def acao_sacar(self):
        dialog = ctk.CTkInputDialog(text="Qual valor deseja sacar?", title="Saque")
        valor_str = dialog.get_input()
        if valor_str:
            try:
                v = float(valor_str)
                if self.conta_logada.sacar(v):
                    self.banco.salvar_dados()
                    self.lbl_saldo.configure(text=f"R$ {self.conta_logada.saldo:.2f}")
                    messagebox.showinfo("Sucesso", "Saque realizado!")
                else:
                    messagebox.showerror("Erro", "Saldo insuficiente")
            except:
                messagebox.showerror("Erro", "Valor inválido")

    def acao_extrato(self):
        # Monta o texto do extrato
        texto = ""
        for item in self.conta_logada.historico:
            texto += f"{item['operacao']}: R$ {item['valor']:.2f}\n"

        messagebox.showinfo("Extrato Recente", texto if texto else "Sem movimentações.")


# --- INICIAR ---
if __name__ == "__main__":
    app = AppBancario()
    app.mainloop()