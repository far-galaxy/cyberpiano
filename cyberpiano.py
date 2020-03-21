import fluidsynth
import sys, os

try:
    from PyQt5 import QtCore, QtSerialPort
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import QIcon, QFont
    
except ModuleNotFoundError:
    if sys.platform.startswith('win'):
        os.system('pip install pyqt5')
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        os.system('sudo apt-get install python3-pyqt5')
        os.system('sudo apt-get install python3-pyqt5.qtserialport')


#print(os.path.abspath("soundfonts/"))

#-----------------------------Init Synth----------------------------------------------
synth = fluidsynth.Synth(1)
#Set gain to 1 in pyfluinsynth
#print(synth.main_volume(1, 0))

if sys.platform.startswith('win'):
    synth.start("dsound")
    
elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
    synth.start("alsa")
    

#synth.load_sound_font('soundfonts/QUEST_O_TIME.SF2')
#synth.set_instrument(0, 0)

opt = os.path.abspath('options.txt')
opt_file = open(opt, 'r')
recent_files = []
for i in opt_file:
    recent_files.append(i[:-1])
opt_file.close()

class Widget(QWidget):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        
        self.soundbank = None
        self.instrument = 0
        self.volume = 127
        
        #-----------------Title---------------------------
        self.setWindowTitle('CyberPiano')
        self.setWindowIcon(QIcon('icon.png'))
        self.resize(800, 600)
        self.setFont(QFont("Calibri", 16, QFont.Normal))
        
        w = self.frameGeometry().width()
        h = self.frameGeometry().height()
        
        #-----------------Keyboard---------------------------
                
        
        # Exit
        self.exitAction = QAction('&Exit', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.triggered.connect(qApp.quit)        
            
        #
        open_file_menu = QAction('Load soundfont', self)
        open_file_menu.setShortcut('Ctrl+O')
        open_file_menu.triggered.connect(self.open_file)   
        
        # Options
        opt_menu = QAction('Options', self)
        opt_menu.setShortcut('F2')
        opt_menu.triggered.connect(self.options_window)   
        
        # Volume
        sld = QSlider(QtCore.Qt.Horizontal, self)
        sld.setMaximum(127)
        sld.setValue(127)
        sld.valueChanged[int].connect(self.set_volume)
        self.sld_ = QLabel('Volume: 127', self)
        
        menubar = QMenuBar() 
        file_menu = menubar.addMenu('&File')
        sf2_menu = menubar.addMenu('&Soundfonts')
        
        help_menu = menubar.addAction('&Help')
        help_menu.triggered.connect(self.help_window)  
        
        about_menu = menubar.addAction('&About')
        about_menu.triggered.connect(self.info_dialog)  
        help_menu.setShortcut('F1')
        
        self.recent_menu = QMenu('Recent soundfonts', self)
        for i in recent_files:
            self.recent_menu.addAction(i, lambda i=i: self.load_file(i))
        
        
        sf2_menu.addAction(open_file_menu) 
        sf2_menu.addMenu(self.recent_menu) 
        
        file_menu.addAction(opt_menu)
        file_menu.addSeparator()
        file_menu.addAction(self.exitAction) 
        
        # Output textbox
        self.infotxt = QTextEdit(readOnly=True)
        self.infotxt_ = QLabel('Information:', self)
        
        # Ports List
        ports = self.find_ports()
        self.current_port = ports[0]
        
        self.ports_box = QComboBox(self)
        for i in ports:
            self.ports_box.addItem(i)   
        self.ports_box.activated[str].connect(self.set_port) 
        self.ports_box_ = QLabel('Port:', self)
        
        # Instruments List
        self.instr_box = QComboBox(self)
        for i in range(0, 128):
            self.instr_box.addItem(str(i)) 
        self.instr_box.activated[str].connect(self.set_instrument)  
        self.instr_box.setEnabled(False)
        self.instr_box_ = QLabel('Instrument:', self)     
        
        
        # Connect button
        self.button = QPushButton(text="Connect", checkable=True, toggled=self.on_toggled)
        
        self.open_button = QPushButton("Load soundfont", self)
        self.open_button.clicked.connect(self.open_file)
        
        
        
        lay = QVBoxLayout(self)
        
        #menulay = QHBoxLayout()
        #menulay.setMenuBar(self.menubar)
        #self.setMenuBar(self.menubar)
        
        hlay1 = QHBoxLayout()
        hlay1.addWidget(self.ports_box_)
        hlay1.addWidget(self.ports_box)
        hlay1.addWidget(self.button)
        
        
        hlay2 = QHBoxLayout()
        hlay2.addWidget(self.instr_box_)
        hlay2.addWidget(self.instr_box)
        hlay2.addWidget(self.open_button)
        
        hlay3 = QHBoxLayout()
        hlay3.addStretch(1)
        hlay3.addWidget(self.sld_)
        hlay3.addWidget(sld)
        
        
        lay.setMenuBar(menubar)
        lay.addLayout(hlay1)
        lay.addLayout(hlay2)
        lay.addLayout(hlay3)
        lay.addStretch(1)
        lay.addWidget(self.infotxt_)
        lay.addWidget(self.infotxt)
        
        
        

        self.serial = QtSerialPort.QSerialPort(self.current_port, baudRate=QtSerialPort.QSerialPort.Baud115200, readyRead=self.receive)
   
    def options_window(self):
        opt_window = Options(self)
        opt_window.show()
        #opt_window._exec_()
    
    def help_window(self):
        window = Help(self)
        window.show()    
        
    def set_volume(self, vol):
        self.volume = vol
        self.sld_.setText("Volume: " + str(vol))
    
    def info_dialog(self):
        msg = QMessageBox() #.about(self, 'About',"CyberPiano\nby far-galaxy")
        msg.setIcon(QMessageBox.Information)
        msg.setText("CyberPiano v.0.22\nby far-galaxy")
        msg.setWindowTitle("About")    
        #msg.resize(400,300)
        msg.exec()
        
     
    def set_instrument(self, instr):
        self.instrument = instr 
        synth.program_select(0, self.soundbank, 0, int(self.instrument))
        self.infotxt.append("Set instrument: " + str(self.instrument))
        
    def open_file(self):
        file = QFileDialog.getOpenFileName(self, "Load .sf2 Soundfont", os.path.abspath("soundfonts/"), "Soundfonts (*.sf2)")
        self.load_file(file[0])
            
    def load_file(self, path):
        if path != "":
            self.soundbank = synth.sfload(path)
            if not path in recent_files:
                recent_files.insert(0, path)
                
            else:
                recent_files.pop(recent_files.index(path))
                recent_files.insert(0, path)
            
            opt_file = open(opt, 'w')
            for i in recent_files[:10]:
                opt_file.write(i + '\n')
            opt_file.close()
            self.recent_menu.clear()
            for i in recent_files[:10]:
                self.recent_menu.addAction(i, lambda i=i: self.load_file(i))
                    
            self.infotxt.append("Opened soundfont: " + path)
            self.instr_box.setEnabled(True)
            synth.program_select(0, self.soundbank, 0, 0)         
    
    def set_port(self, port):
        self.current_port = port
        self.serial.setPortName(port)
        
    def find_ports(self):
        port = []
        for info in QtSerialPort.QSerialPortInfo().availablePorts():
            #print(info.portName())
            port.append(info.portName())
        return port
    
    def draw_keyboard(self, data):
        qp = QPainter()
        qp.begin(self)        

    @QtCore.pyqtSlot()
    def receive(self):
        while self.serial.bytesAvailable():
            cmd = self.serial.read(3)
            #text = text.rstrip('\r\n')
            if cmd[0] == 144:
                self.infotxt.append("Note: " + str(cmd[1]) + "   Velocity: " + str(cmd[2]))
                synth.noteon(0, cmd[1], self.volume if cmd[2] != 0 else 0)

    @QtCore.pyqtSlot()
    def send(self):
        self.serial.write(self.message_le.text().encode())

    @QtCore.pyqtSlot(bool)
    def on_toggled(self, checked):
        self.button.setText("Disconnect" if checked else "Connect")
        if checked:
            if not self.serial.isOpen():
                if not self.serial.open(QtCore.QIODevice.ReadWrite):
                    self.button.setChecked(False)
                    self.infotxt.append("Connected to port: " + str(self.current_port))
        else:
            self.serial.close()
            self.infotxt.append("Disconnected port: " + str(self.current_port))


class Options(QDialog):
    def __init__(self, parent=None):
        super(Options, self).__init__(parent)
        
        #-----------------Title---------------------------
        self.setWindowTitle('CyberPiano Options')
        self.setWindowIcon(QIcon('icon.png'))
        self.resize(400, 300)
        self.setFont(QFont("Calibri", 16, QFont.Normal))
        self.infotxt_ = QLabel("It's empty like in my soul", self)
        lay = QVBoxLayout(self)
        lay.addWidget(self.infotxt_)

class Help(QDialog):
    def __init__(self, parent=None):
        super(Help, self).__init__(parent)
        
        #-----------------Title---------------------------
        self.setWindowTitle('CyberPiano Help')
        self.setWindowIcon(QIcon('icon.png'))
        self.setFixedSize(400, 300)
        self.setFont(QFont("Calibri", 16, QFont.Normal))
        self.infotxt_ = QLabel("I can't help you :(", self)
        lay = QVBoxLayout(self)
        lay.addWidget(self.infotxt_)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec_())