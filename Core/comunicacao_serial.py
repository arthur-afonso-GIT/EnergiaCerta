# Arquivo: Core/comunicacao_serial.py
import math
import random

class LeitorArduino:
    def __init__(self, porta="COM3", baudrate=9600):
        self.porta = porta
        self.baudrate = baudrate
        self.conectado = False
        self.hora_atual = 10.0
        
        # Flags para interceptar a física padrão via botões da interface
        self.forcar_sobrecarga = False
        self.forcar_alta_geracao = False
        
        self.potencia_cargas = {
            "Geladeira": 0.8,
            "Iluminação Sala": 0.3,
            "Roteador Internet": 0.1,
            "Ar-Condicionado": 2.0,
            "Bomba D'água": 1.2,
            "Computador": 0.5
        }
        
    def ler_dados_reais(self, estados_cargas=None):
        if self.conectado:
            try: pass
            except Exception: pass
                
        # Avança o tempo
        self.hora_atual = (self.hora_atual + 0.25) % 24
        
        # 1. CÁLCULO DA GERAÇÃO SOLAR
        if 6.0 <= self.hora_atual <= 18.0:
            angulo_solar = math.sin(math.pi * (self.hora_atual - 6.0) / 12.0)
            # Se o botão de "Alta Geração" estiver ativo, remove o ruído e amplifica o sol
            multiplicador_sol = 9.0 if self.forcar_alta_geracao else 6.0
            geracao_base = multiplicador_sol * angulo_solar
            geracao_simulado = max(0.0, geracao_base + random.uniform(-0.2, 0.1))
        else:
            geracao_simulado = 0.0
            
        # 2. CÁLCULO DO CONSUMO DINÂMICO
        if estados_cargas is None:
            estados_cargas = {carga: True for carga in self.potencia_cargas}
            
        consumo_base = 0.5
        for carga, ativo in estados_cargas.items():
            if ativo and carga in self.potencia_cargas:
                consumo_base += self.potencia_cargas[carga]
                
        # Picos de horário comercial comuns
        if 12.0 <= self.hora_atual <= 14.0:
            consumo_base += 0.8
        elif 18.0 <= self.hora_atual <= 22.0:
            consumo_base += 1.2
            
        # Se o botão de "Simular Sobrecarga" estiver ativo, joga + 4.5 kWh na rede (ex: chuveiro + ferro)
        if self.forcar_sobrecarga:
            consumo_base += 4.5
            
        consumo_simulado = max(0.4, consumo_base + random.uniform(-0.2, 0.2))
        
        return round(consumo_simulado, 1), round(geracao_simulado, 1), round(self.hora_atual, 2)