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
        self.historico.append({"operacao": operacao, "valor": valor})

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
            self.registrar_historico("Pagamento 📄", -valor)
            return True
        return False

    def transferir(self, valor, conta_destino):
        if valor > 0 and self.saldo >= valor:
            self.saldo -= valor
            self.registrar_historico("Envio Pix 📤", -valor)
            conta_destino.saldo += valor
            conta_destino.registrar_historico(f"Pix Recebido 📥 ({self.nome.split()[0]})", valor)
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

    def sacar(self, valor): # Polimorfismo com limite
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
        self.registrar_historico("Rendimento Zen 🍃", rendimento)
        return True