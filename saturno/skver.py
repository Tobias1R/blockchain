import binascii
from pprint import pp, pprint
import tty

from cryptochain import SigningKey, VerifyingKey, BadDigestError, BadSignatureError
from coin import CURVE,SHA
from cryptochain.util import orderlen
from util import sigencode_string
def number_to_string(num, order):
    l = orderlen(order)
    fmt_str = "%x" + str(2 * l)
    string = binascii.unhexlify(str(num).encode())
    assert len(string) == l, (len(string), l)
    return string
SEP = b'|'
SEPTD = b'#s'
SEPTR = b'|#|'
INPUT_SIGNAL = b'<'
OUTPUT_SIGNAL = b'>'
DESTINATION_ADDR = b'ad689f9e10651009d0d1afbe16cc48e0417ce2c51401b46bcbd500cd55e47ad3'
TRANSACTION_ID = b'a1fcad59c8df51a29d841c87f7ffab84fa9960ca8413ff33e194fbf14917c6a7'
# fixed sizes
transaction_data = b'0000' #version
transaction_data += TRANSACTION_ID # transaction id
transaction_data += INPUT_SIGNAL #input=1/output=2


transaction_data += b'100' # amount
transaction_data += SEP
transaction_data += b'1' # sequence
transaction_data += SEP
transaction_data += b'10000100001000010000' # locktime
transaction_data += SEP
transaction_data += b'0' # output index
transaction_data += SEP
transaction_data += b'1' # confirmations
transaction_data += SEP+DESTINATION_ADDR
transaction_data += SEPTD

sk = SigningKey.generate(curve=CURVE)

'''
td max size 303
signature has 132 bytes long
hexdigest 64
'''

public_key = sk.verifying_key.to_pem()
digest = SHA(transaction_data+DESTINATION_ADDR).hexdigest().encode()
import base64
def convert64(data):
    return base64.b64encode(data)


#print(sk.verifying_key.to_string()) 
signature = base64.b64encode(sk.sign_digest_deterministic(digest,hashfunc=SHA,sigencode=sigencode_string))
data = transaction_data+signature 

# OUTPUT
transaction_data = b'0000' #version
transaction_data += TRANSACTION_ID # transaction id
transaction_data += OUTPUT_SIGNAL #input=1/output=2
transaction_data += b'50' # amount
transaction_data += SEP
transaction_data += b'1' # sequence
transaction_data += SEP
transaction_data += b'10000100001000010000' # locktime
transaction_data += SEP
transaction_data += b'1' # output index
transaction_data += SEP
transaction_data += b'1' # confirmations
transaction_data += SEP+DESTINATION_ADDR

transaction_data += SEPTD
output_data = transaction_data+DESTINATION_ADDR
print('INPUT',data)
print('OUTPUT',output_data)
print('size:',len(data))
td, sig = data.split(SEPTD)
otd, destination = output_data.split(SEPTD)
print('extract',td.split(SEP))
#--------------------------------------------------------------------------
# the other side
vk = VerifyingKey.from_public_key_recovery_with_digest(
    signature=base64.b64decode(sig),digest=digest,curve=CURVE,hashfunc=SHA
)
#print(vk)
for v in vk:
    try:
        print(v.verify_digest(base64.b64decode(sig),digest))
    except:
        print('fail')
transactions = [td,otd]
#print(transactions)
for t in transactions:
    # a list with transactions that generated outputs for my wallet
    fixed,sequence,locktime,vout,confirmations,address = t.split(SEP)
    version = fixed[:4]
    txid = fixed[4:68]
    ttype = fixed[68:69]
    amount = fixed[69:]
    #print(version,txid,ttype,amount)
    if ttype==INPUT_SIGNAL:
        print('+',float(amount))
    if ttype==OUTPUT_SIGNAL:
        print('-',float(amount))

TRANSACTIONS_FILE = '/home/ozy/BLOCK_ENV/blockchain/data/transactionsv2.bin'
import mmap
with open(TRANSACTIONS_FILE,'wb') as f:
    f.write(data)
    f.write(SEPTR)
    f.write(output_data)
from chainv2 import ChainTransaction
transactions_found=[]
with open(TRANSACTIONS_FILE,'r+b') as f:
    node = mmap.mmap(f.fileno(),0)
    # mounting the transaction
    
    start=0
    nodefind=node.find(TRANSACTION_ID,start)
    while nodefind>=0:
        node.seek(start)
        end_of_data=node.find(SEPTR,start)
        t=node.read(end_of_data-start)
        transactions_found.append(ChainTransaction.read_data_bytes(t))     
        start=node.tell()+len(SEPTR)    
        end_of_data=node.find(SEPTR,start+2)    
        nodefind=node.find(TRANSACTION_ID,start,end_of_data)
        print(nodefind,start,end_of_data)
    # #print(node.read(-1))
    # # search addr
    # position_addr = node.find(DESTINATION_ADDR,0)
    # position_output = node.find(SEPTR,position_addr-200,position_addr)
    # #print(node[position_output+len(SEPTR):])
    # t=node[position_output+len(SEPTR):]
    # fixed,sequence,locktime,vout,confirmations = t.split(SEP)
    # version = fixed[:4]
    # txid = fixed[4:68]
    # ttype = fixed[68:69]
    # amount = fixed[69:]
    # #print(version,txid,amount,ttype,DESTINATION_ADDR)
    # c=ChainTransaction(
    #     txid=TRANSACTION_ID,
    #     version=version,
    #     direction=ttype,
    #     amount=amount,
    #     sequence=sequence,
    #     output_index=vout,
    #     confirmations=confirmations[:1],        
    #     address=DESTINATION_ADDR,
    #     signature=signature)
    # print('INFO',c.info())
    # print('DATA',c.dump_data_bytes())
    # colunms = ['txid','vout','address','scriptPubkey','amount','confirmations']
    # values = [txid,vout,DESTINATION_ADDR,DESTINATION_ADDR,amount,confirmations[:2]]
    # #pprint(dict(zip(colunms,values)))

print(transactions_found)

c=ChainTransaction(
            txid=txid,
            version=version,
            direction=ttype,
            amount=amount,
            locktime_value=locktime,
            sequence=sequence,
            output_index=vout,
            confirmations=confirmations[:1],        
            address=address,
            signature=signature)
for tx in transactions_found:
    pprint(tx.info())


