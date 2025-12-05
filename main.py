import customtkinter as ctk
from tkinter import messagebox
import re
# Importa o controlador na pasta backend
from backend.controller import BancoController

# --- PALETA DE CORES ZEN ---
COR_FUNDO = "#1E1E1E"  # Cinza Dark Zen
COR_PRIMARIA = "#2CC985"  # Verde Jade (Zen)
COR_TEXTO = "#E0E0E0"  # Branco Suave
COR_BOTAO = "#2b2b2b"  # Botões Secundários
COR_ERRO = "#FF6B6B"  # Vermelho Pastel


class ZenBankApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ZenBank 🍃")
        self.geometry("400x700")
        self._centralizar()

        # Tema Personalizado
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("green")

        self.banco = BancoController()
        self.conta_logada = None
        self.container = ctk.CTkFrame(self, fg_color=COR_FUNDO)
        self.container.pack(fill="both", expand=True)

        self.tela_login()

    def _centralizar(self):
        l, a = 400, 700
        x = (self.winfo_screenwidth() // 2) - (l // 2)
        y = (self.winfo_screenheight() // 2) - (a // 2)
        self.geometry(f"{l}x{a}+{x}+{y}")

    def limpar(self):
        for w in self.container.winfo_children(): w.destroy()

    # --- TELAS ---
    def tela_login(self):
        self.limpar()
        fr = ctk.CTkFrame(self.container, fg_color="transparent")
        fr.pack(pady=100)

        ctk.CTkLabel(fr, text="⭕", font=("Arial", 70), text_color=COR_PRIMARIA).pack()
        ctk.CTkLabel(fr, text="ZenBank", font=("Helvetica", 30, "bold"), text_color=COR_PRIMARIA).pack(pady=5)
        ctk.CTkLabel(fr, text="Fique Zen com suas finanças", font=("Arial", 12), text_color="gray").pack(pady=20)

        self.ent_cpf = ctk.CTkEntry(fr, placeholder_text="CPF", width=260, height=40)
        self.ent_cpf.pack(pady=10)
        self.ent_senha = ctk.CTkEntry(fr, placeholder_text="Senha", show="*", width=260, height=40)
        self.ent_senha.pack(pady=10)

        ctk.CTkButton(fr, text="Entrar", width=260, height=40, fg_color=COR_PRIMARIA, hover_color="#26af74",
                      text_color="#000", font=("Arial", 14, "bold"), command=self.login).pack(pady=20)
        ctk.CTkButton(fr, text="Criar Conta", width=260, fg_color="transparent", border_width=1,
                      border_color=COR_PRIMARIA, text_color=COR_PRIMARIA, command=self.tela_cadastro).pack()

    def tela_cadastro(self):
        self.limpar()
        fr = ctk.CTkFrame(self.container, fg_color="transparent")
        fr.pack(pady=50)

        ctk.CTkLabel(fr, text="Boas Vindas 🍃", font=("Arial", 24, "bold"), text_color=COR_PRIMARIA).pack(pady=20)

        ent_nome = ctk.CTkEntry(fr, placeholder_text="Nome Completo", width=260)
        ent_nome.pack(pady=5)
        ent_cpf = ctk.CTkEntry(fr, placeholder_text="CPF", width=260)
        ent_cpf.pack(pady=5)
        ent_senha = ctk.CTkEntry(fr, placeholder_text="Senha Forte", width=260)
        ent_senha.pack(pady=5)

        tipo_var = ctk.StringVar(value="1")
        ctk.CTkSwitch(fr, text="Conta Poupança?", variable=tipo_var, onvalue="2", offvalue="1",
                      progress_color=COR_PRIMARIA).pack(pady=15)

        lbl_erro = ctk.CTkLabel(fr, text="", text_color=COR_ERRO, font=("Arial", 12))
        lbl_erro.pack(pady=5)

        def confirmar():
            nome, cpf, senha = ent_nome.get(), ent_cpf.get(), ent_senha.get()
            if not nome or not cpf or not senha:
                lbl_erro.configure(text="Preencha todos os campos")
                return
            if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[\W_]).{8,}$", senha):
                lbl_erro.configure(text="Senha fraca (Use Maiusc, Minusc, Símbolo)")
                return

            if self.banco.criar_conta(nome, cpf, senha, tipo_var.get()):
                messagebox.showinfo("ZenBank", "Conta criada com harmonia! 🙏")
                self.tela_login()
            else:
                lbl_erro.configure(text="CPF já existe no sistema")

        ctk.CTkButton(fr, text="Cadastrar", width=260, fg_color=COR_PRIMARIA, text_color="#000",
                      command=confirmar).pack(pady=20)
        ctk.CTkButton(fr, text="Voltar", width=260, fg_color="transparent", text_color="gray",
                      command=self.tela_login).pack()

    def tela_dashboard(self):
        self.limpar()

        # Header Zen
        head = ctk.CTkFrame(self.container, fg_color="#252525", corner_radius=0, height=150)
        head.pack(fill="x")

        ctk.CTkLabel(head, text=f"Olá, {self.conta_logada.nome.split()[0]}", font=("Arial", 18)).pack(pady=(30, 5))
        ctk.CTkLabel(head, text=f"R$ {self.conta_logada.saldo:.2f}", font=("Arial", 40, "bold"),
                     text_color=COR_PRIMARIA).pack(pady=5)

        # Grid de Botões
        grid = ctk.CTkFrame(self.container, fg_color="transparent")
        grid.pack(pady=40)

        def btn_menu(txt, icone, cmd, r, c):
            b = ctk.CTkButton(grid, text=f"{icone}\n{txt}", width=110, height=90,
                              fg_color=COR_BOTAO, hover_color="#333", font=("Arial", 13), command=cmd)
            b.grid(row=r, column=c, padx=10, pady=10)

        btn_menu("Pix", "💠", lambda: self.tela_transacao("Pix"), 0, 0)
        btn_menu("Pagar", "📄", lambda: self.tela_transacao("Pagamento"), 0, 1)
        btn_menu("Depositar", "💰", lambda: self.tela_transacao("Depósito"), 1, 0)
        btn_menu("Sacar", "💸", lambda: self.tela_transacao("Saque"), 1, 1)
        btn_menu("Extrato", "📜", self.tela_extrato, 2, 0)
        btn_menu("Ajuda", "🍃", lambda: messagebox.showinfo("Ajuda", "Respire fundo..."), 2, 1)

        ctk.CTkButton(self.container, text="Sair", fg_color="transparent", text_color=COR_ERRO,
                      command=self.tela_login).pack(side="bottom", pady=30)

    # --- LÓGICA DE LOGIN E TRANSAÇÃO ---
    def login(self):
        conta = self.banco.buscar_conta(self.ent_cpf.get())
        if conta and conta.senha == self.ent_senha.get():
            self.conta_logada = conta
            self.tela_dashboard()
        else:
            messagebox.showerror("Erro", "Dados incorretos")

    def tela_transacao(self, tipo):
        self.limpar()
        ctk.CTkLabel(self.container, text=tipo, font=("Arial", 22, "bold"), text_color=COR_PRIMARIA).pack(pady=40)

        ent_dest = None
        if tipo == "Pix":
            ent_dest = ctk.CTkEntry(self.container, placeholder_text="Chave Pix (CPF)", width=260)
            ent_dest.pack(pady=10)

        ent_val = ctk.CTkEntry(self.container, placeholder_text="Valor R$", width=260)
        ent_val.pack(pady=10)

        def confirmar():
            try:
                v = float(ent_val.get())
                ok, msg = False, ""
                if tipo == "Pix":
                    ok, msg = self.banco.realizar_transferencia(self.conta_logada, ent_dest.get(), v)
                elif tipo == "Depósito":
                    ok, msg = self.conta_logada.depositar(v), "Sucesso!"
                elif tipo == "Saque":
                    ok, msg = self.conta_logada.sacar(v), "Sucesso!"
                elif tipo == "Pagamento":
                    ok, msg = self.conta_logada.pagar(v), "Conta Paga!"

                if ok:
                    self.banco.salvar_dados()
                    messagebox.showinfo("ZenBank", msg)
                    self.tela_dashboard()
                else:
                    messagebox.showerror("Erro", msg if msg else "Saldo insuficiente")
            except:
                messagebox.showerror("Erro", "Valor inválido")

        ctk.CTkButton(self.container, text="Confirmar", width=260, fg_color=COR_PRIMARIA, text_color="#000",
                      command=confirmar).pack(pady=20)
        ctk.CTkButton(self.container, text="Cancelar", width=260, fg_color="transparent",
                      command=self.tela_dashboard).pack()

    def tela_extrato(self):
        self.limpar()
        ctk.CTkLabel(self.container, text="Extrato Zen", font=("Arial", 22, "bold"), text_color=COR_PRIMARIA).pack(
            pady=20)
        scroll = ctk.CTkScrollableFrame(self.container, width=350, height=450, fg_color="#252525")
        scroll.pack()

        for item in reversed(self.conta_logada.historico):
            c = COR_PRIMARIA if item['valor'] > 0 else COR_ERRO
            fr = ctk.CTkFrame(scroll, fg_color="#333")
            fr.pack(fill="x", pady=5, padx=5)
            ctk.CTkLabel(fr, text=item['operacao'], font=("Arial", 12, "bold")).pack(side="left", padx=10, pady=10)
            ctk.CTkLabel(fr, text=f"R$ {item['valor']:.2f}", text_color=c).pack(side="right", padx=10)

        ctk.CTkButton(self.container, text="Voltar", fg_color="transparent", command=self.tela_dashboard).pack(pady=10)


if __name__ == "__main__":
    app = ZenBankApp()
    app.mainloop()