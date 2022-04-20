from datetime import datetime
from hashlib import sha256
import math
from coin import CURVE, SHA, XIL, __version__
from misc import bcolors
from storageio import LocalStorage
from chain import (
    Block, 
    InputTransaction, 
    OutputTransaction, 
    Transaction,
    read_locktime,
    locktime,
    convert_locktime
    )

TRANSACTION_STATUS_CONFIRMED = 'C'
TRANSACTION_STATUS_INVALID = 'I'
TRANSACTION_STATUS_PENDIND = 'Q'
TRANSACTION_STATUS_DENIED = 'D'

BLOCK_DATA_SIZE = 128
LEDGER_DATA_SIZE = 437

DESTINATION_PUBLIC_KEY = b'ad689f9e10651009d0d1afbe16cc48e0417ce2c51401b46bcbd500cd55e47ad3'
 
class Blockchain:
    def __init__(self, storage: LocalStorage) -> None:
        # data dir path
        self.local_storage:LocalStorage = storage
        self.chain = self.local_storage.extract_chain()
        self.validate_local_storage()
        self.transaction_requests = []
        self.chain_transactions = self.local_storage.extract_transactions()
        self.confirmed_transactions = []
        self.active_block = Block()
        
    
    def get_transaction_id(self) -> int:
        return len(self.local_storage.transactions_reader.read(-1)) + 1
    
    def validate_local_storage(self):
        if len(self.chain) == 0:
            print('WE NEED A ROOT BLOCK.')
            self.generate_root_block()
       
    
    def info(self):
        print(bcolors.HEADER,end='')
        print('TOTAL BLOCKS',len(self.chain))
        print('ROOT BLOCK',bcolors.OKCYAN,self.chain[0])
        print(bcolors.HEADER,end='')
        print('LAST HASH',bcolors.OKBLUE,self.get_last_hash())
        print(bcolors.HEADER,end='')
        print('TOTAL TRANSACTIONS',len(self.chain_transactions))
        print('KNOWN PARTICIPANTS')
        print(bcolors.ENDC)
    
    def generate_root_block(self):
        block:Block = Block()
        
        node = b'00000000000050000000342900000000000000000001202201202232423181040000000000000000000100000000000000000000\x00\xf3\xcaU \x06&\xf4S\xd8\t\xb7\x08\xa9\xc3\xfe\x14\x8bjBN|\x1f\xca\x19\xb1\xba\xd2\x85\x08\x16R\x86\x83\xcf\xee\x96\xd3\xda\\>O\xe6\x95\x87\x12\x98\tF\x17\xfa%\xdd\xd4\xba\xe4V\x0b\x86\xc9Z\x86\xeb\xd1c>\x01\x1b\xfd\x8b\xfe\xbe\x81$@\xbe\xfb\xe4<\xaf\xe5\x86\x94\xa8F\xe3\xeboD\xab{g\r^\x87\xaa\xf7\x1b\x96\xbd\x1f\x91\xf2*\x05s\x8f\xd4\xe1\xde\x0fuU\xa2r\x1d\xceP\x1e\x80\xce\xb1\x80\xa6rw\x105\x96\xbe3\xeb\x00\xf8\x9e\xae\r\xa9\xcaf\xa2\x9e\xc6\xff\x03\xf1*-\xe4*@\x14\xed\xd3\x0b\x8e\xfc\xddrm \xf4\xf7\xa6\xa5\x9d\xe0n\xff\xad\xf0\rk\xd2\x8f\x1df\xf7\xfe\x07\x99|l\xb5\xcc\xa4^\xddd%\xa8\xf1\xae|nN\xb8K\x017"Q\xb3\x05\xe1N"\x7f\\\xce\xb6=\xa7\x86?z\xd8\x0c[\x1b\x81HMYh\xd7\xc5\xe7\xb6\x07\xfb\xb3\xccs\x86{\x02<\x91\xf7bgeA\x11B#\x89:S\x0b.\xe4f6)\x8f\x7f\xdf\rL8u1\x1c\x02\xad\xf4\x1c\xab\x95\\\xb5\xa9\'\t\r\xad\xd5\'-\xe9\xc7\xfd\xc6"\xed\xce~\xee\xbf\xfa \x88?B'
        i = InputTransaction.read_data_bytes(node)
        print('blockchain verification',i.dump_data_bytes()==node)
        print('verify sig',i.is_signature_valid())
        token = i.token_data(DESTINATION_PUBLIC_KEY)
        print('root token',token)
        print('token validation',i.validate_token(token))
        #b'ea781b13698c31b8c7588a32509a032d18142c0ba1f3a6c48e765a6bdc494bd7'
        t = Transaction()
        t.add_input(i)
        
        block.transactions.append(t.dump_data_bytes())
        hash = ''
        nonce = 1            
        while not self.is_hash_valid(hash):
            block_hash = '{}:{}:{}:{}:{}'.format(
                block.block_data(), locktime(), 0, 0, nonce)
            hash = sha256(block_hash.encode()).hexdigest()
            nonce += 1
        d = {hash:block.block_data()}
        print(d)
        print('BLOCK SIZE',
              len(block.block_data()))
        self.local_storage.block_writer.write(hash.encode()+block.block_data())
        self.local_storage.chain_writer.write(hash.encode())
        self.local_storage.inputs_writer.write(i.dump_data_bytes())
        #self.local_storage.outputs_writer.write(i.get_output().transaction_data_bytes())
        self.local_storage.transactions_writer.write(t.dump_data_bytes())
        
        
    def hash_block(self, data:Block, timestamp, prev_hash, index):
        hash = ''
        nonce = 1  
        print('IT\'s LIKE MINNING...')          
        while not self.is_hash_valid(hash):
            block = '{}:{}:{}:{}:{}'.format(
                data.block_data(), timestamp, prev_hash, index, nonce
            )
            hash = sha256(block.encode()).hexdigest()
            nonce += 1
        print('!!!NEW BLOCK FOUND!!! ITERATIONS:', 
              nonce,
              'TRANSACTIONS',len(data.transactions)
              )
        hash = hash.encode()
        if not hash in self.chain:
            self.local_storage.block_writer.write(hash+data.block_data())
            self.local_storage.chain_writer.write(hash)
            for t in data.transactions:
                self.local_storage.transactions_writer.write(t.dump_data_bytes())
                self.chain_transactions[SHA(t.dump_data_bytes()).hexdigest().encode()] = t 
                                      
        else:
            print('Duplicated block at',hash)
        
    def beat(self):
        ''' Beat it... just beat it.
        This is for miners and routing servers'''
        for transaction in self.transaction_requests:
            if isinstance(transaction,InputTransaction):
                pass
            if self.validate_transaction(transaction):
                # confirmation goes here
                t = Transaction()
                t.add_input(transaction)
                if len(self.active_block.transactions)>=Block.MAX_TRANSACTIONS:
                    self.add_new_block()
                    continue
                if not t.hash in self.chain_transactions:           
                    self.active_block.transactions.append(t)
                    # keep index
                    self.chain_transactions[t.hash] = t
                self.transaction_requests.remove(transaction)
        if len(self.active_block.transactions) >= 1:
            self.add_new_block()
    
    def validate_transaction(self,transaction:InputTransaction):
        return transaction.is_signature_valid()
        
    
    def get_last_hash(self):
        return self.chain[-1]
        
    
    def is_hash_valid(self, hash):
        index = int(math.floor(len(self.chain)/64))        
        return hash.startswith(str('{:x}'.format(index)))

    def add_new_block(self,):
        index = len(self.chain)+1
        prev_hash = self.get_last_hash()
        timestamp = datetime.utcnow().timestamp()
        self.active_block.status=2 #locked, @todo persist
        self.hash_block(self.active_block, 
                        locktime(),prev_hash,index)    
        self.active_block = Block()
    
    class Meta:
        language = 'python'
        
    
    