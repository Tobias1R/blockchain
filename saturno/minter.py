
from coin import __version__
from hashlib import sha256, sha512
def int_to_bytes(number: int) -> bytes:
    return number.to_bytes(length=(8 + (number + (number < 0)).bit_length()) // 8, byteorder='big', signed=True)

def int_from_bytes(binary_data: bytes):
    return int.from_bytes(binary_data, byteorder='big', signed=True)

class Mint:
    def __init__(self,
                 version=__version__,
                 last_chain_hash=b'',       
                 minter_id=b''          
                 ) -> None:
        self.coins:list[bytearray]=[]
        self.version:bytes=version
        self.minter_id:bytes=minter_id
        self.last_chain_hash:bytes=last_chain_hash
    
    def generate(self):
        amount = self.compute_amount()
        for i in range(1,amount+1):
            coin_data = self.version+self.minter_id+self.last_chain_hash
            coin_data += int_to_bytes(i)
            coin = sha256(coin_data).hexdigest().encode()
            if not coin in self.coins:
                self.coins.append(coin)
    
    def compute_amount(self):
        return 100
    
    
    

minter_id = b'ad689f9e10651009d0d1afbe16cc48e0417ce2c51401b46bcbd500cd55e47ad3'
root_block = b'07b241b33b51e215b07508f2d7e116fb7b0e2a492cba91b498188b4cc867590b'

minter = Mint(last_chain_hash=root_block,minter_id=minter_id)
minter.generate()
print(minter.coins)