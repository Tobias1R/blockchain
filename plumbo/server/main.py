import socket
import types
import os, sys

PROJECT_DIR = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
BASE_DIR = os.path.realpath(os.path.dirname(PROJECT_DIR))

sys.path.append(BASE_DIR+'/')

from plumbo.coin import blockchainv2 as blockchain
from plumbo.coin.storageio import LocalStorage

HOST = '127.0.0.1'  
PORT = 6543       
import selectors
sel = selectors.DefaultSelector()

ACTION_REGISTER_TRANSACTION=b'REQ_TR#'
ACTION_REGISTER_PARTICIPANT=b'REG#'

ACTION_DOWNLOAD_TRANSACTIONS=b'GETTRALL#'
class Router:
    def __init__(self) -> None:        
        self.participants=[]
    
    def register_participant(self,data):
        if data in self.participants:
            return 'you\'re back. cool!'.encode()
        self.participants.append(data)
        return 'registered'.encode()
    
def service_connection(key, mask,router:Router,chain:blockchain.Blockchain):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024) # Should be ready to read
        
        if recv_data.startswith(ACTION_REGISTER_PARTICIPANT):
            data.outb += router.register_participant(recv_data[4:])
        elif recv_data.startswith(ACTION_DOWNLOAD_TRANSACTIONS):
            chain.local_storage.transactions_reader.seek(0)
            data.outb += chain.local_storage.transactions_reader.read(-1)
        elif recv_data.startswith(ACTION_REGISTER_TRANSACTION):
            chain.transaction_requests.append(recv_data[len(ACTION_REGISTER_TRANSACTION):])
            
        else:
            print('closing connection to', data.addr)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print('echoing', repr(data.outb), 'to', data.addr)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

def accept_wrapper(sock,router:Router):
    conn, addr = sock.accept()  # Should be ready to read
    print(router.register_participant(addr),addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)
    
def serve_mult(host,port,router:Router,chain:blockchain.Blockchain):
    
    # ...
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((host, port))
    lsock.listen()
    print('listening on', (host, port))
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)
    
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj,router)
            else:
                service_connection(key, mask,router,chain)

if '__main__' == __name__:
    from plumbo.client.wallet import Wallet
    miner = Wallet.open_wallet(
        '/home/ozy/BLOCK_ENV/blockchain/plumbo/client/wallets/tobias.walt',
        'plade33'
        )
    storage = LocalStorage('/home/ozy/BLOCK_ENV/blockchain/data')    
    blockchain_instance = blockchain.Blockchain(storage,miner.sk)
    serve_mult(HOST,PORT,router=Router(),chain=blockchain_instance)
    