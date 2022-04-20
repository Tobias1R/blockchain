from abc import abstractmethod
from datetime import datetime
from tkinter import SEPARATOR

from coin import CURVE, SHA, XIL, __version__, INPUT_TRANSACTION_DATA_SIZE
from cryptochain import VerifyingKey, BadDigestError, BadSignatureError

TRANSACTION_STATUS_CONFIRMED = 'C'
TRANSACTION_STATUS_INVALID = 'I'
TRANSACTION_STATUS_PENDIND = 'Q'
TRANSACTION_STATUS_DENIED = 'D'

BLOCK_DATA_SIZE = 128
LEDGER_DATA_SIZE = 437
TIME_FACTOR = 0.000001

#2022-01-21 00:24:29.505570
#20220121002429505570
def locktime(fill_encoded=False):
    lock:bytearray = str(datetime.utcnow()).replace('-','').replace(' ','').replace(':','').replace('.','').encode()
    if fill_encoded:
        pass
        #return str(int(lock)).zfill(20).encode()
    return lock

def read_locktime(data:bytes):
    year=int(data[:4])
    month=int(data[4:6])
    day=int(data[6:8])
    hour=int(data[8:10])
    minute=int(data[10:12])
    second=int(data[12:14])
    microsecond=int(data[14:])
    return datetime(year=year,
                    month=month,
                    day=day,
                    hour=hour,
                    minute=minute,
                    second=second,
                    microsecond=microsecond)

def convert_locktime(lockt:datetime,fill_encoded=True):
    if isinstance(lockt,bytes):
        return lockt
    lock = str(lockt).replace('-','').replace(' ','').replace(':','').replace('.','')
    if fill_encoded:
        pass
        #return str(int(lock)).zfill(20).encode()
    return lock.encode()

# def locktime(fill_encoded=False):
#     lock = int(datetime.utcnow().timestamp()/TIME_FACTOR)
#     if fill_encoded:
#         return str(int(lock)).zfill(20).encode()
#     return lock

# def read_locktime(data:bytes):
#     timedata = float(int(data)*TIME_FACTOR)
#     return datetime.utcfromtimestamp(timedata)

# def convert_locktime(lockt:datetime,fill_encoded=True):
#     lock = int(lockt.timestamp()/TIME_FACTOR)
#     if fill_encoded:
#         return str(int(lock)).zfill(20).encode()
#     return lock

class ByteNode:
    SEPARATOR = b'|#'
    DATA_SIZE = 64
    data_dict = {}
    
    @abstractmethod
    def read_data_bytes(cls,transaction_node:bytes):
        '''All subclasses must have'''
        pass
    
    @abstractmethod
    def dump_data_bytes(self):
        '''All subclasses must have'''
        pass
    
    
    @property
    def hash(self):
        return SHA(self.dump_data_bytes()).hexdigest().encode()

class OutputTransaction(ByteNode):
    def __init__(self) -> None:
        #self.token:bytearray=None        
        self.public_key:bytearray=None
        self.amount:float=None
        self.sequence:int=None
        self.locktime:float=datetime.utcnow().timestamp()
        self.transaction_id:int=None
        self.output_index:int=None
    
    
    @classmethod
    def read_data_bytes(cls,transaction_node:bytes):
        c_data = transaction_node # transaction data
        tn = cls()
        
        tn.amount=float(int(c_data[:20]))
        tn.sequence=int(c_data[20:40])
        tn.locktime=read_locktime(c_data[40:60])
        tn.transaction_id=int(c_data[60:80])
        tn.output_index=int(c_data[80:100])
        
        return tn
    
    def token_data(self,public_key:bytes)->bytearray:
        data=self.dump_data_bytes()
        data+=public_key
        return SHA(data).hexdigest().encode()
        
        
        
    
    def dump_data_bytes(self):
        transaction_node:bytearray = bytearray()
        
        transaction_data = str(int(self.amount)).zfill(20).encode()
        transaction_data += str(int(self.sequence)).zfill(20).encode()
        transaction_data += convert_locktime(self.locktime)
        transaction_data += str(int(self.transaction_id)).zfill(20).encode()
        if isinstance(self.output_index,OutputTransaction):
            transaction_data += self.output_index.output_index
        else:
            transaction_data += str(int(self.output_index)).zfill(20).encode()
          
                   
        transaction_node+=transaction_data      
        
        return transaction_node
    
