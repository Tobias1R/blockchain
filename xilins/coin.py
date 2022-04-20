import ipaddress
from hashlib import sha256, sha512
from datetime import datetime
import json
xil = 0.00000001
__xilinversion__ = '0.0.1-alpha-rc0'

class RouterReference:
    hash_id: str = ''
    ip_add: ipaddress.ip_address = ipaddress.ip_address('127.0.0.1')
    time_zone: str = '-0300'
    ip_port:int = 54514
    
    def __str__(self) -> str:
        return str(self.hash_id)+str(self.ip_add)+str(self.time_zone)+str(self.ip_port)
    
class WalletReference:
    last_router: RouterReference
    hash_id: str = ''
    
    def __init__(self,hash_id:str,router:str=None) -> None:
        self.hash_id = hash_id
        self.last_router = router
    
    def __str__(self) -> str:
        return str(self.last_router)+str(self.hash_id)

class Transaction:
    def __init__(self) -> None:
        self.destination: str = None
        self.source: str = None
        self.value: float = 0.00
        self.token: str = ''
        self.router: str = None
        self.status: str = 'CONFIRMED'        
        self.fee: float = xil
        self.fee_destination: str = None
        self.timestamp:str = ''
        
        
    
    @property
    def ledger_data(self):
        return [
            self.source,
            self.destination,
            self.value,
            self.router,
            self.status,            
            self.fee,
            self.fee_destination,
            self.timestamp,
            self.token
        ]
    
    @classmethod
    def load_ledger_data(cls,data):
        if isinstance(data,list):
            parsed = data
        else:
            parsed = json.loads(data)
        t = cls()
        t.source = parsed[0]
        t.destination = parsed[1]
        t.value = parsed[2]
        t.router = parsed[3]
        t.status = parsed[4] 
        t.fee = parsed[5]
        t.fee_destination = parsed[6]
        t.timestamp = parsed[7]
        t.token = parsed[8]
        return t
    
    def __str__(self) -> str:
        return str(self.destination)+str(self.source)+str(self.value)+str(self.router)+str(self.status)+self.token


class Xilin:
    value: float = xil
    
    def __init__(self) -> None:
        self._data = {}
    
    def __str__(self) -> str:
        return str(self.value)

class Block:
    MAX_TRANSACTIONS = 10
    transactions: list[Transaction] = []
    participants: list = []
    block_stamp: float = datetime.utcnow().timestamp()
    confirmations: list = []
    host: str = '127.0.0.1'
    ledger_index: int = 0
    # 0 = created
    # 1 = Opened
    # 2 = full
    # 3 = confirmed
    status: int = 0
    def __init__(self,ledger_index:int) -> None:
        self.transactions: list[Transaction] = []
        self.participants: list = []
        self.block_stamp: float = datetime.utcnow().timestamp()
        self.confirmations: list = []
        self.host: str = '127.0.0.1'
        self.ledger_index: int = ledger_index
        self.status:int = 1 #opened
        self.version:str = __xilinversion__
        
    
    def is_full(self):
        return bool(len(self.transactions) >= self.MAX_TRANSACTIONS)
    
    def add_transaction(self,transaction:Transaction):
        #print('ADDTRANSACTION')
        if len(self.transactions) <= self.MAX_TRANSACTIONS:
            #print('ADDTRANSACTION','<=')
            data = json.dumps(transaction.ledger_data,
                              separators=(',', ':'))
            data = transaction
            if not data in self.transactions:
                #print('ADDTRANSACTION','not in')
                self.transactions.append(data)
                return True            
        return False
    
    @classmethod
    def load_ledger_data(cls,data,ledger_index):
        print('LOADLEDGERDATA:::',data)
        # if isinstance(data,Block):
        #     data = Block()
        #     transactions = [Transaction.load_ledger_data(d) for d in parsed['transactions']]
        #     block = cls(ledger_index)
        #     block.transactions = transactions
        #     block.block_stamp = parsed['block_stamp']
        #     block.confirmations = parsed['confirmations']
        #     block.host = parsed['host']
        #     block.participants = parsed['participants']
        #     block.status = parsed['status']  
            
        #     return data
        if isinstance(data,dict):
            parsed = data            
        else:
            parsed = json.loads(data)
        transactions = [Transaction.load_ledger_data(d) for d in parsed['transactions']]
        block = cls(ledger_index)
        block.transactions = transactions
        block.block_stamp = parsed['block_stamp']
        block.confirmations = parsed['confirmations']
        block.host = parsed['host']
        block.participants = parsed['participants']
        block.status = parsed['status']        
        return block
    
    def get_ledger_data(self,ret='json'):
        data = {}  
        #print(self.transactions)     
        if ret == 'json':
            transactions = [json.loads(l) for l in self.transactions]
        if ret == 'object':
            transactions = [l for l in self.transactions]
        data['transactions'] = transactions
        data['block_stamp'] = self.block_stamp
        data['confirmations'] = self.confirmations
        data['host'] = self.host
        data['participants'] = self.participants
        data['status'] = self.status
        return data
    
    def get_transactions(self):
        transactions = []
        for t in self.transactions:
            if isinstance(t,Transaction):
                transactions.append(t)
            elif isinstance(t,str):
                transactions.append(Transaction.load_ledger_data(t))
        
        return transactions
    
    def __str__(self) -> str:
        return 'BLOCK: transactions'+str(len(self.transactions))