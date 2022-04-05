import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from BACKEND import server, serverAudio
import threading

if __name__ == "__main__":
    threading.Thread(target=lambda: serverAudio.Server()).start()
    threading.Thread(target=lambda: server.ServerMsg()).start()


