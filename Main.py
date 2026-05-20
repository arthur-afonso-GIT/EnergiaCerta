# main.py
import sys
from PySide6.QtWidgets import QApplication

from Interface.dashboard import DashboardEnergia

def acao_ao_clicar():
    print("O botão da interface foi clicado! Executando lógica no main.py...")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    janela = DashboardEnergia()
    
    
    janela.show()
    sys.exit(app.exec())