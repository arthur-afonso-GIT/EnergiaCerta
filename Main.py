import sys
from PySide6.QtWidgets import QApplication

# 1. Imports estruturados do Core e do Dashboard principal
from Interface.dashboard import DashboardEnergia 
from Core import comunicacao_serial 

# 2. Importando as abas da pasta modular
from Interface.abas.aba_cargas import AbaCargas
from Interface.abas.aba_ia import AbaIA
from Interface.abas.aba_graficos import AbaGraficos

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 🔌 Conexão Serial (Arduino)
    arduino_serial = comunicacao_serial
    
    # ⚙ Inicializa o Dashboard base primeiro
    janela = DashboardEnergia()

    # ⚙ Instancia as abas passando as referências corretas
    tela_cargas = AbaCargas(arduino_serial=arduino_serial, dashboard_principal=janela)
    tela_ia = AbaIA()
    tela_graficos = AbaGraficos()
    
    # 🔄 MENSAGENS E LOGS DE SISTEMA OTIMIZADOS
    def sincronizar_mudanca_no_dashboard(nome_carga, esta_ativo, consumo_kw):
        status_simbolo = "🔌 [LIGADO]" if esta_ativo else "❌ [DESLIGADO]"
        print("="*60)
        print(f"🛰️  SISTEMA CENTRAL | MONITORAMENTO DE EVENTOS")
        print(f"   🔹 Dispositivo:  {nome_carga}")
        print(f"   🔹 Operação:     {status_simbolo}")
        print(f"   🔹 Impacto:      {consumo_kw:.2f} kW")
        print("="*60)
        
        # 1. Atualiza os dados da barra lateral no monitoramento geral
        if hasattr(janela, 'atualizar_status_carga_lateral'):
            janela.atualizar_status_carga_lateral(nome_carga, esta_ativo)
            
        # 2. Recalcula a potência total em execução de forma unificada e segura
        consumo_total = 0.0
        if hasattr(tela_cargas, 'lista_cards'):
            consumo_total = sum(card.consumo for card in tela_cargas.lista_cards if card.ativo)
            
            # Atualiza o mostrador numérico grande (0.0 kW) do topo direito
            for var_name in ['lbl_consumo_total', 'label_consumo', 'lbl_potencia', 'label_potencia', 'lbl_kw', 'lbl_consumo_atual']:
                if hasattr(janela, var_name):
                    lbl = getattr(janela, var_name)
                    lbl.setText(f"{consumo_total:.1f} kW")
                    break
                    
            # 📊 Alerta de Consumo Elevado no Terminal
            if consumo_total > 4.0:
                print(f"⚠️  [ALERTA DE PICOS] Consumo total atingiu {consumo_total:.1f} kW! Risco de sobrecarga.")
                print("="*60)

        # 3. Dispara mensagem na barra de status inferior se disponível
        if hasattr(janela, 'statusBar'):
            status_cor = "ativada" if esta_ativo else "desativada"
            janela.statusBar().showMessage(f"Aviso: Carga '{nome_carga}' foi {status_cor} com sucesso.", 4000)
                    
        # 📈 4. Atualiza o gráfico de tempo real com o valor correto e tratado
        if hasattr(tela_graficos, 'atualizar_consumo_grafico'):
            tela_graficos.atualizar_consumo_grafico(consumo_total)

    # 🔗 Conecta o sinal da aba de cargas à nossa regra de sincronização
    tela_cargas.carga_alterada.connect(sincronizar_mudanca_no_dashboard)
    
    try:
        janela.abas.addTab(tela_cargas, "⚙️ Cargas Críticas")
        janela.abas.addTab(tela_graficos, "📈 Gráficos de Desempenho")
        janela.abas.addTab(tela_ia, "🧠 Recomendações e IA")
        
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
        print("Aviso: Verifique a configuração do componente '.abas' dentro do seu DashboardEnergia.")

    janela.show()
    sys.exit(app.exec())