from direct.showbase.ShowBase import ShowBase, CollisionSphere
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import *
from panda3d.bullet import *
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

        self.bullet_world = BulletWorld()
        self.bullet_world.setGravity(Vec3(0, 0, -9.81))

        self.debug = BulletDebugNode('debug')
        self.debug.showBoundingBoxes(True)
        self.debug.showWireframe(True)
        self.debug.showConstraints(True)
        self.debugNP = self.render.attachNewNode(self.debug)
        self.debugNP.show()
        self.bullet_world.setDebugNode(self.debugNP.node())

        self.disableMouse()
        self.ground = self.loader.loadModel('models/my models/ground.bam')
        self.groundShape = BulletPlaneShape(Vec3(0, 0, 1), 3)
        self.groundRigidbody = BulletRigidBodyNode('ground')
        self.groundRigidbody.add_shape(self.groundShape)
        self.bullet_world.attachRigidBody(self.groundRigidbody)
        self.groundNP = self.render.attachNewNode(self.groundRigidbody)
        self.groundNP.setPos(0, 0, -2)
        self.ground.reparentTo(self.groundNP)

        # MAIN PLAYER/CHARACTER
        self.player = self.loader.loadModel('models/my models/sphere.bam')
        self.playerShape = BulletSphereShape(1)
        self.playerRigdbodyNode = BulletRigidBodyNode('player')
        self.playerRigdbodyNode.add_shape(self.playerShape)
        self.playerRigdbodyNode.setMass(1)
        self.bullet_world.attachRigidBody(self.playerRigdbodyNode)
        self.playerNP = self.render.attachNewNode(self.playerRigdbodyNode)
        self.playerNP.setPos(0, 0, 10)
        self.player.setPos(0, 0, 0)
        self.player.reparentTo(self.playerNP)

        # OBSTACLES TO KEEP TRACK OF MOVEMENT
        self.obstacle1 = self.loader.loadModel('models/jack')
        self.obstacle_1_Shape = BulletSphereShape(2)
        self.obstacle_1_RigidbodyNode = BulletRigidBodyNode('obs1')
        self.obstacle_1_RigidbodyNode.add_shape(self.obstacle_1_Shape)
        self.obstacle1NP = self.render.attachNewNode(self.obstacle_1_RigidbodyNode)
        self.bullet_world.attachRigidBody(self.obstacle_1_RigidbodyNode)
        self.obstacle1.reparentTo(self.obstacle1NP)
        self.obstacle1NP.setPos(5, 0, 1)
        self.obstacle1NP.setColor(1, 2, 4, 3)

        self.obstacle2 = self.loader.loadModel('models/jack')
        self.obstacle_2_Shape = BulletSphereShape(2)
        self.obstacle_2_RigidbodyNode = BulletRigidBodyNode('obs2')
        self.obstacle_2_RigidbodyNode.add_shape(self.obstacle_2_Shape)
        self.obstacle2NP = self.render.attachNewNode(self.obstacle_2_RigidbodyNode)
        self.bullet_world.attachRigidBody(self.obstacle_2_RigidbodyNode)
        self.obstacle2.reparentTo(self.obstacle2NP)
        self.obstacle2NP.setColor(1, 2, 4, 3)
        self.obstacle2NP.setPos(15, 15, 5)

        # self.cam.setPos(0, -100, 10)
        self.cam.reparentTo(self.playerNP)
        # # self.cam.setPos(0, 2, 5) / Temporarily disabling this so we can see the collisions happen
        self.cam.setPos(0, 20, 8)
        self.cam.setH(180)
        self.cam.setP(-20)

        # KEYBOARD INPUT
        self.accept("w", updatekeymap, ["forward", True])
        self.accept("w-up", updatekeymap, ["forward", False])

        self.accept("s", updatekeymap, ["backward", True])
        self.accept("s-up", updatekeymap, ["backward", False])

        self.accept("a", updatekeymap, ["strife_left", True])
        self.accept("a-up", updatekeymap, ["strife_left", False])

        self.accept("d", updatekeymap, ["strife_right", True])
        self.accept("d-up", updatekeymap, ["strife_right", False])

        # Other Variables
        self.mousespeed = 1000;
        self.rotate_value = 0
        self.mouse_x = 0
        self.mouse_y = 0
        self.playerspeed = 20

        # RUN UPDATE FUNCTIONS HERE

        self.taskMgr.add(self.movePanda)
        self.taskMgr.add(self.MouseControl)
        self.taskMgr.add(self.applyGravity)
        self.taskMgr.add(self.checkingRaycasting)

    def checkingRaycasting(self, task):
        self.pFrom = Point3(0, 0, 0)
        self.pTo = Point3(3, 0, 0)
        self.result = self.bullet_world.rayTestClosest(self.pFrom, self.pTo)

        if self.result.hasHit():
            print(self.result.hasHit())
            print(self.result.getHitPos())
            print(self.result.getHitNormal())
            print(self.result.getHitFraction())
            print(self.result.getNode())
        return task.cont

    def applyGravity(self, task):
        dt = globalClock.getDt()
        self.bullet_world.doPhysics(dt)
        return task.cont

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
            self.playerNP.setHpr(self.playerNP, -1 * x * dt * self.mousespeed)
        return task.cont

    def movePanda(self, task):
        dt = globalClock.getDt()

        if keymap["forward"]:
            self.playerNP.setY(self.playerNP, -self.playerspeed * dt)

        if keymap["backward"]:
            self.playerNP.setY(self.playerNP, self.playerspeed * dt)

        if keymap["strife_left"]:
            self.playerNP.setX(self.playerNP, self.playerspeed * dt)

        if keymap["strife_right"]:
            self.playerNP.setX(self.playerNP, -self.playerspeed * dt)

        return task.cont


testgame = MainGame()
testgame.run()
