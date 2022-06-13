from direct.directbase.DirectStart import *
from pandac.PandaModules import *
from direct.task import Task
from direct.actor import Actor
import math

# Create a pair of offscreen buffers in which to view the "left"
# and "right" eyes.
leftBuffer = base.win.makeTextureBuffer('left', 512, 512)
leftBuffer.setClearColor(VBase4(0, 0, 0, 0))
base.makeCamera(leftBuffer)
rightBuffer = base.win.makeTextureBuffer('right', 512, 512)
rightBuffer.setClearColor(VBase4(0, 0, 0, 0))
base.makeCamera(rightBuffer)

# Create a pair of cards to display the contents of these buffer
# overlayed with the main window.
leftCard = CardMaker('left')
leftCard.setFrame(-1, 1, -1, 1)
leftCard.setColor(1, 1, 1, 0.5)
leftCardNP = render2d.attachNewNode(leftCard.generate())
leftCardNP.setTransparency(1)
leftCardNP.setTexture(leftBuffer.getTexture())
rightCard = CardMaker('right')
rightCard.setFrame(-1, 1, -1, 1)
rightCard.setColor(1, 1, 1, 0.5)
rightCardNP = render2d.attachNewNode(rightCard.generate())
rightCardNP.setTransparency(1)
rightCardNP.setTexture(rightBuffer.getTexture())

# Turn off the main camera, so we don't get them in triplicate.
base.camNode.setActive(0)

base.makeCamera(base.win, displayRegion=(0, 0.5, 0, 1))
base.makeCamera(base.win, displayRegion=(0.5, 1, 0, 1))

# Move the eyes apart a little bit, and converge them both on a point
# 20 feet ahead.
base.camList[1].setPos(-0.5, 0, 0)
base.camList[1].lookAt(0, 20, 0)
base.camList[2].setPos(0.5, 0, 0)
base.camList[2].lookAt(0, 20, 0)

# load an environment model
environ = loader.loadModel("models/environment")
environ.reparentTo(render)
environ.setScale(0.25, 0.25, 0.25)
environ.setPos(-8, 42, 0)


def SpinCamera1Task(task):
    angledegrees = task.time * 6.0
    angleradians = angledegrees * (math.pi / 180.0)
    base.camList[1].setPos(-20 * math.sin(angleradians), -20.0 * math.cos(angleradians), 3)
    base.camList[1].setHpr(angledegrees, 0, 0)
    return Task.cont


def SpinCamera2Task(task):
    angledegrees = task.time * 6.0
    angleradians = angledegrees * (math.pi / 180.0)
    base.camList[2].setPos(20 * math.sin(angleradians), -20.0 * math.cos(angleradians), 3)
    base.camList[2].setHpr(angledegrees, 0, 0)
    return Task.cont


taskMgr.add(SpinCamera1Task, "SpinCamera1Task")
taskMgr.add(SpinCamera2Task, "SpinCamera2Task")

# Load the panda actor, and loop its animation
pandaActor = Actor.Actor("models/panda-model", {"walk": "models/panda-walk4"})
pandaActor.setScale(0.005, 0.005, 0.005)
pandaActor.reparentTo(render)
pandaActor.loop("walk")

run()
