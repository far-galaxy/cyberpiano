import pyglet
from time import sleep
player = pyglet.media.Player()
song = pyglet.media.load('samples/Piano_C5.wav')
player.queue(song)
player.play()
