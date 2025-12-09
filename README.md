# 🍃 ZenBank - Sistema Bancário Desktop

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Finalizado%20(V8.2)-success?style=for-the-badge)

> *Fique Zen com suas finanças.*

Este projeto consiste em uma aplicação bancária completa simulada, desenvolvida como projeto final prático do **Curso de Aperfeiçoamento Profissional em Python com Framework Flask** do **SENAI (Serviço Nacional de Aprendizagem Industrial)**.

O objetivo foi transcender a lógica básica de programação, aplicando conceitos avançados de **Engenharia de Software**, **Arquitetura MVC** e **Design de Interface (UI/UX)** para criar um produto funcional e esteticamente agradável.

---

## 🚀 Funcionalidades (V8.2)

### 👤 Gestão de Usuário
* **Cadastro Completo:** Validação de campos e política de **senha forte** (Regex).
* **Login Seguro:** Autenticação via CPF e Senha.
* **CRUD de Perfil:** O usuário pode **editar seus dados** e **excluir sua conta** permanentemente (GDPR compliant).

### 💸 Transações Financeiras
* **Dashboard Interativo:** Visualização de saldo com formatação brasileira (R$ 1.000,00) e menu de ações.
* **Operações:** Depósitos, Saques, Pagamento de Boletos e Transferências (Simulação de PIX).
* **Feedback Visual:** Mensagens de sucesso/erro integradas na interface (sem pop-ups intrusivos).
* **Extrato:** Histórico detalhado com identificação visual de entrada (Verde) e saída (Vermelho).

### 🎨 Interface & UX (Destaque Técnico)
* **Splash Screen:** Tela de carregamento animada na inicialização.
* **Visual Imersivo:** Fundo personalizado e identidade visual consistente (Dark/Green Neon).
* **Renderização Híbrida:** Utilização de `Canvas` do Tkinter combinado com `CustomTkinter` para garantir transparência real e evitar artefatos visuais em ambientes Linux/X11.
* **Responsividade:** Layout que se adapta ao redimensionamento da janela.

---

## 🛠️ Arquitetura do Projeto

O projeto foi refatorado da estrutura monolítica para **MVC (Model-View-Controller)** para garantir organização e escalabilidade:

```text
ZenBank/
├── assets/              # Recursos visuais (Ícones, Logos, Backgrounds)
├── backend/             # Lógica de Negócio
│   ├── controller.py    # Gerenciador do Banco e Regras de Negócio
│   └── entidades.py     # Classes Modelo (Conta, Corrente, Poupança)
├── data/                # Persistência
│   └── banco_dados.json # Banco de dados local em JSON
├── main.py              # Frontend (View) e Ponto de Entrada
└── README.md            # Documentação

---
*Desenvolvido por Leonardo Alves - Estudante de T.I. e Ciência de Dados.*
