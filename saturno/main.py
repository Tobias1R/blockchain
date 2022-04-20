import mmap
from random import random
from misc import bcolors
import textwrap
from chain import InputTransaction
from wallet import Wallet
from storageio import Storage, LocalStorage
from coin import CURVE, SHA
from blockchain import Blockchain
import os
from random import randrange
wallets = [
    ('mickey','mouse'),
    ('pato','donald'),
    ('louis','griffin'),
    ('chris','griffin'),
    ('carter','pewtershimit'),
    ('gleen','quagmire'),
    ('joe','swanson'),
    ('mort','goldman'),
    ('dianne','simmons'),
    ('consuela','cleanner'),
    ('cleveland','brown'),
    
]
def create_wallets():
    wallets_objects = []
    for winfo in wallets:
        pem, public_key, filename,filedata = Wallet.generate_wallet(
            winfo[0],
            winfo[1],
            True,
            path_wallet='/home/ozy/BLOCK_ENV/blockchain/wallets/')
    
        decrypted_wallet_data = Wallet.decrypt_wallet(filedata,winfo[1])
        w1 = Wallet(pem_data=pem,password=winfo[1])        
        wallets_objects.append(w1)
    return wallets_objects

PROJECT_DIR = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
BASE_DIR = os.path.realpath(os.path.dirname(PROJECT_DIR))
DATA_DIR = os.path.join(PROJECT_DIR,'data')

if __name__ == '__main__':
    storage = LocalStorage(DATA_DIR)
    #print(DATA_DIR)
    blockchain = Blockchain(storage)
    wallet_file = '/home/ozy/BLOCK_ENV/blockchain/wallets/tobias.walt'
    tobias = Wallet.open_wallet(wallet_file,'plade33')
    wallet_fileo = '/home/ozy/BLOCK_ENV/blockchain/wallets/cleveland.walt'
    ozymandias = Wallet.open_wallet(wallet_fileo,'brown')
    #print('TOBIAS PK',tobias.public_key)
    
    tobias.connect(blockchain)
    ozymandias.connect(blockchain)
    #print(blockchain.chain_transactions)
    blockchain.info()
    print('[TOBIAS BALANCE]',tobias.public_key,tobias.balance)
    print('[OZYMANDIAS BALANCE]',ozymandias.public_key,ozymandias.balance)
    wallets_instances = create_wallets()
    # print('generating transactions...')
    # for i in range(1,50):
    #     windex = randrange(len(wallets_instances))
    #     w1:Wallet = wallets_instances[windex]
    #     w1.connect(blockchain)
    #     tobias.input_transaction(w1.public_key.encode(),(23)+i)
    #     w1.input_transaction(ozymandias.public_key.encode(),10)
    #     if i % 10 == 0:
    #         blockchain.beat()
    #     #print('INPUT TO:',w1.public_key)
    # for w1 in wallets_instances:
    #     w1.connect(blockchain)
    #     print('['+str(w1.public_key)+']',w1.balance)
    # for i in range(0,10000):
    #     tobias.input_transaction(ozymandias.public_key,780*i)
    #tobias.input_transaction(ozymandias.public_key.encode(),78)
    sta=0
    last=0
    stop = 0
    # while stop >= 0:
    #     if stop>0:
    #         sta += stop
        
    #     stop = blockchain.local_storage.transactions.find(b'|#',sta)
    #     if stop == -1:
            
    #         continue
    #     byte = blockchain.local_storage.transactions.read(stop-(sta-last))
    #     #print('-------------------------------------------------------------------------------------------')
    #     #print(byte)
    #     #print('-------------------------------------------------------------------------------------------')
    #     next_start = stop-(sta-last)
    #     print(sta,stop,last,next_start)
    #     print('READ FROM TO',sta-last,stop,stop-(sta-last))
        
    #     last=sta
    #     sta+=2
    # start = 0    
    # with open(blockchain.local_storage.transactionsfile,'r+b') as f:
    #     transactions = mmap.mmap(f.fileno(),0)
    #     endblock = transactions.find(b'|#',0)
    #     byte = transactions.read(endblock)
    #     next_block = endblock+3
    #     previous_byte = 0
    #     while endblock>=0:
    #         # next block is in fact the end of this block
    #         endblock = transactions.find(b'|#',start)
    #         print('FROM:',start,'TO:',endblock,'OFFSET:',endblock+2,'SIZE:',endblock-start)
    #         try:
    #             transactions.seek(start)
    #             #sep = transactions.read(2)        
    #             print('I\'LL TELL YOU ',transactions.tell())
    #             byte = transactions.read(endblock-start)  
    #             print('I\'LL TELL YOU ',transactions.tell())
    #             print(byte)      
    #             previous_byte=byte
    #             start = transactions.tell()+2
                        
    #         except ValueError as ve:
    #             # seek out range
    #             endblock =-1
        
    blockchain.beat()
    # for w1 in wallets_instances:
    #     w1.connect(blockchain)
    #     print('['+str(w1.public_key)+']',w1.balance)
    #print(tobias.info())
    #print(blockchain.chain_transactions.keys())
    # rt:InputTransaction = blockchain.chain_transactions[b'cc3acd4396f796f34596a97e8151fab8c7d6c1f65959037e3ea90c1498eedfad']
    # if tobias.validate_token(rt):
    #     print(bcolors.OKGREEN,'ROOT TOKEN IS FOR YOU',bcolors.ENDC)
    # else:
    #     print(bcolors.FAIL,'ROOT TOKEN IS NOT FOR YOU',bcolors.ENDC)