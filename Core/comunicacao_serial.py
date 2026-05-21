# Arquivo: Core/comunicacao_serial.py
import math
import random

class LeitorArduino:
    def __init__(self, porta="COM3", baudrate=9600):
        self.porta = porta
        self.baudrate = baudrate
        self.conectado = False
        
        # Começa às 10:00 da manhã
        self.hora_atual = 10.0  
        print(f"🔌 Tentando inicializar conexão na porta {self.porta}...")
        
    def ler_dados_reais(self):
        """
        Gera uma simulação física realista baseada na hora do dia e retorna 3 valores:
        consumo_simulado, geracao_simulado, hora_atual
        """
        if self.conectado:
            try:
                pass
            except Exception as e:
                print(f"Erro ao ler hardware: {e}")
                
        # Avança o tempo em 15 minutos (0.25h) a cada ciclo para o gráfico se mexer
        self.hora_atual = (self.hora_atual + 0.25) % 24
        
        # 1. Modelo de Geração Solar (Curva do Sol entre 06h e 18h)
        if 6.0 <= self.hora_atual <= 18.0:
            # Pico ao meio-dia (12h)
            angulo_solar = math.sin(math.pi * (self.hora_atual - 6.0) / 12.0)
            geracao_base = 6.0 * angulo_solar
            geracao_simulado = max(0.0, geracao_base + random.uniform(-0.4, 0.2))
        else:
            geracao_simulado = 0.0
            
        # 2. Modelo de Consumo Residencial
        consumo_base = 2.0
        
        # Picos nos horários de Almoço (12h-14h) e Noite (18h-22h)
        if 12.0 <= self.hora_atual <= 14.0:
            consumo_base += 1.5
        elif 18.0 <= self.hora_atual <= 22.0:
            consumo_base += 2.5
            
        consumo_simulado = max(0.5, consumo_base + random.uniform(-0.5, 0.5))
        
        # RETORNA EXATAMENTE OS 3 VALORES QUE O DASHBOARD PEDIU
        return round(consumo_simulado, 1), round(geracao_simulado, 1), round(self.hora_atual, 2)