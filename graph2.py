import pyglet

win = pyglet.window.Window()
pyglet.gl.glClearColor(1, 1, 1, 1)

@win.event
def on_draw():
    win.clear()

pyglet.app.run()