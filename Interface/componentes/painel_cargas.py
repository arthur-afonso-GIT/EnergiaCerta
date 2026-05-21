from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PySide6.QtCore import Qt

class PainelCargasCriticas(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setStyleSheet("background-color: #1E1E1E; border-radius: 6px; border: 1px solid #333333;")
        self.layout_principal = QVBoxLayout(self)
        
        lbl_titulo = QLabel("Cargas Críticas")
        lbl_titulo.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFFFFF; border: none; background: transparent;")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        self.layout_principal.addWidget(lbl_titulo)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none; background: transparent;")
        
        self.conteudo_scroll = QWidget()
        self.conteudo_scroll.setStyleSheet("background: transparent; border: none;")
        self.layout_lista = QVBoxLayout(self.conteudo_scroll)
        self.layout_lista.setContentsMargins(0, 5, 0, 5)
        dispositivos = ["Geladeira", "Iluminação Sala", "Roteador Internet", "Ar-Condicionado", "Bomba D'água", "Computador"]
        
        for nome in dispositivos:
            lbl_item = QLabel(f"{nome}")
            lbl_item.setStyleSheet("""
                QLabel { 
                    background-color: #2D2D2D; 
                    padding: 12px; 
                    border-radius: 4px; 
                    border: 1px solid #444444;
                    font-size: 12px;
                    font-weight: 500;
                }
                QLabel:hover {
                    background-color: #353535;
                    border: 1px solid #FBC02D;
                }
            """)
            lbl_item.setAlignment(Qt.AlignCenter)
            self.layout_lista.addWidget(lbl_item)
            
        self.scroll_area.setWidget(self.conteudo_scroll)
        self.layout_principal.addWidget(self.scroll_area)