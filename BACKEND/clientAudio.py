import socket
import threading
import pyaudio


class Client:
    sendDataToServer = True
    receiveServerData = True
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        while 1:
            try:
                # self.target_ip = input('Enter IP address of server --> ')
                # self.target_port = int(input('Enter target port of server --> '))
                self.target_ip = "192.168.137.1"
                self.target_port = 5000

                self.s.connect((self.target_ip, self.target_port))

                break
            except:
                print("Couldn't connect to server")

        chunk_size = 1024  # 512
        audio_format = pyaudio.paInt16
        channels = 1
        rate = 20000

        # initialise microphone recording
        self.p = pyaudio.PyAudio()
        self.playing_stream = self.p.open(format=audio_format, channels=channels, rate=rate, output=True,
                                          frames_per_buffer=chunk_size)
        self.recording_stream = self.p.open(format=audio_format, channels=channels, rate=rate, input=True,
                                            frames_per_buffer=chunk_size)

        print("Connected to Server")

        # start threads
        self.receive_thread = threading.Thread(target=self.receive_server_data).start()
        self.send_data_to_server()

    def receive_server_data(self):
        while True:
            if not Client.receiveServerData:
                break
            try:
                data = self.s.recv(1024)
                self.playing_stream.write(data)
            except:
                pass

    def send_data_to_server(self):
        while True:
            if not Client.sendDataToServer:
                break
            try:
                data = self.recording_stream.read(1024)
                self.s.sendall(data)
            except:
                pass

