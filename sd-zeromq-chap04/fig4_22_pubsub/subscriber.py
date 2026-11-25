"""Fig. 4.22 - Padrão PUB/SUB (assinante).

Exemplos:
  python subscriber.py --host IP_DO_PUBLICADOR --topics TIME RAND --count 10
  python subscriber.py --host IP_DO_PUBLICADOR --topics RAND --count 0   # 0 = sem limite (Ctrl+C)
"""
import argparse

import zmq


def main():
    parser = argparse.ArgumentParser(description="Assinante PUB/SUB")
    parser.add_argument("--host", default="127.0.0.1", help="IP do publicador")
    parser.add_argument("--port", default="4567", help="porta do publicador")
    parser.add_argument("--topics", nargs="+", default=["TIME"], help="topicos a assinar")
    parser.add_argument("--count", type=int, default=5, help="mensagens a receber (0 = sem limite)")
    args = parser.parse_args()

    context = zmq.Context()
    s = context.socket(zmq.SUB)
    s.connect("tcp://%s:%s" % (args.host, args.port))
    for topic in args.topics:
        s.setsockopt_string(zmq.SUBSCRIBE, topic)
    print("Assinando", args.topics, "em", args.host, args.port, flush=True)

    received = 0
    try:
        while args.count == 0 or received < args.count:
            msg = s.recv_string()
            topic, _, content = msg.partition(" ")
            received += 1
            print("[%s] %s" % (topic, content), flush=True)
    except KeyboardInterrupt:
        pass
    finally:
        s.close(linger=0)
        context.term()


if __name__ == "__main__":
    main()
