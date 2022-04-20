import time
from cryptochain import VerifyingKey, SigningKey, BadDigestError, BadSignatureError
from coin import SHA, XIL,CURVE
from cryptochain.util import randrange_from_seed__trytryagain
from chain import InputTransaction, OutputTransaction, locktime, read_locktime,convert_locktime
from wallet import Wallet
from misc import bcolors
wallet_file = '/home/ozy/BLOCK_ENV/blockchain/wallets/tobias.walt'
tobias = Wallet.open_wallet(wallet_file,'plade33')
               
ROOT_PUBLIC_KEY = b'0000000000000000000000000000000000000000000000000000000000000000'
DESTINATION_PUBLIC_KEY = b'ad689f9e10651009d0d1afbe16cc48e0417ce2c51401b46bcbd500cd55e47ad3'
version = b'0000'
root_locktime = convert_locktime(read_locktime(locktime(True)))
#transaction_data:bytearray = ROOT_PUBLIC_KEY
transaction_data =  b'00000000500000003429' # amount
transaction_data += b'00000000000000000001' # sequence
transaction_data += root_locktime # locktime
transaction_data += b'00000000000000000001' # transaction id
transaction_data += b'00000000000000000000' # output index

secexp = randrange_from_seed__trytryagain('plade33',CURVE.order)
sk = SigningKey.from_secret_exponent(secexp,curve=CURVE,hashfunc=SHA)
ROOT_FULL_PUBLIC_KEY = SHA(sk.verifying_key.to_pem(point_encoding="compressed",)).digest()
print('LEN ROOT FPK',len(ROOT_FULL_PUBLIC_KEY))
token = SHA(transaction_data+DESTINATION_PUBLIC_KEY).hexdigest().encode()

token_signature = sk.sign_deterministic(
    token,hashfunc=SHA)

data_signed = SHA(transaction_data+ROOT_FULL_PUBLIC_KEY).digest()

public_key_signature = sk.sign_digest_deterministic(
    data_signed,hashfunc=SHA)

pubkey_script = token_signature+public_key_signature

node = version+transaction_data+pubkey_script+ROOT_FULL_PUBLIC_KEY

print('NODE SIZE',len(node))
print('TOKEN SIG',len(token_signature))
print('PUBKEY SIG',len(public_key_signature))
print('NODE',node)

i:InputTransaction = InputTransaction.read_data_bytes(node)
print(i.amount,i.locktime)
o:OutputTransaction = i.get_output()
print('ROOT TRANSACTION DATA',i.dump_data_bytes())

ox:OutputTransaction = OutputTransaction.read_data_bytes(o.dump_data_bytes())
#print(ox.dump_data_bytes())
print('OUTPUT BYTES SIZE',len(ox.dump_data_bytes()))
#print(o.dump_data_bytes()==ox.dump_data_bytes())

print('NOW, LETS CHECK')
print(bcolors.OKCYAN)
print('ROOT',transaction_data)
print(bcolors.OKBLUE)
print('DUMP',i.get_transaction_data())
print(bcolors.ENDC)
print('LOCKTIME',read_locktime(root_locktime),i.locktime)
rt_conv = convert_locktime(read_locktime(root_locktime))
i_conv = convert_locktime(i.locktime)
print('CONVERTED LOCKTIME',rt_conv,i_conv)

print('TRANSACTION DATA',transaction_data==i.get_transaction_data())
print('SIG CHECK',public_key_signature==i.signature)
print('PK',i.issuer_public_key_full==ROOT_FULL_PUBLIC_KEY)
#print('[TOBIAS PK]',tobias.public_key)

def get_verification_key(data_sign,data_digest):
    vks = VerifyingKey.from_public_key_recovery_with_digest(
            signature=data_sign,
            digest=data_digest,
            curve=CURVE,
            hashfunc=SHA
        )
    return vks
def is_signature_valid(transaction:InputTransaction):
    vals = []
    v_full_pk_data = transaction.issuer_public_key_full    
    vdata_sign = transaction.signature
    vdata_digest = SHA(transaction.get_transaction_data()+v_full_pk_data).digest()    
    print('SIGNED CHECK',vdata_digest==data_signed)
    # print('ROOTKEY',public_key_signature)
    # print('RECOVERED',vdata_sign)
    # print('DIGEST',vdata_digest)
    vks = get_verification_key(vdata_sign,vdata_digest)   
    #v_token = SHA(p_data+p_public_key).hexdigest().encode()
    try:
        for vk in vks:
            vk.verify_digest(transaction.signature,
                             digest=vdata_digest)
            vals.append(True)
    except BadSignatureError as bse:
        print(bse)
        pass
    except BadDigestError:
        pass    
    return any(vals)

if is_signature_valid(i):
    print('TRANSACTION SIGNATURE',bcolors.OKGREEN,'CONFIRMED',bcolors.ENDC)
else:
    print('TRANSACTION SIGNATURE',bcolors.FAIL,'INVALID',bcolors.ENDC)

print('GENERATING OUTPUT FOR ROOT TRANSACTION')
print('AMOUNT',ox.amount*XIL)
data=i.get_transaction_data()+DESTINATION_PUBLIC_KEY
token_found = SHA(data).hexdigest().encode()
print('ORIGINAL TOKEN',token)
print('TOKEN FOUND',token_found==token)

print('TOKEN VALIDATION',end='')
if i.validate_token(token_found):
    print(bcolors.OKGREEN,'VALID',bcolors.ENDC)
else:
    print(bcolors.FAIL,'INVALID',bcolors.ENDC)