class InputTransaction(ByteNode):
    def __init__(self) -> None:
        self.version:bytearray=__version__
        self.signature:bytearray=None
        self.issuer_public_key_full:bytearray=None
        #self.token:bytearray=None
        self.token_signature:bytearray=None
        self.public_key:bytearray=None
        self.amount:float=None
        self.sequence:int=None
        self.locktime:float=datetime.utcnow().timestamp()
        self.transaction_id:int=None
        self.output_index:int=None
    
    @classmethod
    def read_data_bytes(cls,transaction_node:bytes):
        c_version = transaction_node[:4]
        c_data = transaction_node[4:104]
        c_pubkey_data = transaction_node[104:]
        v_token_signature = c_pubkey_data[:132]
        v_data_sign = c_pubkey_data[132:264]        
        v_full_pk_data = c_pubkey_data[264:]
        tn = cls()
        tn.version=c_version
        # pubkeyscript data
        tn.issuer_public_key_full = v_full_pk_data
        tn.signature = v_data_sign
        # token data
        tn.token_signature = v_token_signature
        
        # this is that data that will generate the token
        #tn.public_key = td[:64]
        tn.amount=float(int(c_data[:20]))
        tn.sequence=int(c_data[20:40])
        tn.locktime=read_locktime(c_data[40:60])
        tn.transaction_id=int(c_data[60:80])
        tn.output_index=int(c_data[80:100])
        
        return tn
    
    def get_locktime(self):
        return convert_locktime(self.locktime)
        
    def get_transaction_data(self):
        transaction_data = str(int(self.amount)).zfill(20).encode()
        transaction_data += str(int(self.sequence)).zfill(20).encode()
        transaction_data += convert_locktime(self.locktime)
        transaction_data += str(int(self.transaction_id)).zfill(20).encode()
        transaction_data += str(self.output_index).zfill(20).encode()    
        return transaction_data
    
    def dump_data_bytes(self):
        transaction_node:bytearray = bytearray()
        version = __version__        
            
        transaction_data = str(int(self.amount)).zfill(20).encode()
        transaction_data += str(int(self.sequence)).zfill(20).encode()
        transaction_data += convert_locktime(self.locktime)
        transaction_data += str(int(self.transaction_id)).zfill(20).encode()
        transaction_data += str(self.output_index).zfill(20).encode()            
        transaction_node+=transaction_data                
        #pubkey script
        pubkey_script_data=self.token_signature+self.signature
        pubkey_script_data+=self.issuer_public_key_full            
        #data_sign+full_pk_data+token_sign        
        #data = amount+sequence+locktime+transaction_id+output_index
        transaction_data = version+transaction_data+pubkey_script_data    
        
        return transaction_data

    def output(self,output_index)->OutputTransaction:
        ot = OutputTransaction()
        ot.amount=self.amount
        ot.locktime=self.locktime
        ot.output_index=output_index
        ot.sequence=self.sequence
        ot.transaction_id=self.transaction_id
        
        return ot
    
    def token_data(self,public_key:bytes)->bytearray:
        data=self.get_transaction_data()
        data+=public_key
        return SHA(data).hexdigest().encode()
    
    def get_output(self):
        return self.output(self.output_index)
    
    def get_verification_key(self,):
        v_full_pk_data = self.issuer_public_key_full    
        data_sign = self.signature
        data_digest = SHA(self.get_transaction_data()+v_full_pk_data).digest()
        vks = VerifyingKey.from_public_key_recovery_with_digest(
                signature=data_sign,
                digest=data_digest,
                curve=CURVE,
                hashfunc=SHA
            )
        return vks

    def is_signature_valid(self):
        transaction = self
        vals = []
        v_full_pk_data = transaction.issuer_public_key_full    
        vdata_digest = SHA(transaction.get_transaction_data()+v_full_pk_data).digest()    
        
        vks = self.get_verification_key()   
        #v_token = SHA(p_data+p_public_key).hexdigest().encode()
        for vk in vks:
            try:
                vk.verify_digest(transaction.signature,
                                digest=vdata_digest)
                vals.append(True)
            except BadSignatureError as bse:
                print(bse)
                pass
            except BadDigestError:
                pass    
        return any(vals)
        
    def validate_token(self,token:bytes):
        transaction = self
        vals = []
        if self.is_signature_valid(): 
            vks = self.get_verification_key()   
            for vk in vks:
                try:
                    vk.verify(transaction.token_signature,data=token)
                    vals.append(True)
                except BadSignatureError as bse:
                    pass
                except BadDigestError:
                    pass    
        return any(vals)

        

