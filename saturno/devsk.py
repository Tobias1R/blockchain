from cryptochain import VerifyingKey, BadDigestError,BadSignatureError

from wallet import Wallet
from coin import CURVE, SHA
from misc import bcolors

wallet_file = '/home/ozy/BLOCK_ENV/blockchain/wallets/tobias.walt'
tobias = Wallet.open_wallet(wallet_file,'plade33')
wallet_fileo = '/home/ozy/BLOCK_ENV/blockchain/wallets/ozymandias.walt'
ozymandias = Wallet.open_wallet(wallet_fileo,'plade33')

# def create_wallet(winfo):
#     pem, public_key, filename,filedata = Wallet.generate_wallet(winfo[0],
#                                                 winfo[1],True)
        
#     decrypted_wallet_data = Wallet.decrypt_wallet(filedata,winfo[1])
#     return pem
# winfo = ('tobias','plade33')
# pem = create_wallet(winfo=winfo)
# tobias = Wallet(pem_data=pem,password=winfo[1])
# winfo = ('ozymandias','plade33')
# pem = create_wallet(winfo=winfo)
# ozymandias = Wallet(pem_data=pem,password=winfo[1])




amount:float=b'00000000000000000000'
sequence:int=b'00000000000000000000'
locktime:int=b'00000000000000000000'
transaction_id:int=b'00000000000000000000'
output_index:int=b'00000000000000000000'
full_pk_data = tobias.public_key_digest()

public_key=ozymandias.public_key.encode()
        
data = amount+sequence+locktime+transaction_id+output_index # 164

data_digest = SHA(data+full_pk_data).digest()
token = SHA(data+public_key).hexdigest().encode()

data_sign = tobias.sk.sign(data+full_pk_data,hashfunc=SHA)
token_sign = tobias.sk.sign_digest(token)

# confirmation needs
# data digest, but data needs to go to block
# public signature (data_sign)
# public key digest (full_pk_data)
# token signature (token_sign)


pubkey_script_data = data_sign+full_pk_data+token_sign
def get_verification_key(data_sign,data_digest):
    vks = VerifyingKey.from_public_key_recovery_with_digest(
            signature=data_sign,
            digest=data_digest,
            curve=CURVE,
            hashfunc=SHA
        )
    return vks
validations = []

vks = get_verification_key(data_sign,data_digest)      
for vk in vks:
    try:
        vk_pk_data = SHA(vk.to_pem(point_encoding="compressed")).digest()
        #print('VK',vk_pk_data==full_pk_data)
        validations.append(vk.verify_digest(signature=token_sign,
                                            digest=token))        
    except BadSignatureError as bse:
        pass
    except BadDigestError:
        pass
    
version = b'0000'
transaction_data = version+data+pubkey_script_data

#print(transaction_data)
print('PUBKEY SCRIPT LENGTHS:',
    len(data_sign),len(full_pk_data),len(token_sign))
print('DATA LENGTHS:',
    'VERSION:',4,
    'DATA:',len(data),
    'PUBKEY SCRIPT:',len(pubkey_script_data),
    'TOTAL:',len(transaction_data),'bytes/transaction')
print('IS VALID:',any(validations))

########## validate chain data
def is_signature_valid(version,p_data,pubkey_data):
    vals = []
    v_full_pk_data = pubkey_data[132:164]    
    vdata_sign = pubkey_data[:132]
    vdata_digest = SHA(p_data+v_full_pk_data).digest()    
    vks = get_verification_key(vdata_sign,vdata_digest)   
    #v_token = SHA(p_data+p_public_key).hexdigest().encode()
    try:
        for vk in vks:
            vk_pk_data = SHA(vk.to_pem(point_encoding="compressed")).digest()
            pk_in_data = pubkey_data[132:164]
            if vk_pk_data == pk_in_data:
                vals.append(True)
            else:
                vals.append(False)
    except BadSignatureError as bse:
        pass
    except BadDigestError:
        pass    
    return any(vals)

def validate_token(version,p_data,pubkey_data,p_public_key):
    vals = []
    vdata_sign = pubkey_data[:132]
    v_full_pk_data = pubkey_data[132:164]    
    v_token_signature = pubkey_data[164:]    
    vdata_digest = SHA(p_data+v_full_pk_data).digest()    
    vks = get_verification_key(vdata_sign,vdata_digest)   
    v_token = SHA(p_data+p_public_key).hexdigest().encode()    
    for vk in vks:
        try:
            vals.append(vk.verify_digest(signature=v_token_signature,
                                            digest=v_token)) 
            return True
        except BadSignatureError as bse:
            pass
        except BadDigestError:
            pass    
    return any(vals)

c_version = transaction_data[:4]
c_data = transaction_data[4:104]
c_pubkey_data = transaction_data[104:]



print('SPLIT',(c_version+c_data+c_pubkey_data)==transaction_data)
if is_signature_valid(c_version,c_data,c_pubkey_data):
    print(bcolors.OKGREEN,'SIGNATURE IS VALID',bcolors.ENDC)

if validate_token(c_version,c_data,c_pubkey_data,ozymandias.public_key.encode()):
    print(bcolors.OKGREEN,'THIS TOKEN IS FOR YOU',bcolors.ENDC)
else:
    print(bcolors.FAIL,'BUT, THIS TOKEN IS NOT FOR YOU',bcolors.ENDC)

