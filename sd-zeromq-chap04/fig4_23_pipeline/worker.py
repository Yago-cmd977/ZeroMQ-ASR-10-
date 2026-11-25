"""Fig. 4.23 - Pipeline PUSH/PULL: worker.

Recebe tarefas de uma ou mais fontes (PULL), simula o trabalho e envia
o resultado a um sink (PUSH).

Exemplo:
  python worker.py --name w1 --sources 10.0.0.1:4567,10.0.0.2:4568 --sink 10.0.0.3:4569
"""
import argparse
import json
import time

import zmq


def main():
    parser = argparse.ArgumentParser(description="Worker PULL -> PUSH")
    parser.add_argument("--name", default="worker", help="nome do worker")
    parser.add_argument("--sources", default="127.0.0.1:4567,127.0.0.1:4568",
                        help="fontes separadas por virgula (host:porta)")
    parser.add_argument("--sink", default="127.0.0.1:4569", help="sink de resultados (host:porta)")
    args = parser.parse_args()

    context = zmq.Context()
    pull = context.socket(zmq.PULL)
    for src in args.sources.split(","):
        pull.connect("tcp://" + src.strip())
    push = context.socket(zmq.PUSH)
    push.connect("tcp://" + args.sink)
    print(args.name, "iniciado; fontes:", args.sources, "sink:", args.sink, flush=True)

    try:
        while True:
            task = json.loads(pull.recv_string())
            time.sleep(task["workload"] * 0.01)  # simula o trabalho (como no exemplo original)
            result = {
                "worker": args.name,
                "source": task["source"],
                "task": task["task"],
                "workload": task["workload"],
                "result": task["workload"] ** 2,  # resultado "processado"
            }
            push.send_string(json.dumps(result))
            print(args.name, "processou tarefa", task["task"], "da fonte", task["source"], flush=True)
    except KeyboardInterrupt:
        pass
    finally:
        pull.close(linger=0)
        push.close(linger=5000)
        context.term()


if __name__ == "__main__":
    main()
