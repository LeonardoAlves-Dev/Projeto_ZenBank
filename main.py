import random

# Classe Pai
class Conta:
    def __init__(self, nome, cpf, senha):
        self.nome = nome
        self.cpf = cpf
        self.senha = senha
        self.numero_conta = random.randint(1000, 9999)
        self.agencia = '0001'
        self.saldo = 0.0
        self.cheque_especial = 500.0
        self.limite_pix_diurno = 1000.0
        self.limite_pix_noturno = 300.0
        self.ativa = True

    def consultar_saldo(self):
        return self.saldo

    def depositar(self, valor):
        if self.ativa and valor > 0:
            self.saldo += valor
            return True
        return False

    def sacar(self, valor):
        if self.ativa and valor > 0:
            if self.saldo >= valor:
                self.saldo -= valor
                return True
            elif (self.saldo + self.cheque_especial) >= valor:
                self.saldo -= valor
                return True
        return False

    def transferir(self, valor, conta_destino):
        if self.sacar(valor):
            conta_destino.depositar(valor)
            return True
        return False

    def pagar_boleto(self, codigo, valor):
        if self.sacar(valor):
            print(f'Boleto {codigo} pago com sucesso.')
            return True
        return False

    def alterar_senha(self, nova_senha):
        self.senha = nova_senha

    def encerrar_conta(self):
        if self.saldo == 0:
            self.ativa = False
            return True
        return False

# Subclasse 1
class ContaCorrente(Conta):
    def __init__(self, nome, cpf, senha):
        super().__init__(nome, cpf, senha)
        self.compra_internacional = False
        self.cartao_credito = False

    def cobrar_tarifa(self):
        self.saldo -= 19.90

# Subclasse 2
class ContaPoupanca(Conta):
    def __init__(self, nome, cpf, senha):
        super().__init__(nome, cpf, senha)
        self.rendimento = 0.05

    def aplicar_rendimento(self):
        lucro = self.saldo * self.rendimento
        self.saldo += lucro

# Classe Banco Gerenciador
class Banco:
    def __init__(self):
        self.lista_contas = []

    def cadastrar_conta(self, conta):
        self.lista_contas.append(conta)
        print('Conta cadastrada com sucesso!')

    def buscar_conta(self, cpf):
        for conta in self.lista_contas:
            if conta.cpf == cpf:
                return conta
        return None

    def excluir_conta(self, cpf):
        conta = self.buscar_conta(cpf)
        if conta and conta.encerrar_conta():
            self.lista_contas.remove(conta)
            print('Conta removida.')
        else:
            print('Nao foi possivel remover (verifique saldo ou CPF).')

# --- SIMULAÇÃO ---
zenbank = Banco()

# 1. Criando contas
c1 = ContaCorrente('Joao Silva', '00011122233', '1234')
c2 = ContaPoupanca('Maria Souza', '33322211100', '4321')

zenbank.cadastrar_conta(c1)
zenbank.cadastrar_conta(c2)

# 2. Operacoes
print(f'\nSaldo Inicial Joao: {c1.consultar_saldo()}')
c1.depositar(1000)
print(f'Joao depositou 1000. Saldo: {c1.consultar_saldo()}')

print('\n--- Transferencia ---')
if c1.transferir(300, c2):
    print('Transferencia de 300 realizada para Maria.')
else:
    print('Falha na transferencia.')

print(f'Saldo Joao: {c1.consultar_saldo()}')
print(f'Saldo Maria: {c2.consultar_saldo()}')

print('\n--- Poupanca ---')
c2.aplicar_rendimento()
print(f'Rendimento aplicado na conta de Maria. Novo saldo: {c2.consultar_saldo()}')