# -*- coding: utf-8 -*-
#-----------CYBERPIANO-------------
import sys, os
try:
    import fluidsynth
except ModuleNotFoundError:
    os.system('pip install six')


try:
    from PyQt5 import QtCore, QtSerialPort
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import QIcon, QFont, QPainter, QColor, QPen, QBrush
    
except ModuleNotFoundError:
    if sys.platform.startswith('win'):
        os.system('pip install pyqt5')
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        os.system('sudo apt-get install python3-pyqt5')
        os.system('sudo apt-get install python3-pyqt5.qtserialport')
    from PyQt5 import QtCore, QtSerialPort
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import QIcon, QFont    

#-----------------------------Init Synth----------------------------------------------
synth = fluidsynth.Synth(1)
#Set gain to 1 in pyfluinsynth
#print(synth.main_volume(1, 0))

# Detect platform
if sys.platform.startswith('win'):
    synth.start("dsound")
    
elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
    synth.start("alsa")
    
# Open options file
try:
    opt = os.path.abspath('settings/options.txt')
    opt_file = open(opt, 'r')
    opts = opt_file.readline().replace("\n", "").split()
    octaves = int(opts[0])
    first_oct = int(opts[1])
    auto_con = int(opts[2])
    opt_file.close()
    
except FileNotFoundError:
    opt_file = open(opt, 'w')
    octaves = 10
    first_oct = 0
    opt_file.write("10 0 0")
    opt_file.close()

    
# Open list of recent files
try:
    lsf = os.path.abspath('settings/last_sf.txt')
    lsf_file = open(lsf, 'r')
    recent_files = []
    for i in lsf_file:
        recent_files.append(i[:-1])
    lsf_file.close()
except FileNotFoundError:
    lsf_file = open(lsf, 'w')
    recent_files = []
    
# Open list of languages
lst = os.path.abspath('settings/lang/list.txt')
langlist_file = open(lst, 'r')
langs = []
lang = int(langlist_file.readline()[:-1])
for i in langlist_file:
    langs.append(i.replace("\n","").split())
langlist_file.close()
    

    





