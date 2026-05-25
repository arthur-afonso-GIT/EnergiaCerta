import sys
import random
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QFrame, QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis

class CardKPI(QFrame):
    """Componente visual para exibir indicadores-chave de eficiência"""
    def __init__(self, titulo, valor, sufixo, cor_destaque, parent=None):
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
        layout.setContentsMargins(15, 15, 15, 15)
        
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("color: #888888; font-size: 13px; font-weight: bold; background: transparent;")
        
        self.lbl_valor = QLabel(f"{valor} <span style='font-size: 16px; color: #888888;'>{sufixo}</span>")
        self.lbl_valor.setStyleSheet(f"color: {cor_destaque}; font-size: 28px; font-weight: bold; background: transparent;")
        
        layout.addWidget(lbl_titulo)
        layout.addWidget(self.lbl_valor)

class AbaGraficos(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #121212; color: #FFFFFF;")
        
        # Variáveis de controle estáveis para simulação
        self.consumo_base_atual = 0.0
        self.contador_tempo = 0
        
        # Layout Principal
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(25, 25, 25, 25)
        layout_principal.setSpacing(20)
        
        # 1. TÍTULO
        self.titulo = QLabel("📊 Desempenho e Eficiência Energética")
        self.titulo.setStyleSheet("font-size: 22px; font-weight: bold; color: #00E676; background: transparent;")
        layout_principal.addWidget(self.titulo)
        
        # 2. KPIs
        layout_kpis = QHBoxLayout()
        layout_kpis.setSpacing(15)
        
        self.kpi_eficiencia = CardKPI("EFICIÊNCIA GLOBAL", "92.4", "%", "#00E676")
        self.kpi_demanda = CardKPI("FATOR DE DEMANDA", "0.0", "kW", "#3b82f6")
        self.kpi_economia = CardKPI("ECONOMIA ACUMULADA", "R$ 145,20", "", "#FFD700")
        
        layout_kpis.addWidget(self.kpi_eficiencia)
        layout_kpis.addWidget(self.kpi_demanda)
        layout_kpis.addWidget(self.kpi_economia)
        layout_principal.addLayout(layout_kpis)
        
        # 3. GRÁFICOS (Layout Lado a Lado seguro)
        layout_graficos = QHBoxLayout()
        layout_graficos.setSpacing(20)
        
        self.chart_view_linha = self.criar_grafico_linha()
        self.chart_view_barras = self.criar_grafico_barras()
        
        layout_graficos.addWidget(self.chart_view_linha, stretch=1)
        layout_graficos.addWidget(self.chart_view_barras, stretch=1)
        layout_principal.addLayout(layout_graficos, stretch=2)
        
        # 4. TABELA INFERIOR
        self.lbl_subtitulo = QLabel("📋 Histórico Mensal e Impacto Financeiro")
        self.lbl_subtitulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #888888; background: transparent; margin-top: 10px;")
        layout_principal.addWidget(self.lbl_subtitulo)
        
        self.tabela_historico = QTableWidget()
        self.configurar_tabela()
        layout_principal.addWidget(self.tabela_historico, stretch=1)

        # 🕒 TIMER SEGURO: Só inicia após a janela estar totalmente montada
        self.timer_simulacao = QTimer(self)
        self.timer_simulacao.timeout.connect(self.generar_leitura_sensores_ruido)
        self.timer_simulacao.start(1000)

    def criar_grafico_linha(self):
        """Cria o gráfico de linhas puro (altamente estável contra crashes de renderização)"""
        chart = QChart()
        chart.setTitle("📈 Tendências de Consumo Diário (Tempo Real)")
        chart.setTitleBrush(QColor("#FFFFFF"))
        chart.setBackgroundBrush(QColor("#1A1A1A"))
        chart.setAnimationOptions(QChart.NoAnimation) # Evita bugs de animação paralela em tempo real
        
        self.series_linha = QLineSeries()
        self.series_linha.setName("Consumo (kW)")
        self.series_linha.setColor(QColor("#00E676"))
        
        # Inicializa apenas com o ponto zero para evitar estouro de eixos antes do show()
        self.series_linha.append(0, 0.0)
        chart.addSeries(self.series_linha)
        
        # Eixo X
        self.axis_x_linha = QValueAxis()
        self.axis_x_linha.setRange(0, 15)
        self.axis_x_linha.setTitleText("Tempo (Segundos)")
        self.axis_x_linha.setLabelFormat("%d s")
        self.axis_x_linha.setLabelsColor(QColor("#888888"))
        chart.addAxis(self.axis_x_linha, Qt.AlignBottom)
        self.series_linha.attachAxis(self.axis_x_linha)
        
        # Eixo Y
        self.axis_y_linha = QValueAxis()
        self.axis_y_linha.setRange(0, 6.0)
        self.axis_y_linha.setTitleText("Potência (kW)")
        self.axis_y_linha.setLabelsColor(QColor("#888888"))
        chart.addAxis(self.axis_y_linha, Qt.AlignLeft)
        self.series_linha.attachAxis(self.axis_y_linha)
        
        chart.legend().setVisible(False)
        
        view = QChartView(chart)
        view.setRenderHint(QPainter.Antialiasing)
        view.setStyleSheet("border: 1px solid #2D2D2D; border-radius: 10px;")
        return view

    def criar_grafico_barras(self):
        """Cria o gráfico de barras verticais de intensidade"""
        chart = QChart()
        chart.setTitle("⚡ Intensidade de Consumo por Dispositivo")
        chart.setTitleBrush(QColor("#FFFFFF"))
        chart.setBackgroundBrush(QColor("#1A1A1A"))
        
        bar_set = QBarSet("Potência Nominal")
        bar_set.append([0.8, 0.3, 0.1, 2.0, 1.2, 0.5]) 
        bar_set.setBrush(QColor("#3b82f6"))
        
        series = QBarSeries()
        series.append(bar_set)
        chart.addSeries(series)
        
        categorias = ["Geladeira", "Ilum. Sala", "Roteador", "Ar Condic.", "Bomba D'água", "Computador"]
        axis_x = QBarCategoryAxis()
        axis_x.append(categorias)
        axis_x.setLabelsColor(QColor("#888888"))
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(0, 3.0)
        axis_y.setTitleText("kW")
        axis_y.setLabelsColor(QColor("#888888"))
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        chart.legend().setVisible(False)
        
        view = QChartView(chart)
        view.setRenderHint(QPainter.Antialiasing)
        view.setStyleSheet("border: 1px solid #2D2D2D; border-radius: 10px;")
        return view

    def configurar_tabela(self):
        self.tabela_historico.setColumnCount(5)
        self.tabela_historico.setHorizontalHeaderLabels([
            "Mês Referência", "Consumo Total (kWh)", "Custo Estimado", "Economia Gerada", "Status de Eficiência"
        ])
        
        dados = [
            ("Janeiro 2026", "450.5 kWh", "R$ 382,90", "R$ 45,20", "🟢 Excelente"),
            ("Fevereiro 2026", "480.2 kWh", "R$ 408,10", "R$ 32,10", "🔵 Estável"),
            ("Março 2026", "510.9 kWh", "R$ 434,25", "R$ 12,50", "🟡 Atenção"),
            ("Abril 2026", "430.1 kWh", "R$ 365,50", "R$ 55,80", "🟢 Excelente")
        ]
        
        self.tabela_historico.setRowCount(len(dados))
        for linha, row_data in enumerate(dados):
            for coluna, valor in enumerate(row_data):
                item = QTableWidgetItem(valor)
                item.setTextAlignment(Qt.AlignCenter)
                self.tabela_historico.setItem(linha, coluna, item)
        
        self.tabela_historico.setStyleSheet("""
            QTableWidget { background-color: #1A1A1A; border: 1px solid #2D2D2D; gridline-color: #2D2D2D; border-radius: 8px; color: #FFFFFF; }
            QHeaderView::section { background-color: #252525; color: #00E676; padding: 6px; font-weight: bold; border: 1px solid #2D2D2D; }
        """)
        self.tabela_historico.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def generar_leitura_sensores_ruido(self):
        """Simula a telemetria com ruído senoidal estável"""
        try:
            if self.consumo_base_atual > 0:
                ruido = random.uniform(-0.02, 0.02) * self.consumo_base_atual
                consumo_final = max(0.0, self.consumo_base_atual + ruido)
            else:
                consumo_final = random.uniform(0.01, 0.03)
                
            self.kpi_demanda.lbl_valor.setText(f"{consumo_final:.2f} <span style='font-size: 16px; color: #888888;'>kW</span>")
            
            self.contador_tempo += 1
            self.series_linha.append(self.contador_tempo, consumo_final)
            
            # Janela deslizante segura para o eixo X
            if self.contador_tempo >= 15:
                self.axis_x_linha.setRange(self.contador_tempo - 14, self.contador_tempo)
                if self.series_linha.count() > 30: # Limita o histórico na memória
                    self.series_linha.remove(0)
        except Exception as e:
            pass

    def atualizar_consumo_grafico(self, novo_consumo_total):
        self.consumo_base_atual = novo_consumo_total