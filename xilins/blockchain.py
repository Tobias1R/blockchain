from hashlib import sha512
from datetime import datetime
import json
import math
from coin import Transaction, Xilin, Block
from wallet import Wallet

ozy = Wallet.generate_wallet('Ozymandias Wallet','plade33')



class Blockchain:

    def __init__(self):
        self.blocks = []
        self.ledger = {}
        self.genesis_wallet: Wallet = None
        self.set_genesis_block()
        #self.active_block:Block = self.get_active_block()
    
    def get_active_block(self,) -> Block:   
        
        block:Block = self.ledger[self.get_last_hash()]
        if block.status != 1:
            print('GENERATING NEW BLOCK')
            self.add_new_block()
            block:Block = self.ledger[self.get_last_hash()]
        return block
            

    def set_genesis_block(self):
        w1=Wallet(ozy[0],ozy[1])
        self.genesis_wallet=w1
        #print('GENESIS WALLET',w1.data)
        t = Transaction()
        t.source = 'root'
        t.destination = w1.hash_id
        t.status = 'ROOT'
        t.value = 5000
        data = Block(0)
        data.add_transaction(t)
        
        timestamp = datetime.utcnow().timestamp()
        prev_hash = 0
        index = 0
        block = '{}:{}:{}:{}:{}'.format(
                data, timestamp, prev_hash, index, 0
            )
        hash = sha512(block.encode()).hexdigest()
        self.blocks.append(hash)
        data.status = 3
        self.ledger[hash] = data
        self.active_block = None
        self.add_new_block()
        
    
    def hash_block(self, data:Block, timestamp, prev_hash, index):
        hash = ''
        nonce = 1            
        while not self.is_hash_valid(hash):
            block = '{}:{}:{}:{}:{}'.format(
                data, timestamp, prev_hash, index, nonce
            )
            hash = sha512(block.encode()).hexdigest()
            nonce += 1
        print('[nonce]', nonce)
        if not hash in self.ledger:
            self.blocks.append(hash)
            self.ledger[hash] = self.active_block = data
            
        else:
            print('Duplicated block at',hash)
        
    
    def balance_source(self,source):
        balance = 0.00
        for h in self.ledger:
            node = self.ledger[h]
            #print(node)
            if node[1] == source:
                balance += float(node[2])
            if node[0] == source:
                balance -= float(node[2])
        return balance
    
    def validate_transaction(self,transaction:Transaction):
        
        source = transaction.source
        balance = self.balance_source(source=source)
        #print('VALIDATE',source,balance)
        transaction_value = transaction.value + transaction.fee
        if balance - transaction_value < 0:
            transaction.status = 'INVALID'
        return transaction
    
    def get_last_hash(self):
        return self.blocks[-1]
    
    def is_hash_valid(self, hash):
        index = int(math.floor(len(self.blocks)/2))
        return hash.startswith('00'+str(index))

    def add_new_block(self,):
        index = len(self.blocks)
        prev_hash = self.get_last_hash()
        timestamp = datetime.utcnow().timestamp()
        self.hash_block(Block(index), 
                        timestamp,prev_hash,index)
    
    def get_all(self):
        return self.blocks[:]
    
    def add_transaction(self,transaction:Transaction):
        # if valid
        return self.ledger[self.get_last_hash()].add_transaction(transaction)
    
    def chain_index(self):
        return len(self.blocks)