# Arquivo: Core/comunicacao_serial.py
import serial
from PySide6.QtCore import QObject, Signal, QThread

class MonitorConexaoArduino(QThread):
    """
    Roda em background verificando se o Arduino conectou na COM8.
    Emite o sinal 'arduino_conectado' com a corrente lida quando detecta conexão.
    """
    arduino_conectado = Signal(float)   # emite corrente_kw quando conecta
    arduino_desconectado = Signal()

    def __init__(self, porta="COM8", baudrate=9600):
        super().__init__()
        self.porta = porta
        self.baudrate = baudrate
        self.rodando = True
        self.arduino = None
        self.conectado = False
        self.ultima_corrente = 0.0

    def run(self):
        import time
        while self.rodando:
            if not self.conectado:
                try:
                    self.arduino = serial.Serial(self.porta, self.baudrate, timeout=1)
                    self.conectado = True
                    print(f"[ARDUINO] Conectado na {self.porta}!")
                    # Lê a primeira leitura para emitir junto ao sinal
                    time.sleep(2)  # aguarda Arduino inicializar
                    corrente = self._ler_corrente()
                    self.ultima_corrente = corrente
                    self.arduino_conectado.emit(corrente)
                except Exception:
                    self.conectado = False
                    time.sleep(3)  # tenta reconectar a cada 3s
            else:
                # Mantém leitura contínua enquanto conectado
                try:
                    corrente = self._ler_corrente()
                    if corrente is not None:
                        self.ultima_corrente = corrente
                    time.sleep(0.5)
                except Exception:
                    print("[ARDUINO] Conexão perdida.")
                    self.conectado = False
                    try:
                        self.arduino.close()
                    except Exception:
                        pass
                    self.arduino = None
                    self.arduino_desconectado.emit()

    def _ler_corrente(self):
        """Lê uma linha do Arduino e retorna a corrente em kW (ou None se falhar)."""
        if self.arduino and self.arduino.in_waiting > 0:
            try:
                linha = self.arduino.readline().decode('utf-8').strip()
                if "," in linha:
                    partes = linha.split(",")
                    corrente = float(partes[0])
                    # Arduino envia corrente em A, converte para kW (assumindo 220V)
                    # Se já vier em kW, remova a multiplicação
                    potencia_kw = round(corrente * 0.220, 3)
                    return potencia_kw
                else:
                    return float(linha) * 0.220
            except Exception:
                return None
        return None

    def ler_corrente_atual(self):
        """Retorna a última corrente lida (chamado pelo loop do dashboard)."""
        return self.ultima_corrente if self.conectado else 0.0

    def parar(self):
        self.rodando = False
        if self.arduino:
            try:
                self.arduino.close()
            except Exception:
                pass
