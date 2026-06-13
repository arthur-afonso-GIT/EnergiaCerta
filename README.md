# EnergiaCerta

**EnergiaCerta** é um dashboard desktop para monitoramento e gerenciamento inteligente de energia residencial/solar, com interface gráfica em **PySide6 (Qt)**. O sistema simula (ou lê de um Arduino real) dados de geração solar e consumo das cargas, exibe métricas em tempo real e conta com uma **IA de gerenciamento de carga** que desliga e religa automaticamente equipamentos não críticos conforme o saldo de energia disponível.

---

# Funcionalidades

- **Dashboard principal** com KPIs de consumo, geração e saldo de energia em tempo real
- **Aba de Cargas Críticas** — cadastro de cargas (eletrodomésticos/equipamentos), com prioridade, status crítico/não crítico e ligar/desligar manual
- **Aba de Banco de Baterias** — telemetria de tensão, corrente, temperatura e estado de carga (SOC)
- **Aba de Gráficos de Desempenho** — histórico de consumo x geração em gráficos e tabelas
- **Aba de Recomendações e IA** — log de decisões automáticas tomadas pelo algoritmo de gerenciamento
- **IA de corte de carga**: ao detectar déficit energético sustentado, desliga automaticamente a carga não crítica de menor prioridade (maior potência primeiro em caso de empate) e a religa quando há sobra de geração e bateria suficiente
- **Integração com Arduino** via porta serial — detecta a conexão, lê corrente em tempo real e permite cadastrar a carga física detectada através de um popup
- **Persistência em JSON** — configurações de cargas (`cargas_db.json`) e histórico de energia (`historico_energia_db.json`)
- **Modo simulação** completo (sem hardware) para desenvolvimento e testes

---

# Estrutura do Projeto

```
EnergiaCerta/
├── Main.py                          # Ponto de entrada da aplicação
├── leitor.py                        # Leitor de dados (simulação ou Arduino real)
├── cargas_db.json                   # Banco de dados das cargas cadastradas
├── historico_energia_db.json        # Histórico de leituras de energia
│
├── Core/
│   ├── banco_dados.py                # Funções de carregar/salvar dados em JSON
│   ├── comunicacao_serial.py         # Thread de monitoramento da conexão com Arduino
│   └── simulador.py                  # Simulador de dados de consumo/geração
│
└── Interface/
    ├── dashboard.py                  # Janela principal (DashboardEnergia)
    ├── abas/
    │   ├── aba_cargas.py             # Gerenciamento de cargas críticas
    │   ├── aba_baterias.py           # Telemetria do banco de baterias
    │   ├── aba_graficos.py           # Gráficos de desempenho
    │   └── aba_ia.py                 # Recomendações e status da IA
    ├── componentes/
    │   ├── grafico_tempo_real.py     # Canvas de gráfico em tempo real
    │   ├── painel_bateria.py
    │   ├── painel_cargas.py
    │   └── painel_simulacao.py
    └── assets/
        └── logo.png
```

---

## 🔧 Requisitos

- Python 3.10+
- [PySide6](https://pypi.org/project/PySide6/) (inclui PySide6-Charts)
- [pyserial](https://pypi.org/project/pyserial/) (opcional, necessário apenas para integração com Arduino)

---

A aplicação abrirá o dashboard principal com as abas:

| Aba | Descrição |
|---|---|
| ⚙️ Cargas Críticas | Cadastro e controle das cargas do sistema |
| 🔋 Banco de Baterias | Tensão, corrente, temperatura e SOC |
| 📈 Gráficos de Desempenho | Histórico de consumo e geração |
| 🧠 Recomendações e IA | Log de ações automáticas da IA |

---

# Integração com Arduino

Por padrão, o sistema roda em **modo simulação**, gerando dados de consumo e geração automaticamente (veja `Core/simulador.py` e `leitor.py`).

Para usar hardware real:

1. Conecte o Arduino via USB (porta padrão configurada: `COM3`/`COM8`, ajustável em `Main.py` e `Core/comunicacao_serial.py`)
2. O Arduino deve enviar dados pela serial no formato `corrente,...` (em Amperes), a 9600 baud
3. Ao detectar a conexão, um popup permite nomear a carga física, definir potência, prioridade e se é crítica
4. Para ativar a leitura via `leitor.py`, defina `USAR_HARDWARE_REAL = True`

---

# Lógica da IA de Gerenciamento

1. A cada ciclo, calcula o saldo real de energia (geração − consumo, considerando bateria)
2. Se houver déficit por **2 ciclos consecutivos**, desliga a carga não crítica de **menor prioridade** (e maior potência em caso de empate)
3. Registra a ação no log de recomendações e, se houver Arduino conectado, envia o comando de corte via serial
4. Quando há sobra de geração solar e o SOC da bateria está acima de 40%, religa as cargas desligadas anteriormente, respeitando a prioridade e o limite de consumo

---

# Dados Persistidos

- **`cargas_db.json`** — lista de cargas cadastradas (nome, potência, prioridade, status crítico, ativo/inativo)
- **`historico_energia_db.json`** — histórico de leituras (timestamp, geração, consumo, saldo), limitado aos últimos 1000 registros
