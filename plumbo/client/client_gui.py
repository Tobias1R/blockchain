import os
import sys
import traceback
from os import listdir
from os.path import isfile, join
import socket

from plumbo.coin.chainv2 import ChainTransaction, Transaction
HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 6543        # The port used by the server
from PySide6.QtCore import (
    QEvent, QObject,  QRect, QThreadPool,
    Signal, Slot, QRunnable
)
from PySide6.QtGui import (
    QBrush, QColor,  QPaintDevice, QPainter, QPen,
    Qt
)
from PySide6.QtWidgets import (
    QApplication, QFileDialog,  QWidget, QTableWidgetItem
)

import itertools
from datetime import datetime
from ui.plumbo_cli_window import Ui_Form
from wallet import Wallet
class Worker(QRunnable):
    '''
    Worker thread

    Herda de QRunnable para a configuração do thread.

    :param callback: O callback de função a ser executado 
                    neste thread de trabalho. Args fornecidos e
                    kwargs serão passados para o runner.

    :param args: Argumentos para passar a função callback
    :param kwargs: Keywords para passar a função callback

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # iniciais
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        # adiciona callback aos kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @Slot()
    def run(self):
        '''
        Inicializa o runner e passa os argumentos
        '''
        # Obtem e passa os argumentos para a função
        try:
            result = self.fn(
                *self.args, **self.kwargs
            )
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit(
                (exctype, value, traceback.format_exc()))
        else:
            # retorna
            self.signals.result.emit(result)
        finally:
            # fim do thread
            self.signals.finished.emit()
class WorkerSignals(QObject):
    '''
    Signals utilizados pelo runner

    '''
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(str)

class Janela(QWidget):
    """ Janela principal do app.

    Implementa:
        QWidget : Qt6.
    """
    def __init__(self, parent, *args, **kwargs) -> None:
        super().__init__(parent=parent, *args, **kwargs)
        self.form = Ui_Form()
        self.form.setupUi(self)
        self.list_wallets()
        self.form.bt_refresh.clicked.connect(self.load_wallet)
        self.wallet:Wallet=None
        self.form.bt_send.clicked.connect(self.send_to_address)
    
    def list_wallets(self):
        mypath = os.path.join(os.path.dirname(__file__),'wallets')
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        print(onlyfiles)
        for wallet_file in onlyfiles:
            combo = self.form.cb_wallets
            combo.addItem(wallet_file)
        pass
    
    def connect(self):
        pass
        # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        #     s.connect((HOST, PORT))
        #     s.sendall(b'REG#'+self.wallet.public_key.encode())
        #     data = s.recv(1024)
        #     print('Received', repr(data))
        #     s.sendall(b'GETTRALL#')
        #     data = s.recv(1024)
        #     print('transaction data',data)
        
    def update_wallet_info(self):
        self.form.lb_amount_info.setText('PLMB: '+str(self.wallet._balance))
        
    def new_client(self):
        pass
    
    def log(self,data):
        self.form.t_keyviewer.appendPlainText(str('\n'))
        self.form.t_keyviewer.appendPlainText(str(data))
    
    def load_wallet(self):
        file = self.form.cb_wallets.currentText()
        print(file)
        filepath = os.path.join(os.path.dirname(__file__),'wallets',file)
        self.wallet=Wallet.open_wallet(filepath,self.form.t_password.text())
        self.form.t_keyviewer.setPlainText(str(self.wallet.sk.to_pem()))
        self.log('ADDRESS: '+str(self.wallet.public_key))
        self.connect()
        self.wallet.process_blockchain()
        self.update_wallet_info()
        self.populate_table()
        
    
    def send_to_address(self):
        address = self.form.t_send_address.text()
        amount = int(self.form.ds_amount.value())
        self.log('sending to:'+address)
        self.log(address+' -> '+str(amount))
        self.wallet.send_to_address(address,amount)
        self.wallet.process_blockchain()
        self.update_wallet_info()
        pass
    
    def populate_table(self,):
        table = self.form.tableWidget
        table.clearContents()
        table.setRowCount(0)
        transactions = self.wallet.processed_transactions
        def add_item_table(i:ChainTransaction,in_out,row,source,txid):
            
            address=str(i.address)
            if address==str(self.wallet.public_key.encode()):
                address='YOURS'
            amount=str(i.amount)
            lockt=str(i.locktime)
            item=QTableWidgetItem()
            item.setText(in_out)
            table.setItem(row,0,item)
            
            item1=QTableWidgetItem()
            item1.setText(source)
            table.setItem(row,1,item1)
            
            item2=QTableWidgetItem()
            item2.setText(address)
            table.setItem(row,2,item2)
            
            item3=QTableWidgetItem()
            item3.setText(txid)
            table.setItem(row,3,item3)
            
            item4=QTableWidgetItem()
            item4.setText(amount)
            table.setItem(row,4,item4)
            
            item5=QTableWidgetItem()
            item5.setText(lockt)
            table.setItem(row,5,item5)
            
            
            
        for t_key in transactions.keys():
            t:Transaction=transactions[t_key]
            source=str(t.issuer_public_key)
            txid=str(t.txid)
            for i in t.inputs:
                if i:
                    row=table.rowCount()
                    table.insertRow(row)
                    add_item_table(i,'INPUT',row,source,txid)
            for i in t.outputs:
                if i:
                    row=table.rowCount()
                    table.insertRow(row)
                    add_item_table(i,'OUTPUT',row,source,txid)
        #print('PROCESSED TGUI',transactions)
        #table.update()
    
    