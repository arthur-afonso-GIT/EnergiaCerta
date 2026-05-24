from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
import inspect

class AbaGraficos(QWidget): # <-- Classe exata que o Main.py procura!
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        self.titulo = QLabel("📈 Gráficos de Desempenho em Tempo Real")
        self.titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #00E676; background: transparent;")
        layout.addWidget(self.titulo)
        
        self.grafico_widget = None
        try:
            from Interface.componentes import grafico_tempo_real
            from PySide6.QtWidgets import QWidget as QW
            
            # Procura dinamicamente a classe de gráfico para não dar erro de compilação
            classes = [obj for name, obj in inspect.getmembers(grafico_tempo_real, inspect.isclass) if issubclass(obj, QW)]
            if classes:
                self.grafico_widget = classes[0]()
                layout.addWidget(self.grafico_widget)
            else:
                self._erro_visual(layout, "Nenhuma classe visual encontrada em 'grafico_tempo_real.py'.")
        except Exception as e:
            self._erro_visual(layout, f"Aviso: Erro nas variáveis do gráfico ativo: {e}")
            
        self.setStyleSheet("background-color: #121212;")

    def _erro_visual(self, layout, msg):
        erro_box = QLabel(f"⚠ Monitoramento de Gráficos Indisponível.\nMotivo: {msg}")
        erro_box.setStyleSheet("color: #FF5252; background-color: #1A1A1A; border: 1px dashed #FF5252; border-radius: 6px; padding: 15px;")
        layout.addWidget(erro_box)