from PyQt5 import QtCore, QtWidgets, QtSerialPort
from PyQt5.QtGui import QIcon, QFont
import fluidsynth
import sys, os

print(os.path.abspath("soundfonts/"))

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




class Widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        
        self.soundbank = None
        self.instrument = 0
        
        #-----------------Title---------------------------
        self.setWindowTitle('CyberPiano')
        self.setWindowIcon(QIcon('icon.png'))
        self.resize(800, 600)
        self.setFont(QFont("Calibri", 16, QFont.Normal))
        
        # Output textbox
        self.infotxt = QtWidgets.QTextEdit(readOnly=True)
        self.infotxt_ = QtWidgets.QLabel('Information:', self)
        
        # Ports List
        ports = self.find_ports()
        self.current_port = ports[0]
        
        self.ports_box = QtWidgets.QComboBox(self)
        for i in ports:
            self.ports_box.addItem(i)   
        self.ports_box.activated[str].connect(self.set_port) 
        self.ports_box_ = QtWidgets.QLabel('Port:', self)
        
        # Instruments List
        self.instr_box = QtWidgets.QComboBox(self)
        for i in range(0, 128):
            self.instr_box.addItem(str(i)) 
        self.instr_box.activated[str].connect(self.set_instrument)  
        self.instr_box.setEnabled(False)
        self.instr_box_ = QtWidgets.QLabel('Instrument:', self)
        
        
        # Connect button
        self.button = QtWidgets.QPushButton(text="Connect", checkable=True, toggled=self.on_toggled)
        
        self.open_button = QtWidgets.QPushButton("Open .sf2", self)
        self.open_button.clicked.connect(self.open_file)
        
        
        
        lay = QtWidgets.QVBoxLayout(self)
        
        hlay1 = QtWidgets.QHBoxLayout()
        hlay1.addWidget(self.ports_box_)
        hlay1.addWidget(self.ports_box)
        hlay1.addWidget(self.button)
        
        
        hlay2 = QtWidgets.QHBoxLayout()
        hlay2.addWidget(self.instr_box_)
        hlay2.addWidget(self.instr_box)
        hlay2.addWidget(self.open_button)
        
        
        lay.addLayout(hlay1)
        lay.addLayout(hlay2)
        lay.addStretch(1)
        lay.addWidget(self.infotxt_)
        lay.addWidget(self.infotxt)
        
        
        

        self.serial = QtSerialPort.QSerialPort(self.current_port, baudRate=QtSerialPort.QSerialPort.Baud115200, readyRead=self.receive)
     
    def set_instrument(self, instr):
        self.instrument = instr
        synth.program_select(0, self.soundbank, 0, int(instr))
        self.infotxt.append("Set instrument: " + str(instr))
        
    def open_file(self):
        file = QtWidgets.QFileDialog.getOpenFileName(self, "Open .sf2 Soundbank", os.path.abspath("soundfonts/"), "Soundbanks (*.sf2)")
        self.soundbank = synth.sfload(file[0])
        self.infotxt.append("Opened soundfont: " + file[0])
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

    @QtCore.pyqtSlot()
    def receive(self):
        while self.serial.bytesAvailable():
            cmd = self.serial.read(3)
            #text = text.rstrip('\r\n')
            if cmd[0] == 144:
                self.infotxt.append("Note: " + str(cmd[1]) + "   Velocity: " + str(cmd[2]))
                synth.noteon(0, cmd[1], cmd[2])

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

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec_())