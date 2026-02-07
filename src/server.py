#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor TCP para gerenciamento de vagas de estacionamento.
O servidor escuta conexões de clientes e responde a comandos para consultar,
pegar e liberar vagas.

Autor: ChatGPT e Copilot com orientação e revisão de Minora
Data: 2024-06-15

Procure por FIXME para identificar pontos que precisam de implementação adicional.

"""
import socket
import os
import threading
import sys
from dotenv import load_dotenv

# Controle de vagas (recurso compartilhado)
VAGAS_INICIAIS = 10
vagas_disponiveis = VAGAS_INICIAIS

# Locks para implementar leitor/escritor (vários leitores, 1 escritor)
resource_lock = threading.Lock()      # protege escrita no recurso
read_count_lock = threading.Lock()    # protege a variável read_count
read_count = 0


def escutar_cliente(nova_conexao, endereco):
    """Função para tratar a comunicação com cada cliente.

    Cada conexão mantém seu estado local `tem_vaga` para impedir
    que um cliente libere vaga que não possui.
    """
    global vagas_disponiveis, read_count
    tem_vaga = False
    print(f'Cliente conectado de {endereco}')

    try:
        while True:
            mensagem = nova_conexao.recv(1024)
            if not mensagem:
                break
            comando = mensagem.decode("utf-8").strip()
            print(f'Mensagem recebida de {endereco}: {comando}')

            if comando == 'consultar_vaga':
                # leitor: coordenar contagem de leitores
                with read_count_lock:
                    read_count += 1
                    if read_count == 1:
                        resource_lock.acquire()

                # leitura do recurso
                resposta = str(vagas_disponiveis)
                nova_conexao.send(resposta.encode('utf-8'))

                # fim da leitura
                with read_count_lock:
                    read_count -= 1
                    if read_count == 0:
                        resource_lock.release()

            elif comando == 'pegar_vaga':
                # escritor: acesso exclusivo
                resource_lock.acquire()
                try:
                    if vagas_disponiveis > 0 and not tem_vaga:
                        vagas_disponiveis -= 1
                        tem_vaga = True
                        resposta = '1'
                    else:
                        resposta = '0'
                finally:
                    resource_lock.release()

                nova_conexao.send(resposta.encode('utf-8'))

            elif comando == 'liberar_vaga':
                resource_lock.acquire()
                try:
                    if tem_vaga:
                        vagas_disponiveis += 1
                        tem_vaga = False
                        resposta = '1'
                    else:
                        resposta = '0'
                finally:
                    resource_lock.release()

                nova_conexao.send(resposta.encode('utf-8'))
                # após liberar vaga podemos fechar a conexão se desejado
                if resposta == '1':
                    break

            else:
                resposta = '-1'
                nova_conexao.send(resposta.encode('utf-8'))

    except ConnectionResetError:
        print(f'Conexão perdida com {endereco}')
    finally:
        try:
            nova_conexao.close()
        except Exception:
            pass
        print(f'Cliente {endereco} desconectado')


def iniciar_servidor():
    """Função para iniciar o servidor TCP"""
    load_dotenv()
    PORTA = int(os.getenv('PORT', 5000))

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind(('localhost', PORTA))
    servidor.listen(128)
    print(f'Servidor escutando na porta {PORTA}')
    print('Aguardando conexões de clientes...\n')
    return servidor


def main():
    servidor = iniciar_servidor()
    try:
        while True:
            nova_conexao, endereco = servidor.accept()
            thread = threading.Thread(target=escutar_cliente, args=(nova_conexao, endereco))
            thread.daemon = True
            thread.start()

    except KeyboardInterrupt:
        print('\nInterrompido pelo usuário')
    finally:
        servidor.close()
        print('\nServidor encerrado')


if __name__ == '__main__':
    main()