import socket

# Server details
server_address = ("localhost", 12345)

while True:
    # Prompt the user for input
    command = input("Enter command (publish/remove lname fname), or 'exit' to quit: ")

    if command == "exit":
        break

    # Create a socket and connect to the server for each command
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)

    try:
        # Pad the command to a fixed length of 1024 characters
        padded_command = command.ljust(1024)

        # Send the padded command to the server
        client_socket.send(padded_command.encode())

        # Receive the response from the server
        response = client_socket.recv(1024).decode()
        print("Server response:", response)

    except socket.error as e:
        print("Socket error:", str(e))

    finally:
        # Close the socket
        client_socket.close()
