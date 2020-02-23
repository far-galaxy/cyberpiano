import simpleaudio as sa

i = input()
wave_obj = sa.WaveObject.from_wave_file("samples/Piano_C5.wav")
play_obj = wave_obj.play()
play_obj.wait_done()