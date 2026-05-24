from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTextEdit
from PySide6.QtCore import Qt

class PainelBateria(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bateria_soc = 50.0  # Estado de Carga Inicial (50%)
        self.capacidade_total = 5.0  # 5.0 kWh
        self.setup_ui()

    def setup_ui(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)

        # Cabeçalho Informativo
        lbl_titulo = QLabel("Gerenciamento do Banco de Baterias (EMS)")
        lbl_titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        layout_principal.addWidget(lbl_titulo)

        # Container Horizontal para os Cards de Status
        container_cards = QHBoxLayout()

        # Card 1: Estado de Carga (SoC)
        self.card_soc = QFrame()
        self.card_soc.setStyleSheet("background-color: #1E1E1E; border: 1px solid #333333; border-radius: 6px; padding: 15px;")
        ly_soc = QVBoxLayout(self.card_soc)
        lbl_soc_tit = QLabel("ESTADO DE CARGA (SoC)")
        lbl_soc_tit.setStyleSheet("font-size: 10px; color: #888888; border: none;")
        self.lbl_soc_val = QLabel("50%")
        self.lbl_soc_val.setStyleSheet("font-size: 28px; font-weight: bold; color: #00E676; border: none;")
        ly_soc.addWidget(lbl_soc_tit)
        ly_soc.addWidget(self.lbl_soc_val)
        container_cards.addWidget(self.card_soc)

        # Card 2: Fluxo Potência Corrente
        self.card_fluxo = QFrame()
        self.card_fluxo.setStyleSheet("background-color: #1E1E1E; border: 1px solid #333333; border-radius: 6px; padding: 15px;")
        ly_fluxo = QVBoxLayout(self.card_fluxo)
        lbl_fluxo_tit = QLabel("FLUXO DE POTÊNCIA")
        lbl_fluxo_tit.setStyleSheet("font-size: 10px; color: #888888; border: none;")
        self.lbl_fluxo_val = QLabel("0.0 kWh (Ocioso)")
        self.lbl_fluxo_val.setStyleSheet("font-size: 20px; font-weight: bold; color: #B0BEC5; border: none;")
        ly_fluxo.addWidget(lbl_fluxo_tit)
        ly_fluxo.addWidget(self.lbl_fluxo_val)
        container_cards.addWidget(self.card_fluxo)

        layout_principal.addLayout(container_cards)

        # Terminal de telemetria da bateria
        lbl_diag_tit = QLabel("📋 Histórico de Ciclos e Saúde do Banco")
        lbl_diag_tit.setStyleSheet("font-size: 11px; font-weight: bold; color: #00ACC1; margin-top: 15px;")
        layout_principal.addWidget(lbl_diag_tit)

        self.txt_log_bateria = QTextEdit()
        self.txt_log_bateria.setReadOnly(True)
        self.txt_log_bateria.setStyleSheet("""
            background-color: #121212; color: #A5D6A7; 
            font-family: 'Consolas', monospace; font-size: 11px;
            border: 1px solid #2D2D2D; border-radius: 4px;
        """)
        self.txt_log_bateria.append("Bateria Lithium-Ion de 5.0 kWh operacional. SOH: 100%.")
        layout_principal.addWidget(self.txt_log_bateria)
        
        layout_principal.addStretch()

    def atualizar_dados_bateria(self, geracao, consumo):
        """
        Gerencia o fluxo físico da bateria com base na geração solar e consumo da casa.
        Retorna:
            - saldo_final_rede (float): O que sobra ou falta para a concessionária de energia
            - energia_movimentada (float): Potência atual de carga (+) ou descarga (-)
        """
        # Cálculo do balanço inicial da casa
        saldo_bruto = geracao - consumo
        energia_movimentada = 0.0
        
        # Parâmetros físicos reais da bateria
        taxa_maxima_potencia = 1.5  # Máximo de kWh que a bateria consegue puxar/injetar por ciclo
        soc_minimo = 10.0            # Margem de segurança para não danificar a bateria (10%)
        soc_maximo = 100.0           # Limite superior de carga (100%)

        # --- CASO 1: SOBRA ENERGIA (Geração > Consumo) -> Carregar Bateria ---
        if saldo_bruto > 0:
            if self.bateria_soc < soc_maximo:
                # Descobre quanto espaço livre ainda existe em kWh na bateria
                espaco_livre_kwh = ((soc_maximo - self.bateria_soc) / 100.0) * self.capacidade_total
                
                # A carga real será o menor valor entre: o que sobrou do sol, a potência máxima do inversor ou o espaço livre
                energia_movimentada = min(saldo_bruto, taxa_maxima_potencia, espaco_livre_kwh)
                
                # Converte os kWh injetados de volta para incremento de % no SoC
                self.bateria_soc += (energia_movimentada / self.capacidade_total) * 100.0
                self.bateria_soc = min(soc_maximo, self.bateria_soc)
            
            # O saldo final enviado para a rede elétrica é a sobra solar MENOS o que a bateria absorveu
            saldo_final_rede = round(saldo_bruto - energia_movimentada, 1)
            
            # Atualiza interface da bateria (Modo Carga)
            if energia_movimentada > 0:
                self.lbl_fluxo_val.setText(f"+{energia_movimentada:.1f} kWh (Carregando)")
                self.lbl_fluxo_val.setStyleSheet("font-size: 20px; font-weight: bold; color: #4CAF50; border: none;")
            else:
                self.lbl_fluxo_val.setText("0.0 kWh (Cheia / Ociosa)")
                self.lbl_fluxo_val.setStyleSheet("font-size: 20px; font-weight: bold; color: #B0BEC5; border: none;")

        # --- CASO 2: FALTA ENERGIA (Consumo > Geração) -> Descarregar Bateria ---
        else:
            deficit_necessario = abs(saldo_bruto)
            
            if self.bateria_soc > soc_minimo:
                # Descobre quanta energia útil em kWh a bateria ainda tem disponível acima do limite de 10%
                energia_disponivel_kwh = ((self.bateria_soc - soc_minimo) / 100.0) * self.capacidade_total
                
                # A descarga real será o menor valor entre: o déficit da casa, a potência máxima de descarga ou a energia disponível
                energia_movimentada = min(deficit_necessario, taxa_maxima_potencia, energia_disponivel_kwh)
                
                # Deduz os kWh gastos do SoC da bateria
                self.bateria_soc -= (energia_movimentada / self.capacidade_total) * 100.0
                self.bateria_soc = max(soc_minimo, self.bateria_soc)
            
            # O saldo final que precisamos comprar da concessionária é o déficit MENOS o que a bateria conseguiu suprir
            # Como é um déficit, mantemos o sinal negativo para a rede externa
            saldo_final_rede = round(- (deficit_necessario - energia_movimentada), 1)
            
            # Atualiza interface da bateria (Modo Descarga)
            if energia_movimentada > 0:
                self.lbl_fluxo_val.setText(f"-{energia_movimentada:.1f} kWh (Descarregando)")
                self.lbl_fluxo_val.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFC107; border: none;")
            else:
                self.lbl_fluxo_val.setText("0.0 kWh (Esgotada / Rede Ativa)")
                self.lbl_fluxo_val.setStyleSheet("font-size: 20px; font-weight: bold; color: #F44336; border: none;")

        # Atualiza o mostrador textual da porcentagem
        self.lbl_soc_val.setText(f"{int(self.bateria_soc)}%")
        
        fluxo_retorno = energia_movimentada if (geracao - consumo) > 0 else -energia_movimentada
        return saldo_final_rede, fluxo_retorno