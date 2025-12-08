import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import re
import os
from PIL import Image, ImageTk
from backend.controller import BancoController

# --- PALETA DE CORES ---
COR_PRIMARIA = "#00E676"
COR_TEXTO = "#FFFFFF"
COR_ERRO = "#FF5252"
COR_INPUTS = "#1E1E1E"


class ZenBankApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🍃 ZenBank Digital")
        self.geometry("400x750")
        self._centralizar()
        ctk.set_appearance_mode("Dark")

        self.banco = BancoController()
        self.conta_logada = None
        self.imgs = self._carregar_assets()
        self.bg_photo = None

        self.canvas = tk.Canvas(self, width=400, height=750, highlightthickness=0, bg="black")
        self.canvas.pack(fill="both", expand=True)
        self.bg_item = self.canvas.create_image(0, 0, image=None, anchor="nw")

        self.bind("<Configure>", self._ao_redimensionar)
        self.tela_splash()

    def _centralizar(self):
        l, a = 400, 750
        x = (self.winfo_screenwidth() // 2) - (l // 2)
        y = (self.winfo_screenheight() // 2) - (a // 2)
        self.geometry(f"{l}x{a}+{x}+{y}")

    def _get_path(self, filename):
        return os.path.join(os.path.dirname(__file__), "assets", filename)

    def _carregar_assets(self):
        assets = {}
        try:
            bg_path = self._get_path("fundo.jpg")
            if not os.path.exists(bg_path): bg_path = self._get_path("fundo.png")
            if os.path.exists(bg_path): assets['pil_bg'] = Image.open(bg_path)

            logo_path = self._get_path("logo.png")
            if os.path.exists(logo_path):
                pil_logo = Image.open(logo_path).resize((130, 130), Image.LANCZOS)
                assets['logo_canvas'] = ImageTk.PhotoImage(pil_logo)
                assets['logo_ctk'] = ctk.CTkImage(Image.open(logo_path), size=(100, 100))

            def load_icon(name, size=(30, 30)):
                p = self._get_path(name)
                if os.path.exists(p): return ctk.CTkImage(Image.open(p), size=size)
                return None

            assets['pix'] = load_icon("pix.png")
            assets['barcode'] = load_icon("barcode.png")
            assets['saque'] = load_icon("money.png")
            assets['card'] = load_icon("card.png")
            assets['deposito'] = load_icon("deposito.png")
            assets['transferencia'] = load_icon("transferencia.png")
            assets['menu'] = load_icon("menu.png", size=(24, 24))

        except:
            pass
        return assets

    def _ao_redimensionar(self, event):
        if 'pil_bg' in self.imgs:
            if event.widget == self and (event.width > 100 and event.height > 100):
                img_resized = self.imgs['pil_bg'].resize((event.width, event.height), Image.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(img_resized)
                self.canvas.itemconfig(self.bg_item, image=self.bg_photo)
                self.canvas.tag_lower(self.bg_item)

    def limpar_conteudo(self):
        self.canvas.delete("ui")
        for widget in self.canvas.winfo_children(): widget.destroy()
        self.canvas.tag_lower(self.bg_item)

    def add_widget(self, relx, rely, widget, anchor="center"):
        widget.place(relx=relx, rely=rely, anchor=anchor)

    def formatar_moeda(self, valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # ================= TELAS =================

    def tela_splash(self):
        self.limpar_conteudo()
        cx, cy = 200, 375
        if 'logo_canvas' in self.imgs:
            self.canvas.create_image(cx, cy - 100, image=self.imgs['logo_canvas'], tags="ui")
        self.canvas.create_text(cx, cy + 20, text="ZenBank", fill="white", font=("Helvetica", 45, "bold"), tags="ui")
        self.canvas.create_text(cx, cy + 60, text="Fique Zen com suas finanças", fill=COR_PRIMARIA, font=("Arial", 14),
                                tags="ui")
        bar = ctk.CTkProgressBar(self.canvas, width=220, progress_color=COR_PRIMARIA, fg_color="#333")
        self.add_widget(0.5, 0.65, bar)
        bar.set(0)
        bar.start()
        self.after(3500, self.tela_login)

    def tela_login(self):
        self.limpar_conteudo()
        cx = 200
        if 'logo_canvas' in self.imgs:
            self.canvas.create_image(cx, 80, image=self.imgs['logo_canvas'], tags="ui")

        self.canvas.create_text(cx, 160, text="ZenBank", fill="white", font=("Helvetica", 36, "bold"), tags="ui")
        self.canvas.create_text(cx, 195, text="Fique Zen com suas finanças", fill="gray", font=("Arial", 12), tags="ui")
        self.canvas.create_text(cx, 260, text="Acesse sua conta", fill="white", font=("Arial", 16), tags="ui")

        self.ent_cpf = ctk.CTkEntry(self.canvas, placeholder_text="👤 CPF (Números)", width=300, height=50, fg_color=COR_INPUTS,
                                    border_width=0, corner_radius=12, text_color="white")
        self.add_widget(0.5, 0.42, self.ent_cpf)

        self.ent_senha = ctk.CTkEntry(self.canvas, placeholder_text="🔐 Senha", show="*", width=300, height=50,
                                      fg_color=COR_INPUTS, border_width=0, corner_radius=12, text_color="white")
        self.add_widget(0.5, 0.52, self.ent_senha)

        self.lbl_erro = ctk.CTkLabel(self.canvas, text="", text_color=COR_ERRO, fg_color="transparent")
        self.add_widget(0.5, 0.70, self.lbl_erro)

        btn_entrar = ctk.CTkButton(self.canvas, text="ENTRAR", width=300, height=50, fg_color=COR_PRIMARIA,
                                   text_color="black", font=("Arial", 15, "bold"), corner_radius=12,
                                   hover_color="#00C853", command=self.login)
        self.add_widget(0.5, 0.62, btn_entrar)

        self.canvas.create_text(cx, 570, text="ou abra sua conta agora", fill="gray", font=("Arial", 12), tags="ui")

        btn_criar = ctk.CTkButton(self.canvas, text="Criar nova conta", fg_color="transparent", text_color=COR_PRIMARIA,
                                  hover_color="#111", border_width=1, border_color=COR_PRIMARIA, height=45, width=300,
                                  corner_radius=15, command=self.tela_cadastro)
        self.add_widget(0.5, 0.82, btn_criar)

    def tela_cadastro(self):
        self.limpar_conteudo()
        cx = 200
        self.add_widget(0.1, 0.05, ctk.CTkButton(self.canvas, text="⬅️ Voltar", width=80, fg_color="transparent",
                                                 text_color="white", command=self.tela_login, anchor="w"), anchor="w")

        self.canvas.create_text(cx, 80, text="Nova Conta ✨", fill="white", font=("Arial", 28, "bold"), tags="ui")
        y, gap = 0.22, 0.08

        self.ent_nome = ctk.CTkEntry(self.canvas, placeholder_text="📝 Nome Completo", width=300, height=45,
                                     fg_color=COR_INPUTS, border_width=0, corner_radius=10)
        self.add_widget(0.5, y, self.ent_nome)

        self.ent_cpf_cad = ctk.CTkEntry(self.canvas, placeholder_text="👤 CPF (números)", width=300, height=45,
                                        fg_color=COR_INPUTS, border_width=0, corner_radius=10)
        self.add_widget(0.5, y + gap, self.ent_cpf_cad)

        self.ent_s1 = ctk.CTkEntry(self.canvas, placeholder_text="🔐 Senha (min 8 chars)", show="*", width=300,
                                   height=45, fg_color=COR_INPUTS, border_width=0, corner_radius=10)
        self.add_widget(0.5, y + gap * 2, self.ent_s1)

        self.ent_s2 = ctk.CTkEntry(self.canvas, placeholder_text="🔐 Repetir Senha", show="*", width=300, height=45,
                                   fg_color=COR_INPUTS, border_width=0, corner_radius=10)
        self.add_widget(0.5, y + gap * 3, self.ent_s2)

        self.tipo_var = ctk.StringVar(value="1")
        sw = ctk.CTkSwitch(self.canvas, text="É Conta Poupança?", variable=self.tipo_var, onvalue="2", offvalue="1",
                           progress_color=COR_PRIMARIA, text_color="white")
        self.add_widget(0.5, y + gap * 4, sw)

        self.lbl_feed = ctk.CTkLabel(self.canvas, text="", font=("Arial", 12), fg_color="transparent")
        self.add_widget(0.5, y + gap * 4.7, self.lbl_feed)

        btn_cad = ctk.CTkButton(self.canvas, text="FINALIZAR", width=300, height=50, fg_color=COR_PRIMARIA,
                                text_color="black", font=("Arial", 15, "bold"), command=self.confirmar)
        self.add_widget(0.5, 0.85, btn_cad)

    def tela_dashboard(self):
        self.limpar_conteudo()
        nome = self.conta_logada.nome.split()[0].title()
        self.canvas.create_text(30, 80, text=f"Olá, {nome} 👋", fill="white", font=("Arial", 20, "bold"), anchor="w",
                                tags="ui")

        # Menu Sanduiche
        img_menu = self.imgs.get('menu')
        btn_menu = ctk.CTkButton(self.canvas, text="", image=img_menu, width=40, height=40, fg_color="transparent",
                                 hover_color="#333", command=self.tela_configuracoes)
        if not img_menu: btn_menu.configure(text="☰")
        self.add_widget(0.90, 0.05, btn_menu)

        self.canvas.create_text(30, 120, text="Saldo disponível", fill="gray", font=("Arial", 14), anchor="w",
                                tags="ui")
        saldo_texto = self.formatar_moeda(self.conta_logada.saldo)
        font_size = 44 if len(saldo_texto) <= 12 else 30
        self.lbl_saldo = ctk.CTkLabel(self.canvas, text=saldo_texto, font=("Arial", font_size, "bold"),
                                      text_color=COR_PRIMARIA, fg_color="transparent")
        self.add_widget(0.08, 0.22, self.lbl_saldo, anchor="w")

        start_y, gap = 0.35, 0.10
        botoes = [
            ("Área Pix", "pix", lambda: self.tela_transacao("Pix")),
            ("Pagar Boleto", "barcode", lambda: self.tela_transacao("Pagamento")),
            ("Transferir", "transferencia", lambda: self.tela_transacao("Transferência")),
            ("Depositar", "deposito", lambda: self.tela_transacao("Depósito")),
            ("Sacar", "saque", lambda: self.tela_transacao("Saque")),
            ("Ver Extrato", "card", self.tela_extrato)
        ]

        for i, (texto, icone, comando) in enumerate(botoes):
            img = self.imgs.get(icone)
            if not img and self.imgs.get('logo_ctk'): img = self.imgs.get('logo_ctk')
            btn = ctk.CTkButton(self.canvas, text=f"  {texto}", image=img, compound="left", width=340, height=60,
                                fg_color=COR_INPUTS, hover_color="#333", anchor="w", font=("Arial", 16, "bold"),
                                command=comando, corner_radius=15)
            self.add_widget(0.5, start_y + (i * gap), btn)

    # --- TELA EDITAR PERFIL ---
    def tela_configuracoes(self):
        self.limpar_conteudo()
        self.add_widget(0.1, 0.05, ctk.CTkButton(self.canvas, text="⬅️ Voltar", width=80, fg_color="transparent",
                                                 command=self.tela_dashboard, anchor="w"), anchor="w")
        self.canvas.create_text(200, 100, text="Configurações ⚙️", fill="white", font=("Arial", 28, "bold"), tags="ui")

        btn_editar = ctk.CTkButton(self.canvas, text="👤  Editar Perfil", width=340, height=60,
                                   fg_color=COR_INPUTS, hover_color="#333", font=("Arial", 16), anchor="w",
                                   command=self.tela_editar_perfil)
        self.add_widget(0.5, 0.30, btn_editar)

        btn_excluir = ctk.CTkButton(self.canvas, text="🗑️  Excluir Conta", width=340, height=60,
                                    fg_color="#330000", hover_color="#550000", text_color=COR_ERRO,
                                    font=("Arial", 16, "bold"), anchor="w", command=self.confirmar_exclusao)
        self.add_widget(0.5, 0.85, btn_excluir)

        btn_sair = ctk.CTkButton(self.canvas, text="⏻  Sair do App", width=340, height=60, fg_color=COR_INPUTS,
                                 hover_color="#333", text_color=COR_ERRO, font=("Arial", 16), anchor="w",
                                 command=self.tela_login)
        self.add_widget(0.5, 0.42, btn_sair)

    def tela_editar_perfil(self):
        self.limpar_conteudo()
        self.add_widget(0.1, 0.05, ctk.CTkButton(self.canvas, text="⬅️ Voltar", width=80, fg_color="transparent",
                                                 command=self.tela_configuracoes, anchor="w"), anchor="w")
        self.canvas.create_text(200, 80, text="Editar Perfil 📝", fill="white", font=("Arial", 28, "bold"), tags="ui")

        # Labels menores e espaçados
        y, gap = 0.20, 0.12

        self.canvas.create_text(50, 140, text="Nome Completo", fill="gray", font=("Arial", 11), anchor="w", tags="ui")
        self.ent_nome_edit = ctk.CTkEntry(self.canvas, width=300, height=40, fg_color=COR_INPUTS, border_width=0,
                                          corner_radius=10)
        self.ent_nome_edit.insert(0, self.conta_logada.nome)
        self.add_widget(0.5, y + 0.04, self.ent_nome_edit)

        self.canvas.create_text(50, 220, text="CPF (Fixo)", fill="gray", font=("Arial", 11), anchor="w", tags="ui")
        self.ent_cpf_edit = ctk.CTkEntry(self.canvas, width=300, height=40, fg_color="#111", border_width=0,
                                         corner_radius=10, state="readonly")
        self.ent_cpf_edit.insert(0, self.conta_logada.cpf)
        self.add_widget(0.5, y + gap + 0.02, self.ent_cpf_edit)

        self.canvas.create_text(50, 300, text="Telefone", fill="gray", font=("Arial", 11), anchor="w", tags="ui")
        tel = getattr(self.conta_logada, 'telefone', '')
        self.ent_tel_edit = ctk.CTkEntry(self.canvas, placeholder_text="📱 (xx) xxxx-xxxx", width=300, height=40,
                                         fg_color=COR_INPUTS, border_width=0, corner_radius=10)
        self.ent_tel_edit.insert(0, tel)
        self.add_widget(0.5, y + gap * 1.6 + 0.06, self.ent_tel_edit)

        self.canvas.create_text(50, 380, text="Nova Senha (Opcional)", fill="gray", font=("Arial", 11), anchor="w",
                                tags="ui")
        self.ent_senha_edit = ctk.CTkEntry(self.canvas, placeholder_text="🔐 Nova Senha", show="*", width=300, height=40,
                                           fg_color=COR_INPUTS, border_width=0, corner_radius=10)
        self.add_widget(0.5, y + gap * 2.6 + 0.05, self.ent_senha_edit)

        self.lbl_feed_edit = ctk.CTkLabel(self.canvas, text="", font=("Arial", 12), fg_color="transparent")
        self.add_widget(0.5, 0.74, self.lbl_feed_edit)

        btn_salvar = ctk.CTkButton(self.canvas, text="SALVAR ALTERAÇÕES", width=300, height=50, fg_color=COR_PRIMARIA,
                                   text_color="black", font=("Arial", 15, "bold"), command=self.salvar_edicao)
        self.add_widget(0.5, 0.68, btn_salvar)

    def salvar_edicao(self):
        novo_nome = self.ent_nome_edit.get()
        nova_senha = self.ent_senha_edit.get()
        novo_tel = self.ent_tel_edit.get()

        if not novo_nome.strip():
            self.lbl_feed_edit.configure(text="Nome obrigatório", text_color=COR_ERRO)
            return

        ok, msg = self.banco.atualizar_conta(self.conta_logada.cpf, novo_nome, nova_senha, novo_tel)
        if ok:
            self.conta_logada = self.banco.buscar_conta(self.conta_logada.cpf)
            self.lbl_feed_edit.configure(text="✅ " + msg, text_color=COR_PRIMARIA)
            self.after(1500, self.tela_dashboard)
        else:
            self.lbl_feed_edit.configure(text="❌ " + msg, text_color=COR_ERRO)

    def confirmar_exclusao(self):
        if messagebox.askyesno("Excluir Conta", "Tem certeza? Isso apagará tudo permanentemente!"):
            if self.banco.excluir_conta(self.conta_logada.cpf):
                messagebox.showinfo("ZenBank", "Conta excluída.")
                self.conta_logada = None
                self.tela_login()
            else:
                messagebox.showerror("Erro", "Falha ao excluir.")

    # --- TRANSAÇÃO E EXTRATO (Iguais V7.6) ---
    def tela_transacao(self, tipo):
        self.limpar_conteudo()
        self.add_widget(0.1, 0.05, ctk.CTkButton(self.canvas, text="⬅️ Cancelar", width=80, fg_color="transparent",
                                                 command=self.tela_dashboard, anchor="w"), anchor="w")
        self.canvas.create_text(200, 120, text=tipo, fill=COR_PRIMARIA, font=("Arial", 32, "bold"), tags="ui")
        y_pos = 0.35
        self.ent_dest = None
        if tipo in ["Pix", "Transferência"]:
            self.ent_dest = ctk.CTkEntry(self.canvas, placeholder_text="🔑 Chave / Conta", width=300, height=50,
                                         fg_color=COR_INPUTS, border_width=0, font=("Arial", 16))
            self.add_widget(0.5, y_pos, self.ent_dest)
            y_pos += 0.12
        self.ent_val = ctk.CTkEntry(self.canvas, placeholder_text="R$ 0,00", width=300, height=50, fg_color=COR_INPUTS,
                                    border_width=0, font=("Arial", 20, "bold"))
        self.add_widget(0.5, y_pos, self.ent_val)
        self.lbl_msg = ctk.CTkLabel(self.canvas, text="", font=("Arial", 14, "bold"), fg_color="transparent")
        self.add_widget(0.5, y_pos + 0.10, self.lbl_msg)
        btn_conf = ctk.CTkButton(self.canvas, text="CONFIRMAR", width=300, height=50, fg_color=COR_PRIMARIA,
                                 text_color="black", font=("Arial", 16, "bold"),
                                 command=lambda: self.processar_transacao(tipo))
        self.add_widget(0.5, 0.80, btn_conf)

    def tela_extrato(self):
        self.limpar_conteudo()
        self.add_widget(0.1, 0.05, ctk.CTkButton(self.canvas, text="⬅️ Voltar", width=80, fg_color="transparent",
                                                 command=self.tela_dashboard, anchor="w"), anchor="w")
        self.canvas.create_text(200, 100, text="Extrato", fill="white", font=("Arial", 32, "bold"), tags="ui")
        historico_recente = list(reversed(self.conta_logada.historico))[:6]
        y_start = 180
        if not historico_recente: self.canvas.create_text(200, 300, text="Nenhuma movimentação.", fill="gray",
                                                          font=("Arial", 14), tags="ui")
        for item in historico_recente:
            v = item['valor']
            c = COR_PRIMARIA if v > 0 else COR_ERRO
            s = "+" if v > 0 else ""
            txt = item['operacao']
            val = f"{s} {self.formatar_moeda(abs(v))}"
            self.canvas.create_line(50, y_start, 350, y_start, fill="#333", tags="ui")
            self.canvas.create_text(50, y_start + 25, text=txt, fill="white", font=("Arial", 14, "bold"), anchor="w",
                                    tags="ui")
            self.canvas.create_text(350, y_start + 25, text=val, fill=c, font=("Arial", 14, "bold"), anchor="e",
                                    tags="ui")
            y_start += 60

    # --- LÓGICA AUXILIAR ---
    def login(self):
        c = self.banco.buscar_conta(self.ent_cpf.get())
        if c and c.senha == self.ent_senha.get():
            self.conta_logada = c
            self.tela_dashboard()
        else:
            self.lbl_erro.configure(text="Dados inválidos")

    def confirmar(self):
        n, c, s1, s2 = self.ent_nome.get(), self.ent_cpf_cad.get(), self.ent_s1.get(), self.ent_s2.get()
        if not n or not c or not s1: return self.lbl_feed.configure(text="Preencha tudo", text_color=COR_ERRO)
        if s1 != s2: return self.lbl_feed.configure(text="Senhas não conferem", text_color=COR_ERRO)
        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[\W_]).{8,}$", s1): return self.lbl_feed.configure(
            text="Senha fraca", text_color=COR_ERRO)
        if self.banco.criar_conta(n, c, s1, self.tipo_var.get()):
            self.lbl_feed.configure(text="Sucesso!", text_color=COR_PRIMARIA)
            self.after(2000, self.tela_login)
        else:
            self.lbl_feed.configure(text="CPF já existe", text_color=COR_ERRO)

    def processar_transacao(self, tipo):
        try:
            val_str = self.ent_val.get().replace(".", "").replace(",", ".")
            v = float(val_str)
            ok, msg = False, ""
            dest = self.ent_dest.get() if self.ent_dest else None
            if tipo in ["Pix", "Transferência"]:
                ok, msg = self.banco.realizar_transferencia(self.conta_logada, dest, v)
            elif tipo == "Depósito":
                ok, msg = self.conta_logada.depositar(v), "Sucesso!"
            elif tipo == "Saque":
                ok, msg = self.conta_logada.sacar(v), "Sucesso!"
            elif tipo == "Pagamento":
                ok, msg = self.conta_logada.pagar(v), "Pago!"
            if ok:
                self.banco.salvar_dados()
                self.lbl_msg.configure(text=f"✅ {msg}", text_color=COR_PRIMARIA)
                self.after(2000, self.tela_dashboard)
            else:
                self.lbl_msg.configure(text=f"❌ {msg if msg else 'Erro'}", text_color=COR_ERRO)
        except:
            self.lbl_msg.configure(text="❌ Valor inválido", text_color=COR_ERRO)


if __name__ == "__main__":
    app = ZenBankApp()
    app.mainloop()