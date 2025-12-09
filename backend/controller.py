import json
import os
from backend.entidades import ContaCorrente, ContaPoupanca


class BancoController:
    def __init__(self):
        self.contas = []
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.arquivo_db = os.path.join(base_dir, 'data', 'banco_dados.json')
        self.carregar_dados()

    def salvar_dados(self):
        # Agora salvamos o atributo telefone também se ele existir
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

                    # Recupera telefone se existir no JSON antigo, senão fica vazio
                    c.telefone = d.get('telefone', '')
                    self.contas.append(c)
        except:
            pass

    def buscar_conta(self, cpf):
        for c in self.contas:
            if c.cpf == cpf: return c
        return None

    def criar_conta(self, nome, cpf, senha, tipo):
        if self.buscar_conta(cpf): return False
        nova = ContaCorrente(nome, cpf, senha) if tipo == '1' else ContaPoupanca(nome, cpf, senha)
        nova.telefone = ""  # Inicia vazio
        self.contas.append(nova)
        self.salvar_dados()
        return True

    def realizar_transferencia(self, origem, cpf_dest, valor):
        destino = self.buscar_conta(cpf_dest)
        if not destino: return False, "Destino não encontrado."
        if origem.cpf == cpf_dest: return False, "Mesma conta."
        if origem.transferir(valor, destino):
            self.salvar_dados()
            return True, "Pix realizado!"
        return False, "Saldo insuficiente."

    # --- MÉTODOS NOVOS (V8.0/8.1) ---

    def atualizar_conta(self, cpf_original, novo_nome, nova_senha, novo_telefone):
        conta = self.buscar_conta(cpf_original)
        if conta:
            if novo_nome.strip(): conta.nome = novo_nome
            if nova_senha.strip(): conta.senha = nova_senha
            if novo_telefone.strip(): conta.telefone = novo_telefone
            self.salvar_dados()
            return True, "Dados salvos!"
        return False, "Erro ao atualizar."

    def excluir_conta(self, cpf):
        conta = self.buscar_conta(cpf)
        if conta:
            self.contas.remove(conta)
            self.salvar_dados()
            return True
        return False