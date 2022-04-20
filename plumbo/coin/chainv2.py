from abc import abstractmethod
from audioop import add
import base64
from datetime import datetime
from multiprocessing.sharedctypes import Value
from os import urandom
from tkinter import SEPARATOR

from . import CURVE, SHA, XIL, __version__, INPUT_TRANSACTION_DATA_SIZE
from plumbo.cryptochain import VerifyingKey, BadDigestError, BadSignatureError,SigningKey

TRANSACTION_STATUS_CONFIRMED = b'C'
TRANSACTION_STATUS_INVALID = b'I'
TRANSACTION_STATUS_PENDING = b'Q'
TRANSACTION_STATUS_DENIED = b'D'

BLOCK_DATA_SIZE = 128
LEDGER_DATA_SIZE = 437
TIME_FACTOR = 0.000001

def write_number(number):
    return hex(number).encode()

def read_number(byte):
    #print('BYTE',byte)
    return int(byte,16)

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
        #transaction data
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
        '''
        Extract issuer public key from digest.
        '''
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
        '''
        Check if transaction data was signed using the provided public key.
        '''
        transaction = self
        vals = []
        v_full_pk_data = transaction.issuer_public_key_full    
        vdata_digest = SHA(transaction.get_transaction_data()+v_full_pk_data).digest()    
        
        vks = self.get_verification_key()   
        #v_token = SHA(p_data+p_public_key).hexdigest().encode()
        for vk in vks:
            try:
                vals.append(vk.verify_digest(transaction.signature,
                                digest=vdata_digest))
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

        

class ChainTransaction(ByteNode):
    SEPARATOR = b'|#|' #this is expensive
    CONFIRMATION_SIGNAL = b'!'
    FEE_SIGNAL = b'@'
    SEP = b'|'
    SEPTD = b'#s'
    SEPTR = b'|#|'
    INPUT_SIGNAL = b'<'
    OUTPUT_SIGNAL = b'>'
    COINBASE_SIGNAL=b'$'
    
    def __init__(self,
                 txid,
                 version,
                 direction,
                 amount,
                 locktime_value,
                 sequence,
                 output_index,
                 address,
                 confirmations,
                 signature,
                 account=b'',
                 
                 ) -> None:
        self.version=version
        self.txid=txid
        self.direction=direction
        self.amount=amount
        self.locktime=locktime_value
        self.sequence=sequence
        self.output_index=output_index
        self.address=address
        self.account=account
        self.signature=signature
        # total of confirmations
        self.confirmations:int=confirmations
        # fee
        self.fee=XIL/XIL # 1
        # coinbased
        self.coinbased=False
        
    
    def confirm(self):
        self.confirmations+=1
    
    def get_amount(self):
        return read_number(self.amount)
        if isinstance(self.amount,bytes):
            return int(self.amount)
        return self.amount
    
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
        output.output_index = len(self.outputs)+1
        self.outputs.append(output)
    
    def dump_data_bytes(self,):
        transaction_data = self.version #version
        #transaction_data += self.txid # transaction id
        #transaction_data += self.direction #input=1/output=2
        transaction_data += self.SEP
        transaction_data += write_number(self.amount) # amount
        transaction_data += self.SEP
        transaction_data += write_number(self.sequence) # sequence
        transaction_data += self.SEP
        transaction_data += self.locktime # locktime
        transaction_data += self.SEP
        transaction_data += write_number(self.output_index) # output index
        transaction_data += self.SEP
        transaction_data += write_number(self.confirmations) # confirmations
        transaction_data += self.SEP
        transaction_data+=self.address
        
        #if self.direction==self.INPUT_SIGNAL:
        transaction_data += self.SEPTD
        transaction_data+=self.signature
        
        transaction_data+=self.SEPARATOR
        return transaction_data
    
    def signature_data(self):
        transaction_data = self.version #version
        transaction_data += self.txid # transaction id
        #transaction_data += self.direction #input=1/output=2
        transaction_data += write_number(self.amount) # amount
        transaction_data += write_number(self.sequence) # sequence
        transaction_data += self.locktime # locktime
        transaction_data += write_number(self.output_index) # output index
        transaction_data+=self.address
        transaction_data+=self.signature
        return SHA(transaction_data).hexdigest().encode()
    
    def info(self):
        colunms = ['txid','vout','address','scriptPubkey','amount','confirmations']
        txid=self.txid
        vout=self.output_index
        
        values = [txid,vout,self.address,self.address,self.amount,self.confirmations]
        return dict(zip(colunms,values))
    
    def generate_output(self,amount,address,output_index,lockt):
        c:ChainTransaction(
            txid=self.txid,
            amount=amount,
            address=address,
            confirmations=self.confirmations,
            direction=self.OUTPUT_SIGNAL,
            locktime_value=lockt,
            output_index=output_index,
            sequence=self.sequence,            
        )
        return c
    

    @classmethod
    def no_outputs_in_bytes(cls,byte:bytes):
        '''Return true if no outputs found in transaction'''
        return bool(cls.SEPARATOR_INPUTS+cls.SEPARATOR in byte)
    
    @classmethod
    def read_data_bytes(cls,byte:bytes):
        #print('BYTE',byte)
        # read inputs
        # find separator in bytes
        if byte:
            td, signature = byte.split(cls.SEPTD)
            #print('TDDDDDDDDDDD',td,signature)
            try:
                version,amount,sequence,locktime,vout,confirmations,address = td.split(cls.SEP)
            except ValueError:
                return False
            
            # if cls.INPUT_SIGNAL in byte:
                
            # elif cls.OUTPUT_SIGNAL in byte:
            #     td = byte.split(cls.SEPTD)
            #     signature=b''
            #     #print('TD',td)
            #     fixed,sequence,locktime,vout,confirmations,address = td[0].split(cls.SEP)
            # version = fixed[:4]
            # # txid = fixed[4:68]
            # # ttype = fixed[68:69]
            # # amount = fixed[69:]
            # amount = fixed[4:]
            #print(txid,amount,ttype,address)
            c=ChainTransaction(
                txid=b'',
                version=version,
                direction=b'',
                amount=read_number(amount),
                locktime_value=locktime,
                sequence=read_number(sequence),
                output_index=read_number(vout),
                confirmations=read_number(confirmations[:1]),        
                address=address,
                signature=base64.b64decode(signature)
                )
            
            return c
    
    def __str__(self) -> str:
        return str(self.signature_data().decode())

