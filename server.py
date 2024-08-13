import socket
import threading
import time  # Adicionando a importação do módulo time

def handle_client_connection(conn, ender, client_name, clients):
    """
    Handles the communication with a client.
    """
    try:
        while True:
            data = conn.recv(1024)   
            if not data:
                print(f'Connection closed with {client_name}')
                break

            decoded_data = data.decode()
            print(f'Message received from {client_name}: {decoded_data}')

            if decoded_data.startswith('/destinatario'):
                partes = decoded_data.split(' ')
                destinatario = partes[1]
                mensagem = ' '.join(partes[2:])
                if destinatario in clients:
                    clients[destinatario][1].sendall(str.encode(f'Mensagem de {client_name}: {mensagem}'))
                else:
                    print(f'Destinatário {destinatario} não encontrado.')
            else:
                # Process other types of messages if needed
                pass

    except (ConnectionResetError, OSError):
        print(f'Connection lost with {client_name}')
    finally:
        del clients[client_name]  # Remove the disconnected client
        conn.close()

def assign_client_ip(conn, client_name, clients, used_ips):
    """
    DHCP.
    """
    while True:
        if client_name == '0.0.0.0':
            # Atribuir um IP disponível da faixa permitida ao cliente
            available_ips = [f'127.0.0.{i}' for i in range(2, 10) if f'127.0.0.{i}' not in used_ips]
            if available_ips:
                client_name = available_ips[0]
                clients[client_name] = (client_name, conn)  # Atribuir o IP como nome do cliente
                used_ips.add(client_name)
                # Envia uma mensagem ao cliente sobre o IP definido
                conn.sendall(str.encode(f"IP atribuído: {client_name}"))
                return client_name
            else:
                print('Não há IPs disponíveis. Encerrando conexão.') 
                conn.close()
                return None
        elif client_name.startswith('127.0.0.') and int(client_name.split('.')[3]) in range(2, 10):
            if client_name not in used_ips:
                clients[client_name] = (client_name, conn)  # Atribuir o IP como nome do cliente
                used_ips.add(client_name)
                # Envia uma mensagem ao cliente sobre o IP definido
                conn.sendall(str.encode(f"IP atribuído: {client_name}"))
                return client_name  # Retorna o nome do cliente atualizado
            else:
                print('O IP fornecido já está em uso. Solicitando outro IP válido ao cliente...')
                conn.sendall(str.encode("IP está em uso. Por favor, insira outro IP na faixa permitida."))
                client_name = conn.recv(1024).decode().strip()  # Solicita outro IP válido ao cliente
        else:
            print('O IP fornecido não está dentro da faixa permitida (127.0.0.2 a 127.0.0.9).')
            conn.sendall(str.encode("IP inválido. Por favor, forneça um IP dentro da faixa permitida."))
            client_name = conn.recv(1024).decode().strip()

def monitor_clients(clients, used_ips):
    """
    Monitora os clientes e IPs conectados no servidor.
    """
    while True:
        i = 0
        print("Clientes conectados:")
        for client_name, _ in clients.items():
            i += 1
            print(f"Cliente {i}")

        print("\nIPs atribuídos:")
        for ip in used_ips:
            print(f"IP: {ip}")

        print("\n")

        # Atualiza a cada 10 segundos
        time.sleep(10)

# Endereço IP do servidor
server_ip_int_parts = [127, 0, 0, 1]
Host = '.'.join(map(str, server_ip_int_parts))
PORT = 50000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((Host, PORT))
s.listen()

print("Servidor esperando conexões")

clients = {}  # Dicionário para armazenar as conexões dos clientes 
used_ips = set()  # Conjunto para armazenar os IPs já atribuídos

# Iniciar a thread para monitorar os clientes e IPs
monitor_thread = threading.Thread(target=monitor_clients, args=(clients, used_ips))
monitor_thread.start()

while True:
    conn, ender = s.accept()
    
    # Verifica se o IP do cliente está na faixa permitida (127.0.0.1 a 127.0.0.10)
    client_ip = ender[0]
    allowed_ip_range = [f'127.0.0.{i}' for i in range(1, 11)]
    if client_ip not in allowed_ip_range:
        print(f'Conexão recusada do cliente com IP {client_ip}')
        conn.close()
        continue

    client_name = conn.recv(1024).decode()
    
    # Verifica se o cliente forneceu '0.0.0.0' como IP
    if client_name == '0.0.0.0':
        client_name = assign_client_ip(conn, client_name, clients, used_ips)
    else:
        # Atribui um IP para o cliente e atualiza o nome do cliente no servidor
        client_name = assign_client_ip(conn, client_name, clients, used_ips)

    if client_name is not None:
        client_thread = threading.Thread(target=handle_client_connection, args=(conn, ender, client_name, clients))
        client_thread.start()