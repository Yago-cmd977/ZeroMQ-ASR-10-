"""Fig. 4.22 - Padrão PUB/SUB (publicador).

Publica dois tópicos:
  TIME  a cada 5 s (hora atual, como no exemplo original)
  RAND  a cada 2 s (número aleatório entre 1 e 100)
Formato das mensagens: "<TOPICO> <conteudo>".
"""
import os
import random
import time

import zmq

HOST = os.environ.get("ZMQ_BIND", "0.0.0.0")
PORT = os.environ.get("PORT", "4567")


def main():
    context = zmq.Context()
    s = context.socket(zmq.PUB)
    s.bind("tcp://%s:%s" % (HOST, PORT))
    print("Publicador em", HOST, PORT, "- topicos: TIME (5s), RAND (2s)", flush=True)
    time.sleep(1)  # tempo para os assinantes se conectarem
    ticks = 0
    try:
        while True:
            if ticks % 5 == 0:
                s.send_string("TIME " + time.asctime())
            if ticks % 2 == 0:
                s.send_string("RAND %d" % random.randint(1, 100))
            ticks += 1
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        s.close(linger=0)
        context.term()


if __name__ == "__main__":
    main()
