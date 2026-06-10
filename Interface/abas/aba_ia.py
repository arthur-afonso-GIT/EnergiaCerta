import sys
import random
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QFrame, QPushButton, QScrollArea, QProgressBar)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis

class CardStatusIA(QFrame):
    """Cards superiores indicando a telemetria do modelo de IA"""
    def __init__(self, titulo, valor, icone_status, cor_destaque, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #1A1A1A;
                border: 1px solid #2D2D2D;
                border-radius: 10px;
            }}
        """)
        self.setMinimumHeight(100)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 15, 18, 15)
        
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("color: #888888; font-size: 11px; font-weight: bold; letter-spacing: 1px; background: transparent;")
        
        # 🚨 CORRIGIDO: Agora usa 'self.' para ser acessível externamente no método de progresso!
        self.lbl_valor = QLabel(f"{icone_status} {valor}")
        self.lbl_valor.setStyleSheet(f"color: {cor_destaque}; font-size: 20px; font-weight: bold; background: transparent;")
        
        layout.addWidget(lbl_titulo)
        layout.addWidget(self.lbl_valor)

class CardInsight(QFrame):
    """Cards de recomendação inteligente com efeito Hover Premium"""
    def __init__(self, tipo, titulo, descricao, impacto, cor_borda, parent=None):
        super().__init__(parent)
        self.cor_borda = cor_borda
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #1A1A1A;
                border-left: 5px solid {self.cor_borda};
                border-top: 1px solid #2A2A2A;
                border-right: 1px solid #2A2A2A;
                border-bottom: 1px solid #2A2A2A;
                border-radius: 8px;
            }}
            QFrame:hover {{
                background-color: #222222;
                border-top: 1px solid #3E3E3E;
                border-right: 1px solid #3E3E3E;
                border-bottom: 1px solid #3E3E3E;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        
        # Bloco de texto esquerdo
        layout_texto = QVBoxLayout()
        layout_texto.setSpacing(4)
        
        lbl_tipo = QLabel(tipo.upper())
        lbl_tipo.setStyleSheet(f"color: {self.cor_borda}; font-size: 11px; font-weight: bold; letter-spacing: 0.5px; background: transparent;")
        
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("color: #FFFFFF; font-size: 15px; font-weight: bold; background: transparent;")
        
        lbl_desc = QLabel(descricao)
        lbl_desc.setStyleSheet("color: #A0A0A0; font-size: 13px; line-height: 18px; background: transparent;")
        lbl_desc.setWordWrap(True)
        
        layout_texto.addWidget(lbl_tipo)
        layout_texto.addWidget(lbl_titulo)
        layout_texto.addWidget(lbl_desc)
        
        # Bloco de impacto direito (Métrica Financeira / Técnica)
        layout_impacto = QVBoxLayout()
        layout_impacto.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        lbl_imp_titulo = QLabel("RETORNO ESTIMADO")
        lbl_imp_titulo.setStyleSheet("color: #777777; font-size: 10px; font-weight: bold; background: transparent;")
        
        lbl_imp_valor = QLabel(impacto)
        lbl_imp_valor.setStyleSheet(f"color: #00E676; font-size: 16px; font-weight: bold; background: transparent;")
        
        layout_impacto.addWidget(lbl_imp_titulo)
        layout_impacto.addWidget(lbl_imp_valor)
        
        layout.addLayout(layout_texto, stretch=4)
        layout.addLayout(layout_impacto, stretch=1)

class AbaIA(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #121212; color: #FFFFFF;")
        
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(25, 25, 25, 25)
        layout_principal.setSpacing(20)
        
        # 1. CABEÇALHO DA INTERFACE
        layout_header = QHBoxLayout()
        self.titulo = QLabel("🧠 Inteligência Preditiva e Algoritmos de Demanda")
        self.titulo.setStyleSheet("font-size: 22px; font-weight: bold; color: #00E676; background: transparent;")
        
        self.btn_otimizar = QPushButton("⚡ Recomputar Redes")
        self.btn_otimizar.setCursor(Qt.PointingHandCursor)
        self.btn_otimizar.setStyleSheet("""
            QPushButton {
                background-color: #00E676;
                color: #121212;
                font-weight: bold;
                font-size: 13px;
                padding: 10px 24px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #00C865;
            }
            QPushButton:disabled {
                background-color: #2D2D2D;
                color: #888888;
            }
        """)
        self.btn_otimizar.clicked.connect(self.executar_otimizacao)
        
        layout_header.addWidget(self.titulo)
        layout_header.addStretch()
        layout_header.addWidget(self.btn_otimizar)
        layout_principal.addLayout(layout_header)
        
        # Barra de Progresso Avançada
        self.progresso_ia = QProgressBar()
        self.progresso_ia.setStyleSheet("""
            QProgressBar {
                border: 1px solid #2D2D2D;
                border-radius: 6px;
                background-color: #1A1A1A;
                text-align: center;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 11px;
                height: 18px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #00E676);
                border-radius: 5px;
            }
        """)
        self.progresso_ia.setVisible(False)
        layout_principal.addWidget(self.progresso_ia)
        
        # 2. CARDS SUPERIORES DE TELEMETRIA MATEMÁTICA
        layout_cards = QHBoxLayout()
        layout_cards.setSpacing(15)
        
        self.card_modo = CardStatusIA("POLÍTICA OPERACIONAL", "DESPACHO ECONÔMICO", "🛡️", "#00E676")
        self.card_confianca = CardStatusIA("CONFIANÇA DO MODELO (R²)", "98.7 %", "📊", "#3b82f6")
        self.card_proxima_acao = CardStatusIA("PROG. DE ALÍVIO DE CARGA", "Modulação às 18:00h", "⏱️", "#FFD700")
        
        layout_cards.addWidget(self.card_modo)
        layout_cards.addWidget(self.card_confianca)
        layout_cards.addWidget(self.card_proxima_acao)
        layout_principal.addLayout(layout_cards)
        
        # 3. DIVISÃO CENTRAL (GRÁFICO E INSIGHTS SCROLLABLE)
        layout_conteudo = QHBoxLayout()
        layout_conteudo.setSpacing(25)
        
        # Gráfico Preditivo
        self.chart_view_previsao = self.criar_grafico_previsao()
        layout_conteudo.addWidget(self.chart_view_previsao, stretch=5)
        
        # Container de Insights à direita
        layout_insights_container = QVBoxLayout()
        lbl_insights_titulo = QLabel("📋 Diagnósticos e Ações Recomendadas")
        lbl_insights_titulo.setStyleSheet("font-size: 14px; font-weight: bold; color: #888888; background: transparent; margin-bottom: 5px;")
        layout_insights_container.addWidget(lbl_insights_titulo)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical {
                border: none;
                background: #121212;
                width: 8px;
                margin: 0px 0px 0px 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #2D2D2D;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #00E676;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none; background: none;
            }
        """)
        
        self.widget_lista_insights = QWidget()
        self.widget_lista_insights.setStyleSheet("background-color: #121212;")
        self.layout_lista = QVBoxLayout(self.widget_lista_insights)
        self.layout_lista.setContentsMargins(0, 0, 5, 0)
        self.layout_lista.setSpacing(12)
        
        self.popular_insights_default()
        
        scroll.setWidget(self.widget_lista_insights)
        layout_insights_container.addWidget(scroll)
        layout_conteudo.addLayout(layout_insights_container, stretch=5)
        
        layout_principal.addLayout(layout_conteudo, stretch=1)

    def criar_grafico_previsao(self):
        chart = QChart()
        chart.setTitle("🔮 Curva de Carga: Medido vs Projeção de Algoritmo")
        chart.setTitleBrush(QColor("#FFFFFF"))
        chart.setBackgroundBrush(QColor("#1A1A1A"))
        
        series_real = QLineSeries()
        series_real.setName("Consumo em Tempo Real")
        series_real.setColor(QColor("#00E676"))
        
        # Simulação de dados já consolidados do dia
        series_real.append(12, 3.1)
        series_real.append(13, 2.9)
        series_real.append(14, 3.4)
        series_real.append(15, 3.8)
        chart.addSeries(series_real)
        
        series_predicao = QLineSeries()
        series_predicao.setName("Projeção Preditiva (Rede Neural)")
        pen_predicao = QPen(QColor("#3b82f6"))
        pen_predicao.setWidth(3)
        pen_predicao.setStyle(Qt.DashLine)
        series_predicao.setPen(pen_predicao)
        
        # IA inferindo comportamento futuro das cargas baseada no histórico de 2026
        series_predicao.append(15, 3.8)
        series_predicao.append(16, 4.2)
        series_predicao.append(17, 5.5)  # Pico previsto pela chegada do pessoal
        series_predicao.append(18, 5.1)
        series_predicao.append(19, 2.4)
        chart.addSeries(series_predicao)
        
        axis_x = QValueAxis()
        axis_x.setRange(12, 19)
        axis_x.setTitleText("Horário de Operação (Horas)")
        axis_x.setLabelFormat("%d:00")
        axis_x.setLabelsColor(QColor("#888888"))
        chart.addAxis(axis_x, Qt.AlignBottom)
        series_real.attachAxis(axis_x)
        series_predicao.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(0, 6.5)
        axis_y.setTitleText("Demanda (kW)")
        axis_y.setLabelsColor(QColor("#888888"))
        chart.addAxis(axis_y, Qt.AlignLeft)
        series_real.attachAxis(axis_y)
        series_predicao.attachAxis(axis_y)
        
        chart.legend().setVisible(True)
        chart.legend().setBrush(QColor("#FFFFFF"))
        chart.legend().setAlignment(Qt.AlignBottom)
        
        view = QChartView(chart)
        view.setRenderHint(QPainter.Antialiasing)
        view.setStyleSheet("border: 1px solid #2D2D2D; border-radius: 10px;")
        return view

    def popular_insights_default(self):
        insight1 = CardInsight(
            "🔴 Alerta de Demanda Máxima",
            "Sugerido interlocking preventivo de pico às 17h30",
            "A rede neural identificou padrão probabilístico alto de pico de corrente. Sugere-se o desligamento controlado da 'Bomba D'água' por 20 minutos para achatar a curva e mitigar multas de ultrapassagem.",
            "- R$ 55,00 / Mês",
            "#EF4444"
        )
        insight2 = CardInsight(
            "🔵 Despacho Inteligente de Energia",
            "Acionamento Estratégico de Banco de Baterias",
            "Tarifa ponta em vigor. Otimizador recomenda comutar o circuito de 'Servidores Core' para o inversor de baterias híbrido, aliviando a rede externa no horário crítico.",
            "- R$ 34,20 / Mês",
            "#3b82f6"
        )
        insight3 = CardInsight(
            "🟡 Anomalia de Consumo Reativo",
            "Compressor de Ar Condicionado operando fora do padrão",
            "O ciclo térmico do 'Ar Condicionado Lab' demonstrou desvio padrão de 14% em relação ao comportamento padrão. É aconselhável limpar filtros ou checar o nível de gás refrigerante.",
            "Manutenção Preditiva",
            "#F59E0B"
        )
        
        self.layout_lista.addWidget(insight1)
        self.layout_lista.addWidget(insight2)
        self.layout_lista.addWidget(insight3)
        self.layout_lista.addStretch()

    def executar_otimizacao(self):
        """Simula o reprocessamento matemático dos pesos sinápticos"""
        self.btn_otimizar.setEnabled(False)
        self.btn_otimizar.setText("🧠 Analisando histórico...")
        self.progresso_ia.setVisible(True)
        self.progresso_ia.setValue(0)
        
        self.valor_progresso = 0
        self.timer_progresso = QTimer(self)
        self.timer_progresso.timeout.connect(self._atualizar_passo_progresso)
        self.timer_progresso.start(40)

    def _atualizar_passo_progresso(self):
        self.valor_progresso += 4
        self.progresso_ia.setValue(self.valor_progresso)
        
        if self.valor_progresso == 40:
            self.btn_otimizar.setText("⚡ Ajustando Limiares...")
        elif self.valor_progresso == 80:
            self.btn_otimizar.setText("💾 Gravando Setpoints...")
            
        if self.valor_progresso >= 100:
            self.timer_progresso.stop()
            self.progresso_ia.setVisible(False)
            self.btn_otimizar.setEnabled(True)
            self.btn_otimizar.setText("⚡ Recomputar Redes")
            
            # Atualiza o R² com pequena flutuação estatística realista
            nova_confianca = random.uniform(98.2, 99.8)
            self.card_confianca.lbl_valor.setText(f"📊 {nova_confianca:.1f} %")