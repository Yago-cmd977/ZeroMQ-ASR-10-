"""Fig. 4.21 - Padrão REQ/REP (cliente).

Envia uma ou mais requisições em sequência (uma por argumento posicional).

Exemplos:
  python client.py --host IP_DO_SERVIDOR --port 4567 "UPPER oi" "SUM 1 2 3" TIME
  python client.py --host IP_DO_SERVIDOR --port 4568 "Hello world 2"
  python client.py --host IP_DO_SERVIDOR --stop
"""
import argparse

import zmq


def main():
    parser = argparse.ArgumentParser(description="Cliente REQ/REP")
    parser.add_argument("--host", default="127.0.0.1", help="IP do servidor")
    parser.add_argument("--port", default="4567", help="porta do servidor (4567 ou 4568)")
    parser.add_argument("--timeout", type=int, default=5000, help="ms para aguardar resposta")
    parser.add_argument("--stop", action="store_true", help="envia STOP ao final")
    parser.add_argument("requests", nargs="*", help="requisicoes a enviar")
    args = parser.parse_args()

    requests = list(args.requests)
    if args.stop:
        requests.append("STOP")
    if not requests:
        requests = ["Hello world"]

    context = zmq.Context()
    s = context.socket(zmq.REQ)
    s.setsockopt(zmq.RCVTIMEO, args.timeout)
    s.setsockopt(zmq.LINGER, 0)
    s.connect("tcp://%s:%s" % (args.host, args.port))

    try:
        for req in requests:
            s.send_string(req)
            try:
                reply = s.recv_string()
            except zmq.Again:
                # Depois de um timeout o socket REQ fica inutilizavel: encerra.
                print("sem resposta do servidor (timeout) para:", req)
                break
            print("%-25s -> %s" % (req, reply))
    finally:
        s.close()
        context.term()


if __name__ == "__main__":
    main()
