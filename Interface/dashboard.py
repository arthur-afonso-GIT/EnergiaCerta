# Arquivo: Interface/dashboard.py
import os
import math
import random
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QToolButton, QMenu, QSystemTrayIcon, 
                             QPushButton, QInputDialog, QMessageBox, QScrollArea, QTextEdit)
from PySide6.QtCore import Qt, QTimer, QTime
from PySide6.QtGui import QPixmap, QAction, QIcon

from Interface.componentes.grafico_tempo_real import CanvasGraficoEnergia
from Interface.componentes.painel_simulacao import PainelSimulacaoDecisao

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
        
        self.widget_central = QWidget()
        self.setCentralWidget(self.widget_central)
        self.layout_mestre = QHBoxLayout()
        self.widget_central.setLayout(self.layout_mestre)
        
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
        # COLUNA 3: DIREITA (Simulador + Novo Terminal de Decisões)
        # -------------------------------------------------------------
        self.coluna_direita = QVBoxLayout()
        
        # Painel do Slider superior
        self.painel_simulacao = PainelSimulacaoDecisao(callback_alerta=self.notificar_alerta)
        self.coluna_direita.addWidget(self.painel_simulacao, stretch=4)
        
        # --- PAINEL DE DECISÕES RECOMENDADAS ---
        self.container_recomendacoes_LOG = QWidget()
        self.container_recomendacoes_LOG.setStyleSheet("background-color: #1E1E1E; border: 1px solid #333333; border-radius: 6px;")
        layout_log_interno = QVBoxLayout(self.container_recomendacoes_LOG)
        
        lbl_titulo_log = QLabel("📋 Recomendações e Ações da IA")
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
        self.txt_historico_decisoes.append("ℹ️ Sistema iniciado. Monitoramento de IA ativo...")
        layout_log_interno.addWidget(self.txt_historico_decisoes)
        
        self.coluna_direita.addWidget(self.container_recomendacoes_LOG, stretch=5)
        
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
        """Adiciona mensagens em tempo real ao novo painel terminal"""
        hora_atual_sistema = QTime.currentTime().toString("HH:mm:ss")
        if hasattr(self, 'txt_historico_decisoes'):
            self.txt_historico_decisoes.append(f"[{hora_atual_sistema}] {mensagem}")
            self.txt_historico_decisoes.ensureCursorVisible()

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
            # 1. Integração resiliente com o Backend / Geração de dados simulados
            if hasattr(self, 'leitor') and hasattr(self.leitor, 'ler_dados_reais'):
                dados = self.leitor.ler_dados_reais()
                if dados and len(dados) == 3:
                    novo_consumo, nova_geracao, hora_float = dados
                elif dados and len(dados) == 2:
                    novo_consumo, nova_geracao = dados
                    self.hora_atual = (self.hora_atual + 0.25) % 24
                    hora_float = self.hora_atual
                else:
                    raise ValueError()
            else:
                self.hora_atual = (self.hora_atual + 0.25) % 24
                hora_float = self.hora_atual
                consumo_base = 0.5
                for nome, info in self.config_cargas.items():
                    if info["ativo"]: consumo_base += info["potencia"]
                novo_consumo = round(max(0.5, consumo_base + random.uniform(-0.1, 0.1)), 1)
                
                if 6.0 <= hora_float <= 18.0:
                    angulo_solar = math.sin(math.pi * (hora_float - 6.0) / 12.0)
                    nova_geracao = round(6.0 * angulo_solar + random.uniform(-0.2, 0.2), 1)
                else:
                    nova_geracao = 0.0

            saldo = round(nova_geracao - novo_consumo, 1)
            horas_inteiras = int(hora_float)
            minutos = int((hora_float - horas_inteiras) * 60)
            texto_hora = f"{horas_inteiras:02d}:{minutos:02d}"

            # 2. Cálculo da Eficiência Energética em %
            if novo_consumo > 0:
                eficiencia_porcentagem = min(100, int((nova_geracao / novo_consumo) * 100))
            else:
                eficiencia_porcentagem = 100

            self.historico_horas.append(texto_hora)
            self.historico_consumo.append(novo_consumo)
            self.historico_geracao.append(nova_geracao)
            
            if len(self.historico_horas) > 7:
                self.historico_horas.pop(0)
                self.historico_consumo.pop(0)
                self.historico_geracao.pop(0)

            self.lbl_val_consumo.setText(f"{novo_consumo} kWh")
            self.lbl_val_geracao.setText(f"{nova_geracao} kWh")
            sinal = "+" if saldo >= 0 else ""
            self.lbl_val_saldo.setText(f"{sinal}{saldo} kWh")

            # 3. Atualização do Gráfico base
            if hasattr(self.canvas_grafico, 'atualizar_linhas'):
                self.canvas_grafico.atualizar_linhas(self.historico_horas, self.historico_consumo, self.historico_geracao)
            elif hasattr(self.canvas_grafico, 'plotar_dados'):
                self.canvas_grafico.plotar_dados(self.historico_horas, self.historico_consumo, self.historico_geracao)

            # 4. Injeção da Porcentagem por cima do gráfico limpo
            if hasattr(self, 'canvas_grafico') and hasattr(self.canvas_grafico, 'ax'):
                self.canvas_grafico.ax.texts.clear()
                
                if eficiencia_porcentagem >= 90:
                    cor_badge = "#4CAF50"
                elif eficiencia_porcentagem >= 50:
                    cor_badge = "#FFC107"
                else:
                    cor_badge = "#FF5252"
                
                self.canvas_grafico.ax.text(
                    0.96, 0.93, f"Eficiência: {eficiencia_porcentagem}%",
                    transform=self.canvas_grafico.ax.transAxes,
                    color=cor_badge,
                    fontsize=10,
                    fontweight='bold',
                    ha='right',
                    va='top',
                    bbox=dict(
                        boxstyle="round,pad=0.4",
                        facecolor="#181818",
                        edgecolor="#333333",
                        linewidth=1,
                        alpha=0.9
                    )
                )
                self.canvas_grafico.draw()

            # 5. Algoritmo de Inteligência e Decisões de Corte Automático
            cargas_nao_criticas_ativas = [n for n, info in self.config_cargas.items() if not info["critica"] and info["ativo"]]
            cargas_nao_criticas_desligadas = [n for n, info in self.config_cargas.items() if not info["critica"] and not info["ativo"]]

            if saldo < 0:
                if cargas_nao_criticas_ativas:
                    carga_alvo = cargas_nao_criticas_ativas[0]
                    if self.config_cargas[carga_alvo]["ativo"]:
                        self.config_cargas[carga_alvo]["ativo"] = False
                        self.atualizar_visual_botao(carga_alvo)
                        
                        self.lbl_decisao_texto.setText(f"⚠️ CORTE SELETIVO:\nSaldo negativo ({saldo} kWh). Desligado '{carga_alvo}'.")
                        self.lbl_decisao_texto.setStyleSheet("font-size: 11px; font-weight: bold; color: #E53935; background: transparent;")
                        
                        self.adicionar_recomendacao_log(f"⚙️ Decisão: '{carga_alvo}' cortado automaticamente para conter o défice.")
                        self.notificar_alerta("Gestão de Cargas", f"Aparelho desligado automaticamente: {carga_alvo}")
                else:
                    self.lbl_decisao_texto.setText("🚨 ALERTA GERAL:\nConsumo crítico supera a geração!")
                    self.lbl_decisao_texto.setStyleSheet("font-size: 11px; font-weight: bold; color: #FF1744; background: transparent;")
                    
                    linhas_log = self.txt_historico_decisoes.toPlainText().split('\n') if hasattr(self, 'txt_historico_decisoes') else []
                    if "🚨 Alerta Crítico" not in (linhas_log[-1] if linhas_log else ""):
                        self.adicionar_recomendacao_log("🚨 Alerta Crítico: Risco de colapso, cargas essenciais operando sem margem solar.")
            else:
                if cargas_nao_criticas_desligadas:
                    carga_alvo = cargas_nao_criticas_desligadas[-1]
                    if not self.config_cargas[carga_alvo]["ativo"]:
                        self.config_cargas[carga_alvo]["ativo"] = True
                        self.atualizar_visual_botao(carga_alvo)
                        
                        self.lbl_decisao_texto.setText(f"✅ REDE ENERGIZADA:\nSobrou energia solar! Religado '{carga_alvo}'.")
                        self.lbl_decisao_texto.setStyleSheet("font-size: 11px; font-weight: bold; color: #4CAF50; background: transparent;")
                        
                        self.adicionar_recomendacao_log(f"⚙️ Decisão: '{carga_alvo}' reativado de forma segura.")
                else:
                    self.lbl_decisao_texto.setText("✅ OPERAÇÃO NORMAL\nDemanda totalmente suprida.")
                    self.lbl_decisao_texto.setStyleSheet("font-size: 11px; font-weight: bold; color: #4CAF50; background: transparent;")

            # 6. Análise Preditiva e Recomendações de Logs da IA
            ar_ativo = self.config_cargas.get("Ar-Condicionado", {}).get("ativo", False)
            linhas_log = self.txt_historico_decisoes.toPlainText().split('\n') if hasattr(self, 'txt_historico_decisoes') else []
            ultima_linha = linhas_log[-1] if linhas_log else ""
            
            if (hora_float < 8.0 or hora_float > 17.0) and ar_ativo:
                if "Ineficiência" not in ultima_linha:
                    self.adicionar_recomendacao_log("⚠️ Ineficiência: Ar-Condicionado ativo em período de baixa ou nula captação solar.")

            if 6.0 <= hora_float < 10.0:
                if "Sugestão" not in ultima_linha:
                    self.adicionar_recomendacao_log("💡 Sugestão: Programe o uso de aparelhos de alto consumo (Ex: Bomba) para entre as 11h e 14h.")
            
            if eficiencia_porcentagem == 100:
                if "Excelente aproveitamento" not in ultima_linha:
                    self.adicionar_recomendacao_log(f"📈 Eficiência: Matriz solar cobrindo 100% da demanda atual.")
            elif eficiencia_porcentagem < 80:
                if "Eficiência baixa" not in ultima_linha:
                    self.adicionar_recomendacao_log(f"📉 Feedback: Eficiência em {eficiencia_porcentagem}%. Dependência da rede elétrica externa detectada.")

        except Exception as e:
            print(f"Erro interno no loop de atualização: {e}")

    def adicionar_recomendacao_log(self, mensagem):
        """Escreve uma linha com o horário atual dentro do painel e dispara uma notificação na tela"""
        from PySide6.QtCore import QTime
        hora_log = QTime.currentTime().toString("HH:mm:ss")
        
        if hasattr(self, 'txt_historico_decisoes'):
            linhas_atuais = self.txt_historico_decisoes.toPlainText().split('\n')
            ultima_linha = lines_atuais[-1] if linhas_atuais else ""
            
            # Evita duplicar a mesma recomendação em sequência
            if mensagem not in ultima_linha:
                self.txt_historico_decisoes.append(f"[{hora_log}] {mensagem}")
                self.txt_historico_decisoes.ensureCursorVisible()
                
                # --- SISTEMA DE NOTIFICAÇÃO DA IA ---
                # Identifica o tipo de mensagem para mandar o alerta correto na tela
                if hasattr(self, 'notificar_alerta'):
                    if "🚨" in mensagem or "⚠️" in mensagem or "Ineficiência" in mensagem:
                        self.notificar_alerta("IA: Otimização de Carga", mensagem)
                    elif "💡" in mensagem or "Sugestão" in mensagem:
                        self.notificar_alerta("IA: Sugestão de Economia", mensagem)
                    elif "📈" in mensagem or "Eficiência" in mensagem:
                        self.notificar_alerta("IA: Desempenho do Sistema", mensagem)
                    else:
                        self.notificar_alerta("IA: Recomendação", mensagem)