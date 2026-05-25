import sys
from PySide6.QtWidgets import QApplication

# 1. Imports estruturados do Core e do Dashboard principal
from Interface.dashboard import DashboardEnergia 
from Core import comunicacao_serial 

# 2. Importando as abas da pasta modular
from Interface.abas.aba_cargas import AbaCargas
from Interface.abas.aba_baterias import AbaBaterias  
from Interface.abas.aba_ia import AbaIA
from Interface.abas.aba_graficos import AbaGraficos

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 🔌 Conexão Serial (Arduino)
    arduino_serial = comunicacao_serial
    
    # ⚙️ Inicializa o Dashboard base primeiro
    janela = DashboardEnergia()

    # 🛑 RESOLVE O DUPLO BOTÃO: Remove a aba estática/velha gerada pelo dashboard.py
    if hasattr(janela, 'abas') and janela.abas.count() > 1:
        janela.abas.removeTab(1) 

    # ⚙️ Instancia as abas passando as referências corretas
    tela_cargas = AbaCargas(arduino_serial=arduino_serial, dashboard_principal=janela)
    tela_baterias = AbaBaterias()  
    tela_ia = AbaIA()
    tela_graficos = AbaGraficos()
    
    # 🧬 CRÍTICO: Resolve o erro do loop de simulação que procura 'aba_bateria' no dashboard!
    janela.aba_bateria = tela_baterias

    # 🧠 CONTROLE INTELIGENTE: VARIÁVEIS DE ESTADO DA IA
    janela.ciclos_em_defice = 0 
    janela.cargas_desligadas_pela_ia = [] 

    def executar_algoritmo_cortes_ia():
        """
        Analisa o fluxo energético em tempo real, gerencia a bateria,
        desliga cargas seletivas no défice e as religa na sobra de energia.
        """
        # 1. Captura Geração Solar dos Cards do Dashboard de forma segura
        geracao = 0.0
        if hasattr(janela, 'lbl_val_geracao'):
            try:
                geracao = float(janela.lbl_val_geracao.text().replace(" kW", "").strip())
            except ValueError:
                geracao = 0.0

        # 2. Captura o SOC (Carga) da Bateria de forma dinâmica
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

        # 3. Calcula Consumo Atual baseado na lista unificada de cargas da janela principal
        consumo = 0.0
        for nome_carga, info in janela.config_cargas.items():
            if info["ativo"]:
                consumo += info["potencia"]

        saldo = geracao - consumo
        meta_limite = janela.sld_meta_consumo.value() / 10.0  # Captura o slider dinâmico do dashboard

        # --- [CORREÇÃO] LÓGICA DE CORTES (DÉFICE ENERGÉTICO / SOL SUMIU / META EXCEDIDA) ---
        if saldo < 0 or consumo > meta_limite or soc_bateria < 30.0:
            janela.ciclos_em_defice += 1
            
            # Atualização visual do status do painel informativo lateral direito
            if hasattr(janela, 'lbl_bateria_status'):
                if soc_bateria <= 30.0:
                    janela.lbl_bateria_status.setText(f"⚠️ Bateria Crítica ({soc_bateria:.1f}%)! Cortando Cargas...")
                    janela.lbl_bateria_status.setStyleSheet("font-size: 11px; color: #E53935; font-weight: bold; border: none;")
                else:
                    janela.lbl_bateria_status.setText(f"⚠️ Défice Detectado! Geração: {geracao:.1f}kW")
                    janela.lbl_bateria_status.setStyleSheet("font-size: 11px; color: #FF9800; font-weight: bold; border: none;")

            # Histerese: Se houver instabilidade confirmada (2 ciclos = 4 segundos), executa o corte de cargas seletivas
            if janela.ciclos_em_defice >= 2:
                # Prioridade de corte: Das mais pesadas/menos críticas para as mais leves
                ordem_corte = ["Ar-Condicionado", "Bomba D'água", "Computador"]
                
                for nome_alvo in ordem_corte:
                    if nome_alvo in janela.config_cargas and janela.config_cargas[nome_alvo]["ativo"]:
                        # Ignora o corte se a carga for marcada manualmente como CRÍTICA via menu de contexto
                        if janela.config_cargas[nome_alvo].get("critica", False):
                            continue
                            
                        print(f"[IA - AUTOMÁTICO] Cortando dispositivo: {nome_alvo} ({janela.config_cargas[nome_alvo]['potencia']}kW)")
                        
                        # Altera estado no banco de dados centralizado
                        janela.config_cargas[nome_alvo]["ativo"] = False
                        if nome_alvo not in janela.cargas_desligadas_pela_ia:
                            janela.cargas_desligadas_pela_ia.append(nome_alvo)
                        
                        # Atualiza visualmente o botão do Dashboard (fica Vermelho)
                        janela.atualizar_visual_botao(nome_alvo)
                        janela.adicionar_recomendacao_log(f"🚨 IA: Desligamento automático de '{nome_alvo}' para sanar défice de {abs(saldo):.2f} kW.")
                        
                        # Altera o estado na aba secundária de cargas para sincronizar as duas telas
                        if hasattr(tela_cargas, 'atualizar_interface_externa'):
                            tela_cargas.atualizar_interface_externa(nome_alvo, False)
                        elif hasattr(tela_cargas, 'config_cargas') and nome_alvo in tela_cargas.config_cargas:
                            tela_cargas.config_cargas[nome_alvo]["ativo"] = False
                        
                        # Dispara a sincronização de KPIs gerais (recalcula consumo total e plota gráficos)
                        sincronizar_mudanca_no_dashboard(nome_alvo, False, janela.config_cargas[nome_alvo]["potencia"])
                        
                        # Recalcula o saldo temporário após o corte para checar se o sistema estabilizou
                        saldo += janela.config_cargas[nome_alvo]["potencia"]
                        if saldo >= 0 and (consumo - janela.config_cargas[nome_alvo]["potencia"]) <= meta_limite:
                            janela.ciclos_em_defice = 0
                            return
        
        # --- LÓGICA DE RELIGAMENTO INTELIGENTE (SOBRA REAL COM HISTERESE DE SEGURANÇA) ---
        elif saldo > 0 and len(janela.cargas_desligadas_pela_ia) > 0 and soc_bateria > 40.0:
            janela.ciclos_em_defice = 0
            
            if hasattr(janela, 'lbl_bateria_status'):
                janela.lbl_bateria_status.setText("🔋 Sistema Normalizado: Sobra Solar")
                janela.lbl_bateria_status.setStyleSheet("font-size: 11px; color: #4CAF50; font-weight: bold; border: none;")

            # Ordem inversa de retorno (Mais leves voltam primeiro)
            ordem_religamento = ["Computador", "Bomba D'água", "Ar-Condicionado"]
            
            for nome_alvo in ordem_religamento:
                if nome_alvo in janela.cargas_desligadas_pela_ia:
                    if nome_alvo in janela.config_cargas and not janela.config_cargas[nome_alvo]["ativo"]:
                        potencia_carga = janela.config_cargas[nome_alvo]["potencia"]
                        
                        # Trava de Segurança: Só religa se a sobra atual cobrir a carga + uma margem de folga de 0.3kW
                        if saldo > (potencia_carga + 0.3) and (consumo + potencia_carga) <= meta_limite:
                            print(f"[IA - AUTOMÁTICO] Sobrou energia ({saldo:.2f}kW). Religando: {nome_alvo}")
                            
                            janela.config_cargas[nome_alvo]["ativo"] = True
                            janela.cargas_desligadas_pela_ia.remove(nome_alvo)
                            
                            # Atualiza visual do botão do dashboard e joga no terminal de logs
                            janela.atualizar_visual_botao(nome_alvo)
                            janela.adicionar_recomendacao_log(f"💡 IA: Restabelecendo '{nome_alvo}'. Geração solar estabilizada.")
                            
                            # Sincroniza estado visual com a aba secundária de cargas
                            if hasattr(tela_cargas, 'atualizar_interface_externa'):
                                tela_cargas.atualizar_interface_externa(nome_alvo, True)
                            elif hasattr(tela_cargas, 'config_cargas') and nome_alvo in tela_cargas.config_cargas:
                                tela_cargas.config_cargas[nome_alvo]["ativo"] = True
                            
                            sincronizar_mudanca_no_dashboard(nome_alvo, True, potencia_carga)
                            return


    # 🔄 MENSAGENS E LOGS DE SISTEMA OTIMIZADOS (SEM CRASH)
    def sincronizar_mudanca_no_dashboard(nome_carga, esta_ativo, consumo_kw):
        status_simbolo = "🔌 [LIGADO]" if esta_ativo else "❌ [DESLIGADO]"
        print("="*60)
        print(f"🛰️  SISTEMA CENTRAL | MONITORAMENTO DE EVENTOS")
        print(f"   🔹 Dispositivo:  {nome_carga}")
        print(f"   🔹 Operação:     {status_simbolo}")
        print(f"   🔹 Impacto:      {consumo_kw:.2f} kW")
        print("="*60)
        
        # 1. Atualiza os dados da barra lateral esquerda no monitoramento geral
        if hasattr(janela, 'atualizar_status_carga_lateral'):
            janela.atualizar_status_carga_lateral(nome_carga, esta_ativo)
            
        # 2. Recalcula o consumo total baseado no dicionário real unificado
        consumo_total = sum(info["potencia"] for info in janela.config_cargas.values() if info["ativo"])
            
        # 🟢 ATUALIZAÇÃO DO CONSUMO ATUAL (TELA INICIAL) NOS VALORES KPI DO DASHBOARD
        if hasattr(janela, 'lbl_val_consumo'):
            janela.lbl_val_consumo.setText(f"{consumo_total:.1f} kW")
            
        # Atualiza o saldo/balanço também na tela principal
        if hasattr(janela, 'lbl_val_saldo') and hasattr(janela, 'lbl_val_geracao'):
            try:
                geraca_atual = float(janela.lbl_val_geracao.text().replace(" kW", "").strip())
                balanco = geraca_atual - consumo_total
                janela.lbl_val_saldo.setText(f"{balanco:.1f} kW")
            except ValueError:
                pass
                
        if consumo_total > 4.0:
            print(f"⚠️  [ALERTA DE PICOS] Consumo total atingiu {consumo_total:.1f} kW! Risco de sobrecarga.")
            print("="*60)

        # 3. Dispara mensagem na barra de status inferior se disponível
        if hasattr(janela, 'statusBar') and janela.statusBar():
            status_cor = "ativada" if esta_ativo else "desativada"
            janela.statusBar().showMessage(f"Aviso: Carga '{nome_carga}' foi {status_cor} com sucesso.", 4000)
                    
        # 📈 4. ATUALIZAÇÃO DO GRÁFICO DE DESEMPENHO
        if hasattr(tela_graficos, 'atualizar_consumo_grafico'):
            tela_graficos.atualizar_consumo_grafico(consumo_total)


    # 🔗 Conecta o sinal emissor da aba de cargas à nossa regra corrigida
    if hasattr(tela_cargas, 'carga_alterada'):
        tela_cargas.carga_alterada.connect(sincronizar_mudanca_no_dashboard)
    
    # 🔌 INJEÇÃO NO TIMER DO DASHBOARD
    # Sempre que o timer de 2 segundos do dashboard.py bater, ele executa a IA de corte
    janela.timer.timeout.connect(executar_algoritmo_cortes_ia)

    try:
        # Injeta as abas no gerenciador visual
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
        print("Aviso: Verifique a configuração do componente '.abas' dentro do seu DashboardEnergia.")

    janela.show()
    sys.exit(app.exec())