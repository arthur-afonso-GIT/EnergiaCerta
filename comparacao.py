from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class AbaComparacao(QWidget):
    def __init__(self, dashboard_principal):
        super().__init__()
        self.dashboard = dashboard_principal
        self.layout = QVBoxLayout()

        # Label de resultado
        self.lbl_resultado = QLabel("📊 Comparação não iniciada")
        self.layout.addWidget(self.lbl_resultado)

        # Gráfico embutido
        self.fig, self.ax = plt.subplots(figsize=(5,3))
        self.canvas = FigureCanvas(self.fig)
        self.layout.addWidget(self.canvas)

        self.setLayout(self.layout)

        # Dados fictícios de exemplo (você pode trocar por dados reais do dashboard)
        self.dados_antes = [120, 130, 125, 140, 135]
        self.dados_depois = [100, 110, 105, 115, 108]

        # Atualiza comparação inicial
        self.atualizar_comparacao()

    def atualizar_comparacao(self):
        media_antes = sum(self.dados_antes) / len(self.dados_antes)
        media_depois = sum(self.dados_depois) / len(self.dados_depois)
        reducao = ((media_antes - media_depois) / media_antes) * 100

        # Atualiza label
        self.lbl_resultado.setText(
            f"Antes: {media_antes:.2f} kW | Depois: {media_depois:.2f} kW | Redução: {reducao:.1f}%"
        )

        # Atualiza log no dashboard
        if hasattr(self.dashboard, 'adicionar_recomendacao_log'):
            self.dashboard.adicionar_recomendacao_log(
                f"📊 Comparação realizada: redução de {reducao:.1f}% no consumo."
            )

        # Atualiza gráfico
        self.ax.clear()
        self.ax.bar(["Antes", "Depois"], [media_antes, media_depois], color=["#FF9800", "#4CAF50"])
        self.ax.set_title("Comparação Antes vs Depois")
        self.ax.set_ylabel("Consumo Médio (kW)")
        self.canvas.draw()
