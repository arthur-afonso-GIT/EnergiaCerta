import sys
import os
import math
import random
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
    Popup que aparece quando o Arduino conecta na COM8.
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

        # Cabeçalho
        lbl_titulo = QLabel("⚡ Arduino conectado na COM8!")
        lbl_titulo.setStyleSheet("font-size: 15px; font-weight: bold; color: #00E676;")
        layout.addWidget(lbl_titulo)

        lbl_sub = QLabel(
            f"Corrente detectada: <b style='color:#00E676'>{corrente_kw:.3f} kW</b><br>"
            "Configure a carga física abaixo para adicioná-la ao sistema."
        )
        lbl_sub.setWordWrap(True)
        lbl_sub.setStyleSheet("color: #AAAAAA; font-size: 11px;")
        layout.addWidget(lbl_sub)

        # Formulário
        form = QFormLayout()
        form.setSpacing(10)

        self.txt_nome = QLineEdit()
        self.txt_nome.setText("Carga Arduino")
        self.txt_nome.setPlaceholderText("Ex: Bancada Lab, Motor, Freezer...")
        form.addRow("Nome da carga:", self.txt_nome)

        self.spin_potencia = QDoubleSpinBox()
        self.spin_potencia.setRange(0.001, 50.0)
        self.spin_potencia.setDecimals(3)
        self.spin_potencia.setSuffix(" kW")
        self.spin_potencia.setValue(round(corrente_kw, 3))
        self.spin_potencia.setToolTip("Valor inicial lido do Arduino. Pode ajustar manualmente.")
        form.addRow("Potência inicial:", self.spin_potencia)

        self.chk_critica = QCheckBox("Imune a cortes automáticos (Crítica)")
        form.addRow("Tipo:", self.chk_critica)

        self.combo_prio = QComboBox()
        self.combo_prio.addItems(["1 – Cai Primeiro", "2 – Média", "3 – Cai por Último"])
        self.chk_critica.toggled.connect(lambda c: self.combo_prio.setDisabled(c))
        form.addRow("Prioridade IA:", self.combo_prio)

        layout.addLayout(form)

        # Botões
        layout_btns = QHBoxLayout()
        self.btn_cancelar = QPushButton("Ignorar")
        self.btn_cancelar.setStyleSheet(
            "QPushButton { background:#2D2D2D; color:#888; border:1px solid #444; "
            "padding:8px 16px; border-radius:4px; }"
            "QPushButton:hover { background:#3D3D3D; }"
        )
        self.btn_cancelar.clicked.connect(self.reject)

        self.btn_adicionar = QPushButton("➕ Adicionar ao Sistema")
        self.btn_adicionar.setStyleSheet(
            "QPushButton { background:#00E676; color:#121212; font-weight:bold; "
            "padding:8px 16px; border-radius:4px; border:none; }"
            "QPushButton:hover { background:#00C865; }"
        )
        self.btn_adicionar.clicked.connect(self.accept)
        self.btn_adicionar.setDefault(True)

        layout_btns.addWidget(self.btn_cancelar)
        layout_btns.addWidget(self.btn_adicionar)
        layout.addLayout(layout_btns)

    def obter_dados(self):
        return (
            self.txt_nome.text().strip() or "Carga Arduino",
            self.spin_potencia.value(),
            self.combo_prio.currentIndex() + 1,
            self.chk_critica.isChecked()
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Inicia o monitor de Arduino em background
    monitor_arduino = MonitorConexaoArduino(porta="COM3", baudrate=9600)

    janela = DashboardEnergia()
    # ─────────────────────────────────────────────────────────────────────
    # PONTO CRÍTICO: atribuir ANTES de popular_lista_lateral()
    # A lista lateral e o AbaCargas devem enxergar EXATAMENTE este objeto.
    # Nunca fazer: janela.config_cargas = dict(carregar_dados()) — cria cópia.
    janela.config_cargas = carregar_dados()
    # Cria os botões laterais com referência ao dict acima (fonte de verdade única)
    janela.popular_lista_lateral()
    # ─────────────────────────────────────────────────────────────────────

    # Injeta referência do monitor no dashboard
    janela.monitor_arduino = monitor_arduino

    if hasattr(janela, 'abas') and janela.abas.count() > 1:
        janela.abas.removeTab(1)

    tela_cargas = AbaCargas(arduino_serial=monitor_arduino, dashboard_principal=janela)
    tela_baterias = AbaBaterias()
    tela_ia = AbaIA()
    tela_graficos = AbaGraficos()

    janela.aba_bateria = tela_baterias
    janela.aba_baterias = tela_baterias  
    janela.aba_graficos = tela_graficos
    janela.aba_ia = tela_ia

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
            janela.adicionar_recomendacao_log(
                f"🔌 Arduino: Carga '{nome_final}' ({potencia:.3f} kW) registrada via COM8."
            )

            if hasattr(tela_cargas, 'sincronizar_com_monitoramento_geral'):
                tela_cargas.sincronizar_com_monitoramento_geral()

    monitor_arduino.arduino_conectado.connect(ao_arduino_conectar)

    # ------------------------------------------------------------------
    # ALGORITMO DE CORTES DA IA (ESTRUTURA INTELIGENTE E DE DECISÃO PURA)
    # ------------------------------------------------------------------
    def executar_algoritmo_cortes_ia():
        # 1. COLETA AS INFORMAÇÕES DIRETAMENTE DAS VARIÁVEIS MATEMÁTICAS UNIFICADAS DO DASHBOARD
        geracao = getattr(janela, 'geracao_atual', 0.0)
        consumo = getattr(janela, 'consumo_atual', 0.0)
        saldo = getattr(janela, 'saldo_atual', 0.0)
        meta_limite = janela.sld_meta_consumo.value() / 10.0

        soc_bateria = 100.0
        if hasattr(tela_baterias, 'soc_atual'):
            soc_bateria = float(tela_baterias.soc_atual)

        # Salva o histórico energético atualizado no Banco de Dados com dados seguros
        registrar_historico_energia(geracao, consumo)

        # 2. Tomada de Decisão Baseada em Fatos e Balanço Seguro
        if saldo < 0 or consumo > meta_limite or soc_bateria < 30.0:
            janela.ciclos_em_defice += 1

            if hasattr(janela, 'lbl_bateria_status'):
                if soc_bateria <= 30.0:
                    janela.lbl_bateria_status.setText(f"Bateria Crítica ({soc_bateria:.1f}%)! Cortando Cargas...")
                    janela.lbl_bateria_status.setStyleSheet("font-size: 11px; color: #E53935; font-weight: bold; border: none;")
                else:
                    janela.lbl_bateria_status.setText(f"Défice Detectado! Balanço: {saldo:.1f} kW")
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

                    print(f"[IA] Cortando dispositivo devido a sobrecarga real: {nome_alvo} ({potencia_carga}kW)")

                    janela.config_cargas[nome_alvo]["ativo"] = False
                    if nome_alvo not in janela.cargas_desligadas_pela_ia:
                        janela.cargas_desligadas_pela_ia.append(nome_alvo)

                    salvar_dados(janela.config_cargas)
                    janela.atualizar_visual_botao(nome_alvo)
                    janela.adicionar_recomendacao_log(f"IA: Desligamento automático de '{nome_alvo}' (Prioridade {prio_atual}).")

                    if hasattr(tela_cargas, 'atualizar_interface_externa'):
                        tela_cargas.atualizar_interface_externa(nome_alvo, False)

                    sincronizar_mudanca_no_dashboard(nome_alvo, False, potencia_carga)
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

                    if saldo > (potencia_carga + 0.3) and (consumo + potencia_carga) <= meta_limite:
                        print(f"[IA] Sobra de energia detectada. Religando dispositivo: {nome_alvo}")

                        janela.config_cargas[nome_alvo]["ativo"] = True
                        janela.cargas_desligadas_pela_ia.remove(nome_alvo)

                        salvar_dados(janela.config_cargas)
                        janela.atualizar_visual_botao(nome_alvo)
                        janela.adicionar_recomendacao_log(f"IA: Restabelecendo '{nome_alvo}'.")

                        if hasattr(tela_cargas, 'atualizar_interface_externa'):
                            tela_cargas.atualizar_interface_externa(nome_alvo, True)

                        sincronizar_mudanca_no_dashboard(nome_alvo, True, potencia_carga)
                        return

    # ------------------------------------------------------------------
    # RECEPTOR DO SINAL carga_alterada (emitido pelo CardCarga)
    # ------------------------------------------------------------------
    def sincronizar_mudanca_no_dashboard(nome_carga, esta_ativo, consumo_kw):
        """
        Receptor secundário do sinal carga_alterada.
        O CardCarga já atualizou o dict e o Dashboard diretamente.
        Aqui apenas propagamos para gráficos e outros módulos externos.
        NÃO chamar atualizar_status_carga_lateral aqui (já foi feito).
        """
        print(f"[SIGNAL] carga_alterada recebido → '{nome_carga}' | ativo={esta_ativo}")

        # Atualiza gráfico de consumo da aba de gráficos, se presente
        if hasattr(tela_graficos, 'atualizar_consumo_grafico'):
            consumo_total = sum(
                info["potencia"] for info in janela.config_cargas.values() if info.get("ativo", True)
            )
            tela_graficos.atualizar_consumo_grafico(consumo_total)

    if hasattr(tela_cargas, 'carga_alterada'):
        tela_cargas.carga_alterada.connect(sincronizar_mudanca_no_dashboard)

    # Vincula o cérebro da IA para rodar em sincronia com o loop de tela
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

    monitor_arduino.start()
    janela.show()
    
    resultado = app.exec()
    monitor_arduino.parar()
    monitor_arduino.wait()
    sys.exit(resultado)