import sys
from PySide6.QtWidgets import QApplication

# 1. Imports estruturados do Core e do Dashboard principal
from Interface.dashboard import DashboardEnergia 
from Core import comunicacao_serial 

# 2. Importando as abas da pasta modular (Agora que a pasta está no local certo!)
from Interface.abas.aba_cargas import AbaCargas
from Interface.abas.aba_ia import AbaIA
from Interface.abas.aba_graficos import AbaGraficos

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 🔌 Conexão Serial (Arduino)
    arduino_serial = comunicacao_serial
    
    # 📊 Inicializa o Dashboard base (Interface Principal)
    janela = DashboardEnergia()
    
    # ⚙ Instancia as abas de forma independente
    tela_cargas = AbaCargas(arduino_serial=arduino_serial)
    tela_ia = AbaIA()
    tela_graficos = AbaGraficos()  # <-- Nova instância da aba de gráficos
    
    try:
        janela.abas.addTab(tela_cargas, "⚙️ Cargas Críticas")
        janela.abas.addTab(tela_graficos, "📈 Gráficos de Desempenho")
        janela.abas.addTab(tela_ia, "🧠 Recomendações e IA")
        
        # Folha de estilo CSS para a barra superior ficar moderna e linda
        janela.setStyleSheet("""
            QTabBar::tab {
                background: #1E1E1E;
                color: #888888;
                border: 1px solid #2D2D2D;
                padding: 10px 20px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #121212;
                color: #00E676;
                border-bottom: 2px solid #00E676;
            }
        """)
    except AttributeError:
        print("Erro: Verifique o atributo '.abas' no seu DashboardEnergia.")

    janela.show()
    sys.exit(app.exec())