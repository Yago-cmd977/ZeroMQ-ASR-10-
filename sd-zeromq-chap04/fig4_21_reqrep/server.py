"""Fig. 4.21 - Padrão REQ/REP (servidor).

Recebe requisições no formato "COMANDO [argumentos]" e responde.
Comandos:
  ECHO <texto>       devolve o texto com "*" no final (comportamento original)
  UPPER <texto>      devolve o texto em maiúsculas
  REVERSE <texto>    devolve o texto invertido
  SUM <n1> <n2> ...  devolve a soma dos números
  TIME               devolve a hora do servidor
  STOP               responde BYE e encerra o servidor

Mensagens sem comando conhecido são tratadas como ECHO.
"""
import os
import time

import zmq

HOST = os.environ.get("ZMQ_BIND", "0.0.0.0")  # interface onde o servidor escuta
PORTS = [os.environ.get("PORT1", "4567"), os.environ.get("PORT2", "4568")]


def cmd_echo(arg):
    return arg + "*"


def cmd_upper(arg):
    return arg.upper()


def cmd_reverse(arg):
    return arg[::-1]


def cmd_sum(arg):
    total = sum(float(x) for x in arg.split())
    return str(int(total)) if total.is_integer() else str(total)


def cmd_time(_arg):
    return time.asctime()


HANDLERS = {
    "ECHO": cmd_echo,
    "UPPER": cmd_upper,
    "REVERSE": cmd_reverse,
    "SUM": cmd_sum,
    "TIME": cmd_time,
}


def handle(message):
    """Processa uma requisição. Retorna (resposta, deve_parar)."""
    name, _, arg = message.partition(" ")
    name = name.upper()
    if name == "STOP":
        return "BYE", True
    if name in HANDLERS:
        try:
            return HANDLERS[name](arg), False
        except ValueError:
            return "ERR argumentos invalidos para " + name, False
    return message + "*", False  # comportamento original: ecoa com "*"


def main():
    context = zmq.Context()
    s = context.socket(zmq.REP)
    for port in PORTS:
        s.bind("tcp://%s:%s" % (HOST, port))
    print("Servidor REQ/REP em", HOST, "portas", PORTS, flush=True)
    try:
        while True:
            msg = s.recv_string()
            print("recebido:", msg, flush=True)
            reply, stop = handle(msg)
            s.send_string(reply)
            if stop:
                break
    except KeyboardInterrupt:
        pass
    finally:
        s.close(linger=0)
        context.term()


if __name__ == "__main__":
    main()
