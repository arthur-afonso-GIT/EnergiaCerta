from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QGridLayout, QFrame, QDialog, 
                               QLineEdit, QDoubleSpinBox, QFormLayout, QComboBox, QCheckBox)
from PySide6.QtCore import Qt, Signal

class CardCarga(QFrame):
    """Componente visual reutilizável para representar uma carga do sistema com seletor de prioridade"""
    def __init__(self, nome, consumo_kw, prioridade=1, eh_critica=False, callback_hardware=None, sinal_atualizacao=None, aba_pai=None):
        super().__init__(aba_pai)
        self.nome = nome
        self.consumo = consumo_kw
        self.prioridade = prioridade
        self.eh_critica = eh_critica
        self.callback_hardware = callback_hardware
        self.sinal_atualizacao = sinal_atualizacao
        self.aba_pai = aba_pai
        self.ativo = True # Inicia ativo por padrão
        
        self.setObjectName("CardCarga")
        self.setFrameShape(QFrame.StyledPanel)
        self.setMinimumHeight(180) # Aumentado ligeiramente para acomodar os novos seletores
        self.update_card_style()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # --- LINHA SUPERIOR: Nome e Status LED ---
        topo_layout = QHBoxLayout()
        self.lbl_nome = QLabel(nome)
        self.lbl_nome.setStyleSheet("font-size: 15px; font-weight: bold; color: #FFFFFF; background: transparent;")
        
        self.lbl_status_led = QLabel("● ATIVO")
        self.lbl_status_led.setStyleSheet("font-size: 11px; font-weight: bold; color: #00E676; background: transparent;")
        
        topo_layout.addWidget(self.lbl_nome)
        topo_layout.addStretch()
        topo_layout.addWidget(self.lbl_status_led)
        layout.addLayout(topo_layout)
        
        # --- LINHA DO CONSUMO ---
        self.lbl_consumo = QLabel(f"⚡ Consumo: {consumo_kw} kW")
        self.lbl_consumo.setStyleSheet("font-size: 12px; color: #888888; background: transparent; margin-top: 2px;")
        layout.addWidget(self.lbl_consumo)
        
        # --- ⚙️ NOVO: ÁREA DE CONFIGURAÇÃO DE GERENCIAMENTO DA IA ---
        config_layout = QHBoxLayout()
        config_layout.setSpacing(0)        
        # Checkbox para definir se é imune a cortes (Crítica)
        self.chk_critica = QCheckBox("Crítica")
        self.chk_critica.setChecked(self.eh_critica)
        self.chk_critica.setStyleSheet("color: #B0BEC5; font-size: 11px; background: transparent;")
        self.chk_critica.toggled.connect(self.alternar_tipo_critica)
        
        # Menu de prioridade (1 a 3)
        self.combo_prio = QComboBox()
        self.combo_prio.addItems(["Prio 1 (Cai por Último)", "Prio 2", "Prio 3 (Cai Primeiro)"])
        self.combo_prio.setCurrentIndex(max(0, min(2, self.prioridade - 1)))
        self.combo_prio.setStyleSheet("""
            QComboBox { background-color: #252525; color: white; border: 1px solid #444; border-radius: 3px; padding: 2px 5px; font-size: 11px; }
            QComboBox:disabled { background-color: #1A1A1A; color: #555; border: 1px solid #2D2D2D; }
        """)
        self.combo_prio.setEnabled(not self.eh_critica)
        self.combo_prio.currentIndexChanged.connect(self.alterar_prioridade_ia)
        
        config_layout.addWidget(self.chk_critica)
        config_layout.addStretch()
        config_layout.addWidget(self.combo_prio)
        layout.addLayout(config_layout)
        
        layout.addStretch()
        
        # --- BOTÃO DE ACIONAMENTO MANUAL ---
        self.btn_alternar = QPushButton("Desativar Carga")
        self.btn_alternar.setCursor(Qt.PointingHandCursor)
        self.btn_alternar.clicked.connect(self.alternar_estado)
        layout.addWidget(self.btn_alternar)
        self.update_button_style()

    def alternar_estado(self):
        self.ativo = not self.ativo
        self.sincronizar_mudanca_com_sistema()

    def alternar_tipo_critica(self, checked):
        self.eh_critica = checked
        self.combo_prio.setEnabled(not checked)
        
        # Sincroniza com a memória central do dashboard principal
        if self.aba_pai and self.aba_pai.dashboard_principal:
            if self.nome in self.aba_pai.dashboard_principal.config_cargas:
                self.aba_pai.dashboard_principal.config_cargas[self.nome]["critica"] = checked
                self.aba_pai.dashboard_principal.atualizar_visual_botao(self.nome)
                self.aba_pai.dashboard_principal.adicionar_recomendacao_log(
                    f"⚙️ Cards: '{self.nome}' reconfigurado como {'CRÍTICA' if checked else 'SELETIVA'}."
                )

    def alterar_prioridade_ia(self, index):
        nova_prio = index + 1
        self.prioridade = nova_prio
        
        # Sincroniza com a memória central do dashboard principal
        if self.aba_pai and self.aba_pai.dashboard_principal:
            if self.nome in self.aba_pai.dashboard_principal.config_cargas:
                self.aba_pai.dashboard_principal.config_cargas[self.nome]["prioridade"] = nova_prio
                self.aba_pai.dashboard_principal.atualizar_visual_botao(self.nome)
                self.aba_pai.dashboard_principal.adicionar_recomendacao_log(
                    f"⚙️ Cards: Alterada prioridade de '{self.nome}' para {nova_prio}."
                )

    def sincronizar_mudanca_com_sistema(self):
        if self.ativo:
            self.lbl_status_led.setText("● ATIVO")
            self.lbl_status_led.setStyleSheet("font-size: 11px; font-weight: bold; color: #00E676; background: transparent;")
        else:
            self.lbl_status_led.setText("● DESLIGADO")
            self.lbl_status_led.setStyleSheet("font-size: 11px; font-weight: bold; color: #FF5252; background: transparent;")
            
        self.update_card_style()
        self.update_button_style()
        
        # Comunicação com o Hardware
        if self.callback_hardware:
            try:
                comando = f"{'LIGAR' if self.ativo else 'DESLIGAR'}_{self.nome.replace(' ', '')}\n"
                self.callback_hardware(comando)
            except Exception as e:
                print(f"Erro de Hardware: {e}")

        # Envia sinal de atualização para o resto do sistema
        if self.sinal_atualizacao:
            self.sinal_atualizacao.emit(self.nome, self.ativo, self.consumo)
            
        # Sincroniza direto o estado booleano com a tela principal
        if self.aba_pai and self.aba_pai.dashboard_principal:
            self.aba_pai.dashboard_principal.atualizar_status_carga_lateral(self.nome, self.ativo)

    def update_card_style(self):
        borda_cor = "#00E676" if self.ativo else "#2D2D2D"
        background = "#181818" if self.ativo else "#1A1A1A"
        self.setStyleSheet(f"QFrame#CardCarga {{ background-color: {background}; border: 2px solid {borda_cor}; border-radius: 8px; }}")

    def update_button_style(self):
        if self.ativo:
            self.btn_alternar.setText("Desativar Carga")
            self.btn_alternar.setStyleSheet("QPushButton { background-color: #FF5252; color: white; font-weight: bold; border-radius: 5px; padding: 8px; border: none; }")
        else:
            self.btn_alternar.setText("Ativar Carga")
            self.btn_alternar.setStyleSheet("QPushButton { background-color: #252525; color: #00E676; font-weight: bold; border: 1px solid #00E676; border-radius: 5px; padding: 8px; }")


