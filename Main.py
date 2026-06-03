import sys
from PySide6.QtWidgets import QApplication

from Interface.dashboard import DashboardEnergia 
from Core import comunicacao_serial 
# 💾 Importação das funções do banco de dados (Cargas + Histórico de Energia)
from Core.banco_dados import carregar_dados, salvar_dados, registrar_historico_energia
from Interface.abas.aba_cargas import AbaCargas
from Interface.abas.aba_baterias import AbaBaterias  
from Interface.abas.aba_ia import AbaIA
from Interface.abas.aba_graficos import AbaGraficos

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    arduino_serial = comunicacao_serial
    
    janela = DashboardEnergia()
    janela.config_cargas = carregar_dados()
    
    if hasattr(janela, 'abas') and janela.abas.count() > 1:
        janela.abas.removeTab(1) 

    tela_cargas = AbaCargas(arduino_serial=arduino_serial, dashboard_principal=janela)
    tela_baterias = AbaBaterias()  
    tela_ia = AbaIA()
    tela_graficos = AbaGraficos()
    
    janela.aba_bateria = tela_baterias
    
    janela.ciclos_em_defice = 0 
    janela.cargas_desligadas_pela_ia = [] 

    def executar_algoritmo_cortes_ia():
        """Gerencia cortes inteligentes de cargas com base em prioridades."""
        
        geracao = 0.0
        if hasattr(janela, 'lbl_val_geracao'):
            try:
                geracao = float(janela.lbl_val_geracao.text().replace(" kW", "").strip())
            except ValueError:
                geracao = 0.0

        soc_bateria = 100.0
        if hasattr(tela_baterias, 'lbl_soc_valor'): 
            try:
                soc_bateria = float(tela_baterias.lbl_soc_valor.text().replace("%", "").strip())
            except ValueError:
                pass
        elif hasattr(janela, 'lbl_bateria_status'):
            try:
                txt_bat = janela.lbl_bateria_status.text()
                if "%" in txt_bat:
                    soc_bateria = float(txt_bat.split("%")[0].strip().split()[-1])
            except Exception:
                pass

        consumo = 0.0
        for nome_carga, info in janela.config_cargas.items():
            if info["ativo"]:
                consumo += info["potencia"]
                
        saldo = geracao - consumo
        meta_limite = janela.sld_meta_consumo.value() / 10.0

        # 📊 NOVO: Salva os dados de geração e consumo no banco histórico JSON a cada ciclo
        registrar_historico_energia(geracao, consumo)

        if saldo < 0 or consumo > meta_limite or soc_bateria < 30.0:
            janela.ciclos_em_defice += 1
            
            if hasattr(janela, 'lbl_bateria_status'):
                if soc_bateria <= 30.0:
                    janela.lbl_bateria_status.setText(f"Bateria Crítica ({soc_bateria:.1f}%)! Cortando Cargas...")
                    janela.lbl_bateria_status.setStyleSheet("font-size: 11px; color: #E53935; font-weight: bold; border: none;")
                else:
                    janela.lbl_bateria_status.setText(f"Défice Detectado! Geração: {geracao:.1f}kW")
                    janela.lbl_bateria_status.setStyleSheet("font-size: 11px; color: #FF9800; font-weight: bold; border: none;")

            if janela.ciclos_em_defice >= 2:
                cargas_para_cortar = [
                    (nome, info) for nome, info in janela.config_cargas.items()
                    if not info.get("critica", False) and info.get("ativo", True)
                ]
                
                if cargas_para_cortar:
                    cargas_para_cortar.sort(key=lambda x: (x[1].get("prioridade", 1), x[1]["potencia"]))
                    
                    nome_alvo, info_alvo = cargas_para_cortar[0]
                    potencia_carga = info_alvo["potencia"]
                    prio_atual = info_alvo.get("prioridade", 1)
                    
                    print(f"[IA] Cortando dispositivo: {nome_alvo} ({potencia_carga}kW)")
                    
                    janela.config_cargas[nome_alvo]["ativo"] = False
                    if nome_alvo not in janela.cargas_desligadas_pela_ia:
                        janela.cargas_desligadas_pela_ia.append(nome_alvo)
                    
                    # 💾 Salva o estado da carga imediatamente após o corte
                    salvar_dados(janela.config_cargas)
                    
                    janela.atualizar_visual_botao(nome_alvo)
                    janela.adicionar_recomendacao_log(f"IA: Desligamento automático de '{nome_alvo}' (Prioridade {prio_atual}).")
                    
                    if hasattr(tela_cargas, 'atualizar_interface_externa'):
                        tela_cargas.atualizar_interface_externa(nome_alvo, False)
                    elif hasattr(tela_cargas, 'config_cargas') and nome_alvo in tela_cargas.config_cargas:
                        tela_cargas.config_cargas[nome_alvo]["ativo"] = False
                    
                    sincronizar_mudanca_no_dashboard(nome_alvo, False, potencia_carga)
                    
                    saldo += potencia_carga
                    if saldo >= 0 and (consumo - potencia_carga) <= meta_limite:
                        janela.ciclos_em_defice = 0
                        return

        elif saldo > 0 and len(janela.cargas_desligadas_pela_ia) > 0 and soc_bateria > 40.0:
            janela.ciclos_em_defice = 0
            
            if hasattr(janela, 'lbl_bateria_status'):
                janela.lbl_bateria_status.setText("Sistema Normalizado: Sobra Solar")
                janela.lbl_bateria_status.setStyleSheet("font-size: 11px; color: #4CAF50; font-weight: bold; border: none;")

            cargas_para_religar = [
                (nome, janela.config_cargas[nome]) for nome in janela.cargas_desligadas_pela_ia
                if nome in janela.config_cargas and not janela.config_cargas[nome]["ativo"]
            ]
            
            if cargas_para_religar:
                cargas_para_religar.sort(key=lambda x: x[1].get("prioridade", 1))
                
                for nome_alvo, info_alvo in cargas_para_religar:
                    potencia_carga = info_alvo["potencia"]
                    prio_atual = info_alvo.get("prioridade", 1)
                    
                    if saldo > (potencia_carga + 0.3) and (consumo + potencia_carga) <= meta_limite:
                        print(f"[IA] Religando dispositivo: {nome_alvo}")
                        
                        janela.config_cargas[nome_alvo]["ativo"] = True
                        janela.cargas_desligadas_pela_ia.remove(nome_alvo)
                        
                        # 💾 Salva o estado da carga imediatamente após religar
                        salvar_dados(janela.config_cargas)
                        
                        janela.atualizar_visual_botao(nome_alvo)
                        janela.adicionar_recomendacao_log(f"IA: Restabelecendo '{nome_alvo}'.")
                        
                        if hasattr(tela_cargas, 'atualizar_interface_externa'):
                            tela_cargas.atualizar_interface_externa(nome_alvo, True)
                        elif hasattr(tela_cargas, 'config_cargas') and nome_alvo in tela_cargas.config_cargas:
                            tela_cargas.config_cargas[nome_alvo]["ativo"] = True
                        
                        sincronizar_mudanca_no_dashboard(nome_alvo, True, potencia_carga)
                        return


    def sincronizar_mudanca_no_dashboard(nome_carga, esta_ativo, consumo_kw):
        status_simbolo = "[LIGADO]" if esta_ativo else "[DESLIGADO]"
        print("="*60)
        print(f"SISTEMA CENTRAL | MONITORAMENTO")
        print(f"   Dispositivo: {nome_carga}")
        print(f"   Operação: {status_simbolo}")
        print(f"   Impacto: {consumo_kw:.2f} kW")
        print("="*60)
        
        if hasattr(janela, 'atualizar_status_carga_lateral'):
            janela.atualizar_status_carga_lateral(nome_carga, esta_ativo)
            
        consumo_total = sum(info["potencia"] for info in janela.config_cargas.values() if info["ativo"])
            
        if hasattr(janela, 'lbl_val_consumo'):
            janela.lbl_val_consumo.setText(f"{consumo_total:.1f} kW")
            
        if hasattr(janela, 'lbl_val_saldo') and hasattr(janela, 'lbl_val_geracao'):
            try:
                geraca_atual = float(janela.lbl_val_geracao.text().replace(" kW", "").strip())
                balanco = geraca_atual - consumo_total
                janela.lbl_val_saldo.setText(f"{balanco:.1f} kW")
            except ValueError:
                pass
                
        if consumo_total > 4.0:
            print(f"ALERTA DE PICOS: Consumo total atingiu {consumo_total:.1f} kW!")
            print("="*60)

        if hasattr(janela, 'statusBar') and janela.statusBar():
            status_cor = "ativada" if esta_ativo else "desativada"
            janela.statusBar().showMessage(f"Carga '{nome_carga}' foi {status_cor}.", 4000)
                    
        if hasattr(tela_graficos, 'atualizar_consumo_grafico'):
            tela_graficos.atualizar_consumo_grafico(consumo_total)


    if hasattr(tela_cargas, 'carga_alterada'):
        tela_cargas.carga_alterada.connect(sincronizar_mudanca_no_dashboard)
    
    janela.timer.timeout.connect(executar_algoritmo_cortes_ia)

    try:
        janela.abas.addTab(tela_cargas, "⚙️ Cargas Críticas")
        janela.abas.addTab(tela_baterias, "🔋 Banco de Baterias")  
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
        print("Erro: Verifique a configuração do componente '.abas'.")

    janela.show()
    sys.exit(app.exec())