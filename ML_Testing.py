from direct.showbase.InputStateGlobal import inputState
from direct.showbase.ShowBase import ShowBase, CollisionSphere
from direct.showbase.ShowBaseGlobal import globalClock
from direct.showbase.InputStateGlobal import InputState
from panda3d.core import *
from panda3d.bullet import *
from panda3d.physics import *

import math

from panda3d.physics import ActorNode

confvars = """

cursor-hidden true

"""

load_prc_file_data("", confvars)

class MainGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()

        self.bullet_world = BulletWorld()
        self.bullet_world.setGravity(Vec3(0, 0, -9.81))

        self.debug = BulletDebugNode('debug')
        self.debug.showBoundingBoxes(True)
        self.debug.showWireframe(True)
        self.debug.showConstraints(True)
        self.debugNP = self.render.attachNewNode(self.debug)
        self.debugNP.setColor(3,4,2,1)
        self.debugNP.show()
        self.bullet_world.setDebugNode(self.debugNP.node())

        # MAIN PLAYER/CHARACTER

        # Step 1 = Create Shape
        self.height = 1.75
        self.radius = 1
        self.bulletCapShape = BulletCapsuleShape(self.radius, self.height - 2 * self.radius, ZUp)

        # Step 2 - Create Character Controller
        self.player = self.loader.loadModel('models/my models/sphere.bam')
        self.playerBulletCharContNode = BulletCharacterControllerNode(self.bulletCapShape, 0.4, 'player')
        self.playerNP = self.render.attachNewNode(self.playerBulletCharContNode)
        self.playerNP.setCollideMask(BitMask32.allOn())
        self.playerNP.setColor(1,1,1,1)
        self.playerNP.setPos(0, 0, 20)
        self.player.reparentTo(self.playerNP)
        self.player.setPos(0,0,-1)
        self.bullet_world.attachCharacter(self.playerBulletCharContNode)

        inputState.watchWithModifiers('forward', 'w')
        inputState.watchWithModifiers('backward', 's')
        inputState.watchWithModifiers('left', 'a')
        inputState.watchWithModifiers('right', 'd')
        inputState.watchWithModifiers('turnRight', 'space')

        self.ground = self.loader.loadModel('models/my models/ground.bam')
        self.groundShape = BulletPlaneShape(Vec3(0, 0, 1), 3)
        self.groundRigidbody = BulletRigidBodyNode('ground')
        self.groundRigidbody.add_shape(self.groundShape)
        self.bullet_world.attachRigidBody(self.groundRigidbody)
        self.groundNP = self.render.attachNewNode(self.groundRigidbody)
        self.groundNP.setPos(0, 0, -2)
        self.ground.reparentTo(self.groundNP)

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

        # GHOST
        self.obstacle2 = self.loader.loadModel('models/jack')
        self.obstacle_2_Shape = BulletSphereShape(1)
        self.obstacle2Ghost = BulletGhostNode('ob2Ghost')
        self.obstacle2Ghost.addShape(self.obstacle_2_Shape)
        self.obstacle2GhostNP = self.render.attachNewNode(self.obstacle2Ghost)
        self.obstacle2GhostNP.setCollideMask(BitMask32(0x0f))
        self.bullet_world.attachGhost(self.obstacle2Ghost)
        self.obstacle2.reparentTo(self.obstacle2GhostNP)
        self.obstacle2GhostNP.setPos(1,15, 1)
        self.obstacle2GhostNP.setColor(1, 2, 4, 3)

        # self.cam.setPos(0, -100, 10)
        self.cam.reparentTo(self.playerNP)
        # # self.cam.setPos(0, 2, 5) / Temporarily disabling this so we can see the collisions happen
        self.cam.setPos(0, -20, 5)
        #self.cam.setH(90)
        self.cam.setP(-20)

        # KEYBOARD INPUT

        # Other Variables
        self.mousespeed = 1000
        self.rotate_value = 0
        self.mouse_x = 0
        self.mouse_y = 0
        self.playerspeed = 20

        # RUN UPDATE FUNCTIONS HERE

        self.taskMgr.add(self.MouseControl)
        self.taskMgr.add(self.update)
        self.taskMgr.add(self.checkGhost)

    def checkGhost(self, task):
        ghost = self.obstacle2GhostNP.node()
        if ghost.getNumOverlappingNodes():
            # print(ghost.getNumOverlappingNodes())
            for node in ghost.getOverlappingNodes():
                if node.getName() == "player":
                    print(node.getName())
                    return

        return task.cont

    def processInput(self, dt):
        speed = Vec3(0, 0, 0)
        omega = 0.0

        if inputState.isSet('forward'): speed.setY(10.0)
        if inputState.isSet('backward'): speed.setY(-10.0)
        if inputState.isSet('left'):    speed.setX(-10.0)
        if inputState.isSet('right'):   speed.setX(10.0)
        if inputState.isSet('turnLeft'):  omega = 20.0
        if inputState.isSet('turnRight'): omega = -20.0

        self.playerBulletCharContNode.setAngularMovement(omega)
        self.playerBulletCharContNode.setLinearMovement(speed, True)

    def update(self, task):
        dt = globalClock.getDt()

        self.processInput(dt)
        self.bullet_world.doPhysics(dt, 4, 1. / 240.)

        return task.cont

    def MouseControl(self, task):
        if self.mouseWatcherNode.hasMouse():
            dt = globalClock.getDt()
            mw = self.mouseWatcherNode
            x, y = mw.getMouseX(), mw.getMouseY()

            # move mouse back to center
            props = self.win.getProperties()
            self.win.movePointer(0, props.getXSize() // 2, props.getYSize() // 2)
            self.playerNP.setH(self.playerNP, -1 * x * dt * self.mousespeed)
            self.cam.setP(self.cam, 1 * y * dt * self.mousespeed)
        return task.cont


testgame = MainGame()
testgame.run()
