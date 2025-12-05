import customtkinter as ctk
from tkinter import messagebox
import json
import os
import random
import re  # Nova importação para validar senha forte


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

    def pagar(self, valor):
        if valor > 0 and self.saldo >= valor:
            self.saldo -= valor
            self.registrar_historico("Pagamento Boleto 📄", -valor)
            return True
        return False

    def transferir(self, valor, conta_destino):
        if valor > 0 and self.saldo >= valor:
            self.saldo -= valor
            self.registrar_historico("Transf. Enviada 📤", -valor)
            conta_destino.saldo += valor
            conta_destino.registrar_historico(f"Transf. Recebida 📥 ({self.nome})", valor)
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

    def pagar(self, valor):
        saldo_total = self.saldo + self.cheque_especial
        if valor > 0 and saldo_total >= valor:
            self.saldo -= valor
            self.registrar_historico("Pagamento Boleto 📄", -valor)
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
        if not conta_dest: return False, "Destino não encontrado."
        if conta_origem.cpf == cpf_destino: return False, "Operação inválida (mesma conta)."
        if conta_origem.transferir(valor, conta_dest):
            self.salvar_dados()
            return True, "Transferência realizada!"
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
# 🎨 PARTE 2: FRONTEND V4.2 (Validação)
# ==========================================

