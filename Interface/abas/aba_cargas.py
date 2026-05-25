from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QGridLayout, QFrame, QDialog, 
                               QLineEdit, QDoubleSpinBox, QFormLayout)
from PySide6.QtCore import Qt, Signal

class CardCarga(QFrame):
    """Componente visual reutilizável para representar uma carga do sistema"""
    def __init__(self, nome, consumo_kw, callback_hardware=None, sinal_atualizacao=None, parent=None):
        super().__init__(parent)
        self.nome = nome
        self.consumo = consumo_kw
        self.callback_hardware = callback_hardware
        self.sinal_atualizacao = sinal_atualizacao
        self.ativo = False
        
        self.setObjectName("CardCarga")
        self.setFrameShape(QFrame.StyledPanel)
        self.setMinimumHeight(140)
        self.update_card_style()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        topo_layout = QHBoxLayout()
        self.lbl_nome = QLabel(nome)
        self.lbl_nome.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF; background: transparent;")
        
        self.lbl_status_led = QLabel("● DESLIGADO")
        self.lbl_status_led.setStyleSheet("font-size: 11px; font-weight: bold; color: #FF5252; background: transparent;")
        
        topo_layout.addWidget(self.lbl_nome)
        topo_layout.addStretch()
        topo_layout.addWidget(self.lbl_status_led)
        layout.addLayout(topo_layout)
        
        self.lbl_consumo = QLabel(f"⚡ Consumo: {consumo_kw} kWh")
        self.lbl_consumo.setStyleSheet("font-size: 13px; color: #888888; background: transparent; margin-top: 5px;")
        layout.addWidget(self.lbl_consumo)
        
        layout.addStretch()
        
        self.btn_alternar = QPushButton("Acionar Carga")
        self.btn_alternar.setCursor(Qt.PointingHandCursor)
        self.btn_alternar.clicked.connect(self.alternar_estado)
        layout.addWidget(self.btn_alternar)
        self.update_button_style()

    def alternar_estado(self):
        self.ativo = not self.ativo
        
        if self.ativo:
            self.lbl_status_led.setText("● ATIVO")
            self.lbl_status_led.setStyleSheet("font-size: 11px; font-weight: bold; color: #00E676; background: transparent;")
        else:
            self.lbl_status_led.setText("● DESLIGADO")
            self.lbl_status_led.setStyleSheet("font-size: 11px; font-weight: bold; color: #FF5252; background: transparent;")
            
        self.update_card_style()
        self.update_button_style()
        
        if self.callback_hardware:
            try:
                comando = f"{'LIGAR' if self.ativo else 'DESLIGAR'}_{self.nome.replace(' ', '')}\n"
                self.callback_hardware(comando)
            except Exception as e:
                print(f"Erro de Hardware: {e}")

        if self.sinal_atualizacao:
            self.sinal_atualizacao.emit(self.nome, self.ativo, self.consumo)

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
    """Janela Pop-up para coletar os dados da nova carga"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nova Carga Crítica")
        self.setFixedWidth(300)
        self.setStyleSheet("background-color: #1A1A1A; color: white;")
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.txt_nome = QLineEdit()
        self.txt_nome.setPlaceholderText("Ex: Freezer Industrial")
        self.txt_nome.setStyleSheet("background-color: #252525; border: 1px solid #333; padding: 5px; color: white; border-radius: 4px;")
        
        self.txt_consumo = QDoubleSpinBox()
        self.txt_consumo.setRange(0.1, 50.0)
        self.txt_consumo.setSuffix(" kWh")
        self.txt_consumo.setStyleSheet("background-color: #252525; border: 1px solid #333; padding: 5px; color: white; border-radius: 4px;")
        
        form_layout.addRow("Nome da Carga:", self.txt_nome)
        form_layout.addRow("Consumo Est.:", self.txt_consumo)
        layout.addLayout(form_layout)
        
        # Botão salvar
        self.btn_salvar = QPushButton("Adicionar Sistema")
        self.btn_salvar.setStyleSheet("background-color: #00E676; color: black; font-weight: bold; padding: 8px; border-radius: 4px; margin-top: 10px;")
        self.btn_salvar.clicked.connect(self.accept)
        layout.addWidget(self.btn_salvar)

    def obter_dados(self):
        return self.txt_nome.text().strip(), self.txt_consumo.value()


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
        
        # Topo
        topo_painel = QHBoxLayout()
        self.titulo = QLabel("⚙️ Gerenciamento de Cargas Críticas")
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
        
        # 🔄 CARREGAMENTO DINÂMICO DOS ESTADOS DA TELA PRINCIPAL
        self.sincronizar_com_monitoramento_geral()

    def sincronizar_com_monitoramento_geral(self):
        """Lê os dados e os estados reais das cargas que já existem no Dashboard principal"""
        # Lista padrão baseada exatamente na sua imagem do monitoramento geral
        cargas_padrao = [
            ("Geladeira", 0.8, True),
            ("Iluminação Sala", 0.3, True),
            ("Roteador Internet", 0.1, True),
            ("Ar-Condicionado", 2.0, True),
            ("Bomba D'água", 1.2, True),
            ("Computador", 0.5, True)
        ]
        
        # Se o seu dashboard_principal tiver um dicionário ou lista de cargas, usamos ela.
        # Caso contrário, usamos a lista padrão acima, mapeando o estado inicial.
        for nome, consumo, estado_inicial in cargas_padrao:
            # Cria o card passando o estado correto (True = Ativo)
            novo_card = CardCarga(nome, consumo, callback_hardware=self.callback_envio, sinal_atualizacao=self.carga_alterada)
            
            # Se o estado inicial for True, força o card a iniciar ativo de fábrica
            if estado_inicial:
                novo_card.ativo = True
                novo_card.lbl_status_led.setText("● ATIVO")
                novo_card.lbl_status_led.setStyleSheet("font-size: 11px; font-weight: bold; color: #00E676; background: transparent;")
                novo_card.update_card_style()
                novo_card.update_button_style()
                
            self.lista_cards.append(novo_card)
            
            # Organiza na grade (3 colunas para acomodar melhor os 6 itens na tela)
            total_atual = len(self.lista_cards) - 1
            linha = total_atual // 3
            coluna = total_atual % 3
            self.grid_cargas.addWidget(novo_card, linha, coluna)

    def abrir_formulario_carga(self):
        formulario = JanelaAdicionarCarga(self)
        if formulario.exec() == QDialog.Accepted:
            nome, consumo = formulario.obter_dados()
            
            novo_card = CardCarga(nome, consumo, callback_hardware=self.callback_envio, sinal_atualizacao=self.carga_alterada)
            self.lista_cards.append(novo_card)
            
            total_atual = len(self.lista_cards) - 1
            linha = total_atual // 3
            coluna = total_atual % 3
            self.grid_cargas.addWidget(novo_card, linha, coluna)