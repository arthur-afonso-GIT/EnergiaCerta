# Arquivo: Core/simulador.py
import random

class SimuladorEnergia:
    def __init__(self):
        # Histórico inicial para o gráfico não começar zerado (últimos 7 pontos)
        self.historico_horas = ['12h', '13h', '14h', '15h', '16h', '17h', '18h']
        self.historico_consumo = [3.8, 4.2, 4.5, 4.1, 4.8, 5.2, 4.5]
        self.historico_geracao = [2.1, 3.5, 5.8, 6.2, 5.0, 3.1, 1.5]
        
        self.contador_tempo = 19 # Próxima hora simulada seria 19h
        
    def atualizar_dados(self):
        """Gera um novo ponto de dados simulado, adiciona ao histórico e remove o mais antigo"""
        # Gera valores flutuantes realistas ao redor da média atual
        novo_consumo = round(random.uniform(3.5, 5.5), 1)
        nova_geracao = round(random.uniform(1.0, 6.5), 1)
        nova_hora = f"{self.contador_tempo}h"
        
        # Atualiza o contador de horas (rotaciona entre 0h e 23h)
        self.contador_tempo = (self.contador_tempo + 1) % 24
        
        # Adiciona os novos dados ao final das listas
        self.historico_horas.append(nova_hora)
        self.historico_consumo.append(novo_consumo)
        self.historico_geracao.append(nova_geracao)
        
        # Mantém apenas os últimos 7 pontos para o gráfico não espremer infinitamente
        if len(self.historico_horas) > 7:
            self.historico_horas.pop(0)
            self.historico_consumo.pop(0)
            self.historico_geracao.pop(0)
            
        return novo_consumo, nova_geracao