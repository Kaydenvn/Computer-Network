import mysql.connector
import socket
import threading
from datetime import datetime

# MySQL details
host = "127.0.0.1"
port = 3306
database = "file_app"
username = "admin"
password = "password"

# Lock for thread synchronization
lock = threading.Lock()


def handle_client(client_socket):
    try:
        # Receive data from the client
        data = client_socket.recv(1024).decode()
        parts = data.split()

        if len(parts) >= 3 and parts[0] in ["publish", "remove"]:
            command = parts[0]
            lname = parts[1]
            fname = parts[2]

            try:
                # Connect to the MySQL database
                cnx = mysql.connector.connect(
                    host=host, database=database, user=username, password=password
                )
                cursor = cnx.cursor()

                if command == "publish":
                    # Insert the data into the database
                    timestamp = datetime.now()
                    sql = "INSERT INTO files (lname, fname, created_at) VALUES (%s, %s, %s)"
                    values = (lname, fname, timestamp)
                    cursor.execute(sql, values)
                    cnx.commit()

                    response = "Data saved successfully to the database."

                elif command == "remove":
                    # Delete the entry from the database
                    sql = "DELETE FROM files WHERE lname = %s AND fname = %s"
                    values = (lname, fname)
                    cursor.execute(sql, values)
                    cnx.commit()

                    response = "Data removed successfully from the database."

                # Print the response
                print(response)

            except mysql.connector.Error as e:
                response = "Error: " + str(e)
                print(response)

        else:
            response = "Invalid command."

        # Send the response back to the client
        client_socket.send(response.encode())

    except socket.error as e:
        print("Socket error:", str(e))

    finally:
        # Close the client socket
        client_socket.close()


def start_server():
    # Create a socket and bind it to a specific port
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ("localhost", 12345)
    server_socket.bind(server_address)

    # Listen for incoming connections
    server_socket.listen(5)
    print("Server is listening on", server_address)

    while True:
        # Accept a client connection
        client_socket, client_address = server_socket.accept()
        print("Accepted connection from", client_address)

        # Start a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()


# Start the server
if __name__ == "__main__":
    start_server()
