import sys
import random
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QFrame, QProgressBar)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPen, QLinearGradient, QBrush
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis

class CardMetricaBateria(QFrame):
    """Componente premium para telemetria técnica de tensão, corrente e temperatura"""
    def __init__(self, titulo, valor, sufixo, cor_texto, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #1A1A1A;
                border: 1px solid #2D2D2D;
                border-radius: 8px;
            }
        """)
        self.setMinimumHeight(90)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(4)
        
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("color: #888888; font-size: 11px; font-weight: bold; letter-spacing: 0.5px; background: transparent;")
        
        # Referência global para atualização dinâmica pelo timer
        self.lbl_valor = QLabel(f"{valor} <span style='font-size: 13px; color: #666666;'>{sufixo}</span>")
        self.lbl_valor.setStyleSheet(f"color: {cor_texto}; font-size: 24px; font-weight: bold; background: transparent;")
        
        layout.addWidget(lbl_titulo)
        layout.addWidget(self.lbl_valor)

class AbaBaterias(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #121212; color: #FFFFFF;")
        
        # Variáveis de Simulação Química da Bateria (Efeito Arduino)
        self.soc_atual = 100.0  # Estado de Carga Inicial (Começa cheia como na sua imagem)
        self.contador_tempo = 0
        
        # Layout Principal
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(25, 25, 25, 25)
        layout_principal.setSpacing(20)
        
        # 1. CABEÇALHO DO PAINEL
        layout_header = QHBoxLayout()
        self.titulo = QLabel("🔋 Sistema de Armazenamento e Gerenciamento do Banco de Baterias (EMS)")
        self.titulo.setStyleSheet("font-size: 22px; font-weight: bold; color: #00E676; background: transparent;")
        layout_header.addWidget(self.titulo)
        layout_principal.addLayout(layout_header)
        
        # 2. SEÇÃO SUPERIOR: VISUALIZADOR DA CÉLULA E GRID DE MÉTRICAS
        layout_painel_superior = QHBoxLayout()
        layout_painel_superior.setSpacing(20)
        
        # Bloco Esquerdo: Indicador Químico Visual (Célula Grande)
        self.frame_bateria_visual = QFrame()
        self.frame_bateria_visual.setStyleSheet("background-color: #1A1A1A; border: 1px solid #2D2D2D; border-radius: 10px;")
        layout_visual = QVBoxLayout(self.frame_bateria_visual)
        layout_visual.setContentsMargins(20, 20, 20, 20)
        
        lbl_soc_titulo = QLabel("ESTADO DE CARGA (SoC)")
        lbl_soc_titulo.setStyleSheet("color: #888888; font-size: 11px; font-weight: bold; text-align: center;")
        layout_visual.addWidget(lbl_soc_titulo, alignment=Qt.AlignCenter)
        
        # Barra de Progresso estilizada como célula química
        self.bar_soc = QProgressBar()
        self.bar_soc.setRange(0, 100)
        self.bar_soc.setValue(int(self.soc_atual))
        self.bar_soc.setTextVisible(True)
        self.bar_soc.setAlignment(Qt.AlignCenter)
        self.atualizar_estilo_bateria(self.soc_atual)
        self.bar_soc.setMinimumHeight(50)
        layout_visual.addWidget(self.bar_soc)
        
        lbl_tipo = QLabel("Célula Lithium-Ion de 5.0 kWh operacional")
        lbl_tipo.setStyleSheet("color: #666666; font-size: 11px; text-align: center; font-style: italic; margin-top: 5px;")
        layout_visual.addWidget(lbl_tipo, alignment=Qt.AlignCenter)
        
        layout_painel_superior.addWidget(self.frame_bateria_visual, stretch=2)
        
        # Bloco Direito: Grid de Métricas Técnicas detalhadas
        layout_grid_metricas = QVBoxLayout()
        layout_grid_metricas.setSpacing(10)
        
        layout_linha1 = QHBoxLayout()
        # Métrica Financeira de Retorno (Azul, como na IA)
        self.metrica_economia = CardMetricaBateria("RETORNO ACUMULADO", "R$ 38,50", "/Mês", "#3b82f6")
        self.metrica_ciclos = CardMetricaBateria("CONTADOR DE CICLOS", "42", "ciclos", "#FFFFFF")
        layout_linha1.addWidget(self.metrica_economia)
        layout_linha1.addWidget(self.metrica_ciclos)
        
        layout_linha2 = QHBoxLayout()
        self.metrica_temperatura = CardMetricaBateria("TEMPERATURA DAS CÉLULAS", "26.4", "°C", "#FFD700")
        self.metrica_saude = CardMetricaBateria("SAÚDE DO BANCO (SoH)", "100.0", "%", "#00E676")
        layout_linha2.addWidget(self.metrica_temperatura)
        layout_linha2.addWidget(self.metrica_saude)
        
        layout_grid_metricas.addLayout(layout_linha1)
        layout_grid_metricas.addLayout(layout_linha2)
        
        layout_painel_superior.addLayout(layout_grid_metricas, stretch=3)
        layout_principal.addLayout(layout_painel_superior)
        
        # 3. SEÇÃO INFERIOR: GRÁFICO DE FLUXO DE POTÊNCIA BIDIRECIONAL EM WATTS
        self.chart_view_fluxo = self.criar_grafico_fluxo()
        layout_principal.addWidget(self.chart_view_fluxo, stretch=2)
        
        # 🕒 TIMER DE TELEMETRIA CONTÍNUA (Atualiza a cada 1 segundo simulando telemetria do Arduino SCT013)
        self.timer_bateria = QTimer(self)
        self.timer_bateria.timeout.connect(self.atualizar_telemetria_bateria)
        self.timer_bateria.start(1000)

    def criar_grafico_fluxo(self):
        """Cria um gráfico dinâmico centralizado no zero para mostrar carga vs descarga"""
        chart = QChart()
        chart.setTitle("📉 Histórico de Fluxo de Potência (watts)")
        chart.setTitleBrush(QColor("#FFFFFF"))
        chart.setBackgroundBrush(QColor("#1A1A1A"))
        chart.setAnimationOptions(QChart.NoAnimation) # Desativa animações para performance em tempo real
        
        # Série de fluxo (Watts: Positivos = Carregando, Negativos = Sustentando a casa)
        self.series_fluxo = QLineSeries()
        self.series_fluxo.setName("Fluxo Líquido (W)")
        self.series_fluxo.setColor(QColor("#3b82f6")) # Azul para combinar com o tema de fluxo
        self.series_fluxo.append(0, 0.0)
        chart.addSeries(self.series_fluxo)
        
        # Eixo X (Linha do Tempo)
        self.axis_x_fluxo = QValueAxis()
        self.axis_x_fluxo.setRange(0, 15)
        self.axis_x_fluxo.setTitleText("Segundos (Linha do Tempo Contínua)")
        self.axis_x_fluxo.setLabelFormat("%d s")
        self.axis_x_fluxo.setLabelsColor(QColor("#888888"))
        chart.addAxis(self.axis_x_fluxo, Qt.AlignBottom)
        self.series_fluxo.attachAxis(self.axis_x_fluxo)
        
        # Eixo Y (Potência: Positivos e Negativos)
        self.axis_y_fluxo = QValueAxis()
        self.axis_y_fluxo.setRange(-150, 250) # Ex: Sustentando até 150W de cargas ou carregando a 250W via solar
        self.axis_y_fluxo.setTitleText("Potência (Watts)")
        self.axis_y_fluxo.setLabelsColor(QColor("#888888"))
        chart.addAxis(self.axis_y_fluxo, Qt.AlignLeft)
        self.series_fluxo.attachAxis(self.axis_y_fluxo)
        
        chart.legend().setVisible(False)
        
        view = QChartView(chart)
        view.setRenderHint(QPainter.Antialiasing)
        view.setStyleSheet("border: 1px solid #2D2D2D; border-radius: 10px;")
        return view

    def atualizar_estilo_bateria(self, soc):
        """Muda a cor Neon da célula da bateria dinamicamente baseada no nível químico"""
        if soc > 50:
            cor_bateria = "#00E676"  # Verde Neon
        elif soc > 20:
            cor_bateria = "#FFD700"  # Amarelo/Ouro
        else:
            cor_bateria = "#EF4444"  # Vermelho Alerta
            
        self.bar_soc.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid #333333;
                border-radius: 8px;
                background-color: #101010;
                text-align: center;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 18px;
            }}
            QProgressBar::chunk {{
                background-color: {cor_bateria};
                border-radius: 5px;
            }}
        """)

    def atualizar_telemetria_bateria(self):
        """Simula flutuação química e elétrica em tempo real para o simulador"""
        try:
            # 1. Simula variação sutil no Estado de Carga (SoC) baseado em fluxo simulado
            fluxo_watts = random.uniform(-60, 100) # Simula flutuação entre carregando e sustentando
            
            # Converte Watts em alteração percentual química (simulação ultra-simplificada)
            # Watts / Voltagem = Amperes | Amperes / CapacidademAh * Tempo = dSoC
            # Usando fator fictício para simulação visual
            alteracao_soc = (fluxo_watts / 8000) 
            self.soc_atual += alteracao_soc
            self.soc_atual = max(0.0, min(100.0, self.soc_atual))
            
            self.bar_soc.setValue(int(self.soc_atual))
            self.atualizar_estilo_bateria(self.soc_atual)
            
            # 2. Atualiza os Displays Numéricos dos Cards
            tensao = 24.0 + (self.soc_atual * 0.02) + random.uniform(-0.05, 0.05)
            # Simula temperatura variando sutilmente baseada em carga/descarga
            temperatura = 26.0 + (abs(fluxo_watts) * 0.01) + random.uniform(-0.1, 0.1)
            
            # Corrigido bug de NameError e escopo de variável usando 'self.' nos cards técnicos
            self.metrica_temperatura.lbl_valor.setText(f"{temperatura:.1f} <span style='font-size: 13px; color: #666666;'>°C</span>")
            
            # 3. Atualiza o Gráfico de Linha do Tempo
            self.contador_tempo += 1
            self.series_fluxo.append(self.contador_tempo, fluxo_watts)
            
            # Janela deslizante segura para o eixo X (Efeito osciloscópio / Scroll running)
            if self.contador_tempo >= 15:
                self.axis_x_fluxo.setRange(self.contador_tempo - 14, self.contador_tempo)
                if self.series_fluxo.count() > 30: # Evita sobrecarga de memória
                    self.series_fluxo.remove(0)
        except Exception as e:
            pass