import socket
import threading

def send_message(s, client_ip):
    try:
        while True:
            destinatario = input("Digite o IP do destinatario: ")
            mensagem = input("Digite sua mensagem: ")
            s.sendall(str.encode(f'/destinatario {destinatario} {mensagem}'))
    except KeyboardInterrupt:
        s.close()

def connect_to_server(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, PORT))
        return s
    except ConnectionRefusedError:
        return None

# Endereço IP do servidor
server_ip_int_parts = [127, 0, 0, 1]
Host = '.'.join(map(str, server_ip_int_parts))
PORT = 50000

# Conectando-se ao servidor
s = connect_to_server(Host)

if s is None:
    print("Falha ao conectar ao servidor. Encerrando...")
else:
    while True:
        # Solicitar ao usuário que digite o IP (nome do cliente)
        client_ip = input("Digite o nome (que será usado como IP) do cliente: ")

        # Enviar o IP do cliente para o servidor
        s.sendall(str.encode(client_ip))

        # Receber a resposta do servidor
        response = s.recv(1024).decode().strip()

        # Verificar se o IP fornecido pelo cliente é válido
        if response.startswith("IP atribuído"):
            print(response)
            # Atualizar o nome do cliente com o IP validado fornecido pelo servidor
            client_name = response.split(":")[1].strip()
            break
        else:
            print(response)

    # Iniciar uma thread para enviar mensagens constantemente
    send_thread = threading.Thread(target=send_message, args=(s, client_ip))
    send_thread.start()

    try:
        while True:
            data = s.recv(1024)
            if not data:
                print("Conexão encerrada pelo servidor.")
                break
            print(f'Mensagem recebida do servidor: {data.decode()}')
    except KeyboardInterrupt:
        s.close()