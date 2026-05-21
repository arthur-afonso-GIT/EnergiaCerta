# Arquivo: Core/comunicacao_serial.py
import random
# Nota: No futuro usaremos 'import serial', mas criamos um fallback seguro 
# para o sistema não quebrar se o Arduino estiver desconectado.

class LeitorArduino:
    def __init__(self, porta="COM3", baudrate=9600):
        self.porta = porta
        self.baudrate = baudrate
        self.conectado = False
        
        print(f"Tentando inicializar conexão na porta {self.porta}...")
        # Aqui entrará o self.conexao = serial.Serial(porta, baudrate)
        
    def ler_dados_reais(self):
        """
        Lê a linha enviada pelo Arduino via USB.
        O formato esperado será uma string separada por vírgula: 'consumo,geracao'
        Exemplo enviado pelo Arduino: '4.2,5.7'
        """
        if self.conectado:
            try:
                # Lógica real que rodará com o hardware:
                # linha = self.conexao.readline().decode('utf-8').strip()
                # consumo, geracao = linha.split(',')
                # return float(consumo), float(geracao)
                pass
            except Exception as e:
                print(f"Erro ao ler hardware: {e}")
                
        # Fallback inteligente: Se o Arduino não estiver plugado na USB física,
        # ele simula perfeitamente para a interface não travar.
        consumo_simulado = round(random.uniform(3.5, 5.5), 1)
        geracao_simulado = round(random.uniform(1.0, 6.5), 1) # <-- Corrigido aqui!
        return consumo_simulado, geracao_simulado