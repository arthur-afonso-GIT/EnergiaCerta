# Arquivo: Interface/componentes/painel_cargas.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

class PainelCargasCriticas(QWidget):
    def __init__(self):
        super().__init__()
        
        # Guardamos uma variável para rastrear quanta potência foi cortada pela IA
        self.potencia_aliviada_total = 0.0
        
        self.setStyleSheet("""
            QWidget { background-color: #1E1E1E; border: 1px solid #333333; border-radius: 6px; }
            QLabel { color: #FFFFFF; font-size: 14px; font-weight: bold; border: none; background: transparent; }
            QPushButton { 
                background-color: #2D2D2D; color: #FFFFFF; border: 1px solid #444444; 
                border-radius: 4px; padding: 10px; text-align: left; font-size: 12px;
            }
            QPushButton:hover { background-color: #3D3D3D; }
        """)
        
        layout = QVBoxLayout(self)
        
        lbl_titulo = QLabel("Monitoramento e Controle de Cargas")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_titulo)
        
        # 🆕 Nova Label para mostrar a eficiência do gerenciamento de demanda
        self.lbl_status_economia = QLabel("⚡ Sistema operando em carga total")
        self.lbl_status_economia.setStyleSheet("color: #00E676; font-size: 12px; font-weight: normal;")
        self.lbl_status_economia.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_status_economia)
        
        # Mantive exatamente a sua estrutura de dicionário, adicionando o campo "potencia" para a física do simulador
        self.cargas = {
            "Geladeira": {"critica": True, "potencia": 0.4, "botao": QPushButton("⚡ [CRÍTICA] Geladeira")},
            "Iluminação Sala": {"critica": True, "potencia": 0.2, "botao": QPushButton("⚡ [CRÍTICA] Iluminação Sala")},
            "Roteador Internet": {"critica": True, "potencia": 0.1, "botao": QPushButton("⚡ [CRÍTICA] Roteador Internet")},
            "Ar-Condicionado": {"critica": False, "potencia": 2.0, "botao": QPushButton("⚡ [SISTEMA] Ar-Condicionado")},
            "Bomba D'água": {"critica": False, "potencia": 1.2, "botao": QPushButton("⚡ [SISTEMA] Bomba D'água")},
            "Computador": {"critica": False, "potencia": 0.5, "botao": QPushButton("⚡ [SISTEMA] Computador")}
        }
        
        self.estados = {nome: True for nome in self.cargas}
        
        for nome, info in self.cargas.items():
            layout.addWidget(info["botao"])
            
            # 🆕 Conecta o clique do botão para permitir controle manual/interativo
            # Usamos essa construção com lambda para o Python saber qual botão foi clicado
            info["botao"].clicked.connect(lambda checked=False, n=nome: self.alternar_estado_manual(n))
            
            self.atualizar_estilo_botao(nome)
            
    def obter_estados(self):
        return self.estados
        
    def definir_estado_carga(self, nome, ligado):
        """Função que a IA do Dashboard vai chamar para ligar/desligar cargas"""
        if nome in self.estados:
            self.estados[nome] = ligado
            self.atualizar_estilo_botao(nome)
            self.recalcular_alivio_demanda()
            
    def alternar_estado_manual(self, nome):
        """Permite que o usuário clique na tela para ligar/desligar um aparelho"""
        # Cargas críticas não devem ser desligadas manualmente por segurança!
        if self.cargas[nome]["critica"]:
            return 
            
        novo_estado = not self.estados[nome]
        self.definir_estado_carga(nome, novo_estado)
            
    def recalcular_alivio_demanda(self):
        """Calcula quanta energia estamos economizando por ter aparelhos desligados"""
        alivio = 0.0
        for nome, info in self.cargas.items():
            if not self.estados[nome]:  # Se estiver desligado
                alivio += info["potencia"]
        
        self.potencia_aliviada_total = alivio
        if alivio > 0:
            self.lbl_status_economia.setText(f"📉 Alívio de Demanda Ativo: -{alivio:.1f} kWh poupados")
            self.lbl_status_economia.setStyleSheet("color: #FF9800; font-size: 12px; font-weight: bold;")
        else:
            self.lbl_status_economia.setText("⚡ Sistema operando em carga total")
            self.lbl_status_economia.setStyleSheet("color: #00E676; font-size: 12px; font-weight: normal;")

    def atualizar_estilo_botao(self, nome):
        botao = self.cargas[nome]["botao"]
        prefixo = "[CRÍTICA]" if self.cargas[nome]["critica"] else "[SISTEMA]"
        
        if self.estados[nome]:
            botao.setText(f"🟢 {prefixo} {nome} - Ativo ({self.cargas[nome]['potencia']} kWh)")
            botao.setStyleSheet("background-color: #2D2D2D; color: #FFFFFF; border: 1px solid #444444;")
        else:
            botao.setText(f"🔴 ⚠️ {prefixo} {nome} - DESLIGADO (Corte de Pico)")
            botao.setStyleSheet("background-color: #3a1c1c; color: #E53935; border: 1px solid #E53935; font-weight: bold;")