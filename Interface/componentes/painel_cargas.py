import random
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

class PainelCargasCriticas(QWidget):
    def __init__(self):
        super().__init__()
        
        self.potencia_aliviada_total = 0.0
        
        self.callback_serial_arduino = None
        
        self.setStyleSheet("""
            QWidget { background-color: #1E1E1E; border: 1px solid #333333; border-radius: 6px; }
            QLabel { color: #FFFFFF; font-size: 14px; font-weight: bold; border: none; background: transparent; }
            QPushButton { 
                background-color: #2D2D2D; color: #FFFFFF; border: 1px solid #444444; 
                border-radius: 4px; padding: 10px; text-align: left; font-size: 12px;
            }
            QPushButton:hover { background-color: #3D3D3D; }
        """)
        
        layout = QVBoxLayout(self)
        
        lbl_titulo = QLabel("Monitoramento e Controle de Cargas (Pronto para Hardware)")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_titulo)
        
        self.lbl_status_economia = QLabel("Sistema operando em carga total")
        self.lbl_status_economia.setStyleSheet("color: #00E676; font-size: 12px; font-weight: normal;")
        self.lbl_status_economia.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_status_economia)
        
        self.cargas = {
            "Geladeira": {"id": 1, "critica": True, "potencia": 0.4, "botao": QPushButton("⚡ [CRÍTICA] Geladeira")},
            "Iluminação Sala": {"id": 2, "critica": True, "potencia": 0.2, "botao": QPushButton("⚡ [CRÍTICA] Iluminação Sala")},
            "Roteador Internet": {"id": 3, "critica": True, "potencia": 0.1, "botao": QPushButton("⚡ [CRÍTICA] Roteador Internet")},
            "Ar-Condicionado": {"id": 4, "critica": False, "potencia": 2.0, "botao": QPushButton("⚡ [SISTEMA] Ar-Condicionado")},
            "Bomba D'água": {"id": 5, "critica": False, "potencia": 1.2, "botao": QPushButton("⚡ [SISTEMA] Bomba D'água")},
            "Computador": {"id": 6, "critica": False, "potencia": 0.5, "botao": QPushButton("⚡ [SISTEMA] Computador")}
        }
        
        self.estados = {nome: True for nome in self.cargas}
        
        for nome, info in self.cargas.items():
            layout.addWidget(info["botao"])
            info["botao"].clicked.connect(lambda checked=False, n=nome: self.alternar_estado_manual(n))
            self.atualizar_estilo_botao(nome)
            
    def definir_callback_hardware(self, funcao_envio):
        """Permite que o seu Main.py conecte a funcao de transmissao serial aqui"""
        self.callback_serial_arduino = funcao_envio
            
    def obter_estados(self):
        return self.estados
        
    def definir_estado_carga(self, nome, ligado):
        """Modifica o estado (chamado pela IA ou clique) e envia o comando para o Arduino se disponível"""
        if nome in self.estados:

            estado_anterior = self.estados[nome]
            
            self.estados[nome] = ligado
            self.atualizar_estilo_botao(nome)
            self.recalcular_alivio_demanda()
            
            if estado_anterior != ligado:
                self.notificar_mudanca_hardware(nome, ligado)
            
    def alternar_estado_manual(self, nome):
        if self.cargas[nome]["critica"]:
            return # Segurança: cargas críticas não chaveiam manualmente
            
        novo_estado = not self.estados[nome]
        self.definir_estado_carga(nome, novo_estado)
            
    def notificar_mudanca_hardware(self, nome, ligado):
        """Formata e envia a string de comando que o Arduino vai ler no void loop()"""
        id_carga = self.cargas[nome]["id"]
        acao = "1" if ligado else "0"
        
        comando_protocolo = f"#{id_carga},{acao}\n"

    def recalcular_alivio_demanda(self):
        alivio = 0.0
        for nome, info in self.cargas.items():
            if not self.estados[nome]:
                alivio += info["potencia"]
        
        self.potencia_aliviada_total = alivio
        if alivio > 0:
            self.lbl_status_economia.setText(f"Alivio de Demanda Ativo: -{alivio:.1f} kWh poupados")
            self.lbl_status_economia.setStyleSheet("color: #FF9800; font-size: 12px; font-weight: bold;")
        else:
            self.lbl_status_economia.setText("Sistema operando em carga total")
            self.lbl_status_economia.setStyleSheet("color: #00E676; font-size: 12px; font-weight: normal;")

    def atualizar_estilo_botao(self, nome):
        botao = self.cargas[nome]["botao"]
        prefixo = "[CRITICA]" if self.cargas[nome]["critica"] else "[SISTEMA]"
        
        if self.estados[nome]:
            botao.setText(f"[ATIVO] {prefixo} {nome} - Ativo ({self.cargas[nome]['potencia']} kWh)")
            botao.setStyleSheet("background-color: #2D2D2D; color: #FFFFFF; border: 1px solid #444444;")
        else:
            botao.setText(f"[DESLIGADO] {prefixo} {nome} - DESLIGADO (Corte de Pico)")
            botao.setStyleSheet("background-color: #3a1c1c; color: #E53935; border: 1px solid #E53935; font-weight: bold;")