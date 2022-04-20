
class InputTransaction:
    pass

class OutputTransaction:
    def __init__(self) -> None:
        self.input_txid=b''
        self.address=b''
        self.amount=0
        self.locktime=b''
        self.output_index=0
        

class Transaction:
    pass
