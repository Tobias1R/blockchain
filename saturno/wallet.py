import base64
from datetime import datetime
from os import urandom
import os
from re import I
from cryptochain import SigningKey, BadDigestError, BadSignatureError
import json
from cryptochain.util import randrange_from_seed__trytryagain
from coin import CURVE,SHA, XIL,__version__
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from blockchain import Blockchain, locktime
from chain import InputTransaction, OutputTransaction, Transaction

class Wallet:
    def __init__(self,pem_data:str,password:str,) -> None:
        self.blockchain:Blockchain = None
        self.sk = SigningKey.from_pem(pem_data)
        self.vk = self.sk.get_verifying_key()
        self.private_key = self.sk.privkey
        self.full_public_key = self.sk.verifying_key.to_pem(
            point_encoding="compressed",)
        
        self.signature = self.sk.sign_deterministic(
                        data=self.public_key_digest(),
                        hashfunc=SHA)
        self.digest_signature = self.sk.sign_digest_deterministic(
                                        self.public_key.encode(),
                                        hashfunc=SHA)  
        
        self.label = ''        
        self._balance = 0.00
        self.output_index = 0
        self.my_tokens = []
        self.outputs = []
        self.processed_transactions = []
    
    def connect(self,source):
        self.blockchain = source
        self.process_blockchain()
    
    def is_connected(self):
        return bool(self.blockchain)
    
    @property 
    def first_output(self):
        return len(self.outputs)+1
    
    @property
    def public_key(self):
        data = self.full_public_key
        return SHA(data).hexdigest()
    
    def public_key_digest(self):
        data = self.full_public_key
        return SHA(data).digest()
    
    def pubkey_script(self):
        return self.public_key.encode()+self.digest_signature
        
    @classmethod
    def generate_key(cls,password):
        secexp = randrange_from_seed__trytryagain(password, 
                                                  CURVE.order)
        return SigningKey.from_secret_exponent(secexp, 
                                               curve=CURVE,
                                               hashfunc=SHA)
    
    @classmethod
    def generate_fernet_key(self,password:bytes,salt):
        key = b''
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=390000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))  
        return key
    
    @classmethod
    def generate_wallet_file(cls,data:bytes,label:str,path_wallet):
        if path_wallet:
            file = os.path.join(path_wallet,label+'.walt')
        else:
            file = label+'.walt'
        with open(file,'wb') as f:
            f.write(data)
    
    @classmethod
    def decrypt_wallet(cls,filedata:bytes,password:str):
        data = ''
        salt, filebytes = filedata.split('#$#$'.encode())
        key = cls.generate_fernet_key(password.encode(),salt)
        fernet = Fernet(key)
        data = fernet.decrypt(filebytes)
        return data
    
    @classmethod
    def generate_wallet(cls,
                        label:str='New Wallet',
                        password:str='abc321',
                        generate_file=False,
                        path_wallet=None
                        ):
        password = password.encode()
        sk = cls.generate_key(password)
        pk = sk.verifying_key.to_pem()
        salt = os.urandom(16)
        key = cls.generate_fernet_key(password,salt)      
        fernet = Fernet(key)
        file_data = salt+str('#$#$').encode()+fernet.encrypt(sk.to_pem())
        if generate_file:
            cls.generate_wallet_file(file_data,label,path_wallet)
        return (sk.to_pem(),pk,label+str('.walt'),file_data)
    
    @classmethod
    def open_wallet(cls,file,password):
        '''Open Wallet from file'''
        try:
            with open(file,'rb') as f:
                filedata = f.read(-1)
                pem_data = cls.decrypt_wallet(filedata,password)
                wallet = cls(pem_data=pem_data,password=password)
        except Exception as e:
            print(e)
            print('Invalid password')
            return None
        return wallet
    #
    @property
    def balance(self,force=False):
        if self._balance and not force:
            return self._balance
        print('computing balance')
        total = 0.00
        output_index = 0
        transactions = self.blockchain.chain_transactions
        #print(transactions[b'c956a1edb2b32b64da3d1311cff95757c210e80f50f5578afb2aaefe19722620'].inputs[0].amount)
        for t in transactions:
            if len(transactions[t].inputs) > 0:
                for i in range(len(transactions[t].inputs)):
                    transac:InputTransaction = transactions[t].inputs[i]
                    #print('TRANSAC',transac)
                    # check for received tokens                    
                    token = transac.token_data(self.public_key.encode())
                    #print('TEST TOKEN',token)#==b'ea781b13698c31b8c7588a32509a032d18142c0ba1f3a6c48e765a6bdc494bd7')
                    if transac.validate_token(token):
                        total += float(int(transac.amount))
                        self.output_index+=len(self.outputs)
                        #b'e8fba24ba7125c49ee37e8d5005307086eb95edd7e4a5f8a8c6e179b8095ed67'
                    input:InputTransaction = transac
                    # lets assume for a momment, that all transactions here are ok
                    if input.issuer_public_key_full == self.public_key_digest():
                        total -= float(int(input.amount))            
        return total*XIL
    
   
    
    def process_blockchain(self,):
        total = 0.00
        output_index = 0
        transactions = self.blockchain.chain_transactions
        my_public_key = self.public_key.encode()
        for t in transactions:
            if len(transactions[t].inputs) > 0:
                for i in range(len(transactions[t].inputs)):
                    transac:InputTransaction = transactions[t].inputs[i]
                    if transac.hash not in self.processed_transactions:
                        # check for received tokens
                        token = transac.token_data(self.public_key.encode())                    
                        if transac.validate_token(token):
                            total += float(int(transac.amount))
                            self.output_index+=len(transactions[t].outputs)+1 
                            self.my_tokens.append(token)                           
                        # lets assume for a momment, that all 
                        # transactions here are ok
                        if transac.issuer_public_key_full == self.public_key_digest():
                            output:OutputTransaction = transac.get_output() 
                            total -= float(int(output.amount))
                            self.outputs.append(output)
                        self.processed_transactions.append(transac.hash)    
        self._balance = total
        
    def input_transaction(self,public_key:bytes,amount:int):
        self.process_blockchain()
        if self.first_output:
            
            transaction_id = self.blockchain.get_transaction_id()
            i:InputTransaction = InputTransaction()
            i.amount = amount
            i.issuer_public_key_full = self.public_key_digest()
            i.locktime=locktime(fill_encoded=True)
            i.output_index=len(self.outputs)+1
            i.sequence=transaction_id-1
            #i.public_key=public_key
            i.transaction_id=transaction_id
            #build transaction data
            #transaction_data:bytearray = public_key.encode()
            transaction_data = str(int(amount)).zfill(20).encode()
            transaction_data += str(int(i.sequence)).zfill(20).encode()
            transaction_data += i.locktime
            transaction_data += str(i.transaction_id).zfill(20).encode()
            transaction_data += str(len(self.outputs)+1).zfill(20).encode()            
            
            token = SHA(transaction_data+public_key).hexdigest().encode()

            i.token_signature = self.sk.sign_deterministic(
                    token,hashfunc=SHA)
            
            data_signed = SHA(transaction_data+self.public_key_digest()).digest()
            public_key_signature = self.sk.sign_digest_deterministic(
                    data_signed,hashfunc=SHA)
            i.signature=public_key_signature 
            #print(i.locktime,i.get_locktime())
            print(transaction_data)
            #print(i.dump_data_bytes())       
            self.blockchain.transaction_requests.append(i)
        else:
            print('DUDE, YOUR\'re POOR.')
    
    def info(self,):
        inf = {
            'address': self.public_key,
            'version': __version__,
            'connection': self.is_connected(),
            'public_key':self.full_public_key,
            'digest':self.public_key_digest()
        }
        return inf
    
    def validate_token(self,transaction:InputTransaction):
        vals = []
        
        v_token_signature = transaction.token_signature
            
        vk = self.sk.get_verifying_key() 
        v_token = SHA(transaction.get_transaction_data()+self.public_key.encode()).hexdigest().encode()    
        try:
            vals.append(vk.verify_digest(signature=v_token_signature,
                                            digest=v_token)) 
            return True
        except BadSignatureError as bse:
            pass
        except BadDigestError:
            pass    
        return any(vals)