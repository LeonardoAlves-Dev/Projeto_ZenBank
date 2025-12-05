import json
import os
import random

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
            print(f"✅ Depósito de R${valor:.2f} realizado!")
            return True
        return False

    def sacar(self, valor):
        if valor > 0 and self.saldo >= valor:
            self.saldo -= valor
            self.registrar_historico("Saque 💸", -valor)
            print(f"✅ Saque de R${valor:.2f} realizado!")
            return True
        print("❌ Saldo insuficiente.")
        return False

    def ver_extrato(self):
        print(f"\n--- 📜 EXTRATO DE {self.nome.upper()} ---")
        for item in self.historico:
            print(f"{item['operacao']}: R$ {item['valor']:.2f}")
        print(f"----------------------------------")
        print(f"💵 Saldo Atual: R$ {self.saldo:.2f}\n")

    def to_dict(self):
        return {
            "tipo": self.tipo,
            "nome": self.nome,
            "cpf": self.cpf,
            "senha": self.senha,
            "saldo": self.saldo,
            "historico": self.historico,
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
            print(f"✅ Saque realizado! (Usando limite se necessário)")
            return True
        print("❌ Saldo + Limite insuficientes.")
        return False


class ContaPoupanca(Conta):
    def __init__(self, nome, cpf, senha, saldo=0.0, historico=None):
        super().__init__(nome, cpf, senha, saldo, historico)
        self.tipo = 'Poupanca'

    def render(self):
        rendimento = self.saldo * 0.05
        self.saldo += rendimento
        self.registrar_historico("Rendimento 📈", rendimento)
        print(f"✅ Rendimento de R${rendimento:.2f} aplicado!")


class BancoSistema:
    def __init__(self):
        self.contas = []
        self.arquivo_db = "banco_dados.json"
        self.carregar_dados()

    def salvar_dados(self):
        lista_para_salvar = [conta.to_dict() for conta in self.contas]
        with open(self.arquivo_db, 'w') as arquivo:
            json.dump(lista_para_salvar, arquivo, indent=4)
        print("💾 Dados salvos automaticamente...")

    def carregar_dados(self):
        if not os.path.exists(self.arquivo_db):
            return

        try:
            with open(self.arquivo_db, 'r') as arquivo:
                dados = json.load(arquivo)
                for d in dados:
                    if d['tipo'] == 'Corrente':
                        nova_conta = ContaCorrente(d['nome'], d['cpf'], d['senha'], d['saldo'], d['historico'],
                                                   d['extra'])
                    else:
                        nova_conta = ContaPoupanca(d['nome'], d['cpf'], d['senha'], d['saldo'], d['historico'])
                    self.contas.append(nova_conta)
        except:
            print("⚠️ Erro ao carregar banco de dados. Iniciando vazio.")

    def buscar_conta(self, cpf):
        for conta in self.contas:
            if conta.cpf == cpf:
                return conta
        return None

    def criar_conta(self):
        print("\n--- 🆕 NOVA CONTA ---")
        nome = input("Nome Completo: ")
        cpf = input("CPF: ")
        senha = input("Senha (4 digitos): ")
        tipo = input("Tipo (1-Corrente / 2-Poupança): ")

        if self.buscar_conta(cpf):
            print("❌ CPF já cadastrado!")
            return

        if tipo == '1':
            nova = ContaCorrente(nome, cpf, senha)
        else:
            nova = ContaPoupanca(nome, cpf, senha)

        self.contas.append(nova)
        self.salvar_dados()
        print("✅ Conta criada com sucesso!")

    def login(self):
        print("\n--- 🔐 LOGIN ---")
        cpf = input("CPF: ")
        senha = input("Senha: ")
        conta = self.buscar_conta(cpf)

        if conta and conta.senha == senha:
            self.menu_conta(conta)
        else:
            print("❌ Dados inválidos.")

    def menu_conta(self, conta):
        while True:
            print(f"\n--- Olá, {conta.nome} 🏦 ---")
            print("1. Saldo")
            print("2. Depositar")
            print("3. Sacar")
            print("4. Extrato")
            if conta.tipo == 'Poupanca': print("5. Simular Rendimento")
            print("0. Sair")

            op = input("Opção: ")

            if op == '1':
                print(f"💰 Saldo: R${conta.saldo:.2f}")
            elif op == '2':
                v = float(input("Valor: "))
                conta.depositar(v)
            elif op == '3':
                v = float(input("Valor: "))
                conta.sacar(v)
            elif op == '4':
                conta.ver_extrato()
            elif op == '5' and conta.tipo == 'Poupanca':
                conta.render()
            elif op == '0':
                break

            self.salvar_dados()

    def iniciar(self):
        while True:
            print("\n=== 🏧 SISTEMA BANCÁRIO V2 ===")
            print("1. Entrar na Conta")
            print("2. Criar Nova Conta")
            print("3. Sair")
            op = input("Opção: ")

            if op == '1':
                self.login()
            elif op == '2':
                self.criar_conta()
            elif op == '3':
                print("Encerrando sistema... 👋")
                break


if __name__ == "__main__":
    app = BancoSistema()
    app.iniciar()