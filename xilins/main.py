from blockchain import Blockchain
from coin import Transaction
from wallet import Wallet



tobias = Wallet.generate_wallet('Tobias Wallet','plade33')
ozy = Wallet.generate_wallet('Ozymandias Wallet','plade33')

if __name__ == '__main__':
    blockchain = Blockchain()    
    print('ACTUAL INDEX',blockchain.chain_index()-1)
    w1 = Wallet(tobias[0],tobias[1])
    #print(w1.data)
    w2 = Wallet(ozy[0],ozy[1])
    #print(w2.data)
    
    t = Transaction()
    t.destination = w1.hash_id
    t.value = 10
    t.source = blockchain.genesis_wallet.token(t)    
    print('TRANSACTION T',blockchain.add_transaction(t))
    
    t2 = Transaction()    
    t2.value = 7
    t2.destination = w2.hash_id
    t2.source = w1.token(t2)
    print('TRANSACTION T2',blockchain.add_transaction(t2))
    
    #print(blockchain.ledger)
    w1.download_ledge(blockchain)
    print('TOTAL BALANCE w1',w1.balance)
    
    blockchain.genesis_wallet.download_ledge(blockchain)
    print('TOTAL BALANCE ROOT',blockchain.genesis_wallet.balance)
    #print(blockchain.get_all())