import json
import os
# Importando as classes do arquivo vizinho
from backend.entidades import ContaCorrente, ContaPoupanca

class BancoController:
    def __init__(self):
        self.contas = []
        # Lógica para salvar na pasta 'data' que criamos na raiz
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.arquivo_db = os.path.join(base_dir, 'data', 'banco_dados.json')
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
        except: pass

    def buscar_conta(self, cpf):
        for c in self.contas:
            if c.cpf == cpf: return c
        return None

    def realizar_transferencia(self, origem, cpf_dest, valor):
        destino = self.buscar_conta(cpf_dest)
        if not destino: return False, "Destino não encontrado."
        if origem.cpf == cpf_dest: return False, "Mesma conta."
        if origem.transferir(valor, destino):
            self.salvar_dados()
            return True, "Pix realizado com sucesso!"
        return False, "Saldo insuficiente."

    def criar_conta(self, nome, cpf, senha, tipo):
        if self.buscar_conta(cpf): return False
        nova = ContaCorrente(nome, cpf, senha) if tipo == '1' else ContaPoupanca(nome, cpf, senha)
        self.contas.append(nova)
        self.salvar_dados()
        return True