class JanelaAdicionarCarga(QDialog):
    """Janela Pop-up para coletar os dados e prioridade da nova carga"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nova Carga de Sistema")
        self.setFixedWidth(320)
        self.setStyleSheet("background-color: #1A1A1A; color: white;")
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.txt_nome = QLineEdit()
        self.txt_nome.setPlaceholderText("Ex: Freezer Industrial")
        self.txt_nome.setStyleSheet("background-color: #252525; border: 1px solid #333; padding: 5px; color: white; border-radius: 4px;")
        
        self.txt_consumo = QDoubleSpinBox()
        self.txt_consumo.setRange(0.1, 50.0)
        self.txt_consumo.setValue(1.0)
        self.txt_consumo.setSuffix(" kW")
        self.txt_consumo.setStyleSheet("background-color: #252525; border: 1px solid #333; padding: 5px; color: white; border-radius: 4px;")
        
        self.chk_critica = QCheckBox("Imune a cortes automáticos (Crítica)")
        self.chk_critica.setStyleSheet("color: white; font-size: 11px;")
        
        self.combo_prio = QComboBox()
        self.combo_prio.addItems(["1 - Máxima Importância", "2 - Média Importância", "3 - Mínima Importância"])
        self.combo_prio.setStyleSheet("background-color: #252525; color: white; padding: 5px; border-radius: 4px;")
        self.chk_critica.toggled.connect(lambda checked: self.combo_prio.setDisabled(checked))
        
        form_layout.addRow("Nome da Carga:", self.txt_nome)
        form_layout.addRow("Consumo Est.:", self.txt_consumo)
        form_layout.addRow("Tipo:", self.chk_critica)
        form_layout.addRow("Prioridade IA:", self.combo_prio)
        layout.addLayout(form_layout)
        
        self.btn_salvar = QPushButton("Adicionar no Sistema")
        self.btn_salvar.setStyleSheet("background-color: #00E676; color: black; font-weight: bold; padding: 8px; border-radius: 4px; margin-top: 10px;")
        self.btn_salvar.clicked.connect(self.accept)
        layout.addWidget(self.btn_salvar)

    def obtener_dados(self):
        return (
            self.txt_nome.text().strip(),
            self.txt_consumo.value(),
            self.combo_prio.currentIndex() + 1,
            self.chk_critica.isChecked()
        )


class AbaCargas(QWidget):
    carga_alterada = Signal(str, bool, float) 

    def __init__(self, arduino_serial=None, dashboard_principal=None, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #121212;")
        
        self.arduino_serial = arduino_serial
        self.dashboard_principal = dashboard_principal
        self.lista_cards = []
        
        self.callback_envio = None
        if arduino_serial:
            if hasattr(arduino_serial, 'enviar_dados'): self.callback_envio = arduino_serial.enviar_dados
            elif hasattr(arduino_serial, 'write'): self.callback_envio = arduino_serial.write

        # Layout Principal
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(25, 25, 25, 25)
        layout_principal.setSpacing(20)
        
        # Painel Superior
        topo_painel = QHBoxLayout()
        self.titulo = QLabel("⚙️ Gerenciamento Distribuído de Cargas")
        self.titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #00E676; background: transparent;")
        
        self.btn_nova_carga = QPushButton("+ Nova Carga")
        self.btn_nova_carga.setStyleSheet("""
            QPushButton { background-color: #00E676; color: black; font-weight: bold; border-radius: 5px; padding: 8px 15px; }
            QPushButton:hover { background-color: #00B359; }
        """)
        self.btn_nova_carga.clicked.connect(self.abrir_formulario_carga)
        
        topo_painel.addWidget(self.titulo)
        topo_painel.addStretch()
        topo_painel.addWidget(self.btn_nova_carga)
        layout_principal.addLayout(topo_painel)
        
        # Grade de Cards
        self.grid_cargas = QGridLayout()
        self.grid_cargas.setSpacing(20)
        layout_principal.addLayout(self.grid_cargas)
        layout_principal.addStretch()
        
        # 🔄 Renderização dinâmica com sincronização centralizada
        self.sincronizar_com_monitoramento_geral()

    def sincronizar_com_monitoramento_geral(self):
        """Limpa a grade e recria os cards baseando-se no dicionário unificado do Dashboard"""
        # Limpa os componentes antigos para evitar vazamento de memória gráfica
        for card in self.lista_cards:
            self.grid_cargas.removeWidget(card)
            card.deleteLater()
        self.lista_cards.clear()
        
        # Pega a base de dados dinâmica da tela principal. Caso não exista, assume o fallback padrão.
        if self.dashboard_principal and hasattr(self.dashboard_principal, 'config_cargas'):
            dados_cargas = self.dashboard_principal.config_cargas.items()
        else:
            # Fallback seguro estruturado com prioridades iniciais coerentes
            dados_cargas = {
                "Geladeira": {"critica": True, "potencia": 0.8, "ativo": True, "prioridade": 1},
                "Iluminação Sala": {"critica": True, "potencia": 0.3, "ativo": True, "prioridade": 1},
                "Roteador Internet": {"critica": True, "potencia": 0.1, "ativo": True, "prioridade": 1},
                "Ar-Condicionado": {"critica": False, "potencia": 2.0, "ativo": True, "prioridade": 1},
                "Bomba D'água": {"critica": False, "potencia": 1.2, "ativo": True, "prioridade": 3},
                "Computador": {"critica": False, "potencia": 0.5, "ativo": True, "prioridade": 2}
            }.items()
            
        for nome, info in dados_cargas:
            novo_card = CardCarga(
                nome=nome,
                consumo_kw=info.get("potencia", 1.0),
                prioridade=info.get("prioridade", 1),
                eh_critica=info.get("critica", False),
                callback_hardware=self.callback_envio,
                sinal_atualizacao=self.carga_alterada,
                aba_pai=self
            )
            
            # Sincroniza o estado de ativação atualizado da memória
            novo_card.ativo = info.get("ativo", True)
            if not novo_card.ativo:
                novo_card.lbl_status_led.setText("● DESLIGADO")
                novo_card.lbl_status_led.setStyleSheet("font-size: 11px; font-weight: bold; color: #FF5252; background: transparent;")
                novo_card.update_card_style()
                novo_card.update_button_style()
                
            self.lista_cards.append(novo_card)
            
            # Reposicionamento matemático na matriz de 3 colunas
            posicao = len(self.lista_cards) - 1
            linha = posicao // 3
            coluna = posicao % 3
            self.grid_cargas.addWidget(novo_card, linha, coluna)

    def atualizar_interface_externa(self, nome_carga, devera_ativar):
        """Método invocado pelo loop externo do main.py para forçar o card a mudar de cor na tela se a IA cortar"""
        for card in self.lista_cards:
            if card.nome == nome_carga:
                card.ativo = devera_ativar
                card.lbl_status_led.setText("● ATIVO" if devera_ativar else "● DESLIGADO")
                card.lbl_status_led.setStyleSheet(
                    f"font-size: 11px; font-weight: bold; color: {'#00E676' if devera_ativar else '#FF5252'}; background: transparent;"
                )
                card.update_card_style()
                card.update_button_style()
                break

    def abrir_formulario_carga(self):
        formulario = JanelaAdicionarCarga(self)
        if formulario.exec() == QDialog.Accepted:
            nome, consumo, prioridade, eh_critica = formulario.obter_dados()
            
            # Se a janela principal existir, adiciona na memória compartilhada global
            if self.dashboard_principal and hasattr(self.dashboard_principal, 'config_cargas'):
                self.dashboard_principal.config_cargas[nome] = {
                    "critica": eh_critica,
                    "potencia": consumo,
                    "ativo": True,
                    "btn": None,
                    "prioridade": prioridade
                }
                # Cria o botão lá na barra lateral do dashboard
                self.dashboard_principal.criar_e_adicionar_botao_na_tela(nome)
                self.dashboard_principal.adicionar_recomendacao_log(f"➕ Cards: Novo dispositivo '{nome}' integrado via painel secundário.")
            
            # Atualiza a grade local de cards para renderizar o novo elemento
            self.sincronizar_com_monitoramento_geral()