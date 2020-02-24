import time
import fluidsynth

fs = fluidsynth.Synth()
fs.start()

sfid = fs.sfload("soundfonts/Piano.sf2")
fs.program_select(0, sfid, 0, 0)

fs.noteon(0, 60, 30)