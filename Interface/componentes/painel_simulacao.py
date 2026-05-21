from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt

class PainelSimulacaoDecisao(QWidget):
    def __init__(self, callback_alerta=None):
        super().__init__()
        
        # Guardamos a função de disparar alertas (Notify) caso queiramos usar aqui
        self.disparar_alerta = callback_alerta
        
        self.setStyleSheet("background-color: #1E1E1E; border-radius: 6px; border: 1px solid #333333;")
        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setSpacing(15)
        
        # Título do Painel
        lbl_titulo = QLabel("Simulação de Decisão e Economia")
        lbl_titulo.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFFFFF; border: none; background: transparent;")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        self.layout_principal.addWidget(lbl_titulo)
        
        # --- SEÇÃO SLIDER: LIMITE DE CONSUMO ---
        self.lbl_slider_status = QLabel("Meta Limite de Consumo: 5.0 kWh")
        self.lbl_slider_status.setStyleSheet("font-size: 12px; color: #AAAAAA; border: none; background: transparent;")
        self.layout_principal.addWidget(self.lbl_slider_status)
        
        self.slider_limite = QSlider(Qt.Horizontal)
        self.slider_limite.setMinimum(1)
        self.slider_limite.setMaximum(10)
        self.slider_limite.setValue(5) # Padrão 5.0 kWh
        self.slider_limite.setStyleSheet("""
            QSlider::groove:horizontal { height: 6px; background: #2D2D2D; border-radius: 3px; }
            QSlider::handle:horizontal { background: #FBC02D; width: 16px; margin-top: -5px; margin-bottom: -5px; border-radius: 8px; }
        """)
        self.slider_limite.valueChanged.connect(self.atualizar_valor_slider)
        self.layout_principal.addWidget(self.slider_limite)
        
        # --- SEÇÃO BOTÕES: SIMULAR EVENTOS DO ARDUINO/BACKEND ---
        lbl_testes = QLabel("Simular Cenários do Sistema:")
        lbl_testes.setStyleSheet("font-size: 12px; color: #AAAAAA; border: none; background: transparent; margin-top: 10px;")
        self.layout_principal.addWidget(lbl_testes)
        
        # Botão 1: Pico de Consumo
        self.btn_pico = QPushButton("Simular Sobrecarga (Pico)")
        self.btn_pico.setStyleSheet(self.estilo_botao("#D32F2F"))
        self.btn_pico.clicked.connect(self.acao_simular_pico)
        self.layout_principal.addWidget(self.btn_pico)
        
        # Botão 2: Superávit Solar
        self.btn_sol = QPushButton("Simular Alta Geração Solar")
        self.btn_sol.setStyleSheet(self.estilo_botao("#388E3C"))
        self.btn_sol.clicked.connect(self.acao_simular_sol)
        self.layout_principal.addWidget(self.btn_sol)
        
        # Espaçador para empurrar tudo para o topo
        self.layout_principal.addStretch()
        
    def estilo_botao(self, cor_fundo):
        return f"""
            QPushButton {{
                background-color: {cor_fundo};
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 4px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {cor_fundo}CC;
            }}
        """
        
    def atualizar_valor_slider(self, valor):
        self.lbl_slider_status.setText(f"Meta Limite de Consumo: {valor:.1f} kWh")
        
    def acao_simular_pico(self):
        if self.disparar_alerta:
            self.disparar_alerta(
                "Alerta de Sobrecarga", 
                "Consumo ultrapassou a meta definida! Executando corte automático de cargas não críticas."
            )
            
    def acao_simular_sol(self):
        if self.disparar_alerta:
            self.disparar_alerta(
                "Superávit Energético", 
                "Geração solar cobrindo 100% da demanda. Iniciando carregamento das baterias."
            )