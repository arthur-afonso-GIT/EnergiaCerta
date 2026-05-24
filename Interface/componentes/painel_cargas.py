# Arquivo: Interface/componentes/painel_cargas.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

class PainelCargasCriticas(QWidget):
    def __init__(self):
        super().__init__()
        
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
        
        lbl_titulo = QLabel("Monitoramento de Cargas")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_titulo)
        
        # Definição clara: Quais são críticas (nunca desligam) e quais não são (podem ser cortadas)
        self.cargas = {
            "Geladeira": {"critica": True, "botao": QPushButton("⚡ [CRÍTICA] Geladeira")},
            "Iluminação Sala": {"critica": True, "botao": QPushButton("⚡ [CRÍTICA] Iluminação Sala")},
            "Roteador Internet": {"critica": True, "botao": QPushButton("⚡ [CRÍTICA] Roteador Internet")},
            "Ar-Condicionado": {"critica": False, "botao": QPushButton("⚡ [SISTEMA] Ar-Condicionado")},
            "Bomba D'água": {"critica": False, "botao": QPushButton("⚡ [SISTEMA] Bomba D'água")},
            "Computador": {"critica": False, "botao": QPushButton("⚡ [SISTEMA] Computador")}
        }
        
        # Estado interno: True = Ligado, False = Desligado pelo gerenciamento inteligente
        self.estados = {nome: True for nome in self.cargas}
        
        for nome, info in self.cargas.items():
            layout.addWidget(info["botao"])
            # Estilo inicial de ligado
            self.atualizar_estilo_botao(nome)
            
    def obter_estados(self):
        return self.estados
        
    def definir_estado_carga(self, nome, ligado):
        if nome in self.estados:
            self.estados[nome] = ligado
            self.atualizar_estilo_botao(nome)
            
    def atualizar_estilo_botao(self, nome):
        botao = self.cargas[nome]["botao"]
        prefixo = "[CRÍTICA]" if self.cargas[nome]["critica"] else "[SISTEMA]"
        
        if self.estados[nome]:
            botao.setText(f"🟢 {prefixo} {nome} - Ativo")
            botao.setStyleSheet("background-color: #2D2D2D; color: #FFFFFF; border: 1px solid #444444;")
        else:
            botao.setText(f"🔴 ⚠️ {prefixo} {nome} - DESLIGADO (Corte de Pico)")
            botao.setStyleSheet("background-color: #3a1c1c; color: #E53935; border: 1px solid #E53935; font-weight: bold;")