class Transaction(ByteNode):
    SEPARATOR_INPUTS = b'>||'
    SEPARATOR_OUTPUTS= b'||<'
    SEPARATOR_TRANSACTION=b'!TRC'
    SEPARATOR=SEPARATOR_TRANSACTION
    def __init__(self,issuer_public_key,first_input:ChainTransaction) -> None:
        self.txid=b''
        self.version=__version__
        self.inputs:list[ChainTransaction]=[first_input,]
        self.outputs:list[ChainTransaction]=[]
        self.issuer_public_key=issuer_public_key
        self.fee=XIL
        self.signature=b''
        self.status=TRANSACTION_STATUS_PENDING
        self._bytenode=b''
        
    def check_address(self,address:bytes):
        #print('CHECKING',address)
        if self.issuer_public_key==address:
            return True
        for o in self.outputs:
            if o:
                if o.address==address:
                    return True
        for i in self.inputs:
            if i:
                if i.address==address:
                    return True
        return False
    
    def dump_data(self):
        return self.dump_data_bytes()
        
    def dump_data_bytes(self,):
        data:bytes=__version__
        data+=self.txid
        data+=self.issuer_public_key
        data+=self.SEPARATOR_INPUTS
        for t in self.inputs:
            data+=t.dump_data_bytes()
        data+=self.SEPARATOR_OUTPUTS
        for t in self.outputs:
            t.signature=b'!'
            data+=t.dump_data_bytes()
        data+=self.SEPARATOR_TRANSACTION
        return data
    
    @classmethod
    def read_data_bytes(cls, byte: bytes):
        if byte:
            
            version_id,data=byte.split(cls.SEPARATOR_INPUTS)        
            version=version_id[:4]
            
            txid=version_id[4:68]
            issuer_public_key=version_id[68:]
            inputs,outputs=data.split(cls.SEPARATOR_OUTPUTS)
            
            c=cls(issuer_public_key,None)
            c._bytenode=byte
            c.txid=txid
            c.version=version
            c.issuer_public_key=issuer_public_key
            for node in inputs.split(ChainTransaction.SEPTR):
                c.inputs.append(ChainTransaction.read_data_bytes(node))
            for node in outputs.split(ChainTransaction.SEPTR):
                c.outputs.append(ChainTransaction.read_data_bytes(node))
            return c
    
    def list_unspent(self,address):
        total = 0
        for t in self.inputs:
            if t:
                if t.address==address:
                    total += t.get_amount()
        for t in self.outputs:
            if t:
                if t.address==address:
                    total += t.get_amount()
        return total
    
    def get_output_address(self,address,value=False):
        #print('GETOUTPUTADDR',address)
        outs = []
        total = 0
        for out in self.outputs:
            if out:
                print('OUTPUTS/ADDR',out.address==address)
                if (out.address==address and 
                    out.direction==out.OUTPUT_SIGNAL):
                    outs.append(out)
                    total += out.get_amount()
                
        if value:
            return total
        return outs
    
    def value_for_address(self,address):
        return self.get_output_address(address,True)
        
    
    @property        
    def hash(self):
        data = self.dump_data()
        return SHA(data).hexdigest()
    
    def add_input(self,t:ChainTransaction):
        if not t in self.inputs:
            self.inputs.append(t)
    
    def add_output(self,t:ChainTransaction):
        if not t in self.outputs:
            #t.output_index=len(self.outputs)
            self.outputs.append(t)
    
    def add_transaction(self,t:ChainTransaction):
        if t.direction==t.INPUT_SIGNAL:
            self.add_input(t)
        if t.direction==t.OUTPUT_SIGNAL:
            self.add_output(t)
    
    
        
