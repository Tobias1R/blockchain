from hashlib import sha512
from datetime import datetime
import json
import math
import os
from coin import Transaction, Xilin, Block
from wallet import Wallet
import pickle
ozy = Wallet.generate_wallet('Ozymandias Wallet','plade33')

blocksfile = '/home/ozy/BLOCK_ENV/blockchain/xilins/blocks.pkl'
ledgerfile = '/home/ozy/BLOCK_ENV/blockchain/xilins/ledger.pkl'
participantsfile = '/home/ozy/BLOCK_ENV/blockchain/xilins/participants.pkl'
genesiswalletfile = '/home/ozy/BLOCK_ENV/blockchain/xilins/rootwallet.pkl'

TRANSACTION_STATUS_CONFIRMED = 'C'
TRANSACTION_STATUS_INVALID = 'I'
TRANSACTION_STATUS_PENDIND = 'Q'
TRANSACTION_STATUS_DENIED = 'D'

class Blockchain:

    def __init__(self):
        self.blocks = []
        self.ledger = {}
        self.participants = []
        self.genesis_wallet: Wallet = None
        if not self.validate_chain_files():
            self.set_genesis_block()
        #self.active_block:Block = self.get_active_block()
    
    def validate_chain_files(self):
        try:
            print('LOADING: ',blocksfile)
            with open(blocksfile,'rb') as f:
                self.blocks = pickle.load(f)
            
            print('LOADING: ',ledgerfile)
            with open(ledgerfile,'rb') as f:
                self.ledger = pickle.load(f)
            
            print('LOADING: ',participantsfile)
            with open(participantsfile,'rb') as f:
                self.participants = pickle.load(f)
            
            print('LOADING: ',genesiswalletfile)
            with open(genesiswalletfile,'rb') as f:
                self.genesis_wallet = pickle.load(f)
            
            return True
        
        except:
            return False
        
        
    
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
        t.value = 1000
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
        print('!!!NEW BLOCK FOUND!!! ITERATIONS:', nonce)
        if not hash in self.ledger:
            self.blocks.append(hash)
            self.ledger[hash] = self.active_block = data
            
        else:
            print('Duplicated block at',hash)
        
    
    def balance_source(self,source):
        balance = 0.00
        for h in self.ledger:
            node:Block = self.ledger[h]
            #print(node)
            for t in node.get_transactions():
                #t = Transaction()
                if t.source == source:
                    balance += float(t.value)
                if t.destination == source:
                    balance -= float(t.value)
        return balance
    
    def validate_transaction(self,transaction:Transaction):
        source = transaction.source        
            
        balance = self.balance_source(source=source)
        #print('VALIDATE',source,balance)
        transaction_value = transaction.value + transaction.fee
        if balance - transaction_value < 0:
            return TRANSACTION_STATUS_INVALID
        return TRANSACTION_STATUS_CONFIRMED
    
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
    
    def count_transactions(self):
        total = 0
        for h in self.blocks:
            total += len(self.ledger[h].transactions)
        return total
    
    def add_transaction(self,transaction:Transaction):
        active_block = self.get_active_block()
        if active_block.is_full():
            self.ledger[self.get_last_hash()].status = 3            
            self.add_new_block()
        if self.validate_transaction(transaction) == TRANSACTION_STATUS_CONFIRMED:
            return self.ledger[self.get_last_hash()].add_transaction(transaction)
        print('INVALID TRANSACTION:',transaction.token)
    
    def chain_index(self):
        return len(self.blocks)
    
    def register_participant(self,participant_hash):
        if not participant_hash in self.participants:
            self.participants.append(participant_hash)
    
    def write_chain(self):
        #,self.ledger,self.participants,self.genesis_wallet)
        with open(blocksfile,'wb') as f:
            data = self.blocks
            pickle.dump(data,
                        f,
                        protocol=pickle.HIGHEST_PROTOCOL)
        
        with open(ledgerfile,'wb') as f:
            data = self.ledger
            pickle.dump(data,
                        f,
                        protocol=pickle.HIGHEST_PROTOCOL)
        
        with open(participantsfile,'wb') as f:
            data = self.participants
            pickle.dump(data,
                        f,
                        protocol=pickle.HIGHEST_PROTOCOL)
        
        with open(genesiswalletfile,'wb') as f:
            data = self.genesis_wallet
            pickle.dump(data,
                        f,
                        protocol=pickle.HIGHEST_PROTOCOL)
            