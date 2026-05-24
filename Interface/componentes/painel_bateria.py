import math
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTextEdit
from PySide6.QtCore import Qt

class PainelBateria(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bateria_soc = 50.0  # Estado de Carga Inicial (50%)
        self.capacidade_total = 5.0  # 5.0 kWh
        self.setup_ui()

    def setup_ui(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)

        # Cabeçalho Informativo
        lbl_titulo = QLabel("Gerenciamento do Banco de Baterias (EMS)")
        lbl_titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        layout_principal.addWidget(lbl_titulo)

        # Container Horizontal para os Cards de Status
        container_cards = QHBoxLayout()

        # Card 1: Estado de Carga (SoC)
        self.card_soc = QFrame()
        self.card_soc.setStyleSheet("background-color: #1E1E1E; border: 1px solid #333333; border-radius: 6px; padding: 15px;")
        ly_soc = QVBoxLayout(self.card_soc)
        lbl_soc_tit = QLabel("ESTADO DE CARGA (SoC)")
        lbl_soc_tit.setStyleSheet("font-size: 10px; color: #888888; border: none;")
        self.lbl_soc_val = QLabel("50%")
        self.lbl_soc_val.setStyleSheet("font-size: 28px; font-weight: bold; color: #00E676; border: none;")
        ly_soc.addWidget(lbl_soc_tit)
        ly_soc.addWidget(self.lbl_soc_val)
        container_cards.addWidget(self.card_soc)

        # Card 2: Fluxo Potência Corrente
        self.card_fluxo = QFrame()
        self.card_fluxo.setStyleSheet("background-color: #1E1E1E; border: 1px solid #333333; border-radius: 6px; padding: 15px;")
        ly_fluxo = QVBoxLayout(self.card_fluxo)
        lbl_fluxo_tit = QLabel("FLUXO DE POTÊNCIA")
        lbl_fluxo_tit.setStyleSheet("font-size: 10px; color: #888888; border: none;")
        self.lbl_fluxo_val = QLabel("0.0 kWh (Ocioso)")
        self.lbl_fluxo_val.setStyleSheet("font-size: 20px; font-weight: bold; color: #B0BEC5; border: none;")
        ly_fluxo.addWidget(lbl_fluxo_tit)
        ly_fluxo.addWidget(self.lbl_fluxo_val)
        container_cards.addWidget(self.card_fluxo)

        layout_principal.addLayout(container_cards)

        # Terminal de telemetria da bateria
        lbl_diag_tit = QLabel("📋 Histórico de Ciclos e Saúde do Banco")
        lbl_diag_tit.setStyleSheet("font-size: 11px; font-weight: bold; color: #00ACC1; margin-top: 15px;")
        layout_principal.addWidget(lbl_diag_tit)

        self.txt_log_bateria = QTextEdit()
        self.txt_log_bateria.setReadOnly(True)
        self.txt_log_bateria.setStyleSheet("""
            background-color: #121212; color: #A5D6A7; 
            font-family: 'Consolas', monospace; font-size: 11px;
            border: 1px solid #2D2D2D; border-radius: 4px;
        """)
        self.txt_log_bateria.append("Bateria Lithium-Ion de 5.0 kWh operacional. SOH: 100%.")
        layout_principal.addWidget(self.txt_log_bateria)
        
        layout_principal.addStretch()

    def atualizar_dados_bateria(self, saldo_solar, taxa_maxima=0.5):
        """Calcula a carga física e atualiza o visual da aba isolada."""
        energia_movimentada = 0.0

        if saldo_solar > 0:
            # Sobrou energia: Carrega
            if self.bateria_soc < 100.0:
                energia_movimentada = min(saldo_solar, taxa_maxima)
                self.bateria_soc += (energia_movimentada / self.capacidade_total) * 100
                self.bateria_soc = min(100.0, self.bateria_soc)
            
            self.lbl_fluxo_val.setText(f"+{energia_movimentada:.1f} kWh (Carregando)")
            self.lbl_fluxo_val.setStyleSheet("font-size: 20px; font-weight: bold; color: #4CAF50; border: none;")
            saldo_final_rede = round(saldo_solar - energia_movimentada, 1)
        else:
            # Faltou energia: Descarrega
            if self.bateria_soc > 10.0:
                necessidade = abs(saldo_solar)
                energia_movimentada = min(necessidade, taxa_maxima)
                self.bateria_soc -= (energia_movimentada / self.capacidade_total) * 100
                self.bateria_soc = max(10.0, self.bateria_soc)
                
                self.lbl_fluxo_val.setText(f"-{energia_movimentada:.1f} kWh (Descarregando)")
                self.lbl_fluxo_val.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFC107; border: none;")
                saldo_final_rede = round(saldo_solar + energia_movimentada, 1)
            else:
                self.lbl_fluxo_val.setText("0.0 kWh (Esgotada)")
                self.lbl_fluxo_val.setStyleSheet("font-size: 20px; font-weight: bold; color: #F44336; border: none;")
                saldo_final_rede = saldo_solar

        # Atualiza o mostrador do SoC (%)
        self.lbl_soc_val.setText(f"{int(self.bateria_soc)}%")
        
        # Retorna o saldo da rede e quanta energia a bateria usou para o loop principal saber
        return saldo_final_rede, energia_movimentada