class Widget(QWidget):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        
        self.soundbank = None
        self.instrument = 0
        self.volume = 127
        self.drag = 0
        self.octaves = octaves
        self.first_oct = first_oct
        self.auto_con = auto_con

        self.started = False
        self.set_lang(lang)
        self.key_state = [False for i in range(128)]
        
        #-----------------Title---------------------------
        self.setWindowTitle('CyberPiano')
        self.setWindowIcon(QIcon('icon.png'))
        self.resize(800, 600)
        self.setFont(QFont("Calibri", 16, QFont.Normal))
        
        self.w = self.frameGeometry().width()
        self.h = self.frameGeometry().height()
                        
        #-----------------Menubar---------------------------
        menubar = QMenuBar() 
        
        #  File menu
        file_menu = menubar.addMenu('&'+self.lp['file'])
        
        stop_all_menu = QAction(self.lp['stop_all'], self)
        stop_all_menu.setShortcut('Ctrl+D')
        stop_all_menu.triggered.connect(self.stop_all)         
        
        # Exit
        self.exitAction = QAction('&'+self.lp['exit'], self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.triggered.connect(qApp.quit)               
        
        # Load soundfont
        open_file_menu = QAction(self.lp['load_sf'], self)
        open_file_menu.setShortcut('Ctrl+O')
        open_file_menu.triggered.connect(self.open_file) 

        # Recent soundfonts
        self.recent_menu = QMenu(self.lp['res_sf'], self)
        for i in recent_files:
            self.recent_menu.addAction(i, lambda i=i: self.load_file(i))  

        file_menu.addAction(open_file_menu) 
        file_menu.addMenu(self.recent_menu)
        file_menu.addSeparator()
        file_menu.addAction(stop_all_menu)
        file_menu.addSeparator()
        file_menu.addAction(self.exitAction)            

        # Options menu
        opt_menu = menubar.addAction('&'+self.lp['options'])
        opt_menu.triggered.connect(self.options_window) 
        opt_menu.setShortcut('F2')
        
        #  Help menu
        help_menu = menubar.addAction('&'+self.lp['help'])
        help_menu.triggered.connect(self.help_window)  
        
        # About menu
        about_menu = menubar.addAction('&'+self.lp['about'])
        about_menu.triggered.connect(self.info_dialog)  
        help_menu.setShortcut('F1')
            
        
        #--------------Main Window----------------------------
        # Output textbox
        self.infotxt_ = QLabel(" ", self)
        
        # Ports List
        ports = self.find_ports()
        self.current_port = ports[0]
        
        self.ports_box = QComboBox(self)
        for i in ports:
            self.ports_box.addItem(i)   
        self.ports_box.activated[str].connect(self.set_port) 
        self.ports_box_ = QLabel(self.lp['port']+':', self)
        
        # Instruments List
        self.instr_box = QComboBox(self)
        for i in range(0, 128):
            self.instr_box.addItem(str(i)) 
        self.instr_box.activated[str].connect(self.set_instrument)  
        self.instr_box.setEnabled(False)
        self.instr_box_ = QLabel(self.lp['instrument']+':', self)     
        
        
        # Connect button
        self.button = QPushButton(text=self.lp['connect'], checkable=True, toggled=self.on_toggled)
        
        self.open_button = QPushButton(self.lp['load_sf'], self)
        self.open_button.clicked.connect(self.open_file)
        
        # Octaves
        oct_ = QLabel(self.lp['octave'] + ":", self)
        self.oct_d = QLabel('0', self)
        oct_d_button = QPushButton('<', self)
        oct_d_button.clicked.connect(self.oct_down)
        oct_u_button = QPushButton('>', self)
        oct_u_button.clicked.connect(self.oct_up)        
        
        # Volume
        sld = QSlider(QtCore.Qt.Horizontal, self)
        sld.setMaximum(127)
        sld.setValue(127)
        sld.valueChanged[int].connect(self.set_volume)
        self.sld_ = QLabel(self.lp['volume'] + ': 127', self)
        
        
        grid = QGridLayout()
        grid.setMenuBar(menubar)
        
        grid.addWidget(self.ports_box_,  0, 0, 1, 1)
        grid.addWidget(self.ports_box,   0, 1, 1, 3)
        grid.addWidget(self.button,      0, 4, 1, 2)    
        
        grid.addWidget(self.instr_box_,  1, 0, 1, 1)
        grid.addWidget(self.instr_box,   1, 1, 1, 3)
        grid.addWidget(self.open_button, 1, 4, 1, 2)  
        
        grid.addWidget(oct_,             2, 0)
        grid.addWidget(oct_d_button,     2, 1)
        grid.addWidget(self.oct_d,       2, 2)
        grid.addWidget(oct_u_button,     2, 3)
        grid.addWidget(self.sld_,        2, 4)
        grid.addWidget(sld,              2, 5)  
        
        grid.addWidget(self.infotxt_,     3, 0)    
        
        self.setLayout(grid)
        
        
        

        self.serial = QtSerialPort.QSerialPort(self.current_port, baudRate=QtSerialPort.QSerialPort.Baud115200, readyRead=self.receive)
        if self.auto_con == 1: self.on_toggled(True)
    
    def paintEvent(self, event):    
        painter = QPainter(self)
        self.w = self.frameGeometry().width()
        wk = (self.w)//(self.octaves*7)
        dx = (self.w - wk*(self.octaves*7))//2
        
        y = 200
        h = 75
        
        white_keys = [0,2,4,5,7,9,11]
        white_pos = 0
        black_pos = 0
        
        painter.setPen(QPen(QtCore.Qt.black,  1, QtCore.Qt.SolidLine))
        for i in range(len(self.key_state[self.first_oct*12 : self.first_oct*12+self.octaves*12])):
            if i%12 in white_keys:
                painter.setBrush(QtCore.Qt.yellow if self.key_state[i+self.first_oct*12] else QBrush(QColor(255, 255, 255), QtCore.Qt.SolidPattern))
                painter.drawRect(dx + white_pos*wk, y, wk, 2*h)  
                white_pos += 1
                
        painter.setPen(QPen(QtCore.Qt.white,  1, QtCore.Qt.SolidLine))
        for i in range(len(self.key_state[self.first_oct*12 : self.first_oct*12+self.octaves*12])):
            if not i%12 in white_keys:
                painter.setBrush(QtCore.Qt.yellow if self.key_state[i+self.first_oct*12] else QBrush(QColor(0, 0, 0), QtCore.Qt.SolidPattern))
                painter.drawRect(dx + black_pos*(wk) + wk//2, y, wk, h)
                black_pos += 2 if ( i%12 == 3 or i%12 == 10) else 1
                
        painter.setPen(QPen(QtCore.Qt.black,  1, QtCore.Qt.SolidLine))
        painter.drawLine(dx, y, dx + wk*self.octaves*7 , y)    
            
    def set_lang(self, num):
        path = os.path.abspath('settings/lang/'+langs[num][1]+'.lp')
        lang_file = open(path, 'r', encoding='utf-8')
        self.lp = {}
        for i in lang_file:
            key, word = i.split(' = ')
            self.lp[key] = word.replace("\n", "")
        langlist_file = open(lst, 'w')
        langlist_file.write(str(num)+'\n')
        for i in langs:
            langlist_file.write(' '.join(i)+'\n')
        langlist_file.close()
        
        if self.started:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText(self.lp['reboot'])
            msg.setWindowTitle(self.lp['reboot_title'])    
            msg.exec()
        else:
            self.started = True
   
    def options_window(self):
        opt_window = Options(self)
        opt_window.show()
    
    def help_window(self):
        window = Help(self)
        window.show()    
        
    def set_volume(self, vol):
        self.volume = vol
        self.sld_.setText(self.lp['volume']+": " + str(vol))
        
    def oct_down(self):
        self.drag -= 1
        self.oct_d.setText(str(self.drag))
    
    def oct_up(self):
        self.drag += 1
        self.oct_d.setText(str(self.drag))    
        
    def info_dialog(self):
        msg = QMessageBox() 
        msg.setIcon(QMessageBox.Information)
        msg.setText("CyberPiano v.0.30\nby far-galaxy")
        msg.setWindowTitle(self.lp['about'])    
        msg.exec()
             
    def set_instrument(self, instr):
        self.instrument = instr 
        synth.program_select(0, self.soundbank, 0, int(self.instrument))
        
    def open_file(self):
        file = QFileDialog.getOpenFileName(self, self.lp['load_sf2_file'], os.path.abspath("soundfonts/"), "Soundfonts (*.sf2)")
        self.load_file(file[0])
            
    def load_file(self, path):
        if path != "":
            self.soundbank = synth.sfload(path)
            if not path in recent_files:
                recent_files.insert(0, path)
                
            else:
                recent_files.pop(recent_files.index(path))
                recent_files.insert(0, path)
            
            lsf_file = open(lsf, 'w')
            for i in recent_files[:10]:
                lsf_file.write(i + '\n')
            lsf_file.close()
            self.recent_menu.clear()
            for i in recent_files[:10]:
                self.recent_menu.addAction(i, lambda i=i: self.load_file(i))
                    
            self.infotxt_.setText(path.split("/")[-1][:-4])
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
    

        
    def stop_all(self):
        for i in range(128):
            synth.noteon(0, i, 0) 
            self.key_state[i] = False
        self.update()

    @QtCore.pyqtSlot()
    def receive(self):
        while self.serial.bytesAvailable():
            cmd, note, vel = self.serial.read(3)
            note += (self.drag*12)
            if note > 127: note = 127
            if note < 0: note = 0
            if cmd == 144:
                synth.noteon(0, note, self.volume if vel != 0 else 0)
                self.key_state[note] = True if vel != 0 else False
                self.update()

    @QtCore.pyqtSlot()
    def send(self):
        self.serial.write(self.message_le.text().encode())

    @QtCore.pyqtSlot(bool)
    def on_toggled(self, checked):
        self.button.setText(self.lp['disconnect'] if checked else self.lp['connect'])
        if checked:
            if not self.serial.isOpen():
                if not self.serial.open(QtCore.QIODevice.ReadWrite):
                    self.button.setChecked(False)
        else:
            self.serial.close()


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
        
class Options(QDialog):
    def __init__(self, parent=None):
        super(Options, self).__init__(parent)
        self.parent = parent
        self.lp = parent.lp
        self.langs = langs
        
        #-----------------Title---------------------------
        self.setWindowTitle(self.lp['options'])
        self.setWindowIcon(QIcon('icon.png'))
        self.setFixedSize(400, 300)
        self.setFont(QFont("Calibri", 16, QFont.Normal))
        
        #-----------------Language-----------------------
        self.lang_ = QLabel(self.lp['language'] + ":", self)
        self.lang_box = QComboBox(self)
        for i in range(len(langs)):
            self.lang_box.addItem(QIcon('settings/lang/'+langs[i][1]+'.png'),langs[i][0], i)
        self.lang_box.setCurrentIndex(lang)
        self.lang_box.activated.connect(parent.set_lang)
        
        self.font_size = QSpinBox()
        self.font_size.setValue(self.parent.font().pointSize())
        self.font_size.setRange(2,36)
        self.font_size.valueChanged.connect(self.set_font)
        
        #----------------Piano-----------------------------
        self.oct_size_ = QLabel(self.lp['oct_size'] + ":", self)
        self.oct_size = QSpinBox()
        self.oct_size.setValue(self.parent.octaves)
        self.oct_size.setRange(1,10)
        self.oct_size.valueChanged.connect(self.set_oct_size)
        
        self.f_oct_ = QLabel(self.lp['f_oct'] + ":", self)
        self.f_oct = QSpinBox()
        self.f_oct.setValue(self.parent.first_oct)
        self.f_oct.setRange(0,10)
        self.f_oct.valueChanged.connect(self.set_f_oct) 
        
        #--------------Auto connect-------------------------
        ac = QCheckBox(self.lp['auto_con'], self)
        if self.parent.auto_con == 1: ac.toggle()
        ac.stateChanged.connect(self.set_auto_con)
        
        
        lay = QVBoxLayout(self)
        
        hlay1 = QHBoxLayout()
        hlay1.addWidget(self.lang_)
        hlay1.addWidget(self.lang_box)
        
        hlay2 = QHBoxLayout()
        hlay2.addWidget(self.oct_size_)
        hlay2.addWidget(self.oct_size)
        
        hlay3 = QHBoxLayout()
        hlay3.addWidget(self.f_oct_)  
        hlay3.addWidget(self.f_oct)        
        
        lay.addLayout(hlay1)
        lay.addLayout(hlay2)
        lay.addLayout(hlay3)
        lay.addWidget(ac)
        
    def set_auto_con(self, state):
        if state == QtCore.Qt.Checked:
            self.parent.auto_con = 1
        else:
            self.parent.auto_con = 0    
        opt_file = open(opt, 'w')
        opt_file.write(str(self.parent.octaves) + " " + str(self.parent.first_oct) + " " + str(self.parent.auto_con))
        opt_file.close()         
    
    def set_oct_size(self):
        self.parent.octaves = self.oct_size.value()
        opt_file = open(opt, 'w')
        opt_file.write(str(self.parent.octaves) + " " + str(self.parent.first_oct) + " " + str(self.parent.auto_con))
        opt_file.close() 
        self.parent.update()
        
        
    def set_f_oct(self):
        self.parent.first_oct = self.f_oct.value() 
        opt_file = open(opt, 'w')
        opt_file.write(str(self.parent.octaves) + " " + str(self.parent.first_oct) + " " + str(self.parent.auto_con))
        opt_file.close()          
        
    def set_font(self):
        font = self.parent.font()
        font.setPointSize(self.font_size.value())
        self.parent.setFont(font)
    
        


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec_())
