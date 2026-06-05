import math
import random

class LeitorArduino:
    def __init__(self, porta="COM8", baudrate=9600):
        self.porta = porta
        self.baudrate = baudrate
        self.conectado = False
        self.hora_atual = 10.0
        
        self.forcar_sobrecarga = False
        self.forcar_alta_geracao = False
        
        self.potencia_cargas = {
            "Geladeira": 0.8,
            "Iluminação Sala": 0.3,
            "Roteador Internet": 0.1,
            "Ar-Condicionado": 2.0,
            "Bomba D'água": 1.2,
            "Computador": 0.5
        }
        
    def ler_dados_reais(self, estados_cargas=None):
        # Inicializa as variáveis físicas caso não venha nada da serial
        consumo_real = None
        geracao_real = None

        # 🔌 Tenta ler dados físicos do Arduino se estiver conectado
        if self.conectado:
            try:
                # Espera-se que o Arduino envie uma linha de texto contendo os ampères, ex: "15.4"
                # Se mandar mais de um sensor, pode mandar separado por vírgula: "10.2,5.1"
                linha_serial = self.serial.readline().decode('utf-8').strip()
                
                if linha_serial:
                    # Constantes para a conversão elétrica
                    tensao_rede = 220.0  # Mude para 127.0 se sua rede for essa
                    fator_potencia = 0.92
                    
                    # Caso envie apenas uma leitura de corrente (Ex: Sensor de Consumo Geral)
                    if "," not in linha_serial:
                        corrente_amperes = float(linha_serial)
                        # Aplica a fórmula matemática de conversão para kW
                        consumo_real = (tensao_rede * corrente_amperes * fator_potencia) / 1000.0
                    else:
                        # Caso envie duas leituras (Ex: "corrente_consumo,corrente_solar")
                        dados = linha_serial.split(",")
                        corrente_consumo = float(dados[0])
                        corrente_solar = float(dados[1])
                        
                        consumo_real = (tensao_rede * corrente_consumo * fator_potencia) / 1000.0
                        geracao_real = (tensao_rede * corrente_solar * fator_potencia) / 1000.0
                        
            except Exception as e:
                print(f"[SERIAL] Falha ao processar dados do Arduino (Usando Simulação): {e}")
                # Não faz nada, deixa o código seguir para a simulação abaixo servir de fallback
                pass
                
        # ⏰ Avanço do relógio do sistema (Mantido o seu original)
        self.hora_atual = (self.hora_atual + 0.25) % 24
        
        # --- ☀️ CÁLCULO DA GERAÇÃO SOLAR ---
        if geracao_real is not None:
            geracao_simulado = geracao_real
        else:
            # Roda seu código original de simulação solar se não houver leitura real
            if 6.0 <= self.hora_atual <= 18.0:
                angulo_solar = math.sin(math.pi * (self.hora_atual - 6.0) / 12.0)
                multiplicador_sol = 9.0 if self.forcar_alta_geracao else 6.0
                geracao_base = multiplicador_sol * angulo_solar
                geracao_simulado = max(0.0, geracao_base + random.uniform(-0.2, 0.1))
            else:
                geracao_simulado = 0.0
            
        # --- 🔌 CÁLCULO DO CONSUMO ---
        if consumo_real is not None:
            consumo_simulado = consumo_real
        else:
            # Roda seu código original de consumo se o sensor físico falhar/não existir
            if estados_cargas is None:
                estados_cargas = {carga: True for carga in self.potencia_cargas}
                
            consumo_base = 0.5
        for carga, ativo in estados_cargas.items():
            if ativo and carga in self.potencia_cargas:
                # 💡 Se o Arduino estiver conectado e for a lâmpada física, ignora o valor fixo simulado
                if carga == "Iluminação Sala" and consumo_real is not None:
                    consumo_base += consumo_real  # Soma o valor medido pelo ACS712 em kW
                else:
                    consumo_base += self.potencia_cargas[carga]  # Soma o valor fixo simulado das outras cargas
                    
            if 12.0 <= self.hora_atual <= 14.0:
                consumo_base += 0.8
            elif 18.0 <= self.hora_atual <= 22.0:
                consumo_base += 1.2
                
            if self.forcar_sobrecarga:
                consumo_base += 4.5
                
            consumo_simulado = max(0.4, consumo_base + random.uniform(-0.2, 0.2))
        
        # Retorna os valores finais arredondados
        return round(consumo_simulado, 1), round(geracao_simulado, 1), round(self.hora_atual, 2)