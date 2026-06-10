import sys
import os
import math
import random
import re  # 💡 Essencial para extrair os números dos displays sem dar erro de texto
from PySide6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout,
                                QLabel, QLineEdit, QPushButton, QDoubleSpinBox,
                                QCheckBox, QComboBox, QFormLayout)
from PySide6.QtCore import Qt, QTimer

from Interface.dashboard import DashboardEnergia 
from Core.comunicacao_serial import MonitorConexaoArduino
from Core.banco_dados import carregar_dados, salvar_dados, registrar_historico_energia
from Interface.abas.aba_cargas import AbaCargas
from Interface.abas.aba_baterias import AbaBaterias  
from Interface.abas.aba_ia import AbaIA
from Interface.abas.aba_graficos import AbaGraficos


class PopupNovaCargarArduino(QDialog):
    """
    Popup que aparece quando o Arduino conecta.
    Permite nomear a carga física detectada e configurar prioridade.
    """
    def __init__(self, corrente_kw, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔌 Arduino Detectado!")
        self.setFixedWidth(380)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setStyleSheet("""
            QDialog { background-color: #1A1A1A; color: white; }
            QLabel { color: #FFFFFF; font-size: 12px; }
            QLineEdit, QDoubleSpinBox, QComboBox {
                background-color: #252525; border: 1px solid #444; padding: 6px;
                color: white; border-radius: 4px; font-size: 12px;
            }
            QCheckBox { color: #B0BEC5; font-size: 11px; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        lbl_titulo = QLabel("⚡ Arduino conectado!")
        lbl_titulo.setStyleSheet("font-size: 15px; font-weight: bold; color: #00E676;")
        layout.addWidget(lbl_titulo)

        lbl_sub = QLabel(
            f"Corrente detectada: <b style='color:#00E676'>{corrente_kw:.3f} kW</b><br>"
            "Configure a carga física abaixo para adicioná-la ao sistema."
        )
        lbl_sub.setWordWrap(True)
        lbl_sub.setStyleSheet("color: #AAAAAA; font-size: 11px;")
        layout.addWidget(lbl_sub)

        form = QFormLayout()
        form.setSpacing(10)

        self.txt_nome = QLineEdit()
        self.txt_nome.setText("Carga Arduino")
        form.addRow("Nome da carga:", self.txt_nome)

        self.spin_potencia = QDoubleSpinBox()
        self.spin_potencia.setRange(0.001, 50.0)
        self.spin_potencia.setDecimals(3)
        self.spin_potencia.setSuffix(" kW")
        self.spin_potencia.setValue(round(corrente_kw, 3))
        form.addRow("Potência inicial:", self.spin_potencia)

        self.chk_critica = QCheckBox("Imune a cortes automáticos (Crítica)")
        form.addRow("Tipo:", self.chk_critica)

        self.combo_prio = QComboBox()
        self.combo_prio.addItems(["1 – Cai Primeiro", "2 – Média", "3 – Cai por Último"])
        self.chk_critica.toggled.connect(lambda c: self.combo_prio.setDisabled(c))
        form.addRow("Prioridade IA:", self.combo_prio)

        layout.addLayout(form)

        layout_btns = QHBoxLayout()
        self.btn_cancelar = QPushButton("Ignorar")
        self.btn_cancelar.setStyleSheet(
            "QPushButton { background:#2D2D2D; color:#888; border:1px solid #444; padding:8px 16px; border-radius:4px; }"
        )
        self.btn_cancelar.clicked.connect(self.reject)

        self.btn_adicionar = QPushButton("➕ Adicionar ao Sistema")
        self.btn_adicionar.setStyleSheet(
            "QPushButton { background:#00E676; color:#121212; font-weight:bold; padding:8px 16px; border-radius:4px; border:none; }"
        )
        self.btn_adicionar.clicked.connect(self.accept)
        layout_btns.addWidget(self.btn_cancelar)
        layout_btns.addWidget(self.btn_adicionar)
        layout.addLayout(layout_btns)

    def obtener_dados(self):
        return (
            self.txt_nome.text().strip() or "Carga Arduino",
            self.spin_potencia.value(),
            self.combo_prio.currentIndex() + 1,
            self.chk_critica.isChecked()
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    monitor_arduino = MonitorConexaoArduino(porta="COM3", baudrate=9600)

    janela = DashboardEnergia()
    janela.config_cargas = carregar_dados()
    janela.monitor_arduino = monitor_arduino

    if hasattr(janela, 'abas') and janela.abas.count() > 1:
        janela.abas.removeTab(1)

    tela_cargas = AbaCargas(arduino_serial=monitor_arduino, dashboard_principal=janela)
    tela_baterias = AbaBaterias()
    tela_ia = AbaIA()
    tela_graficos = AbaGraficos()

    janela.aba_bateria = tela_baterias
    janela.ciclos_em_defice = 0
    janela.cargas_desligadas_pela_ia = []
    janela.nome_carga_arduino = None

    def ao_arduino_conectar(corrente_kw):
        popup = PopupNovaCargarArduino(corrente_kw, parent=janela)
        if popup.exec() == QDialog.Accepted:
            nome, potencia, prioridade, eh_critica = popup.obter_dados()

            if janela.nome_carga_arduino and janela.nome_carga_arduino in janela.config_cargas:
                btn_antigo = janela.config_cargas[janela.nome_carga_arduino].get("btn")
                if btn_antigo:
                    janela.layout_cargas.removeWidget(btn_antigo)
                    btn_antigo.deleteLater()
                del janela.config_cargas[janela.nome_carga_arduino]

            nome_final = nome
            contador = 2
            while nome_final in janela.config_cargas:
                nome_final = f"{nome} ({contador})"
                contador += 1

            janela.config_cargas[nome_final] = {
                "critica": eh_critica,
                "potencia": potencia,
                "ativo": True,
                "btn": None,
                "prioridade": prioridade,
                "arduino": True
            }
            janela.nome_carga_arduino = nome_final

            janela.criar_e_adicionar_botao_na_tela(nome_final)
            salvar_dados(janela.config_cargas)
            
            if hasattr(tela_cargas, 'sincronizar_com_monitoramento_geral'):
                tela_cargas.sincronizar_com_monitoramento_geral()

    monitor_arduino.arduino_conectado.connect(ao_arduino_conectar)

    # ------------------------------------------------------------------
    # ⚡ ALGORITMO DE CORTES E RECALCULO DE CONSUMO DO DASHBOARD
    # ------------------------------------------------------------------
    def executar_algoritmo_cortes_ia():
        # 1. Captura a Geração Solar limpando qualquer texto ("kW" ou "kWh")
        geracao = 0.0
        if hasattr(janela, 'lbl_val_geracao'):
            try:
                texto_geracao = janela.lbl_val_geracao.text()
                numeros_encontrados = re.findall(r"[-+]?\d*\.\d+|\d+", texto_geracao)
                if numeros_encontrados:
                    geracao = float(numeros_encontrados[0])
            except Exception:
                geracao = 0.0

        # 2. Captura o SoC da Bateria
        soc_bateria = 100.0
        if hasattr(tela_baterias, 'soc_atual') and tela_baterias.soc_atual is not None:
            try:
                soc_bateria = float(tela_baterias.soc_atual)
            except ValueError:
                pass

        # 3. SOMA REAL DO CONSUMO DIRETAMENTE DO BACKEND
        consumo_aparelhos = 0.0
        for nome_carga, info in janela.config_cargas.items():
            if info.get("ativo", False):
                consumo_aparelhos += info.get("potencia", 0.0)
        
        consumo = consumo_aparelhos + 0.2  # Consumo mínimo residencial fixo
        saldo = geracao - consumo
        
        # Captura o limite definido no Slider de Metas
        meta_limite = janela.sld_meta_consumo.value() / 10.0
        if meta_limite == 0:  
            meta_limite = 99.0

        # 4. 🚀 CORREÇÃO CRÍTICA: FORÇA A EXIBIÇÃO EM AMBOS OS FORMATOS (kW / kWh)
        # Identifica dinamicamente o sufixo original da tela para não quebrar o layout
        sufixo = " kWh" if hasattr(janela, 'lbl_val_consumo') and "kWh" in janela.lbl_val_consumo.text() else " kW"

        if hasattr(janela, 'lbl_val_consumo'):
            janela.lbl_val_consumo.setText(f"{consumo:.1f}{sufixo}")

        if hasattr(janela, 'lbl_val_saldo'):
            sinal = "+" if saldo >= 0 else ""
            janela.lbl_val_saldo.setText(f"{sinal}{saldo:.1f}{sufixo}")
            if saldo >= 0:
                janela.lbl_val_saldo.setStyleSheet("color: #00E676; font-size: 24px; font-weight: bold; border: none;")
            else:
                janela.lbl_val_saldo.setStyleSheet("color: #FF5252; font-size: 24px; font-weight: bold; border: none;")

        registrar_historico_energia(geracao, consumo)

        # 5. LÓGICA DE DETECÇÃO DE SOBRECARGA E AGUARDO DE SEGURANÇA
        condicao_saldo_negativo = (saldo < 0)
        condicao_meta_estourada = (consumo > meta_limite)
        condicao_bateria_critica = (soc_bateria < 30.0)

        if condicao_saldo_negativo or condicao_meta_estourada or condicao_bateria_critica:
            janela.ciclos_em_defice += 1

            print(f"[IA MONITOR] Sobrecarga ativa! Consumo: {consumo:.1f}kW | Limite: {meta_limite:.1f}kW | Ciclo: {janela.ciclos_em_defice}/2")

            if janela.ciclos_em_defice >= 2:
                cargas_para_cortar = [
                    (nome, info) for nome, info in janela.config_cargas.items()
                    if not info.get("critica", False) and info.get("ativo", True)
                ]

                if cargas_para_cortar:
                    cargas_para_cortar.sort(key=lambda x: (x[1].get("prioridade", 1), x[1]["potencia"]))
                    nome_alvo, info_alvo = cargas_para_cortar[0]
                    potencia_carga = info_alvo["potencia"]

                    print(f"⚠️ [IA CORTE] Executando desligamento por sobrecarga: {nome_alvo} ({potencia_carga}kW)")

                    janela.config_cargas[nome_alvo]["ativo"] = False
                    if nome_alvo not in janela.cargas_desligadas_pela_ia:
                        janela.cargas_desligadas_pela_ia.append(nome_alvo)

                    salvar_dados(janela.config_cargas)
                    janela.atualizar_visual_botao(nome_alvo)
                    
                    if hasattr(tela_cargas, 'atualizar_interface_externa'):
                        tela_cargas.atualizar_interface_externa(nome_alvo, False)

                    sincronizar_mudanca_no_dashboard(nome_alvo, False, potencia_carga)
                    janela.ciclos_em_defice = 0
        else:
            if janela.ciclos_em_defice > 0:
                janela.ciclos_em_defice = 0

            # Lógica para religar se houver folga energética estável
            if saldo > 0.3 and len(janela.cargas_desligadas_pela_ia) > 0 and soc_bateria > 40.0:
                cargas_para_religar = [
                    (nome, janela.config_cargas[nome]) for nome in janela.cargas_desligadas_pela_ia
                    if nome in janela.config_cargas and not janela.config_cargas[nome]["ativo"]
                ]

                if cargas_para_religar:
                    cargas_para_religar.sort(key=lambda x: x[1].get("prioridade", 1))
                    for nome_alvo, info_alvo in cargas_para_religar:
                        potencia_carga = info_alvo["potencia"]

                        if saldo > (potencia_carga + 0.4) and (consumo + potencia_carga) <= meta_limite:
                            print(f"✅ [IA RELIGA] Restabelecendo dispositivo: {nome_alvo}")
                            janela.config_cargas[nome_alvo]["ativo"] = True
                            janela.cargas_desligadas_pela_ia.remove(nome_alvo)

                            salvar_dados(janela.config_cargas)
                            janela.atualizar_visual_botao(nome_alvo)

                            if hasattr(tela_cargas, 'atualizar_interface_externa'):
                                tela_cargas.atualizar_interface_externa(nome_alvo, True)

                            sincronizar_mudanca_no_dashboard(nome_alvo, True, potencia_carga)
                            return


    # ------------------------------------------------------------------
    # 🔄 SINCRONIZAÇÃO EM TEMPO REAL: CLIQUE DO BOTÃO -> INTERFACE
    # ------------------------------------------------------------------
    def sincronizar_mudanca_no_dashboard(nome_carga, esta_ativo, consumo_kw):
        if nome_carga in janela.config_cargas:
            janela.config_cargas[nome_carga]["ativo"] = esta_ativo
            salvar_dados(janela.config_cargas)

        if hasattr(janela, 'atualizar_status_carga_lateral'):
            janela.atualizar_status_carga_lateral(nome_carga, esta_ativo)

        # Recalcula o consumo consolidado instantaneamente
        consumo_total = sum(info["potencia"] for info in janela.config_cargas.values() if info.get("ativo", False)) + 0.2
        
        sufixo = " kWh" if hasattr(janela, 'lbl_val_consumo') and "kWh" in janela.lbl_val_consumo.text() else " kW"

        if hasattr(janela, 'lbl_val_consumo'):
            janela.lbl_val_consumo.setText(f"{consumo_total:.1f}{sufixo}")

        if hasattr(janela, 'lbl_val_saldo') and hasattr(janela, 'lbl_val_geracao'):
            try:
                texto_geracao = janela.lbl_val_geracao.text()
                numeros_encontrados = re.findall(r"[-+]?\d*\.\d+|\d+", texto_geracao)
                geracao_atual = float(numeros_encontrados[0]) if numeros_encontrados else 0.0
                
                balanco = geracao_atual - consumo_total
                sinal = "+" if balanco >= 0 else ""
                janela.lbl_val_saldo.setText(f"{sinal}{balanco:.1f}{sufixo}")
                
                if balanco >= 0:
                    janela.lbl_val_saldo.setStyleSheet("color: #00E676; font-size: 24px; font-weight: bold; border: none;")
                else:
                    janela.lbl_val_saldo.setStyleSheet("color: #FF5252; font-size: 24px; font-weight: bold; border: none;")
            except Exception:
                pass

        # Força o gráfico na aba de desempenho a plotar o novo valor na hora
        if hasattr(tela_graficos, 'atualizar_consumo_grafico'):
            tela_graficos.atualizar_consumo_grafico(consumo_total)

    # Vincula o evento de mudança das abas secundárias de volta para a Main
    if hasattr(tela_cargas, 'carga_alterada'):
        try:
            tela_cargas.carga_alterada.disconnect()
        except RuntimeError:
            pass
        tela_cargas.carga_alterada.connect(sincronizar_mudanca_no_dashboard)

    # ⏱️ Sincronização dos Timers do Dashboard
    timer_vencido = False
    for attr in ['timer', 'timer_simulacao', 'timer_ia']:
        if hasattr(janela, attr) and getattr(janela, attr) is not None:
            getattr(janela, attr).timeout.connect(executar_algoritmo_cortes_ia)
            timer_vencido = True
            break

    if not timer_vencido:
        janela.timer_independente = QTimer()
        janela.timer_independente.timeout.connect(executar_algoritmo_cortes_ia)
        janela.timer_independente.start(2000)

    try:
        janela.abas.addTab(tela_cargas, "⚙️ Cargas Críticas")
        janela.abas.addTab(tela_baterias, "🔋 Banco de Baterias")
        janela.abas.addTab(tela_graficos, "📈 Gráficos de Desempenho")
        janela.abas.addTab(tela_ia, "🧠 Recomendações e IA")

        janela.setStyleSheet("""
            QTabBar::tab {
                background: #1E1E1E; color: #888888; border: 1px solid #2D2D2D;
                padding: 10px 20px; border-top-left-radius: 6px; border-top-right-radius: 6px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #121212; color: #00E676; border-bottom: 2px solid #00E676;
            }
        """)
    except AttributeError:
        pass

    monitor_arduino.start()
    janela.show()
    
    resultado = app.exec()
    monitor_arduino.parar()
    monitor_arduino.wait()
    sys.exit(resultado)