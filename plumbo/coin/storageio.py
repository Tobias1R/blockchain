
import mmap
import os
from typing import BinaryIO
from hashlib import md5
from bitstring import ConstBitStream
from .chainv2 import (
    Block, ByteNode, ChainTransaction, 
    InputTransaction, 
    OutputTransaction,
    Transaction)
from . import SHA
from .misc import bcolors
FILE_BLOCKS = 'blocks.bin'
FILE_CHAIN = 'chain.bin'
FILE_TRANSACTIONS = 'transactions.bin'
FILE_INPUTS = 'inputs.bin'
FILE_OUTPUTS = 'outputs.bin'

SIZE_BLOCK = 128




class Storage:
    def __init__(self,root) -> None:
        if not os.path.isdir(root):
            raise ValueError('Ohh dear, you need a good place for your data, and '+str(root)+' its not a good a place.')
        self.root = root
        self.checksum = None
        self.block_writer: BinaryIO = open(self.blockfile,'ab+')
        self.block_reader: BinaryIO = open(self.blockfile,'rb+')
        
        self.chain_writer: BinaryIO = open(self.chainfile,'ab')
        self.chain_reader: BinaryIO = open(self.chainfile,'rb')
        
        self.transactions_writer: BinaryIO = open(self.transactionsfile,'ab')
        self.transactions_reader: BinaryIO = open(self.transactionsfile,'rb')
        
        self.inputs_writer: BinaryIO = open(self.inputsfile,'ab')
        self.inputs_reader: BinaryIO = open(self.inputsfile,'rb')
        
        self.outputs_writer: BinaryIO = open(self.outputsfile,'ab')
        self.outputs_reader: BinaryIO = open(self.outputsfile,'rb')
        
        self.checksum = self.check_files()
    
    def file_list(self):
        return [
            self.blockfile,self.chainfile,self.transactionsfile,
            self.inputsfile,self.outputsfile
        ]
    
    def check_files(self):
        checksum = bytearray()
        for file in self.file_list():
            with open(file,'rb') as f:
                checksum += f.read()        
        return md5(checksum).hexdigest()
    
    def files_changed(self):
        return bool(self.check_files()!=self.checksum)
    
    def reload_files(self):
        # change... you must
        self.block_reader.close()
        self.chain_reader.close()
        self.transactions_reader.close()
        self.inputs_reader.close()
        self.outputs_reader.close()
        
        self.block_reader: BinaryIO = open(self.blockfile,'rb+')
        self.chain_reader: BinaryIO = open(self.chainfile,'rb')
        self.transactions_reader: BinaryIO = open(self.transactionsfile,'rb')
        self.inputs_reader: BinaryIO = open(self.inputsfile,'rb')
        self.outputs_reader: BinaryIO = open(self.outputsfile,'rb')
    
    @property
    def blockfile(self):
        return os.path.join(self.root,FILE_BLOCKS)
    
    @property
    def chainfile(self):
        return os.path.join(self.root,FILE_CHAIN)
    
    @property
    def transactionsfile(self):
        return os.path.join(self.root,FILE_TRANSACTIONS)
    
    @property
    def inputsfile(self):
        return os.path.join(self.root,FILE_INPUTS)
    
    @property
    def outputsfile(self):
        return os.path.join(self.root,FILE_OUTPUTS)
    
    def read_file(self,
                  file, 
                  node_class:ByteNode=... , 
                  separator=b'|#',
                  start=0, hash_data=True
    )->list[ByteNode]:
        separator=node_class.SEPARATOR
        start = start
        if hash_data:
            nodes = {}
        else:
            nodes = []
        with open(file,'r+b') as f:
            node = mmap.mmap(f.fileno(),0)
            endblock = node.find(separator,0)
            node.seek(start)
            byte:ByteNode = node_class.read_data_bytes(node.read(endblock))
            while endblock>=0:
                endblock = node.find(separator,start)
                try:
                    node.seek(start)
                    data = node.read(endblock-start)
                    if hash_data:
                        #nodes = {}
                        h = SHA(data).hexdigest().encode()
                        nodes[h] = node_class.read_data_bytes(data)
                    else:
                        nodes.append(node_class.read_data_bytes(data))
                    start = node.tell()+len(separator)                            
                except ValueError as ve:
                    # seek out range
                    print('READING_FILE',ve)
                    endblock =-1
                except Exception as e:
                    print('READING_FILE',e)
                    endblock =-1
                    
        return nodes
    
    def extract_transactions(self,):
        return self.read_file(self.transactionsfile,
                              Transaction,
                              hash_data=False)
    
    def extract_chain(self):
        hashes = []
        with open(self.chainfile,'rb+') as f:
            # 64 is the size of hash digest of block
            byte = f.read(64)
            while byte:
                hashes.append(byte)
                byte = f.read(64)
        return hashes
                
            
class LocalStorage(Storage):
    def __init__(self,root) -> None:
        super().__init__(root)
        if not os.path.isdir(root):
            raise ValueError('Ohh dear, you need a good place for your \
                data, and '+str(root)+' its not a good a place.')
        self.root = root
        self.checksum = None
        # self.blocks = mmap.mmap(open(self.blocksfile,'r+b'),0)
        # self.chain = mmap.mmap(open(self.chainfile,'r+b'),0)
        # self.transactions = mmap.mmap(open(self.transactionsfile,
        #                                    'r+b'),0)
    
    @property
    def blocks(self):
        with open(self.blocksfile,'r+b') as f:
            return mmap.mmap(f.fileno(),0)
    
    @property
    def transactions(self):
        with open(self.transactionsfile,'r+b') as f:
            return mmap.mmap(f.fileno(),0)
    
    @property
    def blocksfile(self):
        return os.path.join(self.root,FILE_BLOCKS)
    
    @property
    def chainfile(self):
        return os.path.join(self.root,FILE_CHAIN)
    
    @property
    def transactionsfile(self):
        return os.path.join(self.root,FILE_TRANSACTIONS)
    
    @property
    def inputsfile(self):
        return os.path.join(self.root,FILE_INPUTS)
    
    @property
    def outputsfile(self):
        return os.path.join(self.root,FILE_OUTPUTS)
            
            