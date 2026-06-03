import os
import json
from datetime import datetime

# Caminhos dos Bancos de Dados em JSON
DB_CARGAS_PATH = os.path.join(os.path.dirname(__file__), "..", "cargas_db.json")
DB_HISTORICO_PATH = os.path.join(os.path.dirname(__file__), "..", "historico_energia_db.json")

# --- FUNÇÕES DAS CARGAS (Já existentes) ---

def carregar_dados():
    """Carrega as configurações das cargas do arquivo JSON."""
    if os.path.exists(DB_CARGAS_PATH):
        try:
            with open(DB_CARGAS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao ler banco de cargas: {e}")
    
    # Retorno padrão caso o arquivo não exista ou esteja corrompido
    return {
        "Geladeira": {"potencia": 0.8, "critica": True, "ativo": True, "prioridade": 1, "btn": None},
        "Iluminação Sala": {"potencia": 0.3, "critica": False, "ativo": True, "prioridade": 2, "btn": None},
        "Roteador Internet": {"potencia": 0.1, "critica": True, "ativo": True, "prioridade": 1, "btn": None},
        "Ar-Condicionado": {"potencia": 2.0, "critica": False, "ativo": True, "prioridade": 3, "btn": None},
        "Bomba D'água": {"potencia": 1.2, "critica": False, "ativo": True, "prioridade": 2, "btn": None},
        "Computador": {"potencia": 0.5, "critica": False, "ativo": True, "prioridade": 1, "btn": None}
    }

def salvar_dados(dados):
    """Salva as configurações atuais das cargas no JSON limpando referências do Qt."""
    dados_limpos = {}
    for nome, info in dados.items():
        dados_limpos[nome] = {
            "potencia": info.get("potencia", 0.5),
            "critica": info.get("critica", False),
            "ativo": info.get("ativo", True),
            "prioridade": info.get("prioridade", 1)
        }
    try:
        with open(DB_CARGAS_PATH, "w", encoding="utf-8") as f:
            json.dump(dados_limpos, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar banco de cargas: {e}")


# --- 📊 NOVO: FUNÇÕES DO HISTÓRICO DE ENERGIA ---

def registrar_historico_energia(geracao, consumo):
    """Salva uma leitura de geração e consumo com a data e hora atual no JSON."""
    historico = []
    if os.path.exists(DB_HISTORICO_PATH):
        try:
            with open(DB_HISTORICO_PATH, "r", encoding="utf-8") as f:
                historico = json.load(f)
        except Exception:
            historico = []

    # Estrutura a nova linha do tempo
    nova_leitura = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "geracao_kw": round(float(geracao), 2),
        "consumo_kw": round(float(consumo), 2),
        "saldo_kw": round(float(geracao - consumo), 2)
    }
    
    historico.append(nova_leitura)
    
    # Mantém o arquivo leve limitando o histórico aos últimos 1000 registros
    if len(historico) > 1000:
        historico = historico[-1000:]
        
    try:
        with open(DB_HISTORICO_PATH, "w", encoding="utf-8") as f:
            json.dump(historico, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar histórico de energia: {e}")

def obter_ultimo_historico():
    """Retorna a lista completa de leituras armazenadas."""
    if os.path.exists(DB_HISTORICO_PATH):
        try:
            with open(DB_HISTORICO_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []