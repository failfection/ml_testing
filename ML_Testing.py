from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
import math

keymap = {
    "forward": False,
    "backward": False,
    "strife_left": False,
    "strife_right": False,
    "rotate": False
}

def updatekeymap(key, state):
    keymap[key] = state


class MainGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.surroundings = self.loader.loadModel('models/my models/ground.bam')
        self.surroundings.reparentTo(self.render)
        self.surroundings.setPos(0, 0, -2)

        #MAIN PLAYER/CHARACTER
        self.player = self.loader.loadModel('models/my models/sphere.bam')
        self.player.reparentTo(self.render)
        self.player.setPos(10, 30, 0)
        self.cam.setPos(0, -100, 10)

        self.cam.reparentTo(self.player)
        self.cam.setPos(0, 2, 5)
        self.cam.setH(180)
        self.cam.setP(-20)

        #OBSTACLES TO KEEP TRACK OF MOVEMENT
        self.obstacle = self.loader.loadModel('models/jack')
        self.obstacle.reparentTo(self.render)
        self.obstacle.setPos(5, 0, 0)
        self.obstacle.setColor(1, 2, 4, 3)

        self.obstacle2 = self.loader.loadModel('models/jack')
        self.obstacle2.reparentTo(self.render)
        self.obstacle2.setPos(15, 15, 0)

        self.accept("w", updatekeymap, ["forward", True])
        self.accept("w-up", updatekeymap, ["forward", False])

        self.accept("s", updatekeymap, ["backward", True])
        self.accept("s-up", updatekeymap, ["backward", False])

        self.accept("a", updatekeymap, ["strife_left", True])
        self.accept("a-up", updatekeymap, ["strife_left", False])

        self.accept("d", updatekeymap, ["strife_right", True])
        self.accept("d-up", updatekeymap, ["strife_right", False])

        self.accept("space", updatekeymap, ["rotate", True])
        self.accept("space-up", updatekeymap, ["rotate", False])


        self.value = 0

        # RUN UPDATE FUNCTIONS HERE
        # self.taskMgr.add(self.camerapositioning)
        self.taskMgr.add(self.movePanda)
        self.taskMgr.add(self.mouse_position)

        #Other Variables
        self.mousespeed = 50;

    # def camerapositioning(self, task):
    #     self.cam.reparentTo(self.player)
    #     self.cam.setPos(0, 2, 5)
    #     self.cam.setH(180)
    #     self.cam.setP(-20)
    #     return task.cont

    def movePanda(self, task):
        if keymap["forward"]:
            print(self.player.getForward())
            pos = self.player.getPos()
            pos.y -= 0.3
            self.player.setPos(pos)
            self.player.setFluidPos()

        if keymap["backward"]:
            pos = self.player.getPos()
            pos.y += 0.3
            self.player.setPos(pos)

        if keymap["strife_left"]:
            pos = self.player.getPos()
            pos.x += 0.3
            self.player.setPos(pos)

        if keymap["strife_right"]:
            pos = self.player.getPos()
            pos.x -= 0.3
            self.player.setPos(pos)

        if keymap["rotate"]:
            self.player.setH(self.value)
            self.value += 1

        return task.cont

    def mouse_position(self, task):
        if self.mouseWatcherNode.hasMouse():
            dt = globalClock.getDt()
            self.mouse_x = 0
            self.mouse_y = 0

            self.mouse_x = self.mouseWatcherNode.getMouseX() * self.mousespeed
            self.mouse_y = self.mouseWatcherNode.getMouseY() * self.mousespeed
            # print(mouse_x)

            self.player.setH(-1 * self.mouse_x)
            # self.player.setH(math.atan2(y,x)*57.29578+90)
        return task.cont


testgame = MainGame()
testgame.run()