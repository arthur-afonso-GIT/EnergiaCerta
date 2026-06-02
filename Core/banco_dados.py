import json
import os

ARQUIVO_JSON = "cargas_db.json"

def inicializar_banco():
    """Se o arquivo JSON não existir, cria com os dados iniciais"""
    if not os.path.exists(ARQUIVO_JSON):
        dados_iniciais = {
            "Geladeira": {"critica": True, "potencia": 0.8, "ativo": True, "prioridade": 1},
            "Iluminação Sala": {"critica": True, "potencia": 0.3, "ativo": True, "prioridade": 1},
            "Roteador Internet": {"critica": True, "potencia": 0.1, "ativo": True, "prioridade": 1},
            "Ar-Condicionado": {"critica": False, "potencia": 2.0, "ativo": True, "prioridade": 1},
            "Bomba D'água": {"critica": False, "potencia": 1.2, "ativo": True, "prioridade": 3},
            "Computador": {"critica": False, "potencia": 0.5, "ativo": True, "prioridade": 2}
        }
        salvar_dados(dados_iniciais)

def carregar_dados():
    """Lê o arquivo e retorna o dicionário"""
    inicializar_banco()
    try:
        with open(ARQUIVO_JSON, 'r', encoding='utf-8') as f:
            config_cargas = json.load(f)
        
        # Garante que o campo 'btn' exista na memória para a interface
        for nome in config_cargas:
            config_cargas[nome]["btn"] = None
        return config_cargas
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return {}

def salvar_dados(dicionario_cargas):
    """Salva as configurações atuais filtrando objetos do Qt"""
    try:
        dados_limpos = {}
        for nome, info in dicionario_cargas.items():
            dados_limpos[nome] = {
                "critica": info.get("critica", False),
                "potencia": info.get("potencia", 1.0),
                "ativo": info.get("ativo", True),
                "prioridade": info.get("prioridade", 1)
            }
        with open(ARQUIVO_JSON, 'w', encoding='utf-8') as f:
            json.dump(dados_limpos, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar arquivo: {e}")