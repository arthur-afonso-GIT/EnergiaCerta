import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class CanvasGraficoEnergia(FigureCanvas):
    def __init__(self, largura=5, altura=4, dpi=100):
        figura = Figure(figsize=(largura, altura), dpi=dpi, facecolor='#1E1E1E')
        self.eixos = figura.add_subplot(111)
        self.eixos.set_facecolor('#1E1E1E')
        super().__init__(figura)
        
    def atualizar_linhas(self, horas, consumo, geracao):
        """Redesenha o gráfico com os dados atuais"""
        self.eixos.clear()
        self.eixos.set_facecolor('#1E1E1E')
        
        self.eixos.plot(horas, consumo, color='#E53935', marker='o', linewidth=2, label='Consumo (kWh)')
        self.eixos.plot(horas, geracao, color='#4CAF50', marker='o', linewidth=2, label='Geração (kWh)')
        
        self.eixos.set_title("Histórico de Geração vs Consumo", color='white', fontsize=12, fontweight='bold', pad=10)
        self.eixos.tick_params(colors='white', labelsize=9)
        
        for spine in self.eixos.spines.values():
            spine.set_visible(False)
        self.eixos.grid(True, color='#333333', linestyle='--', linewidth=0.5)
        
        legenda = self.eixos.legend(facecolor='#1E1E1E', edgecolor='#333333', loc='upper right')
        for texto in legenda.get_texts():
            texto.set_color('white')
        self.draw()