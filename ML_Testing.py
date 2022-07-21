from direct.showbase.InputStateGlobal import inputState
from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import *
from panda3d.core import GraphicsWindow
from panda3d.bullet import *
from panda3d.physics import *
import numpy as np
import cv2
from direct.gui.OnscreenImage import OnscreenImage
from pandac.PandaModules import loadPrcFileData

confvars = """

cursor-hidden true

"""
# loadPrcFileData("", "want-directtools #t")
# loadPrcFileData("", "want-tk #t")

load_prc_file_data("", confvars)

class MainGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        # self.disableMouse()
        self.bullet_world = BulletWorld()
        self.bullet_world.setGravity(Vec3(0, 0, -9.81))

        self.debug = BulletDebugNode('debug')
        self.debug.showBoundingBoxes(True)
        self.debug.showWireframe(True)
        self.debug.showConstraints(True)
        self.debugNP = self.render.attachNewNode(self.debug)
        self.debugNP.setColor(3,4,2,1)
        # self.debugNP.show()
        self.bullet_world.setDebugNode(self.debugNP.node())

        # MAIN PLAYER/CHARACTER

        # Step 1 = Create Shape
        self.height = 1.75
        self.radius = 1
        self.bulletCapShape = BulletCapsuleShape(self.radius, self.height - 2 * self.radius, ZUp)

        # Step 2 - Create Character Controller
        self.isPLayer1Active = True;

        # PLAYER_ONE
        self.player1 = self.loader.loadModel('models/my models/sphere.bam')
        self.player1BulletCharContNode = BulletCharacterControllerNode(self.bulletCapShape, 0.4, 'player1')
        self.player1NP = self.render.attachNewNode(self.player1BulletCharContNode)
        self.player1NP.setCollideMask(BitMask32.allOn())
        self.player1NP.setColor(1, 1, 1, 1)
        self.player1NP.setPos(0, -50, 20)
        self.player1.reparentTo(self.player1NP)
        self.player1.setPos(0, 0, -1)
        self.bullet_world.attachCharacter(self.player1BulletCharContNode)

        # PLAYER_TWO

        self.player2 = self.loader.loadModel('models/my models/sphere.bam')
        self.player2BulletCharContNode = BulletCharacterControllerNode(self.bulletCapShape, 0.4, 'player2')
        self.player2NP = self.render.attachNewNode(self.player2BulletCharContNode)
        self.player2NP.setCollideMask(BitMask32.allOn())
        self.player2NP.setColor(1, 1, 1, 1)
        self.player2NP.setPos(-10, 0, 20)
        self.player2.reparentTo(self.player2NP)
        self.player2.setPos(0, 0, -1)
        self.bullet_world.attachCharacter(self.player2BulletCharContNode)

        inputState.watchWithModifiers('forward', 'w')
        inputState.watchWithModifiers('backward', 's')
        inputState.watchWithModifiers('left', 'a')
        inputState.watchWithModifiers('right', 'd')
        inputState.watchWithModifiers('turnRight', 'space')
        inputState.watchWithModifiers('switchPlayer', 'p')
        inputState.watchWithModifiers('detectObject', 't')

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

        # Create a pair of offscreen buffers for each player/ball

        # VERY IMPORTANT LINE OF CODE BELOW ( camNode.setActive(0) ) disables main camera so we can use multiple cameras

        self.camNode.setActive(0)

        # CAM 1
        # Create Camera Node
        self.camera_one = Camera("camera_one")
        # Create Texture Buffer
        self.camera_one_buffer = self.win.makeTextureBuffer('buffer_one', 700, 500)
        # Clear bufer
        self.camera_one_buffer.setClearColor(VBase4(0, 0, 0, 0))
        # use Buffer as Camera
        self.cam1 = self.makeCamera(self.camera_one_buffer)
        self.cam1.reparentTo(self.player1NP)
        self.cam1.setPos(0, 0, 3)

        # Create a pair of cards to display the contents of these buffer
        self.camera_one_Card = CardMaker('cam1 Card')
        self.camera_one_Card.setFrame(-1, 1, -1, 1)
        self.camera_one_Card.setColor(1, 1, 1, 0.5)
        self.camera_one_CardNP = self.render.attachNewNode(self.camera_one_Card.generate())
        self.camera_one_CardNP.setTransparency(1)
        self.camera_one_CardNP.setTexture(self.camera_one_buffer.getTexture())

        # CAM 2

        self.camera_two = Camera("camera_two")
        self.camera_two_buffer = self.win.makeTextureBuffer('buffer_two', 700, 500)
        self.camera_two_buffer.setClearColor(VBase4(0, 0, 0, 0))
        self.cam2 = self.makeCamera(self.camera_two_buffer)
        self.cam2.reparentTo(self.player2NP)
        self.cam2.setPos(0, -20, 3)

        # Create a pair of cards to display the contents of these buffer
        # overlayed with the main window.
        self.camera_two_Card = CardMaker('cam2 Card')
        self.camera_two_Card.setFrame(-1, 1, -1, 1)
        self.camera_two_Card.setColor(1, 1, 1, 0.5)
        self.camera_two_CardNP = self.render.attachNewNode(self.camera_two_Card.generate())
        self.camera_two_CardNP.setTransparency(1)
        self.camera_two_CardNP.setTexture(self.camera_two_buffer.getTexture())

        # Turn off the main camera, so we don't get them in triplicate.

        #Testing 2D render



        #Choose Which Camera is associated with the Display Region
        self.dr = self.win.getDisplayRegion(1)
        self.dr.setCamera(self.cam1)

        # CUBE
        self.cube = self.loader.loadModel('models/my models/cube.bam')
        self.cube.setScale(0.010, 0.010, 0.010)

        #RENDER 2D
                                        # start, end, start, end
        # self.dr2 = self.win.makeDisplayRegion(L, R, B, T)
        self.dr2 = self.win.getDisplayRegion(2)
        self.dr2.sort = 20

        self.myCamera2d = NodePath(Camera('myCam2d'))
        self.lens = OrthographicLens()
        self.lens.setFilmSize(2, 2)
        self.lens.setNearFar(-1000, 1000)
        self.myCamera2d.node().setLens(self.lens)

        self.myRender2d = NodePath('myRender2d')
        self.myRender2d.setDepthTest(False)
        self.myRender2d.setDepthWrite(False)
        self.myCamera2d.reparentTo(self.myRender2d)
        self.cube.reparentTo(self.myRender2d)
        self.dr2.setCamera(self.myCamera2d)

        print(self.camList)

        # Other Variables
        self.mousespeed = 1000
        self.rotate_value = 0
        self.mouse_x = 0
        self.mouse_y = 0
        self.playerspeed = 20
        self.leftValue = 0
        self.cx = 0
        self.cy = 0
        self.move = 0.00

        # RUN UPDATE FUNCTIONS HERE
        self.taskMgr.add(self.MouseControl)
        self.taskMgr.add(self.update)
        self.taskMgr.add(self.checkGhost)
        self.taskMgr.add(self.motionDetection)

        # Store initial Value of Screenshot

        self.ourScreenshot1 = self.dr.getScreenshot()
        self.ourScData = self.ourScreenshot1.getRamImage()
        self.mv = memoryview(self.ourScData).tolist()

        self.numpyImg1 = np.array(self.mv, dtype=np.uint8)
        self.numpyImg1 = self.numpyImg1.reshape( (self.ourScreenshot1.getYSize(), self.ourScreenshot1.getXSize(), 4))
        print("Screenshot Y Size" + str(self.ourScreenshot1.getXSize()))
        self.numpyImg1 = self.numpyImg1[::-1]

        self.previous_frame = self.numpyImg1

        self.runcount = 0


        # print("Display Regions ", self.win.getDisplayRegions())
        # self.win.removeDisplayRegion(self.win.getDisplayRegion(1))
        # self.win.removeDisplayRegion(self.win.getDisplayRegion(1))
        # self.win.removeDisplayRegion(self.win.getDisplayRegion(1))
        print(len(self.win.getDisplayRegions()))
        # print("Display Regions ", self.win.getDisplayRegions())
        print("cam1 display regions" , self.cam1.node().display_regions)
        print("cam2 display regions" , self.cam2.node().display_regions)
        print("myCamera2d display regions" , self.myCamera2d.node().display_regions)



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

        if inputState.isSet('forward'):speed.setY(10.0)
        if inputState.isSet('backward'): speed.setY(-10.0)
        if inputState.isSet('left'):    speed.setX(-10.0)
        if inputState.isSet('right'):   speed.setX(10.0)
        if inputState.isSet('turnLeft'):  omega = 20.0
        if inputState.isSet('turnRight'): omega = -20.0
        if inputState.isSet('switchPlayer'):
            if self.isPLayer1Active == True:
                self.isPLayer1Active = False;
            elif self.isPLayer1Active == False:
                self.isPLayer1Active = True;
        # if inputState.isSet('detectObject'):

        if self.isPLayer1Active == True:
            # getdr = self.win.getActiveDisplayRegion(1)
            # getdr.setActive(1)

            # CAMERA
            self.camera_two_buffer.setClearColor(VBase4(0, 0, 0, 0))
            self.camera_one_buffer.setClearColor(VBase4(0, 0, 0, 0))
            # self.win.getActiveDisplayRegion(1).setActive(1)

            # print(self.numpyImg)

            # self.camera_one_np.reparentTo(self.player1NP)
            # MOVEMENT
            self.player1BulletCharContNode.setAngularMovement(omega)
            self.player1BulletCharContNode.setLinearMovement(speed, True)

            # print(self.player2NP.getPos())

            self.leftValue += (1*dt)

            # print(self.leftValue)
            if 0 <= self.leftValue <= 3:
                self.player2NP.setPos(self.player2NP, (2 * dt, 0, 0))
            elif 3 < self.leftValue <= 6:
                self.player2NP.setPos(self.player2NP, (-2 * dt, 0, 0))
            else:
                self.leftValue = 0

        else:
            # CAMERA
            self.camera_two_buffer.setClearColor(VBase4(0, 0, 0, 0))
            self.camera_one_buffer.setClearColor(VBase4(0, 0, 0, 0))
            # self.dr.setCamera(self.cam2)

            # self.camera_one_np.reparentTo(self.player2NP)
            # MOVEMENT
            self.player2BulletCharContNode.setAngularMovement(omega)
            self.player2BulletCharContNode.setLinearMovement(speed, True)

    def motionDetection(self, task):

        # cap = cv2.VideoCapture('Test Video 4.mp4')

        self.ourScreenshot2 = self.dr.getScreenshot()
        self.ourScData2 = self.ourScreenshot2.getRamImage()
        self.mv2 = memoryview(self.ourScData2).tolist()

        self.numpyImg2 = np.array(self.mv2, dtype=np.uint8)
        self.numpyImg2 = self.numpyImg2.reshape(
            (self.ourScreenshot2.getYSize(), self.ourScreenshot2.getXSize(), 4))
        self.numpyImg2 = self.numpyImg2[::-1]
        self.current_frame = self.numpyImg2
        self.framecopy = self.current_frame.copy()
        # ret, frame = cap.read()
        diff = cv2.absdiff(self.previous_frame, self.current_frame)
        # converting from color to gray because it is easy to find contour in grayscale mode
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        # Threshold makes sure something is either full black or full white, based on threshold defined
        _, threshold = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(threshold, None, iterations=3)
        _, contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # cv2.drawContours(self.previous_frame, contours, -1, (0, 255, 0), 2)

        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            # print("x=" + str(x) + " y=" + str(y))
            if cv2.contourArea(contour) > 1200:
                cv2.rectangle(self.framecopy, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(self.framecopy, "Status: {}".format('Movement'), (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 0, 255), 3)

            M = cv2.moments(contour)

            self.cx = int(M["m10"] / M["m00"])
            self.cy = int(M["m01"] / M["m00"])
            # draw the contour and center of the shape on the image
            # cv2.drawContours(self.framecopy, [contour], -1, (0, 255, 0), 2)
            cv2.circle(self.framecopy, (self.cx, self.cy), 7, (255, 255, 255), -1)
            cv2.putText(self.framecopy, "center", (self.cx - 20, self.cy - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            # print("screen width",  self.win.getXSize())
            # print("dr width",  self.dr.getPixelWidth())
            # print("dr height",  self.dr.getPixelHeight())
            # print("ball X ",  self.cx)
            # print("ball Y ",  self.cy)

        self.cube.setPos(self.convertToScreen(self.cx, self.cy))
        self.previous_frame = self.current_frame
        cv2.imshow('hi', self.framecopy)
        if cv2.waitKey(1) == ord('q'):
            cv2.destroyAllWindows()
            return

        return task.cont

    def convertToScreen(self, x, y):

        winWidth = self.dr2.getPixelWidth()
        winHeight= self.dr2.getPixelHeight()
        #
        # print("winHeight=", winHeight, "winWidth= ", winWidth)
        # print("cx=", self.cx, " cy=", self.cy)

        self.screenpointX = ( (self.cx) / winWidth * 2) - 1
        self.screenpointY = ( (self.cy) / winHeight * 2) - 1

        self.screenPoints = (self.screenpointX, 0, self.screenpointY)
        # print(self.screenPoints)
        return self.screenPoints

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
            # self.camera_one_np.setP(self.camera_one_np, 1 * y * dt * self.mousespeed)

            if self.isPLayer1Active == True:
                self.player1NP.setH(self.player1NP, -1 * x * dt * self.mousespeed)
            elif self.isPLayer1Active == False:
                self.player2NP.setH(self.player2NP, -1 * x * dt * self.mousespeed)

        return task.cont

    def empty(self, x):
        pass

    def templateMatchingScreenshot(self):
        # OpenCV

        #Send Screenshot as a numpy array to OpenCV so we use it as our image

        self.ourScreenshot =  self.dr.getScreenshot()
        self.ourScRawData = self.ourScreenshot.getRamImage()
        self.mv = memoryview(self.ourScRawData).tolist()

        self.numpyImg = np.array(self.mv, dtype=np.uint8)
        self.numpyImg = self.numpyImg.reshape((self.ourScreenshot.getYSize(), self.ourScreenshot.getXSize(), 4))
        self.numpyImg = self.numpyImg[::-1]

        # load image
        self.mainScreenshot = self.numpyImg  # cv2.imread('screenshot.jpg', 0) ##
        self.mainScreenshot_GRAYSCALE = cv2.cvtColor(self.mainScreenshot, 1)
        self.mytemp =cv2.imread('Images for OpenCV/Blue Ball Sample.jpg') # cv2.imread('Images for OpenCV/Blue Ball Sample.jpg', 0)
        h, w, c = self.mytemp.shape

        # # took this method out , cv2.TM_CCORR, it almost never gave good results

        # methods = [cv2.TM_CCOEFF, cv2.TM_CCOEFF_NORMED,
        #            cv2.TM_CCORR_NORMED, cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]
        self.ourMethod = cv2.TM_CCOEFF_NORMED

        self.scCopy = self.mainScreenshot_GRAYSCALE.copy()
        result = cv2.matchTemplate(self.scCopy, self.mytemp, self.ourMethod)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        print(cv2.minMaxLoc(result))
        #
        # if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        #     drawRectangle_start_top_left = min_loc
        # else:
        drawRectangle_start_top_left = max_loc

        bottom_right = (drawRectangle_start_top_left[0] + w, drawRectangle_start_top_left[1] + h)

        cv2.rectangle(self.scCopy, drawRectangle_start_top_left, bottom_right, 255, 5)
        # print (min_loc, max_loc)
        cv2.imshow('Template Match', self.scCopy)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


testgame = MainGame()
testgame.run()
