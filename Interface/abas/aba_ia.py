from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel, QPushButton

class AbaIA(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        self.titulo = QLabel("🧠 Inteligência Artificial & Recomendações")
        self.titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #00E676;")
        layout.addWidget(self.titulo)
        
        # Log de IA estilizado
        self.painel_recomendacoes = QTextEdit()
        self.painel_recomendacoes.setReadOnly(True)
        self.painel_recomendacoes.setStyleSheet("""
            QTextEdit {
                background-color: #1A1A1A; 
                border: 1px solid #2D2D2D; 
                border-radius: 8px;
                padding: 15px;
                color: #FFFFFF;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
        """)
        self.painel_recomendacoes.setHtml("""
            <p style='color: #888888;'>[SISTEMA] Inicializando EMS Core v2.0...</p>
            <p style='color: #00E676;'>✔ Conexão com banco de baterias estabelecida (SoC: 50%).</p>
            <p style='color: #FFB300;'>⚠ Recomendação: Reduzir uso da Bomba D'água caso o superávit solar caia.</p>
        """)
        layout.addWidget(self.painel_recomendacoes)
        
        # Botão interativo para forçar otimização
        self.btn_otimizar = QPushButton("Forçar Otimização do Fluxo")
        self.btn_otimizar.setStyleSheet("""
            QPushButton {
                background-color: #00E676;
                color: #000000;
                font-weight: bold;
                border-radius: 6px;
                padding: 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #00B359;
            }
            QPushButton:pressed {
                background-color: #00803C;
            }
        """)
        # Exemplo de interatividade: limpando ou acionando algo ao clicar
        self.btn_otimizar.clicked.connect(self.executar_otimizacao)
        layout.addWidget(self.btn_otimizar)
        
        self.setStyleSheet("background-color: #121212;")

    def executar_otimizacao(self):
        self.painel_recomendacoes.append("<p style='color: #00E676;'>[EMS] Re-analisando histórico de geração e consumo... Tudo estável!</p>")