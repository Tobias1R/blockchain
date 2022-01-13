import ipaddress
import constants
from hashlib import sha512
from cryptography.fernet import Fernet
import json

from coin import Transaction, Block


tobias_wallet = ''


class Wallet:
    #hash_id:str = ''
    last_ip:ipaddress.IPv6Address = ''
    last_router:ipaddress.IPv6Address = ''
    fernet_key:str = ''
    balance:float  = 0.00
    label:str = ''
    tokens:list = []
    
    def __init__(self,hash_id:str,password:str,) -> None:
        self.fernet = Fernet(password)
        self.key = self.fernet.generate_key()
        self.data = self.decrypt(hash_id)
        self.wallet_hash = hash_id
    
    def identify_token(self,token,ledger_data):
        token_ledger = sha512(str(json.dumps(ledger_data)+str(self.key)).encode()).hexdigest()
        #print('TOKEN ID:',json.dumps(ledger_data))
        return bool(token==token_ledger)
    
    
    
    def download_ledge(self,server):
        
        ledger = server.ledger
        #print('LEDGER',ledger)
        for h in ledger:
            #print('HASH',h)
            if isinstance(ledger[h],Block):
                node = ledger[h]
            else:
                node:Block = Block.load_ledger_data(ledger[h],len(ledger))
            #print('LEDGER NODE TRANSACTIONS',node.get_transactions())
            for t in node.get_transactions():
                print('TRANSACTION',t.ledger_data)
                if self.identify_token(t.destination,t.ledger_data):
                    print('DUDE, you received something!')
                    self.balance += float(t.value)
                if self.identify_token(t.source,t.ledger_data):
                    self.balance -= float(t.value)
    
    @property
    def hash_id(self):
        return sha512(str(self.wallet_hash).encode()).hexdigest()
    
    
    def token(self, transaction:Transaction):
        transaction.source = self.hash_id
        print('TOKENIZE:',json.dumps(transaction.ledger_data))        
        return sha512(str(json.dumps(transaction.ledger_data)+str(self.key)).encode()).hexdigest()
    
    def send(self,destination:str,value:float):
        pass
    
    def decrypt(self,hash_id):
        return json.loads(self.fernet.decrypt(hash_id))
    
    @classmethod
    def generate_wallet(cls,label:str='New Wallet',password:str=''):
        key = Fernet.generate_key()
        fernet = Fernet(key)
        
        data = json.dumps({
                'hash_id':sha512(str(key).encode()).hexdigest(),
                'last_ip':cls.last_ip,
                'last_router':cls.last_router,
                #'key':str(key),
                'balance':0.00,
                'label':label
            }).encode()
        return (fernet.encrypt_at_time(data,1),key)
        