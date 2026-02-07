**Título**: Implementação do Problema Leitores/Escritores usando Sockets em Python

**Contexto inicial**:
- Disciplina: Sistemas Operacionais (2025.2)
- Objetivo: Implementar uma solução distribuída (cliente/servidor via sockets) para o problema clássico de leitores/escritores aplicando sincronização remota e evitando condições de corrida e impasses.

**Descrição da solução**:
- Arquivos principais:
  - `src/server.py`: servidor TCP que gerencia 10 vagas de estacionamento e atende comandos dos clientes.
  - `src/cliente.py`: cliente que cria 50 threads simulando 50 clientes concorrentes.

- Protocolo entre cliente/servidor:
  - `consultar_vaga` -> servidor responde com número inteiro de vagas disponíveis.
  - `pegar_vaga` -> servidor responde `1` (sucesso) ou `0` (falha).
  - `liberar_vaga` -> servidor responde `1` (sucesso) ou `0` (o cliente não possuía vaga).

**Implementação do servidor**:
- O servidor mantém um contador global `vagas_disponiveis` inicializado com 10.
- Para suportar múltiplos leitores e um escritor exclusivo foi adotado o padrão leitor/escritor com dois locks:
  - `read_count_lock`: protege a contagem de leitores ativos (`read_count`).
  - `resource_lock`: garante exclusão mútua para escritores (e para a primeira/última entrada/saída de leitores quando necessário).
- Fluxo:
  - Ao receber `consultar_vaga` o servidor executa a seção de leitura: incrementa `read_count` sob `read_count_lock`; se for o primeiro leitor, adquire `resource_lock` para bloquear escritores; lê `vagas_disponiveis` e, ao terminar, decrementa `read_count` e libera `resource_lock` se `read_count` for zero.
  - Ao receber `pegar_vaga` ou `liberar_vaga` o servidor trata como operação de escrita: adquire `resource_lock`, modifica `vagas_disponiveis` e libera `resource_lock`.
- Cada conexão de cliente tem estado local `tem_vaga` (boolean) para impedir que um cliente libere vaga que não possui.

**Implementação do cliente**:
- `ClienteEstacionamento` é uma `thread` que cria um socket para o servidor e tenta operar no protocolo:
  - Opcionalmente consulta vagas.
  - Tenta `pegar_vaga` repetidamente até conseguir (limite de tentativas configurado).
  - Ao obter vaga, simula uso com `passear()` (sleep aleatório) e depois envia `liberar_vaga`.
- O script `main()` cria 50 instâncias de `ClienteEstacionamento` (50 clientes concorrentes) e aguarda todas terminarem.

**Tratamento de impasse (deadlock)**:
- Estratégia adotada:
  - Uso de locks simples (`resource_lock`) e um protocolo de leitor/escritor que evita que leitores e escritores esperem em cadeias circulares. Não há aquisição de múltiplos locks em ordens conflitantes, portanto o risco de deadlock por ordem reversa de locks é mitigado.
  - Operações de escrita são breves e sempre adquirem apenas `resource_lock` (sem tentar adquirir outro lock enquanto seguram `resource_lock`). Leituras adquirem `read_count_lock` só para atualizar `read_count` e, ocasionalmente, `resource_lock` (somente na transição 0->1 e 1->0). Essa ordem fixa evita ciclos de espera.
- Observação sobre starvation (inanição):
  - A implementação favorece leitores (múltiplos leitores podem bloquear escritores se houver leitura contínua). Em cenários com muitas leituras contínuas, escritores podem sofrer demora. Para a atividade isso é aceitável, mas para produção é possível implementar prioridades ou filas para evitar starvation.

**Execução e comportamento observado**:
- Dependências (arquivo `requeriments.txt` contém `python-dotenv`). Foi instalada a dependência no ambiente virtual usado nos testes.
- Comandos para executar manualmente:

```bash
# Iniciar servidor (porta padrão 5000)
python3 src/server.py

# Em outro terminal, executar clientes (50 clientes)
python3 src/cliente.py
```

- Resultado observado nos testes locais realizados aqui:
  - O servidor iniciou corretamente e ficou escutando na porta 5000.
  - Ao executar `src/cliente.py` foram abertas 50 conexões; cada cliente relatou "Conectado ao servidor de estacionamento" e, após execução concorrente, o script terminou com "Todos os clientes finalizaram".
  - As operações de `pegar_vaga` respeitaram a contagem de vagas (até 10 vagas atribuídas simultaneamente) e `liberar_vaga` restaurou as vagas corretamente.

**Considerações finais**:
- A solução demonstra os conceitos de sockets, exclusão mútua remota e sincronização, aplicando o padrão leitores/escritores.
- Pontos de melhoria:
  - Implementar prioridade para escritores (evitar starvation de escritores).
  - Adicionar logs com timestamps e contadores para melhor análise do comportamento concorrente.
  - Adicionar testes automatizados que verificam invariantes (por exemplo, 0 <= vagas_disponiveis <= 10) durante execução concorrente.

**Anexos / Apêndice**:
- Local dos arquivos relevantes:
  - `src/server.py`
  - `src/cliente.py`
  - `requeriments.txt`


---
Relatório gerado com base no código implementado localmente em 07/02/2026.
