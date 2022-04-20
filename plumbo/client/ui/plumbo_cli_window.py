# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'plumbo_cli.ui'
##
## Created by: Qt User Interface Compiler version 6.2.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDoubleSpinBox, QFrame,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QPlainTextEdit, QPushButton, QSizePolicy,
    QTableWidget, QTableWidgetItem, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1223, 594)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(10, 10, 1201, 31))
        self.frame.setAutoFillBackground(False)
        self.frame.setStyleSheet(u"color: rgb(238, 238, 236);\n"
"background-color: rgb(52, 101, 164);")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setLineWidth(0)
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 10, 221, 18))
        self.tableWidget = QTableWidget(Form)
        if (self.tableWidget.columnCount() < 6):
            self.tableWidget.setColumnCount(6)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setGeometry(QRect(10, 50, 861, 391))
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.groupBox = QGroupBox(Form)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(890, 50, 321, 261))
        self.bt_refresh = QPushButton(self.groupBox)
        self.bt_refresh.setObjectName(u"bt_refresh")
        self.bt_refresh.setGeometry(QRect(10, 200, 301, 51))
        self.cb_wallets = QComboBox(self.groupBox)
        self.cb_wallets.setObjectName(u"cb_wallets")
        self.cb_wallets.setGeometry(QRect(110, 30, 201, 26))
        self.t_password = QLineEdit(self.groupBox)
        self.t_password.setObjectName(u"t_password")
        self.t_password.setGeometry(QRect(112, 70, 201, 26))
        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(20, 70, 81, 18))
        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(20, 30, 81, 18))
        self.label_6 = QLabel(self.groupBox)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(20, 100, 71, 18))
        self.lb_amount_info = QLabel(self.groupBox)
        self.lb_amount_info.setObjectName(u"lb_amount_info")
        self.lb_amount_info.setGeometry(QRect(110, 100, 201, 18))
        self.groupBox_2 = QGroupBox(Form)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(10, 455, 861, 91))
        self.horizontalLayout = QHBoxLayout(self.groupBox_2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout.addWidget(self.label_2)

        self.t_send_address = QLineEdit(self.groupBox_2)
        self.t_send_address.setObjectName(u"t_send_address")

        self.horizontalLayout.addWidget(self.t_send_address)

        self.label_4 = QLabel(self.groupBox_2)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout.addWidget(self.label_4)

        self.ds_amount = QDoubleSpinBox(self.groupBox_2)
        self.ds_amount.setObjectName(u"ds_amount")
        self.ds_amount.setMinimumSize(QSize(150, 0))

        self.horizontalLayout.addWidget(self.ds_amount)

        self.bt_send = QPushButton(self.groupBox_2)
        self.bt_send.setObjectName(u"bt_send")

        self.horizontalLayout.addWidget(self.bt_send)

        self.t_keyviewer = QPlainTextEdit(Form)
        self.t_keyviewer.setObjectName(u"t_keyviewer")
        self.t_keyviewer.setGeometry(QRect(890, 320, 321, 241))
        self.frame_2 = QFrame(Form)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setGeometry(QRect(10, 570, 1201, 20))
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.lb_progress = QLabel(self.frame_2)
        self.lb_progress.setObjectName(u"lb_progress")
        self.lb_progress.setGeometry(QRect(10, 0, 1301, 18))
        sizePolicy1 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.lb_progress.sizePolicy().hasHeightForWidth())
        self.lb_progress.setSizePolicy(sizePolicy1)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"PlumboCoin", None))
        self.label.setText(QCoreApplication.translate("Form", u"PLUMBO WALLETS", None))
        ___qtablewidgetitem = self.tableWidget.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("Form", u"direction", None));
        ___qtablewidgetitem1 = self.tableWidget.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("Form", u"source", None));
        ___qtablewidgetitem2 = self.tableWidget.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("Form", u"address", None));
        ___qtablewidgetitem3 = self.tableWidget.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("Form", u"txid", None));
        ___qtablewidgetitem4 = self.tableWidget.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("Form", u"amount", None));
        ___qtablewidgetitem5 = self.tableWidget.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("Form", u"locktime", None));
        self.groupBox.setTitle(QCoreApplication.translate("Form", u"Wallet", None))
        self.bt_refresh.setText(QCoreApplication.translate("Form", u"refresh", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"Password:", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"PEM:", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"Balance:", None))
        self.lb_amount_info.setText(QCoreApplication.translate("Form", u"TextLabel", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Form", u"Send", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Address:", None))
        self.t_send_address.setText(QCoreApplication.translate("Form", u"7b770e37f29d20b189d9780d0726e5e695ece22ccb529e50d8826fc52af79c12", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"Amount:", None))
        self.bt_send.setText(QCoreApplication.translate("Form", u"SEND", None))
        self.lb_progress.setText(QCoreApplication.translate("Form", u"TextLabel", None))
    # retranslateUi

