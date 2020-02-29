from PyQt5 import QtCore, QtWidgets, QtSerialPort
from PyQt5.QtGui import QIcon, QFont
from mingus.midi import fluidsynth 


#-----------------------------Init Synth----------------------------------------------
synth = fluidsynth.FluidSynthSequencer()
synth.init()

if sys.platform.startswith('win'):
    synth.start_audio_output("dsound")
    
elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
    synth.start_audio_output("alsa")
    

synth.load_sound_font('soundfonts/QUEST_O_TIME.SF2')
synth.set_instrument(0, 0)

class Widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        
        self.setWindowTitle('CyberPiano')
        self.setWindowIcon(QIcon('icon.png'))
        
        self.output_te = QtWidgets.QTextEdit(readOnly=True)
        self.button = QtWidgets.QPushButton(
            text="Connect", 
            checkable=True,
            toggled=self.on_toggled
        )
        ports = []
        for info in QtSerialPort.QSerialPortInfo().availablePorts():
            print(info.portName())
            ports.append(info.portName())
        
        lay = QtWidgets.QVBoxLayout(self)
        hlay = QtWidgets.QHBoxLayout()
        lay.addLayout(hlay)
        lay.addWidget(self.output_te)
        lay.addWidget(self.button)
        
        

        self.serial = QtSerialPort.QSerialPort(
            ports[0],
            baudRate=QtSerialPort.QSerialPort.Baud115200,
            readyRead=self.receive
        )

    @QtCore.pyqtSlot()
    def receive(self):
        while self.serial.bytesAvailable():
            text = self.serial.read(3)
            #text = text.rstrip('\r\n')
            self.output_te.append(str(text))
            synth.play_event(text[1],0,text[2])

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
        else:
            self.serial.close()

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec_())