class Transaction(ByteNode):
    SEPARATOR = b'|#|' #this is expensive
    SEPARATOR_INPUTS = b'>||'
    def __init__(self) -> None:
        # a list of inputs
        self.inputs:list[InputTransaction]=[]
        # a list of outputs
        self.outputs:list[OutputTransaction]=[]
        # the input that originated the transaction
        
        # 
        #self.output=input.output(output_index)
    
    def add_input(self,input:InputTransaction):
        
        # the first validation
        # checks if the provided public key was used with a private key
        # to sign the data of the input transaction
        if input.is_signature_valid():
            self.inputs.append(input)
            self.add_output(input.get_output())
        else:
            raise BadSignatureError("Signature verification failed", input)
    
    def add_output(self,output:OutputTransaction):
        self.outputs.append(output)
    
    def dump_data_bytes(self,):
        ba:bytearray = bytearray()
        
        for i in self.inputs:
            ba += i.dump_data_bytes()        
        ba += self.SEPARATOR_INPUTS
        
        for o in self.outputs:
            ba += o.dump_data_bytes()
        #ba += self.output.dump_data_bytes()
        ba += self.SEPARATOR
        return ba
    
    @classmethod
    def no_outputs_in_bytes(cls,byte:bytes):
        '''Return true if no outputs found in transaction'''
        return bool(cls.SEPARATOR_INPUTS+cls.SEPARATOR in byte)
    
    @classmethod
    def read_data_bytes(cls,byte:bytes):
        #print(byte)
        # read inputs
        # find separator in bytes
        t = cls()
        start = 0
        position_separator = byte.find(t.SEPARATOR_INPUTS,start)
        #print(position_separator)
        
        while start+INPUT_TRANSACTION_DATA_SIZE <= position_separator+1:
            bi = byte[start:start+INPUT_TRANSACTION_DATA_SIZE]
            #print(bi)
            i:InputTransaction = InputTransaction.read_data_bytes(bi)
            #print(i.amount)
            t.inputs.append(i)
            start = start+INPUT_TRANSACTION_DATA_SIZE
        start = position_separator+position_separator
        
        
        #print(o.dump_data_bytes()==byte[752:])
        return t
        
        
class Block(ByteNode):
    SEPARATOR = b'#'
    MAX_TRANSACTIONS = 100
    def __init__(self) -> None:
        self.transactions:list[Transaction] = []
        self.locktime:int=locktime()
        self.status = 1 # open
    
    def block_data(self):
        ba:bytearray = bytearray()
        ba += __version__
        ba += locktime(fill_encoded=True)
        for t in self.transactions[:self.MAX_TRANSACTIONS]:
            #print('TT',t.input.public_key)
            if isinstance(t,Transaction):
                ba += SHA(t.dump_data_bytes()).hexdigest().encode()
            else:
                ba += SHA(t).hexdigest().encode()
        ba += self.SEPARATOR
        return ba

# class Chain:
#     SEPARATOR = None
#     def __init__(self) -> None:
#         self.transactions = []
#         self.max = 99999999999999
    
#     def dump_data_bytes(self,):
#         ba:bytearray = bytearray()
#         for t in self.transactions:
#             if isinstance(t,str):
#                 data = t.encode()
#             else:
#                 data = t
#         ba += t        
#         return ba
    
#     @classmethod
#     def read_data_bytes(cls,byte:bytes):
        
#         return i
    
#     def __iter__(self):
#         self.n = 0
#         return self.transactions
    
#     def __next__(self):
#         if self.n <= self.max:
#             self.n += 1
#             return self.transactions[self.n]
#         else:
#             raise StopIteration