from direct.showbase.ShowBase import ShowBase, CollisionSphere
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import *

import math

confvars = """

cursor-hidden true

"""

load_prc_file_data("", confvars)
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

        self.disableMouse()
        self.surroundings = self.loader.loadModel('models/my models/ground.bam')
        self.surroundings.reparentTo(self.render)
        self.surroundings.setPos(0, 0, -2)

        # MAIN PLAYER/CHARACTER
        self.player = self.loader.loadModel('models/my models/sphere.bam')
        self.player.reparentTo(self.render)
        self.player.setPos(10, 30, 0)
        self.cam.setPos(0, -100, 10)

        self.cam.reparentTo(self.player)
        # self.cam.setPos(0, 2, 5) / Temporarily disabling this so we can see the collisions happen
        self.cam.setPos(0, 20, 8)
        self.cam.setH(180)
        self.cam.setP(-20)

        #COLLISION

        playerColSpshere = CollisionSphere(0, 0, 0, 2)
        cnodePath = self.player.attachNewNode(CollisionNode('cnode'))
        cnodePath.node().addSolid(playerColSpshere)
        cnodePath.show()

        # OBSTACLES TO KEEP TRACK OF MOVEMENT
        self.obstacle = self.loader.loadModel('models/jack')
        self.obstacle.reparentTo(self.render)
        self.obstacle.setPos(5, 0, 0)
        self.obstacle.setColor(1, 2, 4, 3)

        self.obstacle2 = self.loader.loadModel('models/jack')
        self.obstacle2.setPos(15, 15, 0)
        #Obstacle 2 Collision
        obs2ColSpshere = CollisionSphere(0, 0, 0, 2)
        cnodePathObs2 = self.obstacle2.attachNewNode(CollisionNode('cnodeObs2'))
        cnodePathObs2.node().addSolid(obs2ColSpshere)
        cnodePathObs2.show()
        self.obstacle2.reparentTo(self.render)

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

        # Other Variables
        self.mousespeed = 1000;
        self.rotate_value = 0
        self.mouse_x = 0
        self.mouse_y = 0
        self.playerspeed = 20

        # Solid = adding collider
        # Traverser = Checks for collisions/detections
        # Handler = action that happens when collision occurs can be Queue, Event or Pusher

        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()
        self.pusher.setHorizontal(True)

        self.pusher.addCollider(cnodePath, self.player)
        self.cTrav.addCollider(cnodePath, self.pusher)

        # RUN UPDATE FUNCTIONS HERE
        # self.taskMgr.add(self.camerapositioning)
        self.taskMgr.add(self.movePanda)
        self.taskMgr.add(self.MouseControl)

    def MouseControl(self, task):
        if self.mouseWatcherNode.hasMouse():
            dt = globalClock.getDt()
            mw = self.mouseWatcherNode
            x, y = mw.getMouseX(), mw.getMouseY()

            # move mouse back to center
            props = self.win.getProperties()
            self.win.movePointer(0,
                                 props.getXSize() // 2,
                                 props.getYSize() // 2)
            self.player.setH(self.player, -1 * x * dt * self.mousespeed)
        return task.cont

    def movePanda(self, task):
        dt = globalClock.getDt()

        if keymap["forward"]:
            self.player.setY(self.player, -self.playerspeed * dt)

        if keymap["backward"]:
            self.player.setY(self.player, self.playerspeed * dt)

        if keymap["strife_left"]:
            self.player.setX(self.player, self.playerspeed * dt)

        if keymap["strife_right"]:
            self.player.setX(self.player, -self.playerspeed * dt)

        if keymap["rotate"]:
            self.player.setH(self.rotate_value)
            self.rotate_value += 1

        return task.cont


testgame = MainGame()
testgame.run()