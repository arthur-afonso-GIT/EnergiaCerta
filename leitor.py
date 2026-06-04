import random
import math
import time

USAR_HARDWARE_REAL = False 

try:
    import serial
except ImportError:
    if USAR_HARDWARE_REAL:
        print("Alerta: Biblioteca 'pyserial' nao encontrada. Instale com: pip install pyserial")
    USAR_HARDWARE_REAL = False

class LeitorHardware:
    def __init__(self, porta='COM3', baudrate=9600):
        self.usar_hardware = USAR_HARDWARE_REAL
        self.conexao = None
        self.hora_simulada = 12.0

        if self.usar_hardware:
            try:
                self.conexao = serial.Serial(porta, baudrate, timeout=1)
                time.sleep(2)
                print(f"[HARDWARE] Conectado com sucesso ao Arduino na porta {porta}!")
            except Exception as e:
                print(f"[HARDWARE] Falha ao abrir a porta {porta}: {e}")
                print("[Revertendo automaticamente para Modo Simulacao de Dados...")
                self.usar_hardware = False

        if not self.usar_hardware:
            print("[SIMULADOR] Rodando em modo de dados virtuais integrados.")

    def ler_dados_reais(self):
        """
        Retorna uma tupla (consumo, geracao, hora_float)
        Independente de vir do cabo ou da simulacao, o formato de saida eh identico!
        """
        if self.usar_hardware and self.conexao:
            try:
                if self.conexao.in_waiting > 0:
                    linha = self.conexao.readline().decode('utf-8').strip()
                    if linha:
                        dados = linha.split(',')
                        if len(dados) == 2:
                            consumo = float(dados[0])
                            geracao = float(dados[1])
                            self.hora_simulada = (self.hora_simulada + 0.25) % 24
                            return consumo, geracao, self.hora_simulada
            except Exception as e:
                print(f"Erro ao ler dados do cabo USB: {e}")
            
            return 0.5, 0.0, self.hora_simulada

        else:
            # Avança o relógio da simulação (15 minutos por ciclo de leitura)
            self.hora_simulada = (self.hora_simulada + 0.25) % 24
            
            # Gera consumo base flutuante
            consumo_base = 2.2 + random.uniform(-0.3, 0.4)
            
            # Gera curva de geração solar baseada na hora do dia (senoide perfeita)
            if 6.0 <= self.hora_simulada <= 18.0:
                # Pico solar entre 11h e 14h
                angulo_solar = math.sin(math.pi * (self.hora_simulada - 6.0) / 12.0)
                geracao_base = 5.5 * angulo_solar + random.uniform(-0.2, 0.2)
                geracao = round(max(0.0, geracao_base), 1)
            else:
                geracao = 0.0 # Noite não gera energia

            consumo = round(max(0.5, consumo_base), 1)
            return consumo, geracao, self.hora_simulada

    def enviar_comando_corte(self, comando):
        """Manda um sinal de volta pelo cabo para o Arduino acionar os Reles fisicos"""
        if self.usar_hardware and self.conexao:
            try:
                payload = f"{comando}\n".encode('utf-8')
                self.conexao.write(payload)
                print(f"[CABO] Comando enviado ao Arduino: {comando}")
            except Exception as e:
                print(f"Erro ao enviar comando via cabo: {e}")