class Block(ByteNode):
    SEPARATOR = b'!BLK'
    MAX_TRANSACTIONS = 100
    OP_INDEX = b'('
    OP_NONCE = b')'
    def __init__(self,
                 last_chain_hash=0,
                 version=__version__,
                 minter_id=b'',
                 signing_key:SigningKey=None
                 ) -> None:
        self.transactions:list[Transaction] = []
        self.locktime:bytes=locktime(True)
        self.status = 1 # open
        self.miner_id=minter_id
        self.version=version
        self.last_chain_hash=last_chain_hash
        self.signing_key=signing_key
        self.coins = self.generate_coins()
        
    
    def generate_coins(self):
        from .minter import Mint
        m=Mint(last_chain_hash=self.last_chain_hash,
               version=self.version,
               minter_id=self.miner_id)
        m.generate()
        return m.coins
    
    def output_from_coins(self):
        coinbase_value = int(len(self.coins)/XIL)
        coindata = b''.join(self.coins)
        coindata+=hex(coinbase_value).encode()
        coindata+=self.miner_id
        coindata+=self.locktime
        coin_digest=SHA(coindata).hexdigest().encode()
        signature=base64.b64encode(self.signing_key.sign_digest_deterministic(
            digest=coin_digest,hashfunc=SHA
        ))
        ic=ChainTransaction(
            txid=coin_digest,
            version=self.version,
            direction=ChainTransaction.COINBASE_SIGNAL,
            amount=coinbase_value,
            locktime_value=self.locktime,
            sequence=0,
            output_index=0,
            address=coin_digest,
            confirmations=1,
            signature=signature
        )
        ot = Transaction(issuer_public_key=coin_digest,first_input=ic,)
        ot.txid=coin_digest
        
        op=ChainTransaction(
            txid=SHA(coindata).hexdigest().encode(),
            version=self.version,
            direction=ChainTransaction.OUTPUT_SIGNAL,
            amount=coinbase_value,
            locktime_value=self.locktime,
            sequence=1,
            output_index=0,
            address=self.miner_id,
            confirmations=1,
            signature=signature
        )
        ot.add_output(op)
        return ot
    
    def block_data(self,prev_hash, index, nonce):
        ba:bytearray = bytearray()
        ba += __version__ #4
        ba += locktime(fill_encoded=True) #20
        ba += str(prev_hash).encode() # 64
        ba += self.OP_INDEX
        ba += str(index).encode() 
        ba += self.OP_NONCE
        ba += str(nonce).encode()
        for t in self.transactions[:self.MAX_TRANSACTIONS]:
            #print('TT',t.input.public_key)
            if isinstance(t,Transaction):
                ba += t.hash.encode()
            else:
                ba += SHA(t).hexdigest().encode()
        
        ba += self.SEPARATOR
        return ba
