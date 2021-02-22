import socket
import pickle
from datetime import datetime
import sys
import select
import os


HOST = '127.0.0.1'
PORT = 65432


def try_run_server(name):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
        try:
            tcp_sock.bind((HOST, PORT))
            tcp_sock.listen()
            print('Server is up. Waiting for connection...')
            conn, addr = tcp_sock.accept()
            client_name = ''
            client_addr = None
            with conn:
                client_name = conn.recv(1024).decode('utf-8')
                client_addr = addr
                print(f'{client_name} connected from {addr}')
                conn.sendall(name.encode('utf-8'))
            tcp_sock.close()
            return True, client_addr
        except OSError:
            return False, None


def run_client(name):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
        tcp_sock.connect((HOST, PORT))
        tcp_sock.sendall(name.encode('utf-8'))
        server_name = tcp_sock.recv(1024).decode('utf-8')
        print(f'You are connected to {server_name}')
        client_addr = tcp_sock.getsockname()
        tcp_sock.close()
        return client_addr


def run_udp_chat(addr_to_send, addr_to_recv, name):
    messages = []
    print('>>> ', end='', flush=True)    
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
        udp_sock.bind(addr_to_recv)
        while True:
            sockets = [udp_sock, sys.stdin]
            read_sockets, _, _ = select.select(sockets, [], [])

            for s in read_sockets:
                if s == udp_sock:    
                    reply = pickle.loads(udp_sock.recv(1024))
                    messages.append(reply)
                    refresh_content(messages)
                else:
                    message = sys.stdin.readline()
                    message_obj = {'from': name, 'time': datetime.now(), 'message': message}
                    encoded = pickle.dumps(message_obj)
                    messages.append(message_obj)
                    udp_sock.sendto(encoded, addr_to_send)
                    refresh_content(messages)


def refresh_content(messages=None):
    os.system('clear')
    if messages:
        messages.sort(key=lambda item: item['time'])
        for msg in messages:
            print(f'{msg["time"].time().isoformat("minutes")} {msg["from"]}: {msg["message"]}')
    print('>>> ', end='', flush=True)


def main():
    os.system('clear')
    your_name = str(input('Your name: '))
    addr_to_recv = (HOST, PORT)
    success, addr_to_send = try_run_server(your_name)
    
    if not success:
        # requested port is already busy so try to connect to it
        # also swap the addresses of sender and receiver
        addr_to_recv, addr_to_send = run_client(your_name), addr_to_recv

    run_udp_chat(addr_to_send, addr_to_recv, your_name)
    

if __name__ == '__main__':
    main()