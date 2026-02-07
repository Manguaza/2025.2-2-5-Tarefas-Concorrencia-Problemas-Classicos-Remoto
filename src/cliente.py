#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cliente TCP para gerenciamento de vagas de estacionamento.
O cliente envia comandos ao servidor para consultar,
pegar e liberar vagas.

Autor: ChatGPT e Copilot com orientação e revisão de Minora
Data: 2024-06-15

Procure por FIXME para identificar pontos que precisam de implementação adicional.

"""

import threading
import socket
import os
from dotenv import load_dotenv
import time
import random


class ClienteEstacionamento(threading.Thread):
    def __init__(self, socket_cliente):
        threading.Thread.__init__(self)
        self.socket_cliente = socket_cliente
        self.tem_vaga = False

    def run(self):
        # Método de execução da thread.
        try:
            # Tentar pegar uma vaga até conseguir
            tentativas = 0
            while tentativas < 50:
                # consulta opcional
                vagas = self.consultar_vaga()
                # tentar pegar
                ok = self.pegar_vaga()
                if ok:
                    self.tem_vaga = True
                    # passear (usar a vaga por um tempo)
                    self.passear()
                    # liberar e encerrar
                    self.liberar_vaga()
                    break

                # aguardar e tentar novamente
                tentativas += 1
                time.sleep(random.uniform(0.05, 0.2))

        finally:
            try:
                self.socket_cliente.close()
            except Exception:
                pass

    def consultar_vaga(self):
        # Consulta a quantidade de vagas disponíveis no servidor.
        try:
            self.socket_cliente.send(b'consultar_vaga')
            resp = self.socket_cliente.recv(1024)
            if not resp:
                return None
            return int(resp.decode('utf-8').strip())
        except Exception:
            return None

    def pegar_vaga(self):
        # Tenta pegar uma vaga no servidor.
        try:
            self.socket_cliente.send(b'pegar_vaga')
            resp = self.socket_cliente.recv(1024)
            if not resp:
                return False
            return resp.decode('utf-8').strip() == '1'
        except Exception:
            return False

    def liberar_vaga(self):
        # Libera a vaga ocupada no servidor.
        try:
            self.socket_cliente.send(b'liberar_vaga')
            resp = self.socket_cliente.recv(1024)
            if not resp:
                return False
            ok = resp.decode('utf-8').strip() == '1'
            if ok:
                self.tem_vaga = False
            return ok
        except Exception:
            return False
    
    def passear(self):
        # Simula o tempo que o cliente fica com a vaga ocupada.
        time.sleep(random.uniform(0.2, 1.0))

def criar_socket_cliente():
    # Cria e retorna um socket TCP para o cliente.
    load_dotenv()
    PORTA = int(os.getenv('PORT', 5000))

    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect(('localhost', PORTA))
    print('Conectado ao servidor de estacionamento')
    return cliente

def main():
    # Função principal para iniciar o cliente.
    # FIXME: Implemente a lógica para iniciar 50 clientes concorrentes
    # Lembre que são 50 clientes concorrentes
    # Código comentado abaixo é apenas um exemplo de como iniciar um cliente
    ### socket = criar_socket_cliente()
    ### cliente = ClienteEstacionamento(socket)
    ### cliente.start()
    clientes = []
    for i in range(50):
        try:
            sock = criar_socket_cliente()
        except Exception as e:
            print('Erro ao criar socket:', e)
            break
        cliente = ClienteEstacionamento(sock)
        cliente.daemon = True
        cliente.start()
        clientes.append(cliente)
        # pequeno atraso para não sobrecarregar o servidor no instante
        time.sleep(0.01)

    # aguardar término dos threads
    for c in clientes:
        c.join()

    print('Todos os clientes finalizaram')

if __name__ == "__main__":
    main()