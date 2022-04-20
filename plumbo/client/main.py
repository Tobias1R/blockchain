import socket
import os, sys

PROJECT_DIR = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
BASE_DIR = os.path.realpath(os.path.dirname(PROJECT_DIR))

sys.path.append(BASE_DIR+'/')
HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server
from plumbo.cryptochain import VerifyingKey
from client_gui import Janela

from PySide6.QtWidgets import (
    QApplication, QFileDialog,  QWidget
)
if __name__ == '__main__':
    
    # inicia aplicativo Qt
    app = QApplication(sys.argv)
    # instancia e mostra widget da janela.
    janela = Janela(None)
    janela.show()
    # executa applicativo 
    sys.exit(app.exec())
    