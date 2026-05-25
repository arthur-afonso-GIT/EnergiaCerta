import os
import math
import random
from collections import deque
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QToolButton, QMenu, QSystemTrayIcon, 
                               QPushButton, QInputDialog, QFrame, QTabWidget, 
                               QMessageBox, QScrollArea, QTextEdit, QSlider)
from PySide6.QtCore import Qt, QTimer, QTime
from PySide6.QtGui import QPixmap, QAction, QIcon

from Interface.componentes.grafico_tempo_real import CanvasGraficoEnergia

class DashboardEnergia(QMainWindow): 
    def __init__(self, aba_cargas=None, aba_graficos=None, aba_ia=None, aba_baterias=None, parent=None):
        super().__init__(parent)
        
        # 📥 Recebe as referências externas injetadas pelo Main.py
        self.aba_cargas = aba_cargas
        self.aba_graficos = aba_graficos
        self.aba_ia = aba_ia
        self.aba_baterias = aba_baterias
        
        # 🔌 Inicialização das Configurações de Janela
        self.setWindowTitle("Energia Certa - Dashboard Principal")
        self.resize(1240, 720)
        
        # 🎨 Folha de Estilos Global (Modo Escuro Premium)
        self.setStyleSheet("""
            QMainWindow { background-color: #121212; }
            QLabel { color: #FFFFFF; font-family: 'Segoe UI', sans-serif; }
            QMenu { background-color: #1E1E1E; color: white; border: 1px solid #333333; border-radius: 4px; padding: 5px; }
            QMenu::item:selected { background-color: #00E676; color: #121212; font-weight: bold; }
            QToolButton { background-color: #2D2D2D; color: white; border: 1px solid #444444; border-radius: 4px; padding: 8px; font-weight: bold; }
            QToolButton:hover { background-color: #444444; }
        """)
        
        # 🔔 Inicialização do Ícone da Bandeja de Sistema (Tray Icon)
        self.tray_icon = QSystemTrayIcon(self)
        caminho_logo = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
        if os.path.exists(caminho_logo):
            self.tray_icon.setIcon(QIcon(caminho_logo))
        self.tray_icon.show()
        
        # 📈 Vetores de Histórico e Variáveis de Controle
        self.hora_atual = 10.0
        self.historico_horas = []
        self.historico_consumo = []
        self.historico_geracao = []
        
        # Otimização: Uso de deque com maxlen garante controle de memória cronológico rígido
        self._ultimas_mensagens_ia = deque(maxlen=10)
        
        # 🧠 Base de Dados Inicializada com Prioridades Padrão (Alteráveis pelo Usuário)
        # Prioridade: 1 = Cai Primeiro, 3 = Segura mais tempo ligado antes de cair
        self.config_cargas = {
            "Geladeira": {"critica": True, "potencia": 0.8, "ativo": True, "btn": None, "prioridade": 3},
            "Iluminação Sala": {"critica": True, "potencia": 0.3, "ativo": True, "btn": None, "prioridade": 3},
            "Roteador Internet": {"critica": True, "potencia": 0.1, "ativo": True, "btn": None, "prioridade": 3},
            "Bomba D'água": {"critica": False, "potencia": 1.2, "ativo": True, "btn": None, "prioridade": 1},
            "Computador": {"critica": False, "potencia": 0.5, "ativo": True, "btn": None, "prioridade": 2},
            "Ar-Condicionado": {"critica": False, "potencia": 2.0, "ativo": True, "btn": None, "prioridade": 3}
        }
        
        # ======================================================================
        # 🧱 CONSTRUÇÃO DOS LAYOUTS DA ABA PRINCIPAL
        # ======================================================================
        
        # --- COLUNA 1: ESQUERDA (Logo, Cargas e Resumo IA) ---
        self.coluna_esquerda = QVBoxLayout()
        
        # Bloco Superior: Logo e Menu Hamburguer
        self.container_logo = QWidget()
        self.container_logo.setStyleSheet("background-color: #1E1E1E; border-radius: 6px; border: 1px solid #333333;")
        self.layout_logo_bloco = QHBoxLayout(self.container_logo)
        
        self.lbl_logo_imagem = QLabel()
        pixmap = QPixmap(caminho_logo)
        if not pixmap.isNull():
            self.lbl_logo_imagem.setPixmap(pixmap.scaled(130, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.lbl_logo_imagem.setText("⭐ Energia Certa")
            self.lbl_logo_imagem.setStyleSheet("font-size: 16px; font-weight: bold; color: #00ACC1;")
            
        self.botao_menu = QToolButton()
        self.botao_menu.setText("☰ Menu")
        self.botao_menu.setPopupMode(QToolButton.InstantPopup)
        self.dropmenu = QMenu(self)
        self.dropmenu.addAction(QAction("⚙️ Configurações", self))
        self.botao_menu.setMenu(self.dropmenu)
        
        self.layout_logo_bloco.addWidget(self.lbl_logo_imagem, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        self.layout_logo_bloco.addWidget(self.botao_menu, alignment=Qt.AlignRight | Qt.AlignVCenter)
        
        # Bloco Central: Lista Dinâmica de Cargas com Scroll
        self.painel_cargas_container = QWidget()
        self.painel_cargas_container.setStyleSheet("background-color: #1E1E1E; border: 1px solid #333333; border-radius: 6px;")
        layout_container_vertical = QVBoxLayout(self.painel_cargas_container)
        
        lbl_tit_cargas = QLabel("Gerenciamento de Cargas")
        lbl_tit_cargas.setAlignment(Qt.AlignCenter)
        lbl_tit_cargas.setStyleSheet("font-weight: bold; font-size: 13px; padding: 5px; border: none;")
        layout_container_vertical.addWidget(lbl_tit_cargas)
        
        self.btn_add_carga = QPushButton("➕ ADICIONAR NOVA CARGA")
        self.btn_add_carga.setStyleSheet("""
            QPushButton { background-color: #00ACC1; color: white; font-weight: bold; border: none; padding: 10px; border-radius: 4px; }
            QPushButton:hover { background-color: #00838F; }
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
        
        # Popula os botões originais das cargas
        for nome in list(self.config_cargas.keys()):
            self.criar_e_adicionar_botao_na_tela(nome)
        
        # Bloco Inferior: Box de Feedback rápido de decisões
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
        
        # --- COLUNA 2: CENTRAL (Cards KPI e Matplotlib) ---
        self.coluna_central = QVBoxLayout()
        self.linha_cards = QHBoxLayout()
        
        self.card_consumo, self.lbl_val_consumo = self.criar_card_kpi("CONSUMO ATUAL", "0.0 kW", "#E53935")
        self.card_geracao, self.lbl_val_geracao = self.criar_card_kpi("GERAÇÃO SOLAR", "0.0 kW", "#4CAF50")
        self.card_saldo, self.lbl_val_saldo = self.criar_card_kpi("BALANÇO DA REDE", "0.0 kW", "#00ACC1")
        
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
        
        # --- COLUNA 3: DIREITA (Metas, Agendamento e Logs Internos) ---
        self.coluna_right = QVBoxLayout()
        
        # Configuração de Metas / Slider
        self.container_metas = QWidget()
        self.container_metas.setStyleSheet("background-color: #1E1E1E; border: 1px solid #333333; border-radius: 6px;")
        layout_metas_interno = QVBoxLayout(self.container_metas)
        layout_metas_interno.setContentsMargins(10, 10, 10, 10)
        
        lbl_titulo_metas = QLabel("Configuração de Metas")
        lbl_titulo_metas.setStyleSheet("font-weight: bold; font-size: 14px; color: #FFFFFF; border: none;")
        layout_metas_interno.addWidget(lbl_titulo_metas)
        
        self.lbl_meta_status = QLabel("Meta Limite de Consumo: 5.0 kW")
        self.lbl_meta_status.setStyleSheet("font-size: 11px; color: #B0BEC5; border: none; margin-top: 5px;")
        layout_metas_interno.addWidget(self.lbl_meta_status)
        
        self.sld_meta_consumo = QSlider(Qt.Horizontal)
        self.sld_meta_consumo.setMinimum(10)  
        self.sld_meta_consumo.setMaximum(100) 
        self.sld_meta_consumo.setValue(50)    
        self.sld_meta_consumo.setStyleSheet("""
            QSlider::groove:horizontal { height: 6px; background: #2D2D2D; border-radius: 3px; }
            QSlider::handle:horizontal { background: #00ACC1; width: 14px; margin-top: -4px; margin-bottom: -4px; border-radius: 7px; }
        """)
        self.sld_meta_consumo.valueChanged.connect(
            lambda v: self.lbl_meta_status.setText(f"Meta Limite de Consumo: {v/10.0:.1f} kW")
        )
        layout_metas_interno.addWidget(self.sld_meta_consumo)
        self.coluna_right.addWidget(self.container_metas, stretch=3)
        
        # Otimização / Agendamento Preditivo
        self.container_preditivo = QWidget()
        self.container_preditivo.setStyleSheet("background-color: #1E1E1E; border: 1px solid #333333; border-radius: 6px;")
        layout_preditivo_interno = QVBoxLayout(self.container_preditivo)
        
        lbl_titulo_preditivo = QLabel("Agendamento Inteligente")
        lbl_titulo_preditivo.setStyleSheet("font-weight: bold; font-size: 12px; color: #00ACC1; border: none;")
        layout_preditivo_interno.addWidget(lbl_titulo_preditivo)
        
        self.box_melhor_horario = QFrame()
        self.box_melhor_horario.setStyleSheet("background-color: #121212; border: 1px solid #2D2D2D; border-radius: 4px;")
        layout_box1 = QVBoxLayout(self.box_melhor_horario)
        self.lbl_carga_titulo = QLabel("JANELA DE USO RECOMENDADA")
        self.lbl_carga_titulo.setStyleSheet("font-size: 9px; font-weight: bold; color: #888888; border: none;")
        self.lbl_carga_status = QLabel("Aguardando análise de fluxo...")
        self.lbl_carga_status.setStyleSheet("font-size: 11px; color: #4CAF50; font-weight: bold; border: none;")
        layout_box1.addWidget(self.lbl_carga_titulo)
        layout_box1.addWidget(self.lbl_carga_status)
        layout_preditivo_interno.addWidget(self.box_melhor_horario)
        
        self.box_bateria_horario = QFrame()
        self.box_bateria_horario.setStyleSheet("background-color: #121212; border: 1px solid #2D2D2D; border-radius: 4px;")
        layout_box2 = QVBoxLayout(self.box_bateria_horario)
        self.lbl_bat_titulo = QLabel("DIRETRIZ DE CARGA DA BATERIA")
        self.lbl_bat_titulo.setStyleSheet("font-size: 9px; font-weight: bold; color: #888888; border: none;")
        self.lbl_bateria_status = QLabel("Aguardando estabilização...")
        self.lbl_bateria_status.setStyleSheet("font-size: 11px; color: #FFC107; font-weight: bold; border: none;")
        layout_box2.addWidget(self.lbl_bat_titulo)
        layout_box2.addWidget(self.lbl_bateria_status)
        layout_preditivo_interno.addWidget(self.box_bateria_horario)
        self.coluna_right.addWidget(self.container_preditivo, stretch=4)
        
        # Histórico de Logs Interno
        self.container_recomendacoes_LOG = QWidget()
        self.container_recomendacoes_LOG.setStyleSheet("background-color: #1E1E1E; border: 1px solid #333333; border-radius: 6px;")
        layout_log_interno = QVBoxLayout(self.container_recomendacoes_LOG)
        lbl_titulo_log = QLabel("Ações Recentes da IA")
        lbl_titulo_log.setStyleSheet("font-weight: bold; font-size: 12px; color: #00ACC1; border: none;")
        layout_log_interno.addWidget(lbl_titulo_log)
        
        self.txt_historico_decisoes = QTextEdit()
        self.txt_historico_decisoes.setReadOnly(True)
        self.txt_historico_decisoes.setStyleSheet("""
            QTextEdit { background-color: #121212; color: #A5D6A7; font-family: 'Consolas', monospace; font-size: 11px; border: 1px solid #2D2D2D; border-radius: 4px; }
        """)
        self.txt_historico_decisoes.append("Sistema iniciado. Monitoramento de IA ativo...")
        layout_log_interno.addWidget(self.txt_historico_decisoes)
        self.coluna_right.addWidget(self.container_recomendacoes_LOG, stretch=5)

        # ======================================================================
        # 📂 ESTRUTURAÇÃO MULTI-ABA (SISTEMA DE NAVEGAÇÃO CENTRAL)
        # ======================================================================
        self.abas = QTabWidget()
        self.setCentralWidget(self.abas)
        self.abas.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #333333; background-color: #121212; }
            QTabBar::tab { background: #1E1E1E; color: #888888; padding: 10px 20px; font-weight: bold; border: 1px solid #2D2D2D; border-top-left-radius: 4px; border-top-right-radius: 4px; }
            QTabBar::tab:selected { background: #121212; color: #00E676; border-bottom: 2px solid #00E676; }
        """)

        # Montagem da Aba Principal (Dashboard Geral)
        self.aba_principal = QWidget()
        self.layout_mestre = QHBoxLayout(self.aba_principal)
        self.layout_mestre.addLayout(self.coluna_esquerda, stretch=3)
        self.layout_mestre.addLayout(self.coluna_central, stretch=5)
        self.layout_mestre.addLayout(self.coluna_right, stretch=4)
        
        self.abas.addTab(self.aba_principal, "📊 Monitoramento Geral")
        
        # ⏱️ Configuração do Clock Loop (Atualização de 2 em 2 segundos)
        self.timer = QTimer()
        self.timer.timeout.connect(self.loop_atualizacao_tempo_real)
        self.timer.start(2000)

    # ======================================================================
    # ⚙️ MÉTODOS COMPLEMENTARES E EVENTOS DA INTERFACE
    # ======================================================================
    def notificar_alerta(self, titulo, mensagem):
        if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
            self.tray_icon.showMessage(titulo, mensagem, QSystemTrayIcon.Information, 3000)

    def adicionar_recomendacao_log(self, mensagem):
        hora_log = QTime.currentTime().toString("HH:mm:ss")
        if hasattr(self, 'txt_historico_decisoes'):
            linhas_atuais = self.txt_historico_decisoes.toPlainText().split('\n')
            if len(linhas_atuais) == 1 and "Monitoramento de IA ativo" in linhas_atuais[0]:
                self.txt_historico_decisoes.clear()

            if mensagem not in self._ultimas_mensagens_ia:
                self.txt_historico_decisoes.append(f"[{hora_log}] {mensagem}")
                self.txt_historico_decisoes.ensureCursorVisible()
                self._ultimas_mensagens_ia.append(mensagem)
                
                # 🔔 SISTEMA DE NOTIFICAÇÕES CORRIGIDO (Sem 'message' em inglês)
                if hasattr(self, 'notificar_alerta'):
                    if any(x in mensagem for x in ["🚨", "⚠️", "Decisão", "Configuração"]):
                        self.notificar_alerta("IA: Gerenciamento Ativo", mensagem)
                    elif any(x in mensagem for x in ["💡", "Sugestão"]):
                        self.notificar_alerta("IA: Sugestão de Economia", mensagem)
                        
                        
    def closeEvent(self, event):
        print("Finalizando aplicação e liberando recursos...")
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
        event.accept()

    def criar_card_kpi(self, titulo, valor_inicial, cor_borda):
        card = QWidget()
        card.setStyleSheet(f"QWidget {{ background-color: #1E1E1E; border: 2px solid {cor_borda}; border-radius: 8px; }}")
        layout = QVBoxLayout(card)
        t = QLabel(titulo)
        t.setStyleSheet("font-size: 10px; font-weight: bold; color: #AAAAAA; border: none; background: transparent;")
        t.setAlignment(Qt.AlignCenter)
        v = QLabel(valor_inicial)
        v.setStyleSheet("font-size: 22px; font-weight: bold; border: none; background: transparent;")
        v.setAlignment(Qt.AlignCenter)
        layout.addWidget(t)
        layout.addWidget(v)
        return card, v

    def criar_e_adicionar_botao_na_tela(self, nome_carrega):
        btn_novo = QPushButton()
        self.config_cargas[nome_carrega]["btn"] = btn_novo
        self.layout_cargas.addWidget(btn_novo)
        self.atualizar_visual_botao(nome_carrega)
        btn_novo.clicked.connect(lambda: self.abrir_menu_contexto_carga(nome_carrega))

    def atualizar_visual_botao(self, nome):
        if nome not in self.config_cargas: return
        info = self.config_cargas[nome]
        if info["btn"] is None: return
        tipo = "[CRÍTICA]" if info["critica"] else "[SELETIVA]"
        pot = info["potencia"]
        prio = info.get("prioridade", 1)
        
        # 🔢 Exibe o nível de prioridade no botão para o usuário ver
        prio_txt = f" [Prio: {prio}]" if not info["critica"] else ""
        
        if info["ativo"]:
            info["btn"].setText(f"🟢 {tipo}{prio_txt} {nome} ({pot}kW) - Ativo")
            info["btn"].setStyleSheet("background-color: #2D2D2D; color: white; border: 1px solid #444444; padding: 10px; text-align: left; font-size: 11px; border-radius: 4px;")
        else:
            info["btn"].setText(f"🔴 {tipo}{prio_txt} {nome} ({pot}kW) - CORTADO")
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

        # 🔢 NOVO: Permite alterar a prioridade das cargas seletivas dinamicamente
        if not self.config_cargas[nome]["critica"]:
            acao_prioridade = QAction("🔢 Alterar Nível de Prioridade", self)
            acao_prioridade.triggered.connect(lambda: self.alterar_prioridade_manual(nome))
            menu.addAction(acao_prioridade)
        
        menu.addSeparator()
        acao_remover = QAction("❌ Excluir do Sistema", self)
        acao_remover.triggered.connect(lambda: self.excluir_carga(nome))
        menu.addAction(acao_remover)
        menu.exec(self.config_cargas[nome]["btn"].mapToGlobal(self.config_cargas[nome]["btn"].rect().bottomLeft()))

    # 🔢 NOVO: Processa a caixa de diálogo de prioridades das cargas existentes
    def alterar_prioridade_manual(self, nome):
        prio_atual = self.config_cargas[nome].get("prioridade", 1)
        nova_prio, ok = QInputDialog.getInt(
            self, "Alterar Prioridade", 
            f"Nova prioridade para '{nome}' (1 = Cai Primeiro, 3 = Cai por Último):", 
            prio_atual, 1, 3, 1
        )
        if ok:
            self.config_cargas[nome]["prioridade"] = nova_prio
            self.atualizar_visual_botao(nome)
            self.adicionar_recomendacao_log(f"Configuração: Prioridade de '{nome}' alterada para {nova_prio}.")

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

    # 🔢 ATUALIZADO: Cadastro de Novas Cargas perguntando prioridades
    def abrir_dialogo_adicionar_carga(self):
        nome, ok1 = QInputDialog.getText(self, "Nova Carga", "Nome do Aparelho:")
        if not ok1 or not nome.strip(): return
        if nome in self.config_cargas: return
        
        potencia, ok2 = QInputDialog.getDouble(self, "Nova Carga", "Potência Absorvida (em kW):", 1.0, 0.1, 15.0, 1)
        if not ok2: return
        
        prioridade, ok_prio = QInputDialog.getInt(
            self, "Nova Carga", 
            "Nível de Prioridade (1 = Cai Primeiro, 3 = Cai por Último):", 
            1, 1, 3, 1
        )
        if not ok_prio: return
        
        itens = ["Seletiva (Pode ser desligada pelo sistema)", "Crítica (Imune a cortes automáticos)"]
        tipo, ok3 = QInputDialog.getItem(self, "Nova Carga", "Tipo de Gerenciamento:", itens, 0, False)
        if not ok3: return
        
        is_critica = (tipo == "Crítica (Imune a cortes automáticos)")
        self.config_cargas[nome] = {
            "critica": is_critica, 
            "potencia": potencia, 
            "ativo": True, 
            "btn": None, 
            "prioridade": prioridade
        }
        self.criar_e_adicionar_botao_na_tela(nome)
        self.adicionar_recomendacao_log(f"Cadastro: Nova carga '{nome}' adicionada ({potencia} kW) | Prioridade: {prioridade}.")

    def atualizar_status_carga_lateral(self, nome_carga, esta_ativo):
        if nome_carga in self.config_cargas:
            self.config_cargas[nome_carga]["ativo"] = esta_ativo
            self.atualizar_visual_botao(nome_carga)

    # ======================================================================
    # 🔄 LOOP DE PROCESSAMENTO EM TEMPO REAL OPERACIONAL
    # ======================================================================
    def loop_atualizacao_tempo_real(self):
        try:
            # 🕒 1. PROGRESSÃO DO RELÓGIO SOLAR
            self.hora_atual = (self.hora_atual + 0.25) % 24
            horas_inteiras = int(self.hora_atual)
            minutos = int((self.hora_atual - horas_inteiras) * 60)
            texto_hora = f"{horas_inteiras:02d}:{minutos:02d}"

            # 📊 2. CÁLCULO SEGURO DO CONSUMO REAL DA CASA
            novo_consumo = sum(info["potencia"] for info in self.config_cargas.values() if info.get("ativo", True))
            novo_consumo = round(max(0.2, novo_consumo + random.uniform(-0.08, 0.08)), 2)

            # ☀️ 3. SIMULAÇÃO DA CURVA DA GERAÇÃO FOTOVOLTAICA
            fator_solar = math.sin(math.pi * (self.hora_atual - 6.0) / 12.0) if 6.0 <= self.hora_atual <= 18.0 else 0.0
            nova_geracao = round(4.5 * fator_solar + random.uniform(-0.03, 0.03), 2) if fator_solar > 0 else 0.0

            # 🔋 4. INTEGRAÇÃO PREMIUM DO BALANÇO DE BATERIAS
            instancia_bateria = getattr(self, 'aba_baterias', None) or getattr(self, 'aba_bateria', None)
            fluxo_bateria = 0.0
            soc_atual_bateria = 100.0

            if instancia_bateria and hasattr(instancia_bateria, 'soc_atual'):
                soc_atual_bateria = instancia_bateria.soc_atual
                if nova_geracao > novo_consumo:
                    if instancia_bateria.soc_atual < 100.0:
                        fluxo_bateria = round(min(nova_geracao - novo_consumo, 2.0), 2)
                        instancia_bateria.soc_atual += (fluxo_bateria * 0.15)
                else:
                    if instancia_bateria.soc_atual > 10.0:
                        fluxo_bateria = round(max(nova_geracao - novo_consumo, -2.0), 2)
                        instancia_bateria.soc_atual += (fluxo_bateria * 0.15)
                
                instancia_bateria.soc_atual = max(0.0, min(100.0, instancia_bateria.soc_atual))
            else:
                excedente = nova_geracao - novo_consumo
                fluxo_bateria = round(max(-1.5, min(excedente, 2.0)), 2)

            # ⚡ 5. CÁLCULO MATEMÁTICO REAL DO SALDO DA REDE EXTERNA
            saldo_rede_externa = round(nova_geracao - novo_consumo - fluxo_bateria, 2)
            eficiencia_porcentagem = min(100, int((nova_geracao / novo_consumo) * 100)) if novo_consumo > 0 else 100

            # 📈 6. ATUALIZAÇÃO DOS HISTÓRICOS DO GRÁFICO CENTRAL
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
                cor_badge = "#00E676" if eficiencia_porcentagem >= 90 else "#FFC107" if eficiencia_porcentagem >= 50 else "#FF5252"
                self.canvas_grafico.ax.text(
                    0.96, 0.93, f"Eficiência: {eficiencia_porcentagem}%",
                    transform=self.canvas_grafico.ax.transAxes, color=cor_badge,
                    fontsize=10, fontweight='bold', ha='right', va='top',
                    bbox=dict(boxstyle="round,pad=0.4", facecolor="#181818", edgecolor="#333333", linewidth=1, alpha=0.9)
                )
                self.canvas_grafico.draw()

            # 📺 7. ATUALIZAÇÃO RENDERIZADA DOS DISPLAYS KPI DO TOPO
            self.lbl_val_consumo.setText(f"{novo_consumo:.1f} kW")
            self.lbl_val_geracao.setText(f"{nova_geracao:.1f} kW")
            
            sinal = "+" if saldo_rede_externa > 0 else ""
            self.lbl_val_saldo.setText(f"{sinal}{saldo_rede_externa:.1f} kW")
            if saldo_rede_externa >= 0:
                self.lbl_val_saldo.setStyleSheet("font-size: 22px; font-weight: bold; color: #00E676; border: none; background: transparent;")
            else:
                self.lbl_val_saldo.setStyleSheet("font-size: 22px; font-weight: bold; color: #E53935; border: none; background: transparent;")

            # 🧠 8. ALIMENTAÇÃO DINÂMICA DAS EXTENSÕES MODULARES (IA E GRÁFICOS)
            if self.aba_ia and hasattr(self.aba_ia, 'setHtml'):
                status_cor = "#00E676" if nova_geracao > novo_consumo else "#FF5252"
                dica_ia = "Fluxo superavitário. Matriz injetando energia no banco de baterias." if nova_geracao > novo_consumo else "Atenção: Sistema em déficit. Célula de Lítio sustentando cargas seletivas."
                self.aba_ia.setHtml(f"""
                    <h2 style='color: #00E676; font-family: sans-serif;'>🧠 Recomendações de Inteligência (EMS)</h2>
                    <p style='color: white; font-size: 13px;'><b>Horário de Análise:</b> {texto_hora}</p>
                    <p style='color: white; font-size: 13px;'><b>Eficiência Operacional:</b> <span style='color: {status_cor};'>{eficiencia_porcentagem}%</span></p>
                    <p style='color: white; font-size: 13px;'><b>Geração Ativa:</b> {nova_geracao:.2f} kW | <b>Carga Solicitada:</b> {novo_consumo:.2f} kW</p>
                    <hr style='border: 1px solid #333;'>
                    <p style='color: #FF9800; font-size: 14px;'><b>⚡ Diagnóstico de Ouro:</b> {dica_ia}</p>
                """)

            if self.aba_graficos:
                if hasattr(self.aba_graficos, 'update_plot'):
                    self.aba_graficos.update_plot(novo_consumo, nova_geracao)
                elif hasattr(self.aba_graficos, 'atualizar_linhas'):
                    self.aba_graficos.atualizar_linhas(self.historico_horas, self.historico_consumo, self.historico_geracao)

            # 📝 Atualização Preditiva das caixas informativas do painel direito
            if nova_geracao > 2.0:
                self.lbl_carga_status.setText("Excelência Solar das 11h às 14h")
                self.lbl_bateria_status.setText("Modo: Armazenamento Ativo")
            else:
                self.lbl_carga_status.setText("Moderação recomendada")
                self.lbl_bateria_status.setText("Modo: Descarregamento Seguro")

            if self.lbl_decisao_texto:
                self.lbl_decisao_texto.setText(f"⏱️ [{texto_hora}] Fluxo Coberto: {eficiencia_porcentagem}% | Bateria: {soc_atual_bateria:.1f}%")

        except Exception as e:
            print(f"Erro no processamento do loop central do dashboard: {e}")