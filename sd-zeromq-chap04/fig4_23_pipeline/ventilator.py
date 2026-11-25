"""Fig. 4.23 - Pipeline PUSH/PULL: fonte de tarefas (ventilator).

Cada fonte gera tarefas com carga aleatoria e as distribui (round-robin)
entre os workers conectados. Cada fonte escuta em sua propria porta.

Exemplos:
  python ventilator.py --id 1 --port 4567 --tasks 100
  python ventilator.py --id 2 --port 4568 --tasks 100
"""
import argparse
import json
import random
import time

import zmq


def main():
    parser = argparse.ArgumentParser(description="Fonte de tarefas PUSH")
    parser.add_argument("--id", default="1", help="identificador da fonte")
    parser.add_argument("--bind", default="0.0.0.0", help="interface onde escutar")
    parser.add_argument("--port", default="4567", help="porta de escuta")
    parser.add_argument("--tasks", type=int, default=100, help="numero de tarefas")
    parser.add_argument("--delay", type=float, default=1.0, help="segundos entre tarefas")
    args = parser.parse_args()

    context = zmq.Context()
    s = context.socket(zmq.PUSH)
    s.bind("tcp://%s:%s" % (args.bind, args.port))
    print("Fonte", args.id, "em", args.bind, args.port, flush=True)

    try:
        for i in range(args.tasks):
            time.sleep(args.delay)
            task = {"source": args.id, "task": i, "workload": random.randint(1, 100)}
            s.send_string(json.dumps(task))
        print("Fonte", args.id, ": todas as tarefas enviadas", flush=True)
    except KeyboardInterrupt:
        pass
    finally:
        s.close(linger=5000)  # aguarda entrega das mensagens pendentes
        context.term()


if __name__ == "__main__":
    main()
