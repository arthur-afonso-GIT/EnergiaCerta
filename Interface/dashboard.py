# Arquivo: Interface/dashboard.py
import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QToolButton, QMenu, QSystemTrayIcon)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QAction, QIcon

# --- IMPORTANDO NOSSOS COMPONENTES ISOLADOS ---
from Interface.componentes.painel_cargas import PainelCargasCriticas
from Interface.componentes.grafico_tempo_real import CanvasGraficoEnergia

class DashboardEnergia(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Energia Certa - Dashboard Principal")
        self.resize(1240, 720)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #121212; }
            QLabel { color: #FFFFFF; font-family: 'Segoe UI', sans-serif; }
            QMenu { background-color: #1E1E1E; color: white; border: 1px solid #333333; border-radius: 4px; padding: 5px; }
            QMenu::item:selected { background-color: #FBC02D; color: #121212; font-weight: bold; }
            QToolButton { background-color: #2D2D2D; color: white; border: 1px solid #444444; border-radius: 4px; padding: 8px; font-weight: bold; }
            QToolButton:hover { background-color: #444444; }
            
            /* Scrollbar Global do App */
            QScrollBar:vertical { border: none; background: #121212; width: 6px; }
            QScrollBar::handle:vertical { background: #444444; border-radius: 3px; }
        """)
        
        # Configuração do Notify
        self.tray_icon = QSystemTrayIcon(self)
        caminho_logo = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
        if os.path.exists(caminho_logo):
            self.tray_icon.setIcon(QIcon(caminho_logo))
        self.tray_icon.show()
        
        self.widget_central = QWidget()
        self.setCentralWidget(self.widget_central)
        self.layout_mestre = QHBoxLayout()
        self.widget_central.setLayout(self.layout_mestre)
        
        # -------------------------------------------------------------
        # COLUNA 1: ESQUERDA
        # -------------------------------------------------------------
        self.coluna_esquerda = QVBoxLayout()
        
        # Bloco da Logo e Menu
        self.container_logo = QWidget()
        self.container_logo.setStyleSheet("background-color: #1E1E1E; border-radius: 6px; border: 1px solid #333333;")
        self.layout_logo_bloco = QHBoxLayout(self.container_logo)
        
        self.lbl_logo_imagem = QLabel()
        pixmap = QPixmap(caminho_logo)
        if not pixmap.isNull():
            self.lbl_logo_imagem.setPixmap(pixmap.scaled(130, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.lbl_logo_imagem.setText("⭐ Energia Certa")
        
        self.botao_menu = QToolButton()
        self.botao_menu.setText("☰ Menu")
        self.botao_menu.setPopupMode(QToolButton.InstantPopup)
        self.dropmenu = QMenu(self)
        self.acao_config = QAction("⚙️ Configurações", self)
        self.acao_hardware = QAction("🔌 Conectar Arduino", self)
        self.acao_sobre = QAction("ℹ️ Sobre o Projeto", self)
        self.dropmenu.addAction(self.acao_config)
        self.dropmenu.addAction(self.acao_hardware)
        self.dropmenu.addSeparator()
        self.dropmenu.addAction(self.acao_sobre)
        self.botao_menu.setMenu(self.dropmenu)
        
        self.layout_logo_bloco.addWidget(self.lbl_logo_imagem, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        self.layout_logo_bloco.addWidget(self.botao_menu, alignment=Qt.AlignRight | Qt.AlignVCenter)
        
        # INSTANCIANDO O PAINEL DE CARGAS (Vindo do arquivo separado!)
        self.painel_cargas = PainelCargasCriticas()
        
        # Recomendação Automática
        self.painel_recomendacoes = self.criar_painel_teste("Recomendação de decisão automática", "#1E1E1E")
        
        self.coluna_esquerda.addWidget(self.container_logo, stretch=1)
        self.coluna_esquerda.addWidget(self.painel_cargas, stretch=4)
        self.coluna_esquerda.addWidget(self.painel_recomendacoes, stretch=2)
        
        # -------------------------------------------------------------
        # COLUNA 2: CENTRAL
        # -------------------------------------------------------------
        self.coluna_central = QVBoxLayout()
        self.linha_cards = QHBoxLayout()
        self.linha_cards.addWidget(self.criar_card_kpi("CONSUMO ATUAL", "4.5 kWh", "#E53935"))
        self.linha_cards.addWidget(self.criar_card_kpi("GERAÇÃO ATUAL", "5.2 kWh", "#4CAF50"))
        self.linha_cards.addWidget(self.criar_card_kpi("SALDO ENERGÉTICO", "+0.7 kWh", "#00ACC1"))
        self.coluna_central.addLayout(self.linha_cards, stretch=2)
        
        # CONTAINER E INSTÂNCIA DO GRÁFICO (Vindo do arquivo separado!)
        self.container_grafico = QWidget()
        self.container_grafico.setStyleSheet("background-color: #1E1E1E; border-radius: 6px; border: 1px solid #333333;")
        self.layout_grafico_bloco = QVBoxLayout(self.container_grafico)
        
        self.canvas_grafico = CanvasGraficoEnergia()
        self.layout_grafico_bloco.addWidget(self.canvas_grafico)
        self.coluna_central.addWidget(self.container_grafico, stretch=5)
        
        # -------------------------------------------------------------
        # COLUNA 3: DIREITA
        # -------------------------------------------------------------
        self.coluna_direita = QVBoxLayout()
        self.painel_simulacao = self.criar_painel_teste("Painel de Simulação de Decisão e Economia", "#1E1E1E")
        self.coluna_direita.addWidget(self.painel_simulacao)
        
        # Acoplamento das Colunas no Layout Mestre
        self.layout_mestre.addLayout(self.coluna_esquerda, stretch=3)
        self.layout_mestre.addLayout(self.coluna_central, stretch=5)
        self.layout_mestre.addLayout(self.coluna_direita, stretch=3)

    def notificar_alerta(self, titulo, message):
        self.tray_icon.showMessage(titulo, message, QSystemTrayIcon.Information, 3000)

    def criar_painel_teste(self, texto, cor_fundo):
        painel = QWidget()
        painel.setStyleSheet(f"QWidget {{ background-color: {cor_fundo}; border: 1px solid #333333; border-radius: 6px; }}")
        layout = QVBoxLayout(painel)
        lbl = QLabel(texto)
        lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #888888; border: none; background: transparent;")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setWordWrap(True)
        layout.addWidget(lbl)
        return painel

    def criar_card_kpi(self, titulo, valor, cor_borda):
        card = QWidget()
        card.setStyleSheet(f"QWidget {{ background-color: #1E1E1E; border: 2px solid {cor_borda}; border-radius: 8px; }}")
        layout = QVBoxLayout(card)
        t = QLabel(titulo); t.setStyleSheet("font-size: 10px; font-weight: bold; color: #AAAAAA; border: none; background: transparent;")
        t.setAlignment(Qt.AlignCenter)
        v = QLabel(valor); v.setStyleSheet("font-size: 22px; font-weight: bold; border: none; background: transparent;")
        v.setAlignment(Qt.AlignCenter)
        layout.addWidget(t); layout.addWidget(v)
        return card