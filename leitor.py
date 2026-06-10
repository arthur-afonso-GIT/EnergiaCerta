import random
import math
import time

# 💡 CONFIGURAÇÃO COMPLETA: Mude para True quando o Arduino estiver pronto!
USAR_HARDWARE_REAL = False 

try:
    import serial
except ImportError:
    # Caso não tenhas o pyserial instalado ainda, o modo simulação continua a rodar
    if USAR_HARDWARE_REAL:
        print("⚠️ Alerta: Biblioteca 'pyserial' não encontrada. Instale com: pip install pyserial")
    USAR_HARDWARE_REAL = False

class LeitorHardware:
    def __init__(self, porta='COM3', baudrate=9600):
        self.usar_hardware = USAR_HARDWARE_REAL
        self.conexao = None
        self.hora_simulada = 12.0 # Começa ao meio-dia na simulação

        if self.usar_hardware:
            try:
                # Tenta abrir a conexão com o cabo do Arduino
                self.conexao = serial.Serial(porta, baudrate, timeout=1)
                time.sleep(2) # Aguarda o Arduino reiniciar
                print(f"🔌 [HARDWARE] Conectado com sucesso ao Arduino na porta {porta}!")
            except Exception as e:
                print(f"❌ [HARDWARE] Falha ao abrir a porta {porta}: {e}")
                print("🔄 Revertendo automaticamente para Modo Simulação de Dados...")
                self.usar_hardware = False

        if not self.usar_hardware:
            print("🤖 [SIMULADOR] Rodando em modo de dados virtuais integrados.")

    def ler_dados_reais(self):
        """
        Retorna uma tupla (consumo, geracao, hora_float)
        Independente de vir do cabo ou da simulação, o formato de saída é idêntico!
        """
        # ==========================================
        # MODO 1: LENDO DO ARDUINO REAL (FUTURO)
        # ==========================================
        if self.usar_hardware and self.conexao:
            try:
                if self.conexao.in_waiting > 0:
                    linha = self.conexao.readline().decode('utf-8').strip()
                    if linha:
                        # Espera o formato "consumo,geracao" enviado pelo Arduino (Ex: "3.4,5.1")
                        dados = linha.split(',')
                        if len(dados) == 2:
                            consumo = float(dados[0])
                            geracao = float(dados[1])
                            # Avança a hora do sistema com base no relógio real
                            self.hora_simulada = (self.hora_simulada + 0.25) % 24
                            return consumo, geracao, self.hora_simulada
            except Exception as e:
                print(f"⚠️ Erro ao ler dados do cabo USB: {e}")
            
            # Fallback rápido caso a leitura falhe temporariamente
            return 0.5, 0.0, self.hora_simulada

        # ==========================================
        # MODO 2: SIMULADOR DE SUPORTE (ATUAL)
        # ==========================================
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
        """Manda um sinal de volta pelo cabo para o Arduino acionar os Relés físicos"""
        if self.usar_hardware and self.conexao:
            try:
                # Adiciona quebra de linha para o Arduino saber o fim do comando
                payload = f"{comando}\n".encode('utf-8')
                self.conexao.write(payload)
                print(f"📡 [CABO] Comando enviado ao Arduino: {comando}")
            except Exception as e:
                print(f"❌ Erro ao enviar comando via cabo: {e}")