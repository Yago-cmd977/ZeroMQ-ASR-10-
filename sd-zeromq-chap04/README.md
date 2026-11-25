# Sistemas Distribuídos — Cap. 4: Diferentes paradigmas de interação com ZeroMQ (ASR 10)

Implementação em Python dos exemplos das **Figuras 4.21, 4.22 e 4.23** do livro-texto, com
novas funcionalidades e configuração de endereços para execução em máquinas diferentes
(por exemplo, instâncias EC2 na AWS).

## Estrutura

| Pasta | Figura | Padrão ZeroMQ | Arquivos |
|---|---|---|---|
| `fig4_21_reqrep/` | 4.21 | REQ/REP (requisição-resposta) | `server.py`, `client.py` |
| `fig4_22_pubsub/` | 4.22 | PUB/SUB (publicação-assinatura) | `publisher.py`, `subscriber.py` |
| `fig4_23_pipeline/` | 4.23 | PUSH/PULL (pipeline) | `ventilator.py`, `worker.py`, `sink.py` |

## Instalação

Recomendado usar um ambiente virtual:

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt  # instala pyzmq
```

## Novas funcionalidades (em relação aos exemplos originais)

- **REQ/REP:** o servidor interpreta comandos (`ECHO`, `UPPER`, `REVERSE`, `SUM`, `TIME`, `STOP`).
  O cliente envia várias requisições em uma execução e tem timeout para não bloquear
  indefinidamente se o servidor estiver fora do ar.
- **PUB/SUB:** o publicador envia dois tópicos (`TIME` a cada 5 s e `RAND` a cada 2 s); o
  assinante escolhe quais tópicos quer receber e quantas mensagens.
- **PUSH/PULL:** as fontes são parametrizadas (ID, porta, número de tarefas). Foi acrescentado um
  **sink**: os workers enviam os resultados de volta, e o sink mostra um resumo por worker.
- **Endereços configuráveis:** nada de IPs fixos no código. Os hosts são passados por argumento
  (ou variáveis de ambiente `ZMQ_BIND`, `PORT`, `PORT1`, `PORT2` no lado do servidor).
- **Serialização:** as mensagens da Fig. 4.23 usam JSON em vez de `pickle`, pois `pickle` executa
  código ao desserializar dados vindos da rede.

## Como executar

### Teste local (tudo na mesma máquina, cada comando em um terminal)

```bash
# Fig. 4.21
python fig4_21_reqrep/server.py
python fig4_21_reqrep/client.py "ECHO oi" "UPPER hello" "SUM 1 2 3.5" TIME --stop

# Fig. 4.22
python fig4_22_pubsub/publisher.py
python fig4_22_pubsub/subscriber.py --topics TIME RAND --count 6

# Fig. 4.23 (sink primeiro, depois fontes e workers)
python fig4_23_pipeline/sink.py --port 4569 --expect 40
python fig4_23_pipeline/ventilator.py --id 1 --port 4567 --tasks 20 --delay 0.2
python fig4_23_pipeline/ventilator.py --id 2 --port 4568 --tasks 20 --delay 0.2
python fig4_23_pipeline/worker.py --name w1 --sources 127.0.0.1:4567,127.0.0.1:4568 --sink 127.0.0.1:4569
python fig4_23_pipeline/worker.py --name w2 --sources 127.0.0.1:4567,127.0.0.1:4568 --sink 127.0.0.1:4569
```

### Teste em máquinas diferentes (AWS)

1. Abra as portas **4567**, **4568** e **4569** (TCP de entrada) no security group das instâncias
   que recebem conexões.
2. Em cada instância, instale o pyzmq e copie o projeto.
3. Exemplo de topologia: a máquina **A** roda o servidor REQ/REP e o publicador; a máquina **B**
   roda os clientes e assinantes; as máquinas **C** e **D** rodam as fontes e os workers, e a
   máquina **E** roda o sink.

```bash
# Máquina A (IP privado 172.31.18.70)
python fig4_21_reqrep/server.py
python fig4_22_pubsub/publisher.py

# Máquina B
python fig4_21_reqrep/client.py --host 172.31.18.70 --port 4567 "UPPER teste" TIME
python fig4_22_pubsub/subscriber.py --host 172.31.18.70 --topics TIME RAND --count 0

# Máquina E (sink)
python fig4_23_pipeline/sink.py --port 4569 --expect 40

# Máquina C (fonte 1) e D (fonte 2)
python fig4_23_pipeline/ventilator.py --id 1 --port 4567 --tasks 20 --delay 0.2   # na C
python fig4_23_pipeline/ventilator.py --id 2 --port 4568 --tasks 20 --delay 0.2   # na D

# Workers: podem rodar em qualquer máquina que alcance as fontes e o sink
python fig4_23_pipeline/worker.py --name w1 --sources IP_C:4567,IP_D:4568 --sink IP_E:4569
```

Para o REQ/REP, o servidor escuta em todas as interfaces (`0.0.0.0`) por padrão. Use
`ZMQ_BIND` para mudar isso.