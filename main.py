import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import re
import os
from PIL import Image, ImageTk
from backend.controller import BancoController

# --- PALETA DE CORES ---
COR_PRIMARIA = "#00E676"  # Verde Neon
COR_TEXTO = "#FFFFFF"  # Branco
COR_ERRO = "#FF5252"  # Vermelho
COR_INPUTS = "#1E1E1E"  # Cor sólida para campos e botões


class ZenBankApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ZenBank Digital")
        self.geometry("400x750")
        self._centralizar()
        ctk.set_appearance_mode("Dark")
        self.configure(fg_color="#0a1a10")

        self.banco = BancoController()
        self.conta_logada = None

        self.imgs = self._carregar_assets()

        # CANVAS PRINCIPAL
        self.canvas = tk.Canvas(self, width=400, height=750, highlightthickness=0, bg="#0a1a10")
        self.canvas.pack(fill="both", expand=True)

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
            if os.path.exists(bg_path):
                pil_bg = Image.open(bg_path).resize((400, 750), Image.LANCZOS)
                assets['bg_canvas'] = ImageTk.PhotoImage(pil_bg)

            logo_path = self._get_path("logo.png")
            if os.path.exists(logo_path):
                pil_logo = Image.open(logo_path).resize((130, 130), Image.LANCZOS)
                assets['logo_canvas'] = ImageTk.PhotoImage(pil_logo)

            def load_ctk_icon(name):
                p = self._get_path(name)
                if os.path.exists(p):
                    i = Image.open(p)
                    return ctk.CTkImage(i, i, size=(30, 30))
                return None

            assets['pix'] = load_ctk_icon("pix.png")
            assets['barcode'] = load_ctk_icon("barcode.png")
            assets['saque'] = load_ctk_icon("money.png")
            assets['card'] = load_ctk_icon("card.png")
            assets['deposito'] = load_ctk_icon("deposito.png")
            assets['transferencia'] = load_ctk_icon("transferencia.png")
        except:
            pass
        return assets

    def resetar_canvas(self):
        self.canvas.delete("all")
        for widget in self.canvas.winfo_children(): widget.destroy()
        if 'bg_canvas' in self.imgs:
            self.canvas.create_image(0, 0, image=self.imgs['bg_canvas'], anchor="nw")

    def add_widget(self, x, y, widget, anchor="center"):
        self.canvas.create_window(x, y, window=widget, anchor=anchor)

    # ================= TELAS =================

    def tela_splash(self):
        self.resetar_canvas()
        cx, cy = 200, 375
        if 'logo_canvas' in self.imgs:
            self.canvas.create_image(cx, cy - 100, image=self.imgs['logo_canvas'])
        else:
            self.canvas.create_text(cx, cy - 100, text="⭕", fill=COR_PRIMARIA, font=("Arial", 80))

        self.canvas.create_text(cx, cy + 20, text="ZenBank", fill="white", font=("Helvetica", 45, "bold"))
        self.canvas.create_text(cx, cy + 60, text="Fique Zen com suas finanças", fill=COR_PRIMARIA, font=("Arial", 14))

        bar = ctk.CTkProgressBar(self.canvas, width=220, progress_color=COR_PRIMARIA, fg_color="#333",
                                 bg_color="#0a1a10")
        self.add_widget(cx, cy + 120, bar)
        bar.set(0)
        bar.start()
        self.after(3500, self.tela_login)

    def tela_login(self):
        self.resetar_canvas()
        cx = 200
        if 'logo_canvas' in self.imgs:
            self.canvas.create_image(cx, 80, image=self.imgs['logo_canvas'])

        self.canvas.create_text(cx, 160, text="ZenBank", fill="white", font=("Helvetica", 36, "bold"))
        self.canvas.create_text(cx, 200, text="Acesse sua conta", fill="white", font=("Arial", 16))

        self.ent_cpf = ctk.CTkEntry(self.canvas, placeholder_text="CPF", width=300, height=50, fg_color=COR_INPUTS,
                                    border_width=0, corner_radius=15, text_color="white", bg_color="#0a1a10")
        self.add_widget(cx, 280, self.ent_cpf)

        self.ent_senha = ctk.CTkEntry(self.canvas, placeholder_text="Senha", show="*", width=300, height=50,
                                      fg_color=COR_INPUTS, border_width=0, corner_radius=15, text_color="white",
                                      bg_color="#0a1a10")
        self.add_widget(cx, 350, self.ent_senha)

        btn_entrar = ctk.CTkButton(self.canvas, text="ENTRAR", width=300, height=50, fg_color=COR_PRIMARIA,
                                   text_color="black", font=("Arial", 15, "bold"), corner_radius=15,
                                   hover_color="#00C853", bg_color="#0a1a10", command=self.login)
        self.add_widget(cx, 430, btn_entrar)

        btn_criar = ctk.CTkButton(self.canvas, text="Criar nova conta", fg_color="transparent", text_color=COR_PRIMARIA,
                                  hover_color="#111", border_width=1, border_color=COR_PRIMARIA, height=45, width=300,
                                  corner_radius=15, bg_color="#0a1a10", command=self.tela_cadastro)
        self.add_widget(cx, 520, btn_criar)

        self.lbl_erro = ctk.CTkLabel(self.canvas, text="", text_color=COR_ERRO, fg_color="transparent",
                                     bg_color="#0a1a10")
        self.add_widget(cx, 570, self.lbl_erro)

    def tela_cadastro(self):
        self.resetar_canvas()
        cx = 200
        btn_voltar = ctk.CTkButton(self.canvas, text="< Voltar", width=80, fg_color="transparent", text_color="white",
                                   command=self.tela_login, anchor="w", bg_color="#0a1a10")
        self.add_widget(30, 30, btn_voltar, anchor="w")

        self.canvas.create_text(cx, 80, text="Nova Conta ✨", fill="white", font=("Arial", 28, "bold"))

        y = 150
        gap = 60
        self.ent_nome = ctk.CTkEntry(self.canvas, placeholder_text="Nome Completo", width=300, height=45,
                                     fg_color=COR_INPUTS, border_width=0, corner_radius=10, bg_color="#0a1a10")
        self.add_widget(cx, y, self.ent_nome)

        self.ent_cpf_cad = ctk.CTkEntry(self.canvas, placeholder_text="CPF (números)", width=300, height=45,
                                        fg_color=COR_INPUTS, border_width=0, corner_radius=10, bg_color="#0a1a10")
        self.add_widget(cx, y + gap, self.ent_cpf_cad)

        self.ent_s1 = ctk.CTkEntry(self.canvas, placeholder_text="Senha (min 8 chars)", show="*", width=300, height=45,
                                   fg_color=COR_INPUTS, border_width=0, corner_radius=10, bg_color="#0a1a10")
        self.add_widget(cx, y + gap * 2, self.ent_s1)

        self.ent_s2 = ctk.CTkEntry(self.canvas, placeholder_text="Repetir Senha", show="*", width=300, height=45,
                                   fg_color=COR_INPUTS, border_width=0, corner_radius=10, bg_color="#0a1a10")
        self.add_widget(cx, y + gap * 3, self.ent_s2)

        self.tipo_var = ctk.StringVar(value="1")
        sw = ctk.CTkSwitch(self.canvas, text="É Conta Poupança?", variable=self.tipo_var, onvalue="2", offvalue="1",
                           progress_color=COR_PRIMARIA, text_color="white", bg_color="#0a1a10")
        self.add_widget(cx, y + gap * 4, sw)

        self.lbl_feed = ctk.CTkLabel(self.canvas, text="", font=("Arial", 12), fg_color="transparent",
                                     bg_color="#0a1a10")
        self.add_widget(cx, y + gap * 4.7, self.lbl_feed)

        btn_cad = ctk.CTkButton(self.canvas, text="FINALIZAR", width=300, height=50, fg_color=COR_PRIMARIA,
                                text_color="black", font=("Arial", 15, "bold"), bg_color="#0a1a10",
                                command=self.confirmar)
        self.add_widget(cx, 650, btn_cad)

    def tela_dashboard(self):
        self.resetar_canvas()

        nome = self.conta_logada.nome.split()[0].title()
        self.canvas.create_text(30, 80, text=f"Olá, {nome} 👋", fill="white", font=("Arial", 22, "bold"), anchor="w")
        self.canvas.create_text(30, 120, text="Saldo disponível", fill="gray", font=("Arial", 14), anchor="w")
        self.canvas.create_text(30, 160, text=f"R$ {self.conta_logada.saldo:.2f}", fill=COR_PRIMARIA,
                                font=("Arial", 40, "bold"), anchor="w")

        # --- AQUI ESTAVA O PROBLEMA: REMOVEMOS O SCROLLABLE FRAME ---
        # Vamos desenhar os botões DIRETO no Canvas, um embaixo do outro.

        start_y = 240
        gap = 70

        # Lista de botões para gerar
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
            btn = ctk.CTkButton(self.canvas,
                                text=f"  {texto}",
                                image=img,
                                compound="left",
                                width=340, height=60,
                                fg_color=COR_INPUTS,
                                hover_color="#333",
                                anchor="w",
                                font=("Arial", 16, "bold"),
                                command=comando,
                                corner_radius=15,
                                bg_color="#0a1a10")  # bg_color ajuda a suavizar a borda

            # Posiciona diretamente no Canvas
            self.add_widget(200, start_y + (i * gap), btn)

        # Botão Sair
        btn_sair = ctk.CTkButton(self.canvas, text="SAIR", fg_color=COR_INPUTS, text_color=COR_ERRO, hover_color="#222",
                                 command=self.tela_login, width=100, bg_color="#0a1a10")
        self.add_widget(350, 50, btn_sair)

    def tela_transacao(self, tipo):
        self.resetar_canvas()
        cx = 200
        self.add_widget(30, 30, ctk.CTkButton(self.canvas, text="< Cancelar", width=80, fg_color="transparent",
                                              command=self.tela_dashboard, anchor="w", bg_color="#0a1a10"), anchor="w")

        self.canvas.create_text(cx, 120, text=tipo, fill=COR_PRIMARIA, font=("Arial", 32, "bold"))

        y_pos = 220
        self.ent_dest = None
        if tipo in ["Pix", "Transferência"]:
            self.ent_dest = ctk.CTkEntry(self.canvas, placeholder_text="Chave / Conta Destino", width=300, height=50,
                                         fg_color=COR_INPUTS, border_width=0, font=("Arial", 16), bg_color="#0a1a10")
            self.add_widget(cx, y_pos, self.ent_dest)
            y_pos += 70

        self.ent_val = ctk.CTkEntry(self.canvas, placeholder_text="Valor R$ 0.00", width=300, height=50,
                                    fg_color=COR_INPUTS, border_width=0, font=("Arial", 20, "bold"), bg_color="#0a1a10")
        self.add_widget(cx, y_pos, self.ent_val)

        self.lbl_msg = ctk.CTkLabel(self.canvas, text="", font=("Arial", 14, "bold"), fg_color="transparent",
                                    bg_color="#0a1a10")
        self.add_widget(cx, y_pos + 60, self.lbl_msg)

        btn_conf = ctk.CTkButton(self.canvas, text="CONFIRMAR", width=300, height=50, fg_color=COR_PRIMARIA,
                                 text_color="black", font=("Arial", 16, "bold"), bg_color="#0a1a10",
                                 command=lambda: self.processar_transacao(tipo))
        self.add_widget(cx, 650, btn_conf)

    def tela_extrato(self):
        self.resetar_canvas()
        self.add_widget(30, 30, ctk.CTkButton(self.canvas, text="< Voltar", width=80, fg_color="transparent",
                                              command=self.tela_dashboard, anchor="w", bg_color="#0a1a10"), anchor="w")
        self.canvas.create_text(200, 100, text="Extrato", fill="white", font=("Arial", 32, "bold"))

        # Extrato Simplificado (Lista fixa dos ultimos 6 itens para caber na tela sem scroll)
        # Isso evita o bug do ScrollableFrame no Canvas
        historico_recente = list(reversed(self.conta_logada.historico))[:6]

        y_start = 180
        gap = 80

        if not historico_recente:
            self.canvas.create_text(200, 300, text="Nenhuma movimentação.", fill="gray", font=("Arial", 14))

        for item in historico_recente:
            v = item['valor']
            c = COR_PRIMARIA if v > 0 else COR_ERRO
            s = "+" if v > 0 else ""
            txt = item['operacao']
            val = f"{s}R$ {abs(v):.2f}"

            # Desenha um "Card" falso usando texto e um botão inativo como fundo se quiser,
            # ou apenas o texto limpo sobre o fundo verde. Vamos usar texto limpo e elegante.

            # Linha separadora
            self.canvas.create_line(50, y_start, 350, y_start, fill="#333")

            # Texto
            self.canvas.create_text(50, y_start + 25, text=txt, fill="white", font=("Arial", 14, "bold"), anchor="w")
            self.canvas.create_text(350, y_start + 25, text=val, fill=c, font=("Arial", 14, "bold"), anchor="e")

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
            self.lbl_feed.configure(text="Sucesso! Redirecionando...", text_color=COR_PRIMARIA)
            self.after(2000, self.tela_login)
        else:
            self.lbl_feed.configure(text="CPF já existe", text_color=COR_ERRO)

    def processar_transacao(self, tipo):
        try:
            v = float(self.ent_val.get())
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