class AppBancario(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Itaú Clone (Senai Edition)")
        self.geometry("400x650")
        self.centralizar_janela(400, 650)
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("green")

        self.banco = BancoController()
        self.conta_logada = None
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        self.mostrar_tela_login()

    def centralizar_janela(self, l, a):
        x = (self.winfo_screenwidth() // 2) - (l // 2)
        y = (self.winfo_screenheight() // 2) - (a // 2)
        self.geometry(f"{l}x{a}+{x}+{y}")

    def limpar_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # --- TELA: LOGIN ---
    def mostrar_tela_login(self):
        self.limpar_container()
        frame = ctk.CTkFrame(self.container, fg_color="transparent")
        frame.pack(pady=80)

        # Logo simulado (laranja Itaú para testar)
        ctk.CTkLabel(frame, text="🟧", font=("Arial", 60)).pack(pady=10)
        ctk.CTkLabel(frame, text="Acesse sua conta", font=("Arial", 20, "bold")).pack(pady=5)

        self.entry_cpf = ctk.CTkEntry(frame, placeholder_text="CPF", width=250)
        self.entry_cpf.pack(pady=10)
        self.entry_senha = ctk.CTkEntry(frame, placeholder_text="Senha", show="*", width=250)
        self.entry_senha.pack(pady=10)

        ctk.CTkButton(frame, text="Acessar", width=250, fg_color="#EC7000", hover_color="#d66300",
                      command=self.fazer_login).pack(pady=20)
        ctk.CTkButton(frame, text="Abrir nova conta", width=250, fg_color="transparent", border_width=1,
                      command=self.mostrar_tela_cadastro).pack()

    def fazer_login(self):
        cpf = self.entry_cpf.get()
        senha = self.entry_senha.get()
        conta = self.banco.buscar_conta(cpf)
        if conta and conta.senha == senha:
            self.conta_logada = conta
            self.mostrar_dashboard()
        else:
            messagebox.showerror("Ops", "Dados incorretos. Tente novamente.")

    # --- TELA: CADASTRO (MELHORADA V4.2) ---
    def mostrar_tela_cadastro(self):
        self.limpar_container()
        frame = ctk.CTkFrame(self.container, fg_color="transparent")
        frame.pack(pady=40)

        ctk.CTkLabel(frame, text="Nova Conta ✨", font=("Arial", 22, "bold")).pack(pady=10)

        entry_nome = ctk.CTkEntry(frame, placeholder_text="Nome Completo", width=250)
        entry_nome.pack(pady=5)
        entry_cpf = ctk.CTkEntry(frame, placeholder_text="CPF (apenas números)", width=250)
        entry_cpf.pack(pady=5)

        # Tooltip visual sobre a senha
        ctk.CTkLabel(frame, text="Senha: 8+ carac, Maiusc, Minusc, Especial", font=("Arial", 10),
                     text_color="gray").pack()
        entry_senha = ctk.CTkEntry(frame, placeholder_text="Sua Senha Forte", width=250)
        entry_senha.pack(pady=5)

        tipo_var = ctk.StringVar(value="1")
        ctk.CTkSwitch(frame, text="Conta Poupança?", variable=tipo_var, onvalue="2", offvalue="1",
                      progress_color="#EC7000").pack(pady=15)

        # LABEL DE ERRO (Invisível no início)
        lbl_erro = ctk.CTkLabel(frame, text="", text_color="#FF5555", font=("Arial", 12))
        lbl_erro.pack(pady=5)

        def validar_senha_forte(senha):
            # Regex: Pelo menos 1 minuscula, 1 maiuscula, 1 digito/especial, min 8 chars
            padrao = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[\W_]).{8,}$"
            return re.match(padrao, senha)

        def confirmar():
            nome = entry_nome.get().strip()
            cpf = entry_cpf_cad = entry_cpf.get().strip()
            senha = entry_senha.get().strip()

            # 1. Validação de Campos Vazios
            if not nome or not cpf or not senha:
                lbl_erro.configure(text="⚠️ Preencha todos os campos!")
                return

            # 2. Validação de Senha Forte
            if not validar_senha_forte(senha):
                lbl_erro.configure(text="⚠️ Senha fraca! Use Maiúscula, Minúscula e Símbolo.")
                return

            # 3. Tentativa de Criação
            if self.banco.criar_conta_nova(nome, cpf, senha, tipo_var.get()):
                messagebox.showinfo("Sucesso", "Conta criada! Faça login.")
                self.mostrar_tela_login()
            else:
                lbl_erro.configure(text="⚠️ CPF já cadastrado.")

        ctk.CTkButton(frame, text="Confirmar Abertura", width=250, fg_color="#EC7000", hover_color="#d66300",
                      command=confirmar).pack(pady=10)
        ctk.CTkButton(frame, text="Voltar", width=250, fg_color="gray", command=self.mostrar_tela_login).pack()

    # --- TELA: DASHBOARD (Principal) ---
    def mostrar_dashboard(self):
        self.limpar_container()
        topo = ctk.CTkFrame(self.container, fg_color="#1e1e1e", corner_radius=0)
        topo.pack(fill="x", ipady=20)

        primeiro_nome = self.conta_logada.nome.split()[0].title()
        ctk.CTkLabel(topo, text=f"Olá, {primeiro_nome}", font=("Arial", 16)).pack()
        ctk.CTkLabel(topo, text=f"R$ {self.conta_logada.saldo:.2f}", font=("Arial", 36, "bold"),
                     text_color="#EC7000").pack(pady=5)

        # Botão discreto de 'olho' para esconder saldo seria legal depois
        ctk.CTkLabel(topo, text="saldo disponível", font=("Arial", 12), text_color="gray").pack()

        grid = ctk.CTkFrame(self.container, fg_color="transparent")
        grid.pack(pady=30)

        def criar_botao(txt, icone, cmd, l, c):
            b = ctk.CTkButton(grid, text=f"{icone}\n{txt}", width=100, height=80,
                              font=("Arial", 13), fg_color="#2b2b2b", hover_color="#3a3a3a", command=cmd)
            b.grid(row=l, column=c, padx=8, pady=8)

        criar_botao("Pix", "💠", lambda: self.tela_transacao("Transferência"), 0, 0)
        criar_botao("Pagar", "📄", lambda: self.tela_transacao("Pagamento"), 0, 1)
        criar_botao("Depositar", "💰", lambda: self.tela_transacao("Depósito"), 1, 0)
        criar_botao("Sacar", "💸", lambda: self.tela_transacao("Saque"), 1, 1)
        criar_botao("Extrato", "📜", self.mostrar_extrato, 2, 0)
        criar_botao("Ajuda", "❓", self.mostrar_ajuda, 2, 1)

        ctk.CTkButton(self.container, text="Sair da Conta", fg_color="transparent", border_width=1, border_color="gray",
                      width=200, command=self.mostrar_tela_login).pack(side="bottom", pady=30)

    # --- TELA GENÉRICA: TRANSAÇÕES ---
    def tela_transacao(self, tipo):
        self.limpar_container()
        ctk.CTkLabel(self.container, text=tipo, font=("Arial", 22, "bold")).pack(pady=30)

        entry_dest = None
        if tipo == "Transferência":
            ctk.CTkComboBox(self.container, values=["Chave Pix", "CPF", "Agência/Conta"], width=250).pack(pady=5)
            entry_dest = ctk.CTkEntry(self.container, placeholder_text="Chave ou Dados", width=250)
            entry_dest.pack(pady=10)

        entry_val = ctk.CTkEntry(self.container, placeholder_text="R$ 0,00", width=250)
        entry_val.pack(pady=10)

        def confirmar():
            try:
                v = float(entry_val.get())
                ok, msg = False, ""
                if tipo == "Depósito":
                    ok = self.conta_logada.depositar(v)
                    msg = "Depósito realizado!"
                elif tipo == "Saque":
                    ok = self.conta_logada.sacar(v)
                    msg = "Saque realizado!" if ok else "Saldo insuficiente"
                elif tipo == "Pagamento":
                    ok = self.conta_logada.pagar(v)
                    msg = "Conta Paga!" if ok else "Saldo insuficiente"
                elif tipo == "Transferência":
                    ok, msg = self.banco.realizar_transferencia(self.conta_logada, entry_dest.get(), v)

                if ok:
                    self.banco.salvar_dados()
                    messagebox.showinfo("Sucesso", msg)
                    self.mostrar_dashboard()
                else:
                    messagebox.showerror("Erro", msg)
            except:
                messagebox.showerror("Erro", "Valor inválido")

        ctk.CTkButton(self.container, text="Confirmar", width=250, fg_color="#EC7000", hover_color="#d66300",
                      command=confirmar).pack(pady=20)
        ctk.CTkButton(self.container, text="Cancelar", fg_color="gray", width=250,
                      command=self.mostrar_dashboard).pack()

    def mostrar_extrato(self):
        self.limpar_container()
        ctk.CTkLabel(self.container, text="Extrato", font=("Arial", 22, "bold")).pack(pady=20)
        scroll = ctk.CTkScrollableFrame(self.container, width=350, height=400)
        scroll.pack()
        if not self.conta_logada.historico:
            ctk.CTkLabel(scroll, text="Sem movimentações").pack(pady=20)
        for item in reversed(self.conta_logada.historico):
            c = "#2CC985" if item['valor'] > 0 else "white"
            fr = ctk.CTkFrame(scroll, fg_color="#2b2b2b")
            fr.pack(fill="x", pady=5, padx=5)
            ctk.CTkLabel(fr, text=item['operacao'], font=("Arial", 12, "bold")).pack(side="left", padx=10, pady=10)
            ctk.CTkLabel(fr, text=f"R$ {item['valor']:.2f}", text_color=c).pack(side="right", padx=10)
        ctk.CTkButton(self.container, text="Voltar", width=250, fg_color="gray", command=self.mostrar_dashboard).pack(
            pady=20)

    def mostrar_ajuda(self):
        self.limpar_container()
        ctk.CTkLabel(self.container, text="Atendimento", font=("Arial", 22)).pack(pady=20)
        msg = "Precisa de ajuda?\nLigue para nossa central.\n\n0800 728 0728"
        ctk.CTkLabel(self.container, text=msg).pack(pady=20)
        ctk.CTkButton(self.container, text="Voltar", width=250, command=self.mostrar_dashboard).pack()


if __name__ == "__main__":
    app = AppBancario()
    app.mainloop()