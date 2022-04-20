from copyreg import pickle
from blockchain import Blockchain
from coin import Transaction, xil
from wallet import Wallet
import pickle

tobiaswalletfile = '/home/ozy/BLOCK_ENV/blockchain/xilins/tobias.pkl'
ozywalletfile = '/home/ozy/BLOCK_ENV/blockchain/xilins/ozy.pkl'

tobias = Wallet.generate_wallet('Tobias Wallet','plade33')
ozy = Wallet.generate_wallet('Ozymandias Wallet','plade33')

def save_wallet(wallet,file):
    
    with open(file,'wb') as f:
        pickle.dump(wallet,f,protocol=pickle.HIGHEST_PROTOCOL)

def load_wallet(file):
    with open(file,'rb') as f:
        return pickle.load(f)
    

if __name__ == '__main__':
    blockchain = Blockchain()    
    print('ACTUAL INDEX',blockchain.chain_index()-1)
    #w1 = Wallet(tobias[0],tobias[1])
    #save_wallet(w1,tobiaswalletfile)
    #print(w1.data)
    #w2 = Wallet(ozy[0],ozy[1])
    #save_wallet(w2,ozywalletfile)
    w1 = load_wallet(tobiaswalletfile)
    w2 = load_wallet(ozywalletfile)
    walletinvalida = Wallet.generate_wallet('invalida wallet','asdasd')
    w3 = Wallet(walletinvalida[0],walletinvalida[1])
    #print(w2.data)
    blockchain.register_participant(w1.hash_id)
    blockchain.register_participant(w2.hash_id)
    
    #print('INITIAL LEDGER',blockchain.ledger)
    for i in range(1,10):
        # tx = Transaction()
        # tx.destination = w1.hash_id
        # tx.value = 77-i
        # tx.source = w3.hash_id
        # tx.token = w3.token(tx)
        # blockchain.add_transaction(tx)
        
        txx = Transaction()
        txx.destination = w3.hash_id
        txx.value = xil
        txx.source = blockchain.genesis_wallet.hash_id
        txx.token = blockchain.genesis_wallet.token(txx)
        print(blockchain.add_transaction(txx))
        # t = Transaction()
        # t.destination = w1.hash_id
        # t.value = 10
        # t.source = blockchain.genesis_wallet.hash_id
        # t.token = blockchain.genesis_wallet.token(t)  
        # blockchain.add_transaction(t)  
        # #print('TRANSACTION T',blockchain.add_transaction(t))
        
        # t2 = Transaction()    
        # t2.value = 7
        # t2.destination = w2.hash_id
        # t2.source = w1.hash_id
        # t2.token = w1.token(t2)
        # blockchain.add_transaction(t2)
        #print('TRANSACTION T2',blockchain.add_transaction(t2))
        
        blockchain.write_chain()
    
    #print('FINAL LEDGER',blockchain.ledger)
    
    blockchain.genesis_wallet.download_ledge(blockchain)
    print('TOTAL BALANCE ROOT',blockchain.genesis_wallet.balance)
    
    #print(blockchain.ledger)
    w1.download_ledge(blockchain)
    print('TOTAL BALANCE w1',w1.balance)
   
    #print(blockchain.get_all())
    
    w2.download_ledge(blockchain)
    print('TOTAL BALANCE w2',w2.balance)
    
    w3.download_ledge(blockchain)
    print('TOTAL BALANCE w3',w3.balance)
    
    print('TOTAL TRANSACTIONS:',blockchain.count_transactions())
    #print('BLOCKS',blockchain.blocks)
    