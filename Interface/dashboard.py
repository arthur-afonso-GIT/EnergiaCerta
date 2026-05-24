# Arquivo: Interface/dashboard.py
import os
import math
import random
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QToolButton, QMenu, QSystemTrayIcon, 
                             QPushButton, QInputDialog, QFrame, QTabWidget, QMessageBox, QScrollArea, QTextEdit, QFrame)
from PySide6.QtCore import Qt, QTimer, QTime
from PySide6.QtGui import QPixmap, QAction, QIcon

from Interface.componentes.grafico_tempo_real import CanvasGraficoEnergia
from Interface.componentes.painel_simulacao import PainelSimulacaoDecisao
from leitor import LeitorHardware
from Interface.componentes.painel_bateria import PainelBateria
from PySide6.QtWidgets import QTabWidget 

class DashboardEnergia(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.leitor = LeitorHardware(porta='COM3')
        self.setWindowTitle("Energia Certa - Dashboard Principal")
        self.resize(1240, 720)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #121212; }
            QLabel { color: #FFFFFF; font-family: 'Segoe UI', sans-serif; }
            QMenu { background-color: #1E1E1E; color: white; border: 1px solid #333333; border-radius: 4px; padding: 5px; }
            QMenu::item:selected { background-color: #FBC02D; color: #121212; font-weight: bold; }
            QToolButton { background-color: #2D2D2D; color: white; border: 1px solid #444444; border-radius: 4px; padding: 8px; font-weight: bold; }
            QToolButton:hover { background-color: #444444; }
        """)
        
        self.tray_icon = QSystemTrayIcon(self)
        caminho_logo = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
        if os.path.exists(caminho_logo):
            self.tray_icon.setIcon(QIcon(caminho_logo))
        self.tray_icon.show()
        
        self.hora_atual = 10.0
        self.historico_horas = []
        self.historico_consumo = []
        self.historico_geracao = []
        
        # -------------------------------------------------------------
        # COLUNA 1: ESQUERDA (Logo, Cargas e Resumo IA)
        # -------------------------------------------------------------
        self.coluna_esquerda = QVBoxLayout()
        
        # Bloco da Logo
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
        self.dropmenu.addAction(QAction("⚙️ Configurações", self))
        self.botao_menu.setMenu(self.dropmenu)
        
        self.layout_logo_bloco.addWidget(self.lbl_logo_imagem, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        self.layout_logo_bloco.addWidget(self.botao_menu, alignment=Qt.AlignRight | Qt.AlignVCenter)
        
        # Container de Gerenciamento das Cargas
        self.painel_cargas_container = QWidget()
        self.painel_cargas_container.setStyleSheet("background-color: #1E1E1E; border: 1px solid #333333; border-radius: 6px;")
        layout_container_vertical = QVBoxLayout(self.painel_cargas_container)
        
        lbl_tit_cargas = QLabel("Gerenciamento de Cargas")
        lbl_tit_cargas.setAlignment(Qt.AlignCenter)
        lbl_tit_cargas.setStyleSheet("font-weight: bold; font-size: 13px; padding: 5px; border: none;")
        layout_container_vertical.addWidget(lbl_tit_cargas)
        
        self.btn_add_carga = QPushButton("➕ ADICIONAR NOVA CARGA")
        self.btn_add_carga.setStyleSheet("""
            background-color: #00ACC1; color: white; font-weight: bold; 
            border: none; padding: 10px; text-align: center; border-radius: 4px;
        """)
        self.btn_add_carga.clicked.connect(self.abrir_dialogo_adicionar_carga)
        layout_container_vertical.addWidget(self.btn_add_carga)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none; background: transparent;")
        
        self.widget_lista_cargas = QWidget()
        self.widget_lista_cargas.setStyleSheet("background: transparent; border: none;")
        self.layout_cargas = QVBoxLayout(self.widget_lista_cargas)
        self.layout_cargas.setContentsMargins(0, 5, 0, 5)
        self.layout_cargas.setAlignment(Qt.AlignTop)
        
        self.scroll_area.setWidget(self.widget_lista_cargas)
        layout_container_vertical.addWidget(self.scroll_area)
        
        self.config_cargas = {
            "Geladeira": {"critica": True, "potencia": 0.8, "ativo": True, "btn": None},
            "Iluminação Sala": {"critica": True, "potencia": 0.3, "ativo": True, "btn": None},
            "Roteador Internet": {"critica": True, "potencia": 0.1, "ativo": True, "btn": None},
            "Ar-Condicionado": {"critica": False, "potencia": 2.0, "ativo": True, "btn": None},
            "Bomba D'água": {"critica": False, "potencia": 1.2, "ativo": True, "btn": None},
            "Computador": {"critica": False, "potencia": 0.5, "ativo": True, "btn": None}
        }
        
        for nome in list(self.config_cargas.keys()):
            self.criar_e_adicionar_botao_na_tela(nome)
        
        # Painel de Resumo de Decisão Rápida
        self.painel_recomendacoes = QWidget()
        self.painel_recomendacoes.setStyleSheet("background-color: #1E1E1E; border: 1px solid #333333; border-radius: 6px;")
        layout_rec = QVBoxLayout(self.painel_recomendacoes)
        self.lbl_decisao_texto = QLabel("Analisando fluxo energético...")
        self.lbl_decisao_texto.setStyleSheet("font-size: 11px; font-weight: bold; color: #FBC02D; border: none; background: transparent;")
        self.lbl_decisao_texto.setAlignment(Qt.AlignCenter)
        self.lbl_decisao_texto.setWordWrap(True)
        layout_rec.addWidget(self.lbl_decisao_texto)
        
        self.coluna_esquerda.addWidget(self.container_logo, stretch=1)
        self.coluna_esquerda.addWidget(self.painel_cargas_container, stretch=5)
        self.coluna_esquerda.addWidget(self.painel_recomendacoes, stretch=2)
        
        # -------------------------------------------------------------
        # COLUNA 2: CENTRAL (Cards KPI e Gráfico Matplotlib)
        # -------------------------------------------------------------
        self.coluna_central = QVBoxLayout()
        self.linha_cards = QHBoxLayout()
        
        self.card_consumo, self.lbl_val_consumo = self.criar_card_kpi("CONSUMO ATUAL", "0.0 kWh", "#E53935")
        self.card_geracao, self.lbl_val_geracao = self.criar_card_kpi("GERAÇÃO ATUAL", "0.0 kWh", "#4CAF50")
        self.card_saldo, self.lbl_val_saldo = self.criar_card_kpi("SALDO ENERGÉTICO", "0.0 kWh", "#00ACC1")
        
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
        # COLUNA 3: DIREITA (Configurações, Agendamento e Logs)
        # -------------------------------------------------------------
        self.coluna_direita = QVBoxLayout()
        
        # --- PAINEL DE METAS E PARAMETRIZAÇÃO ---
        self.container_metas = QWidget()
        self.container_metas.setStyleSheet("background-color: #1E1E1E; border: 1px solid #333333; border-radius: 6px;")
        layout_metas_interno = QVBoxLayout(self.container_metas)
        layout_metas_interno.setContentsMargins(10, 10, 10, 10)

        lbl_titulo_metas = QLabel("Configuracao de Metas")
        lbl_titulo_metas.setStyleSheet("font-weight: bold; font-size: 14px; color: #FFFFFF; border: none;")
        layout_metas_interno.addWidget(lbl_titulo_metas)

        self.lbl_meta_status = QLabel("Meta Limite de Consumo: 5.0 kWh")
        self.lbl_meta_status.setStyleSheet("font-size: 11px; color: #B0BEC5; border: none; margin-top: 5px;")
        layout_metas_interno.addWidget(self.lbl_meta_status)

        from PySide6.QtWidgets import QSlider
        self.sld_meta_consumo = QSlider(Qt.Horizontal)
        self.sld_meta_consumo.setMinimum(10)  
        self.sld_meta_consumo.setMaximum(100) 
        self.sld_meta_consumo.setValue(50)    
        self.sld_meta_consumo.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #2D2D2D;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #00ACC1;
                width: 14px;
                margin-top: -4px;
                margin-bottom: -4px;
                border-radius: 7px;
            }
        """)
        layout_metas_interno.addWidget(self.sld_meta_consumo)
        
        self.sld_meta_consumo.valueChanged.connect(
            lambda v: self.lbl_meta_status.setText(f"Meta Limite de Consumo: {v/10.0:.1f} kWh")
        )

        self.coluna_direita.addWidget(self.container_metas, stretch=3)
        
        # --- PAINEL PREDITIVO DE AGENDAMENTO INTELIGENTE ---
        self.container_preditivo = QWidget()
        self.container_preditivo.setStyleSheet("background-color: #1E1E1E; border: 1px solid #333333; border-radius: 6px;")
        layout_preditivo_interno = QVBoxLayout(self.container_preditivo)
        layout_preditivo_interno.setContentsMargins(10, 10, 10, 10)

        lbl_titulo_preditivo = QLabel("Agendamento Inteligente (Otimizacao)")
        lbl_titulo_preditivo.setStyleSheet("font-weight: bold; font-size: 12px; color: #00ACC1; border: none;")
        layout_preditivo_interno.addWidget(lbl_titulo_preditivo)

        # Caixa 1: Melhor horário para aparelhos pesados
        self.box_melhor_horario = QFrame()
        self.box_melhor_horario.setStyleSheet("background-color: #121212; border: 1px solid #2D2D2D; border-radius: 4px;")
        layout_box1 = QVBoxLayout(self.box_melhor_horario)
        
        self.lbl_carga_titulo = QLabel("JANELA DE USO RECOMENDADA")
        self.lbl_carga_titulo.setStyleSheet("font-size: 9px; font-weight: bold; color: #888888; border: none;")
        self.lbl_carga_status = QLabel("Aguardando analise de fluxo...")
        self.lbl_carga_status.setStyleSheet("font-size: 11px; color: #4CAF50; font-weight: bold; border: none;")
        
        layout_box1.addWidget(self.lbl_carga_titulo)
        layout_box1.addWidget(self.lbl_carga_status)
        layout_preditivo_interno.addWidget(self.box_melhor_horario)

        # Caixa 2: Status e recomendação da bateria
        self.box_bateria_horario = QFrame()
        self.box_bateria_horario.setStyleSheet("background-color: #121212; border: 1px solid #2D2D2D; border-radius: 4px;")
        layout_box2 = QVBoxLayout(self.box_bateria_horario)
        
        self.lbl_bat_titulo = QLabel("DIRETRIZ DE CARGA DA BATERIA")
        self.lbl_bat_titulo.setStyleSheet("font-size: 9px; font-weight: bold; color: #888888; border: none;")
        self.lbl_bateria_status = QLabel("Aguardando estabilizacao de matriz...")
        self.lbl_bateria_status.setStyleSheet("font-size: 11px; color: #FFC107; font-weight: bold; border: none;")
        
        layout_box2.addWidget(self.lbl_bat_titulo)
        layout_box2.addWidget(self.lbl_bateria_status)
        layout_preditivo_interno.addWidget(self.box_bateria_horario)

        self.coluna_direita.addWidget(self.container_preditivo, stretch=4)
        
        # --- PAINEL DE DECISÕES RECOMENDADAS ---
        self.container_recomendacoes_LOG = QWidget()
        self.container_recomendacoes_LOG.setStyleSheet("background-color: #1E1E1E; border: 1px solid #333333; border-radius: 6px;")
        layout_log_interno = QVBoxLayout(self.container_recomendacoes_LOG)
        
        lbl_titulo_log = QLabel("Recomendações e Ações da IA")
        lbl_titulo_log.setStyleSheet("font-weight: bold; font-size: 12px; color: #00ACC1; border: none;")
        layout_log_interno.addWidget(lbl_titulo_log)
        
        self.txt_historico_decisoes = QTextEdit()
        self.txt_historico_decisoes.setReadOnly(True)
        self.txt_historico_decisoes.setStyleSheet("""
            QTextEdit {
                background-color: #121212;
                color: #A5D6A7;
                font-family: 'Consolas', monospace;
                font-size: 11px;
                border: 1px solid #2D2D2D;
                border-radius: 4px;
            }
        """)
        self.txt_historico_decisoes.append("Sistema iniciado. Monitoramento de IA ativo...")
        layout_log_interno.addWidget(self.txt_historico_decisoes)
        
        self.coluna_direita.addWidget(self.container_recomendacoes_LOG, stretch=5)

        # -------------------------------------------------------------
        # 🚀 CONFIGURAÇÃO PRINCIPAL DO SISTEMA DE ABAS (CORRIGIDO)
        # -------------------------------------------------------------
        from PySide6.QtWidgets import QTabWidget
        self.abas = QTabWidget()
        self.setCentralWidget(self.abas)
        
        # Customização escura para as abas se integrarem ao layout
        self.abas.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #333333; background-color: #121212; }
            QTabBar::tab { background: #1E1E1E; color: #888888; padding: 10px 20px; font-weight: bold; border: 1px solid #2D2D2D; }
            QTabBar::tab:selected { background: #121212; color: #00ACC1; border-bottom: 2px solid #00ACC1; }
        """)

        # --- ABA 1: MONITORAMENTO GERAL ---
        self.aba_principal = QWidget()
        
        # Criamos o layout interno da Aba 1 e linkamos o ponteiro antigo
        # para que as linhas de código abaixo (ex: linha 295) funcionem sem quebrar!
        self.layout_mestre = QHBoxLayout(self.aba_principal)
        
        # Adiciona os componentes existentes à primeira aba usando os comandos originais
        self.layout_mestre.addLayout(self.coluna_esquerda, stretch=3)
        self.layout_mestre.addLayout(self.coluna_central, stretch=5)
        self.layout_mestre.addLayout(self.coluna_direita, stretch=4)
        
        # Entrega a aba principal montada ao gerenciador
        self.abas.addTab(self.aba_principal, "📊 Monitoramento Geral")

        # --- ABA 2: BANCO DE BATERIAS ---
        # Instancia a nova tela modular do arquivo separado
        self.aba_bateria = PainelBateria()
        self.abas.addTab(self.aba_bateria, "🔋 Banco de Baterias")
        
        
        # -------------------------------------------------------------
        # Montagem Final da Tela
        # -------------------------------------------------------------
        self.layout_mestre.addLayout(self.coluna_esquerda, stretch=3)
        self.layout_mestre.addLayout(self.coluna_central, stretch=5)
        self.layout_mestre.addLayout(self.coluna_direita, stretch=3)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.loop_atualizacao_tempo_real)
        self.timer.start(2000)

    def notificar_alerta(self, titulo, message):
        self.tray_icon.showMessage(titulo, message, QSystemTrayIcon.Information, 3000)

    def adicionar_recomendacao_log(self, mensagem):
        """Escreve uma linha com o horário atual dentro do painel e dispara uma notificação na tela"""
        from PySide6.QtCore import QTime
        hora_log = QTime.currentTime().toString("HH:mm:ss")
        
        # Cria um atributo de histórico na janela se ele não existir ainda
        if not hasattr(self, '_ultimas_mensagens_ia'):
            self._ultimas_mensagens_ia = set()

        if hasattr(self, 'txt_historico_decisoes'):
            linhas_atuais = self.txt_historico_decisoes.toPlainText().split('\n')
            
            # Limpa o "Monitoramento de IA ativo..." inicial no primeiro log real
            if len(linhas_atuais) == 1 and "Monitoramento de IA ativo" in linhas_atuais[0]:
                self.txt_historico_decisoes.clear()

            # SÓ DISPARA SE A MENSAGEM FOR INÉDITA NAS ÚLTIMAS LEITURAS
            if mensagem not in self._ultimas_mensagens_ia:
                self.txt_historico_decisoes.append(f"[{hora_log}] {mensagem}")
                self.txt_historico_decisoes.ensureCursorVisible()
                
                # Guarda na memória para não repetir o popup
                self._ultimas_mensagens_ia.add(mensagem)
                
                # Limita o tamanho da memória para não acumular lixo
                if len(self._ultimas_mensagens_ia) > 10:
                    self._ultimas_mensagens_ia.pop()

                # --- DISPARAR NOTIFICAÇÕES VISUAIS DA IA ---
                if hasattr(self, 'notificar_alerta'):
                    if "🚨" in mensagem or "⚠️" in mensagem or "Decisão" in mensagem:
                        self.notificar_alerta("IA: Gerenciamento Ativo", mensagem)
                    elif "💡" in mensagem or "Sugestão" in mensagem:
                        self.notificar_alerta("IA: Sugestão de Economia", mensagem)
                    elif "📈" in mensagem or "Eficiência" in mensagem:
                        self.notificar_alerta("IA: Desempenho do Sistema", mensagem)
            
    def closeEvent(self, event):
        """Método nativo do PySide que é disparado automaticamente quando a janela fecha"""
        print("Stopping background activities and closing...")
        
        # 1. Procura pelo timer e para a execução dele imediatamente
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
        elif hasattr(self, 'timer_atualizacao') and self.timer_atualizacao.isActive():
            self.timer_atualizacao.stop()
            
        # 2. Se o leitor de hardware estiver aberto, fecha a conexão serial
        if hasattr(self, 'leitor') and hasattr(self.leitor, 'conexao') and self.leitor.conexao:
            try:
                self.leitor.conexao.close()
                print("🔌 Conexão serial com o Arduino encerrada com segurança.")
            except Exception as e:
                print(f"Erro ao fechar serial: {e}")

        # Aceita o fechamento da janela e encerra o processo do PySide
        event.accept()

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

    def criar_e_adicionar_botao_na_tela(self, nome_carrega):
        btn_novo = QPushButton()
        self.config_cargas[nome_carrega]["btn"] = btn_novo
        self.atualizar_visual_botao(nome_carrega)
        self.layout_cargas.addWidget(btn_novo)
        btn_novo.clicked.connect(lambda: self.abrir_menu_contexto_carga(nome_carrega))

    def atualizar_visual_botao(self, nome):
        if nome not in self.config_cargas: return
        info = self.config_cargas[nome]
        if info["btn"] is None: return
        tipo = "[CRÍTICA]" if info["critica"] else "[SELETIVA]"
        pot = info["potencia"]
        
        if info["ativo"]:
            info["btn"].setText(f"🟢 {tipo} {nome} ({pot}kW) - Ativo")
            info["btn"].setStyleSheet("background-color: #2D2D2D; color: white; border: 1px solid #444444; padding: 10px; text-align: left; font-size: 11px; border-radius: 4px;")
        else:
            info["btn"].setText(f"🔴 {tipo} {nome} ({pot}kW) - CORTADO")
            info["btn"].setStyleSheet("background-color: #3A1C1C; color: #E53935; border: 1px solid #E53935; font-weight: bold; padding: 10px; text-align: left; font-size: 11px; border-radius: 4px;")

    def abrir_menu_contexto_carga(self, nome):
        menu = QMenu(self)
        texto_estado = "🔴 Forçar Desligamento" if self.config_cargas[nome]["ativo"] else "🟢 Reativar Aparelho"
        acao_estado = QAction(texto_estado, self)
        acao_estado.triggered.connect(lambda: self.alternar_carga_manual(nome))
        menu.addAction(acao_estado)
        
        texto_tipo = "🔄 Tornar Carga Comum (Seletiva)" if self.config_cargas[nome]["critica"] else "🔄 Elevar para CRÍTICA"
        acao_tipo = QAction(texto_tipo, self)
        acao_tipo.triggered.connect(lambda: self.alternar_tipo_critica(nome))
        menu.addAction(acao_tipo)
        
        menu.addSeparator()
        acao_remover = QAction("❌ Excluir do Sistema", self)
        acao_remover.triggered.connect(lambda: self.excluir_carga(nome))
        menu.addAction(acao_remover)
        menu.exec(self.config_cargas[nome]["btn"].mapToGlobal(self.config_cargas[nome]["btn"].rect().bottomLeft()))

    def alternar_carga_manual(self, nome):
        self.config_cargas[nome]["ativo"] = not self.config_cargas[nome]["ativo"]
        self.atualizar_visual_botao(nome)
        self.adicionar_recomendacao_log(f"Controle Manual: '{nome}' alterado para {'Ativo' if self.config_cargas[nome]['ativo'] else 'Desligado'}.")

    def alternar_tipo_critica(self, nome):
        self.config_cargas[nome]["critica"] = not self.config_cargas[nome]["critica"]
        self.atualizar_visual_botao(nome)
        self.adicionar_recomendacao_log(f"Configuração: '{nome}' reclassificado como {'CRÍTICA' if self.config_cargas[nome]['critica'] else 'SELETIVA'}.")

    def excluir_carga(self, nome):
        confirmacao = QMessageBox.question(self, "Remover Dispositivo", f"Tem certeza que deseja apagar a carga '{nome}'?", QMessageBox.Yes | QMessageBox.No)
        if confirmacao == QMessageBox.Yes:
            botao = self.config_cargas[nome]["btn"]
            self.layout_cargas.removeWidget(botao)
            botao.deleteLater()
            del self.config_cargas[nome]
            self.adicionar_recomendacao_log(f"Remoção: Dispositivo '{nome}' excluído do banco do sistema.")

    def abrir_dialogo_adicionar_carga(self):
        nome, ok1 = QInputDialog.getText(self, "Nova Carga", "Nome do Aparelho:")
        if not ok1 or not nome.strip(): return
        if nome in self.config_cargas: return
        
        potencia, ok2 = QInputDialog.getDouble(self, "Nova Carga", "Potência Absorvida (em kW):", 1.0, 0.1, 15.0, 1)
        if not ok2: return
        
        itens = ["Seletiva (Pode ser desligada pelo sistema)", "Crítica (Imune a cortes automáticos)"]
        tipo, ok3 = QInputDialog.getItem(self, "Nova Carga", "Tipo de Gerenciamento:", itens, 0, False)
        if not ok3: return
        
        is_critica = (tipo == "Crítica (Imune a cortes automáticos)")
        self.config_cargas[nome] = {"critica": is_critica, "potencia": potencia, "ativo": True, "btn": None}
        self.criar_e_adicionar_botao_na_tela(nome)
        self.adicionar_recomendacao_log(f"Cadastro: Nova carga '{nome}' adicionada ({potencia} kW).")


    def loop_atualizacao_tempo_real(self):
        try:
            # ======================================================================
            # 🕒 1. CONTROLE DE TEMPO E LEITURA DE PARÂMETROS
            # ======================================================================
            meta_limite = self.sld_meta_consumo.value() / 10.0 if hasattr(self, 'sld_meta_consumo') else 5.0
            ar_info = self.config_cargas.get("Ar-Condicionado", {"ativo": False, "potencia": 2.0})
            bomba_info = self.config_cargas.get("Bomba D'água", {"ativo": False, "potencia": 1.2})
            
            # Captura a última linha do log para checagem de duplicatas
            linhas_log = self.txt_historico_decisoes.toPlainText().split('\n') if hasattr(self, 'txt_historico_decisoes') else []
            ultima_linha = lines_log[-1] if lines_log else ""

            # ======================================================================
            # 📊 2. DEFINIÇÃO DE CONSUMO E GERAÇÃO (HARDWARE OU SIMULAÇÃO COMPORTAMENTAL)
            # ======================================================================
            if hasattr(self, 'leitor') and hasattr(self.leitor, 'ler_dados_reais'):
                dados = self.leitor.ler_dados_reais()
                if dados and len(dados) == 3:
                    novo_consumo, nova_geracao, hora_float = dados
                    self.hora_atual = hora_float
                elif dados and len(dados) == 2:
                    novo_consumo, nova_geracao = dados
                    self.hora_atual = (self.hora_atual + 0.25) % 24
                    hora_float = self.hora_atual
                else:
                    raise ValueError("Dados de leitura inválidos, recorrendo ao simulador.")
            else:
                # Avança o relógio do simulador (+15 minutos por ciclo)
                self.hora_atual = (self.hora_atual + 0.25) % 24
                hora_float = self.hora_atual

                # 🔌 SUB-BLOCO SUBSTITUÍDO: MODELAGEM DE CONSUMO RESIDENCIAL AVANÇADA
                consumo_basal = 0.25  
                dia_util = True  # Altere para False se quiser simular a dinâmica de um Domingo
                
                if dia_util:
                    if 6.0 <= hora_float <= 9.0:
                        pico_horario = 0.7 * math.sin(math.pi * (hora_float - 6.0) / 3.0)
                    elif 18.0 <= hora_float <= 22.0:
                        pico_horario = 2.1 * math.sin(math.pi * (hora_float - 18.0) / 4.0)
                    elif 22.0 < hora_float or hora_float < 6.0:
                        pico_horario = 0.08
                    else:
                        pico_horario = 0.35  
                else:
                    if 10.0 <= hora_float <= 16.0:
                        pico_horario = 1.2 * math.sin(math.pi * (hora_float - 10.0) / 6.0)  
                    elif 18.0 <= hora_float <= 23.0:
                        pico_horario = 1.8 * math.sin(math.pi * (hora_float - 18.0) / 5.0)
                    else:
                        pico_horario = 0.15

                # Surtos aleatórios de alta potência (Chuveiro, Micro-ondas)
                import random
                surto_eletrico = 0.0
                if 7.0 <= hora_float <= 8.3 or 19.0 <= hora_float <= 21.5:
                    if random.random() < 0.15:  # 15% de chance a cada iteração nesses horários
                        surto_eletrico = random.uniform(1.5, 3.0)  

                ruido_constante = random.uniform(-0.08, 0.08)
                consumo_ambiente = consumo_basal + pico_horario + surto_eletrico + ruido_constante

                # Soma das Cargas Interativas Dinâmicas (Com termostato virtual)
                consumo_cargas_ativas = 0.0
                if hasattr(self, 'config_cargas'):
                    for nome_carga, info in self.config_cargas.items():
                        if info.get("ativo", False):
                            potencia_nominal = info.get("potencia", 0.0)
                            if nome_carga == "Ar-Condicionado" and 11.0 <= hora_float <= 15.0:
                                potencia_nominal *= 1.15  # Compressor se esforça mais no calor do meio-dia
                            consumo_cargas_ativas += potencia_nominal

                novo_consumo = max(0.15, round(consumo_ambiente + consumo_cargas_ativas, 2))

                # Geração Solar Dinâmica
                fator_solar = 0.0
                if 6.0 <= hora_float <= 18.0:
                    fator_solar = math.sin(math.pi * (hora_float - 6.0) / 12.0)
                
                nova_geracao = round(4.5 * fator_solar + random.uniform(-0.05, 0.05), 2) if fator_solar > 0 else 0.0

            # ======================================================================
            # DO SINAL EM DIANTE TUDO CONTINUA IGUAL (Cálculos, Bateria, Gráficos...)
            # ======================================================================
            horas_inteiras = int(hora_float)
            minutos = int((hora_float - horas_inteiras) * 60)
            texto_hora = f"{horas_inteiras:02d}:{minutos:02d}"

            eficiencia_porcentagem = min(100, int((nova_geracao / novo_consumo) * 100)) if novo_consumo > 0 else 100

            # 🔋 GERENCIAMENTO FÍSICO DA BATERIA & REDE EXTERNA
            saldo_rede_externa, fluxo_bateria = self.aba_bateria.atualizar_dados_bateria(nova_geracao, novo_consumo)
            saldo_bruto_antigo = round(nova_geracao - novo_consumo, 1)

            # HISTÓRICOS E ATUALIZAÇÃO DOS GRÁFICOS
            self.historico_horas.append(texto_hora)
            self.historico_consumo.append(novo_consumo)
            self.historico_geracao.append(nova_geracao)
            
            if len(self.historico_horas) > 7:
                self.historico_horas.pop(0)
                self.historico_consumo.pop(0)
                self.historico_geracao.pop(0)

            if hasattr(self.canvas_grafico, 'atualizar_linhas'):
                self.canvas_grafico.atualizar_linhas(self.historico_horas, self.historico_consumo, self.historico_geracao)
            elif hasattr(self.canvas_grafico, 'plotar_dados'):
                self.canvas_grafico.plotar_dados(self.historico_horas, self.historico_consumo, self.historico_geracao)

            if hasattr(self, 'canvas_grafico') and hasattr(self.canvas_grafico, 'ax'):
                self.canvas_grafico.ax.texts.clear()
                cor_badge = "#4CAF50" if eficiencia_porcentagem >= 90 else "#FFC107" if eficiencia_porcentagem >= 50 else "#FF5252"
                self.canvas_grafico.ax.text(
                    0.96, 0.93, f"Eficiencia: {eficiencia_porcentagem}%",
                    transform=self.canvas_grafico.ax.transAxes, color=cor_badge,
                    fontsize=10, fontweight='bold', ha='right', va='top',
                    bbox=dict(boxstyle="round,pad=0.4", facecolor="#181818", edgecolor="#333333", linewidth=1, alpha=0.9)
                )
                self.canvas_grafico.draw()

            # ATUALIZAÇÃO DOS CARDS VISUAIS
            self.lbl_val_consumo.setText(f"{novo_consumo:.1f} kWh")
            self.lbl_val_geracao.setText(f"{nova_geracao:.1f} kWh")
            
            sinal = "+" if saldo_rede_externa >= 0 else ""
            self.lbl_val_saldo.setText(f"{sinal}{saldo_rede_externa:.1f} kWh")
            
            if saldo_rede_externa > 0:
                self.lbl_val_saldo.setStyleSheet("font-size: 28px; font-weight: bold; color: #4CAF50; border: none;")
            elif saldo_rede_externa == 0:
                self.lbl_val_saldo.setStyleSheet("font-size: 28px; font-weight: bold; color: #00ACC1; border: none;")
            else:
                self.lbl_val_saldo.setStyleSheet("font-size: 28px; font-weight: bold; color: #E53935; border: none;")

            # AUTOMAÇÃO DE CORTE SELETIVO & PAINEL DE CONSELHOS IA
            cargas_nao_criticas_ativas = [n for n, info in self.config_cargas.items() if not info.get("critica", False) and info.get("ativo", False)]
            cargas_nao_criticas_desligadas = [n for n, info in self.config_cargas.items() if not info.get("critica", False) and not info.get("ativo", False)]

            if saldo_bruto_antigo < 0:
                if cargas_nao_criticas_ativas:
                    carga_alvo = cargas_nao_criticas_ativas[0]
                    self.config_cargas[carga_alvo]["ativo"] = False
                    self.atualizar_visual_botao(carga_alvo)
                    self.lbl_decisao_texto.setText(f"CORTE SELETIVO ATIVADO\nDeficit de {abs(saldo_bruto_antigo)} kWh. Dispositivo '{carga_alvo}' desligado.")
                    self.lbl_decisao_texto.setStyleSheet("font-size: 11px; font-weight: bold; color: #FF5252; background: transparent;")
                    self.adicionar_recomendacao_log(f"Acao: Desconexao automatica de '{carga_alvo}' para estabilizacao da rede.")
                else:
                    self.lbl_decisao_texto.setText("ALERTA CRITICO\nDemanda essencial excede a capacidade de geracao solar atual.")
                    self.lbl_decisao_texto.setStyleSheet("font-size: 11px; font-weight: bold; color: #FF1744; background: transparent;")
                    self.adicionar_recomendacao_log("Alerta: Colapso iminente. Cargas criticas operando sem margem de seguranca.")
            else:
                if cargas_nao_criticas_desligadas:
                    carga_alvo = cargas_nao_criticas_desligadas[-1]
                    self.config_cargas[carga_alvo]["ativo"] = True
                    self.atualizar_visual_botao(carga_alvo)
                    self.lbl_decisao_texto.setText(f"SISTEMA ENERGIZADO\nSuperavit de +{saldo_bruto_antigo} kWh. Dispositivo '{carga_alvo}' reativado.")
                    self.lbl_decisao_texto.setStyleSheet("font-size: 11px; font-weight: bold; color: #4CAF50; background: transparent;")
                    self.adicionar_recomendacao_log(f"Acao: Reativacao segura do dispositivo '{carga_alvo}'.")
                else:
                    self.lbl_decisao_texto.setText("OPERACAO NORMAL\nGeracao solar estavel e demanda totalmente suprida.")
                    self.lbl_decisao_texto.setStyleSheet("font-size: 11px; font-weight: bold; color: #4CAF50; background: transparent;")

            # 6.1 - Janela de Uso Recomendada
            fator_solar_painel = math.sin(math.pi * (hora_float - 6.0) / 12.0) if 6.0 <= hora_float <= 18.0 else 0.0
            eficiencia_fator_pct = int(fator_solar_painel * 100)

            if 10.0 <= hora_float <= 14.0:
                if hasattr(self, 'lbl_carga_status'):
                    self.lbl_carga_status.setText(f"Janela ideal ativa. Eficiencia solar em {eficiencia_fator_pct}%.")
                    self.lbl_carga_status.setStyleSheet("font-size: 11px; color: #4CAF50; font-weight: bold; border: none;")
            else:
                if hasattr(self, 'lbl_carga_status'):
                    self.lbl_carga_status.setText("Evite cargas pesadas. Sugerido postergar para as 12:00.")
                    self.lbl_carga_status.setStyleSheet("font-size: 11px; color: #FF9800; font-weight: bold; border: none;")

            # 6.2 - Diretriz dinâmica da Bateria
            if hasattr(self, 'lbl_bateria_status'):
                soc_atual = self.aba_bateria.bateria_soc
                if soc_atual >= 100.0:
                    self.lbl_bateria_status.setText(f"Bateria em {int(soc_atual)}% (Cheia). Excedente exportado para a rede externa.")
                    self.lbl_bateria_status.setStyleSheet("font-size: 11px; color: #00E676; font-weight: bold; border: none;")
                elif fluxo_bateria > 0:
                    self.lbl_bateria_status.setText(f"Armazenando Sobra Solar (+{fluxo_bateria:.1f} kWh em uso). SoC: {int(soc_atual)}%.")
                    self.lbl_bateria_status.setStyleSheet("font-size: 11px; color: #4CAF50; font-weight: bold; border: none;")
                elif fluxo_bateria < 0:
                    self.lbl_bateria_status.setText(f"Suprindo casa com Bateria (-{abs(fluxo_bateria):.1f} kWh desc.). SoC: {int(soc_atual)}%.")
                    self.lbl_bateria_status.setStyleSheet("font-size: 11px; color: #FFC107; font-weight: bold; border: none;")
                else:
                    if soc_atual <= 10.0:
                        self.lbl_bateria_status.setText(f"Bateria Esgotada ({int(soc_atual)}%). Sistema operando 100% via concessionária.")
                        self.lbl_bateria_status.setStyleSheet("font-size: 11px; color: #F44336; font-weight: bold; border: none;")
                    else:
                        self.lbl_bateria_status.setText(f"Bateria Estabilizada em {int(soc_atual)}%. Aguardando fluxo de carga/descarga.")
                        self.lbl_bateria_status.setStyleSheet("font-size: 11px; color: #9E9E9E; font-weight: bold; border: none;")

            # 6.3 - Logs inteligentes da IA
            if novo_consumo > meta_limite:
                excesso = round(novo_consumo - meta_limite, 1)
                if ar_info.get("ativo") and "responsavel por" not in ultima_linha.lower():
                    impacto_ar = int((ar_info["potencia"] / novo_consumo) * 100)
                    self.adicionar_recomendacao_log(f"Otimizacao: Limite excedido em {excesso} kWh. O Ar-Condicionado representa {impacto_ar}% do consumo.")

            if bomba_info.get("ativo") and fator_solar_painel < 0.6 and "desloque" not in ultima_linha.lower():
                self.adicionar_recomendacao_log(f"Sugestao: Eficiencia solar de apenas {eficiencia_fator_pct}%. Desloque a Bomba para as 12:00.")

            if eficiencia_porcentagem == 100 and nova_geracao > (novo_consumo + 1.0) and "superavit solar" not in ultima_linha.lower():
                sobra = round(nova_geracao - novo_consumo, 1)
                self.adicionar_recomendacao_log(f"Analise: Superavit solar de {sobra} kWh verificado. Capacidade livre para novas cargas.")

        except Exception as e:
            print(f"Erro no loop de atualizacao: {e}")

    def adicionar_recomendacao_log(self, mensagem):
        from PySide6.QtCore import QTime
        hora_log = QTime.currentTime().toString("HH:mm:ss")
        
        if not hasattr(self, '_ultimas_mensagens_ia'):
            self._ultimas_mensagens_ia = set()

        if hasattr(self, 'txt_historico_decisoes'):
            linhas_atuais = self.txt_historico_decisoes.toPlainText().split('\n')
            if len(linhas_atuais) == 1 and "Monitoramento de IA" in linhas_atuais[0]:
                self.txt_historico_decisoes.clear()

            if mensagem not in self._ultimas_mensagens_ia:
                self.txt_historico_decisoes.append(f"[{hora_log}] {mensagem}")
                self.txt_historico_decisoes.ensureCursorVisible()
                
                self._ultimas_mensagens_ia.add(mensagem)
                if len(self._ultimas_mensagens_ia) > 10:
                    # Correção: sets usam pop() mas removem itens aleatórios.
                    # Convertido para manter as mensagens recentes organizadas de forma segura.
                    self._ultimas_mensagens_ia.remove(list(self._ultimas_mensagens_ia)[0])

                if hasattr(self, 'notificar_alerta') and hasattr(self, 'isVisible') and self.isVisible():
                    self.notificar_alerta("Gerenciamento de Energia", mensagem)

    def closeEvent(self, event):
        print("Finalizando aplicacao...")
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
        elif hasattr(self, 'timer_atualizacao') and self.timer_atualizacao.isActive():
            self.timer_atualizacao.stop()
            
        if hasattr(self, 'leitor') and hasattr(self.leitor, 'conexao') and self.leitor.conexao:
            try:
                self.leitor.conexao.close()
            except Exception:
                pass

        event.accept()
        from PySide6.QtCore import QCoreApplication
        QCoreApplication.quit()