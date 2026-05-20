import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt

class DashboardEnergia(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Energia Certa - Dashboard")
        self.resize(900, 600)
        
        # Dark mode
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QLabel {
                color: #FFFFFF;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        
        self.widget_central = QWidget()
        self.setCentralWidget(self.widget_central)
        
        self.layout_principal = QVBoxLayout()
        self.widget_central.setLayout(self.layout_principal)
        
        self.linha_cards = QHBoxLayout()
        self.layout_principal.addLayout(self.linha_cards) 
        
        
        self.card_consumo = self.criar_card("CONSUMO ATUAL", "4.5 kWh", "#E53935") # Vermelho
        self.card_geracao = self.criar_card("GERAÇÃO ATUAL", "5.2 kWh", "#4CAF50") # Verde
        self.card_saldo = self.criar_card("SALDO ENERGÉTICO", "+0.7 kWh", "#00ACC1") # Azul
        
        
        self.linha_cards.addWidget(self.card_consumo)
        self.linha_cards.addWidget(self.card_geracao)
        self.linha_cards.addWidget(self.card_saldo)
        
        
        self.layout_principal.addStretch()

   
    def criar_card(self, titulo, valor, cor_borda):
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background-color: #1E1E1E;
                border: 2px solid {cor_borda};
                border-radius: 8px;
            }}
        """)
        card.setFixedSize(260, 100) 
        
        
        layout_card = QVBoxLayout(card)
        
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("font-size: 11px; font-weight: bold; color: #AAAAAA; border: none;")
        
        lbl_valor = QLabel(valor)
        lbl_valor.setStyleSheet("font-size: 24px; font-weight: bold; border: none;")
        lbl_valor.setAlignment(Qt.AlignCenter)
        
        layout_card.addWidget(lbl_titulo)
        layout_card.addWidget(lbl_valor)
        
        return card

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = DashboardEnergia()
    janela.show()
    sys.exit(app.exec())