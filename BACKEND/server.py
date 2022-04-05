import socket
import threading
from person import Person
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine

# GLOBAL CONSTANTS
BUFSIZ = 512  # buffer size
PORT = 5500
HOST = 'localhost'
ADDR = (HOST, PORT)
MAX_CONNECTIONS = 10  # connections allowed to server at a time

# GLOBAL VARIABLES
SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER.bind(ADDR)  # setup the server
persons = []  # list of users connected

engine = create_engine('postgresql://postgres:toor@localhost:5432/Baras')
db = scoped_session(sessionmaker(bind=engine))

class ServerMsg:
    def __init__(self):
        SERVER.listen(MAX_CONNECTIONS)
        print("[SERVER] Waiting for connections ...")
        start_thread = threading.Thread(target=self.waiting_for_connection)
        start_thread.start()
        start_thread.join()
        SERVER.close()

    def broadcast(self, msg, name):
        """
        broadcasts messages to everyone on chat room
        :param msg: str
        :param name: str
        :return: None
        """
        for person in persons:
            client = person.client
            try:
                if name == "":
                    client.send(bytes(msg, 'utf-8'))
                else:
                    client.send(bytes(f'{str(name)}: ' + msg, 'utf-8'))
            except Exception  as e:
                print(f'[EXCEPTION] {e}')


    def client_communication(self, person):
        """
        To handle all the messages from the clients
        :param person: Person
        :return: None
        """
        client = person.client
        name = client.recv(BUFSIZ).decode("utf-8")  # first message has to be name. Accepting name of person connected
        print(f'{name} has connected to chat room.')
        person.set_name(name)  # setting name of person
        msg = f'PERFORM UPDATE TABLE ACTION'
        self.broadcast(msg, "")  # sending message to everyone on server that {name} has joined the room
        query = f"UPDATE members SET status = 1 WHERE username = '{name}'"
        db.execute(query)
        db.commit()
        while True:
            try:
                msg = client.recv(BUFSIZ).decode("utf-8")
                if msg == "/quit":  # checks whether user requested to quit the chat room
                    client.close()
                    persons.remove(person)  # remove person from client list
                    self.broadcast(f'PERFORM UPDATE TABLE ACTION', "")  # prints on chat room
                    query = f"UPDATE members SET status = 0 WHERE username = '{name}'"
                    print(query)
                    db.execute(query)
                    db.commit()
                    print(f"[DISCONNECT] {name} disconnected")  # prints on the server
                    break
                elif msg == '/join_audio':
                    audio_client = AudioClient(person)
                    print(f'{name} has joined the voice chat')
                else:  # else it sends to all users
                    self.broadcast(msg, name)
                    print(f'[CLIENT MSG] {name} : ' + msg)
            except Exception as e:
                print(f'[EXCEPTION] {e}')


    def waiting_for_connection(self):
        """
        Waits for connections from persons, need to start new thread once server is connected
        :return: None
        """
        while True:
            try:
                client, addr = SERVER.accept()  # waiting for connections
                person = Person(addr, client)  # creating person and
                persons.append(person)  # adding to client list
                print(f"Connection established from {addr}")
                threading.Thread(target=self.client_communication, args=(person,)).start()  #
            except Exception as e:
                print(f'[EXCEPTION] ', e)
        print("[SERVER] CRASHED (ಥ⌣ಥ) ")


if __name__ == "__main__":
    server = ServerMsg()
    # SERVER.listen(MAX_CONNECTIONS)
    # print("[SERVER] Waiting for connections ...")
    # start_thread = threading.Thread(target=waiting_for_connection)
    # start_thread.start()
    # start_thread.join()
    # SERVER.close()
