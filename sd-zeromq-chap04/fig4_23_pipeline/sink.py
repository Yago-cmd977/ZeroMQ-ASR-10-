"""Fig. 4.23 - Pipeline PUSH/PULL: sink (coletor de resultados).

Recebe os resultados dos workers e mostra um resumo por worker.
Exemplo:
  python sink.py --port 4569 --expect 200   (0 = sem limite, Ctrl+C para sair)
"""
import argparse
import collections
import json

import zmq


def main():
    parser = argparse.ArgumentParser(description="Coletor de resultados PULL")
    parser.add_argument("--bind", default="0.0.0.0", help="interface onde escutar")
    parser.add_argument("--port", default="4569", help="porta de escuta")
    parser.add_argument("--expect", type=int, default=0, help="resultados a esperar (0 = sem limite)")
    args = parser.parse_args()

    context = zmq.Context()
    s = context.socket(zmq.PULL)
    s.bind("tcp://%s:%s" % (args.bind, args.port))
    print("Sink em", args.bind, args.port, flush=True)

    per_worker = collections.Counter()
    total = 0
    try:
        while args.expect == 0 or total < args.expect:
            r = json.loads(s.recv_string())
            total += 1
            per_worker[r["worker"]] += 1
            print("#%d %s: fonte %s tarefa %d (carga %d) -> %d" % (
                total, r["worker"], r["source"], r["task"], r["workload"], r["result"]), flush=True)
    except KeyboardInterrupt:
        pass
    finally:
        print("\nResumo por worker:", dict(per_worker), "| total =", total)
        s.close(linger=0)
        context.term()


if __name__ == "__main__":
    main()
