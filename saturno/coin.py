from hashlib import sha256, sha512


from cryptochain import BRAINPOOLP512r1,SECP256k1, NIST256p, NIST521p

class CoinVersion:        
    # Version
    __version__ = b'0000'
    # Minimum value
    XIL = 0.00000001
    # Curve
    CURVE = NIST521p
    # sha algo
    SHA = sha256
    # root network router
    XILIN_ROUTER = '127.0.0.1'
    # internet router
    ROOT_REGISTER = 'xilin.plumbo.com.br'
    ROOT_REGISTER_PORT = 49657

# Version
__version__ = b'0000'
# Minimum value
XIL = 0.00000001
# Curve
CURVE = NIST521p
# sha algo
SHA = sha256
# root network router
XILIN_ROUTER = '127.0.0.1'
# internet router
ROOT_REGISTER = 'xilin.plumbo.com.br'
ROOT_REGISTER_PORT = 49657
INPUT_TRANSACTION_DATA_SIZE=400

    
        
