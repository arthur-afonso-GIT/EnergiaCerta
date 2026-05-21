import sys
from PySide6.QtWidgets import QApplication
from Interface.dashboard import DashboardEnergia 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = DashboardEnergia()
    
    janela.show()
    
    # --- DISPARANDO NOTIFICAÇÃO DE TESTE ---
    # Simulando um evento que virá do seu backend/Arduino no futuro!
    janela.notificar_alerta(
        "⚠️ Sistema Energia Certa", 
        "Dashboard integrado com sucesso! O sistema de avisos via Notify está ativo."
    )
    
    sys.exit(app.exec())