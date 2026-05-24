from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from Interface.componentes.painel_cargas import PainelCargasCriticas

class AbaCargas(QWidget):  
    def __init__(self, arduino_serial=None, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título Interno Bonito
        self.titulo = QLabel("⚙️ Gerenciamento de Cargas Críticas")
        self.titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #00E676; background: transparent;")
        layout.addWidget(self.titulo)
        
        # Instancia o painel real interativo
        self.painel = PainelCargasCriticas()
        
        # Conexão segura ao hardware
        if arduino_serial:
            if hasattr(arduino_serial, 'enviar_dados'):
                self.painel.definir_callback_hardware(arduino_serial.enviar_dados)
            elif hasattr(arduino_serial, 'write'):
                self.painel.definir_callback_hardware(arduino_serial.write)
                
        layout.addWidget(self.painel)
        self.setStyleSheet("background-color: #121212;")