from direct.showbase.ShowBase import ShowBase

class MainGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.player = self.loader.loadModel('models/jack')
        self.player.reparentTo(self.render)
        self.cam.setPos(0, -20, 0)


testgame = MainGame()
testgame.run()