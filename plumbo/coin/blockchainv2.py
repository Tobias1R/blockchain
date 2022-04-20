from datetime import datetime
from hashlib import sha256
import math
from os import urandom
from . import CURVE, SHA, XIL, __version__
from .misc import bcolors
from .storageio import LocalStorage
from .chainv2 import (
    Block,
    ChainTransaction, 
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
    def __init__(self, storage: LocalStorage,signing_key) -> None:
        # data dir path
        self.signing_key=signing_key
        self.local_storage:LocalStorage = storage
        self.chain = self.local_storage.extract_chain()
        self.validate_local_storage()
        self.transaction_requests = []
        self.chain_transactions = self.local_storage.extract_transactions()
        self.confirmed_transactions = []
        
        self.active_block = Block(
            last_chain_hash=self.get_last_hash(),
            minter_id=DESTINATION_PUBLIC_KEY,
            signing_key=self.signing_key
        )
        print('TOTAL CHAIN TR',len(self.chain_transactions))
        
    
    def get_transaction_sequence(self) -> int:
        return len(self.chain_transactions) + 1
    
    def get_transaction_id(self,issuer_public_key:bytes):
        seq = self.get_transaction_sequence()
        data = bytes(seq)+locktime(True)+issuer_public_key+urandom(254)
        id = SHA(data).hexdigest().encode()
        return id
    
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
        block:Block = Block(
            last_chain_hash=b'0000000000000000000000000000000000000000000000000000000000000000',
            version=__version__,
            minter_id=DESTINATION_PUBLIC_KEY,signing_key=self.signing_key)        
        
        
        t = ChainTransaction(
            txid=b'0000000000000000000000000000000000000000000000000000000000000000',
            version=b'0000',
            direction=ChainTransaction.INPUT_SIGNAL,
            amount=1000,
            address=DESTINATION_PUBLIC_KEY,
            confirmations=1,
            locktime_value=locktime(True),
            output_index=0,
            sequence=0,
            signature=b'ROOTNODE'
        )
        #block.transactions.append(t.dump_data_bytes())
        to = ChainTransaction(
            txid=b'0000000000000000000000000000000000000000000000000000000000000000',
            version=b'0000',
            direction=ChainTransaction.OUTPUT_SIGNAL,
            amount=1000,
            address=DESTINATION_PUBLIC_KEY,
            confirmations=1,
            locktime_value=locktime(True),
            output_index=1,
            sequence=1,
            signature=b'ROOTNODE'
        )
        #block.transactions.append(to.dump_data_bytes())
        # tr:Transaction=Transaction(t)
        # tr.add_output(to)
        # tr.txid=b'0000000000000000000000000000000000000000000000000000000000000000'
        
        trx=block.output_from_coins()
        
        block.transactions.append(trx)
        hash = ''
        nonce = 1            
        while not self.is_hash_valid(hash):
            blockdata = block.block_data(0, 0, nonce)
            hash = sha256(blockdata).hexdigest()
            nonce += 1
            
        d = {hash:blockdata}
        print(d)
        print('BLOCK SIZE',len(blockdata))
        self.local_storage.block_writer.write(hash.encode()+blockdata)
        self.local_storage.chain_writer.write(hash.encode())
        #self.local_storage.inputs_writer.write(i.dump_data_bytes())
        #self.local_storage.outputs_writer.write(i.get_output().transaction_data_bytes())
        self.local_storage.transactions_writer.write(trx.dump_data())
        #self.local_storage.transactions_writer.write(to.dump_data_bytes())
        
        
    def hash_block(self, block:Block, timestamp, prev_hash, index):
        hash = ''
        nonce = 1  
        print('IT\'s LIKE MINNING...')   
               
        while not self.is_hash_valid(hash):
            blockdata = block.block_data(prev_hash, index, nonce)
            hash = sha256(blockdata).hexdigest()
            nonce += 1
        print('!!!NEW BLOCK FOUND!!! ITERATIONS:', 
              nonce,
              'TRANSACTIONS',len(block.transactions)
              )
        hash = hash.encode()
        if not hash in self.chain:
            self.local_storage.block_writer.write(hash+blockdata)
            self.local_storage.chain_writer.write(hash)
            for t in block.transactions:
                self.local_storage.transactions_writer.write(t.dump_data())
                self.chain_transactions.append(t) 
                                      
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
                t:Transaction = transaction
                
                if len(self.active_block.transactions)>=Block.MAX_TRANSACTIONS:
                    self.add_new_block()
                    continue
                if not t.hash in self.chain_transactions:           
                    self.active_block.transactions.append(t)
                    # keep index
                    #self.chain_transactions[t.hash] = t
                self.transaction_requests.remove(transaction)
        if len(self.active_block.transactions) >= 1:
            self.add_new_block()
    
    def validate_transaction(self,transaction:Transaction):
        return True#transaction.is_signature_valid()
        
    
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
        self.active_block = Block(
            last_chain_hash=self.get_last_hash(),
            minter_id=DESTINATION_PUBLIC_KEY,
            signing_key=self.signing_key)
    
    class Meta:
        language = 'python'
        
    
    