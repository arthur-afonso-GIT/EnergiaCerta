# Arquivo: Interface/dashboard.py
import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QToolButton, QMenu, QSystemTrayIcon)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QAction, QIcon

# Importando nossos componentes e o leitor do Core
from Interface.componentes.painel_cargas import PainelCargasCriticas
from Interface.componentes.grafico_tempo_real import CanvasGraficoEnergia
from Interface.componentes.painel_simulacao import PainelSimulacaoDecisao
from Core.comunicacao_serial import LeitorArduino # <-- IMPORTANDO O NOVO LEITOR CORRIGIDO

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
            QScrollBar:vertical { border: none; background: #121212; width: 6px; }
            QScrollBar::handle:vertical { background: #444444; border-radius: 3px; }
        """)
        
        # Configuração do Notify
        self.tray_icon = QSystemTrayIcon(self)
        caminho_logo = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
        if os.path.exists(caminho_logo):
            self.tray_icon.setIcon(QIcon(caminho_logo))
        self.tray_icon.show()
        
        # --- INICIALIZAÇÃO DO LEITOR DE HARDWARE ---
        self.leitor = LeitorArduino()
        
        # Histórico local limpo para receber a simulação em tempo real
        self.historico_horas = []
        self.historico_consumo = []
        self.historico_geracao = []
        self.contador_tempo = 10 # Começa em sincronia com o Core
        
        self.widget_central = QWidget()
        self.setCentralWidget(self.widget_central)
        self.layout_mestre = QHBoxLayout()
        self.widget_central.setLayout(self.layout_mestre)
        
        # -------------------------------------------------------------
        # COLUNA 1: ESQUERDA
        # -------------------------------------------------------------
        self.coluna_esquerda = QVBoxLayout()
        
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
        
        self.painel_cargas = PainelCargasCriticas()
        
        self.painel_recomendacoes = QWidget()
        self.painel_recomendacoes.setStyleSheet("background-color: #1E1E1E; border: 1px solid #333333; border-radius: 6px;")
        layout_rec = QVBoxLayout(self.painel_recomendacoes)
        self.lbl_decisao_texto = QLabel("Analisando fluxo energético...")
        self.lbl_decisao_texto.setStyleSheet("font-size: 13px; font-weight: bold; color: #FBC02D; border: none; background: transparent;")
        self.lbl_decisao_texto.setAlignment(Qt.AlignCenter)
        self.lbl_decisao_texto.setWordWrap(True)
        layout_rec.addWidget(self.lbl_decisao_texto)
        
        self.coluna_esquerda.addWidget(self.container_logo, stretch=1)
        self.coluna_esquerda.addWidget(self.painel_cargas, stretch=4)
        self.coluna_esquerda.addWidget(self.painel_recomendacoes, stretch=2)
        
        # -------------------------------------------------------------
        # COLUNA 2: CENTRAL
        # -------------------------------------------------------------
        self.coluna_central = QVBoxLayout()
        self.linha_cards = QHBoxLayout()
        
        self.card_consumo, self.lbl_val_consumo = self.criar_card_kpi("CONSUMO ATUAL", "4.5 kWh", "#E53935")
        self.card_geracao, self.lbl_val_geracao = self.criar_card_kpi("GERAÇÃO ATUAL", "5.2 kWh", "#4CAF50")
        self.card_saldo, self.lbl_val_saldo = self.criar_card_kpi("SALDO ENERGÉTICO", "+0.7 kWh", "#00ACC1")
        
        self.linha_cards.addWidget(self.card_consumo)
        self.linha_cards.addWidget(self.card_geracao)
        self.linha_cards.addWidget(self.card_saldo)
        self.coluna_central.addLayout(self.linha_cards, stretch=2)
        
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
        self.painel_simulacao = PainelSimulacaoDecisao(callback_alerta=self.notificar_alerta)
        self.coluna_direita.addWidget(self.painel_simulacao)
        
        self.layout_mestre.addLayout(self.coluna_esquerda, stretch=3)
        self.layout_mestre.addLayout(self.coluna_central, stretch=5)
        self.layout_mestre.addLayout(self.coluna_direita, stretch=3)
        
        # Timer de Atualização
        self.timer = QTimer()
        self.timer.timeout.connect(self.loop_atualizacao_tempo_real)
        self.timer.start(2000)
        
        self.atualizar_visual_grafico()

    def notificar_alerta(self, titulo, message):
        self.tray_icon.showMessage(titulo, message, QSystemTrayIcon.Information, 3000)

    def criar_card_kpi(self, titulo, valor_inicial, cor_borda):
        card = QWidget()
        card.setStyleSheet(f"QWidget {{ background-color: #1E1E1E; border: 2px solid {cor_borda}; border-radius: 8px; }}")
        layout = QVBoxLayout(card)
        t = QLabel(titulo); t.setStyleSheet("font-size: 10px; font-weight: bold; color: #AAAAAA; border: none; background: transparent;")
        t.setAlignment(Qt.AlignCenter)
        v = QLabel(valor_inicial); v.setStyleSheet("font-size: 22px; font-weight: bold; border: none; background: transparent;")
        v.setAlignment(Qt.AlignCenter)
        layout.addWidget(t); layout.addWidget(v)
        return card, v

    def atualizar_visual_grafico(self):
        self.canvas_grafico.atualizar_linhas(
            self.historico_horas,
            self.historico_consumo,
            self.historico_geracao
        )

    def loop_atualizacao_tempo_real(self):
        """Coleta dados do backend baseados física solar e empurra para a interface"""
        # 1. Coleta os dados e o tempo do novo simulador matemático
        novo_consumo, nova_geracao, hora_float = self.leitor.ler_dados_reais()
        saldo = round(nova_geracao - novo_consumo, 1)
        
        # Converte a hora float (ex: 10.5) para formato de texto amigável (ex: "10:30")
        horas_inteiras = int(hora_float)
        minutos = int((hora_float - horas_inteiras) * 60)
        texto_hora = f"{horas_inteiras:02d}:{minutos:02d}"
        
        # 2. Atualiza os históricos locais para o gráfico seguir a linha do tempo linearmente
        self.historico_horas.append(texto_hora)
        self.historico_consumo.append(novo_consumo)
        self.historico_geracao.append(nova_geracao)
        
        if len(self.historico_horas) > 7:
            self.historico_horas.pop(0)
            self.historico_consumo.pop(0)
            self.historico_geracao.pop(0)
        
        # 3. Atualiza os componentes visuais dos Cards KPI
        self.lbl_val_consumo.setText(f"{novo_consumo} kWh")
        self.lbl_val_geracao.setText(f"{nova_geracao} kWh")
        sinal = "+" if saldo >= 0 else ""
        self.lbl_val_saldo.setText(f"{sinal}{saldo} kWh")
        
        self.atualizar_visual_grafico()
        
        # 4. Lógica de decisão automática (Consumo > Geração)
        if saldo < 0:
            self.lbl_decisao_texto.setText(f"⚠️ DÉFICIT DE ENERGIA\nConsumo superando geração em {abs(saldo)} kWh. Recomendado desligar cargas não críticas.")
            self.lbl_decisao_texto.setStyleSheet("font-size: 13px; font-weight: bold; color: #E53935; background: transparent;")
        else:
            self.lbl_decisao_texto.setText(f"✅ SISTEMA EM SUPERÁVIT\nGeração solar cobrindo toda a demanda com sobra de {saldo} kWh.")
            self.lbl_decisao_texto.setStyleSheet("font-size: 13px; font-weight: bold; color: #4CAF50; background: transparent;")