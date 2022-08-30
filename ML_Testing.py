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
import os
from ConvertToScreenPoint import convertToScreen


confvars = """

cursor-hidden true

"""
# win-size 800 600

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
        self.debugNP.setColor(3, 4, 2, 1)
        # self.debugNP.show()
        self.bullet_world.setDebugNode(self.debugNP.node())

        # MAIN PLAYER/CHARACTER

        # Step 1 = Create Shape
        self.height = 1.75
        self.radius = 1
        self.bulletCapShape = BulletCapsuleShape(self.radius, self.height - 2 * self.radius, ZUp)

        # Step 2 - Create Character Controller
        self.isPLayer1Active = True

        # PLAYER_ONE
        self.player1 = self.loader.loadModel('models/my models/sphere.bam')
        self.player1BulletCharContNode = BulletCharacterControllerNode(self.bulletCapShape, 0.4, 'player1')
        self.player1NP = self.render.attachNewNode(self.player1BulletCharContNode)
        self.player1NP.setCollideMask(BitMask32.allOn())
        self.player1NP.setColor(1, 1, 1, 1)
        self.player1NP.setPos(0, -50, 1)
        self.player1.reparentTo(self.player1NP)
        self.player1.setPos(0, 0, -1)
        self.bullet_world.attachCharacter(self.player1BulletCharContNode)

        # PLAYER_TWO

        self.player2 = self.loader.loadModel('models/my models/sphere.bam')
        self.player2BulletCharContNode = BulletCharacterControllerNode(self.bulletCapShape, 0.4, 'player2')
        self.player2NP = self.render.attachNewNode(self.player2BulletCharContNode)
        self.player2NP.setCollideMask(BitMask32.allOn())
        self.player2NP.setColor(1, 1, 1, 1)
        self.player2NP.setPos(-10, 0, 1)
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
        self.obstacle2GhostNP.setPos(1, 15, 1)
        self.obstacle2GhostNP.setColor(1, 2, 4, 3)

        # CUBE

        self.blackSquareImage = OnscreenImage(image='black square.png')
        self.blackSquareImage.setScale(0.02, 0.02, 0.02)

        self.yellowSquareImage = OnscreenImage(image='yellow square.png')
        self.yellowSquareImage.setScale(0.02, 0.02, 0.02)

        self.yellowSquareImage2 = OnscreenImage(image='yellow square.png')
        self.yellowSquareImage2.setScale(0.02, 0.02, 0.02)

        self.yellowSquareImage3 = OnscreenImage(image='yellow square.png')
        self.yellowSquareImage3.setScale(0.02, 0.02, 0.02)

        self.yellowSquareImage4 = OnscreenImage(image='yellow square.png')
        self.yellowSquareImage4.setScale(0.02, 0.02, 0.02)

        self.RectangleOverObject = LineSegs()


        # self.cube = self.loader.loadModel('models/my models/cube.bam')
        # self.cube.setScale(0.010, 0.010, 0.010)
        # self.cube.reparentTo(self.render2d)

        # Create a pair of offscreen buffers for each player/ball

        # CAM 1
        # Create Texture
        # Make Texture Buffer from Texture above and save to ram
        # Set Buffer Sort with setSort
        # Make camera from buffer with display region
        # Render Frame
        # re-parent and setPos (Optional)

        # BUFFER 1
        self.myTexture1 = Texture()
        """ using self.win.getXSize() for the buffer so it is always same size as the main window. 
                so its easier for center point translation"""
        self.camera_one_buffer = self.win.makeTextureBuffer('buffer_one', self.win.getXSize(), self.win.getYSize(),
                                                            self.myTexture1, to_ram=True)
        self.camera_one_buffer.setSort(-100)

        self.cam1 = self.makeCamera(self.camera_one_buffer, displayRegion=(0, 1, 0, 1))
        self.cam1.reparentTo(self.player1NP)
        self.cam1.setPos(0, 0, 3)
        self.cam.reparentTo(self.player1NP)
        self.cam.setPos(0, 0, 3)

        # BUFFER 2
        self.myTexture2 = Texture()
        """ using self.win.getXSize() for the buffer so it is always same size as the main window. 
        so its easier for center point translation"""
        self.camera_two_buffer = self.win.makeTextureBuffer('buffer_two', self.win.getXSize(), self.win.getYSize(),
                                                            self.myTexture2, to_ram=True)
        self.camera_two_buffer.setSort(-500)

        self.cam2 = self.makeCamera(self.camera_two_buffer, displayRegion=(0, 1, 0, 1))
        self.cam2.reparentTo(self.player2NP)
        self.cam2.setPos(0, -20, 3)

        self.graphicsEngine.renderFrame()

        print(self.camera_one_buffer.getActiveDisplayRegions())

        # print(self.cube_buffer.getActiveDisplayRegions())
        # self.camera_one_buffer.getActiveDisplayRegion(0).saveScreenshotDefault('lets see cube')

        #----------------------------------------------------------------------------------------#

        print('Cameras', self.camList, "\n")

        print('Total Number Of Display Regions', self.win.getNumDisplayRegions(), "\n")

        print('Active Display Regions')
        print(self.win.getActiveDisplayRegions(), "\n")

        print("List of display regions")
        print(self.win.getDisplayRegions(), "\n")

        print('Number Of Display Regions')
        print(self.win.getNumDisplayRegions(), "\n")

        self.dr = self.win.makeDisplayRegion()
        self.dr.setCamera(self.cam)



        #RENDER 2D
                                        # start, end, start, end
        # self.dr2 = self.win.makeDisplayRegion(L, R, B, T)
        # self.dr2.sort = 20
        # self.myCamera2d = NodePath(Camera('myCam2d'))
        # self.lens = OrthographicLens()
        # self.lens.setFilmSize(2, 2)
        # self.lens.setNearFar(-1000, 1000)
        # self.myCamera2d.node().setLens(self.lens)
        #
        # self.myRender2d = NodePath('myRender2d')
        # self.myRender2d.setDepthTest(False)
        # self.myRender2d.setDepthWrite(False)
        # self.myCamera2d.reparentTo(self.myRender2d)
        # dr.setCamera(myCamera2d)
        #
        # self.myRender2d = NodePath('myRender2d')
        # self.myRender2d.setDepthTest(False)
        # self.myRender2d.setDepthWrite(False)
        # self.myCamera2d.reparentTo(self.myRender2d)
        # self.cube.reparentTo(self.myRender2d)
        # self.dr2.setCamera(self.myCamera2d)


        # print(self.camList)

        # Other Variables
        self.mousespeed = 1000
        self.rotate_value = 0
        self.mouse_x = 0
        self.mouse_y = 0
        self.playerspeed = 20
        self.leftValue = 0
        self.centerX = 0
        self.centerY = 0
        self.move = 0.00
        self.savedContours = []
        self.arrayContourList = []
        """using arrayContourList because we need to convert the arrayContour to list for comparison 
                instead of arrayContour which is numpy array"""

        print("Aspect Ratio", self.getAspectRatio())

        # RUN UPDATE FUNCTIONS HERE
        self.taskMgr.add(self.MouseControl)
        self.taskMgr.add(self.update)
        self.taskMgr.add(self.checkGhost)
        self.taskMgr.add(self.motionDetection)

        # Store initial Value of Screenshot

        self.ourScreenshot1 = self.camera_one_buffer.getActiveDisplayRegion(0).getScreenshot()
        self.ourScData = self.ourScreenshot1.getRamImage()
        self.mv = memoryview(self.ourScData).tolist()

        self.numpyImg1 = np.array(self.mv, dtype=np.uint8)
        self.numpyImg1 = self.numpyImg1.reshape( (self.ourScreenshot1.getYSize(), self.ourScreenshot1.getXSize(), 4))
        # print("Screenshot Y Size" + str(self.ourScreenshot1.getXSize()))
        self.numpyImg1 = self.numpyImg1[::-1]

        self.previous_frame = self.numpyImg1

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
            if self.isPLayer1Active:
                self.isPLayer1Active = False
            elif not self.isPLayer1Active:
                self.isPLayer1Active = True
        # if inputState.isSet('detectObject'):

        if self.isPLayer1Active:
            self.cam.reparentTo(self.player1NP)
            self.cam.setPos(0, 0, 3)
            # print("CAMERA ASSOCIATED ", self.dr.getCamera().name)

            # MOVEMENT
            self.player1BulletCharContNode.setAngularMovement(omega)
            self.player1BulletCharContNode.setLinearMovement(speed, True)

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
            self.cam.reparentTo(self.player2NP)
            self.cam.setPos(0, 0, 3)

            # self.camera_one_np.reparentTo(self.player2NP)
            # MOVEMENT
            self.player2BulletCharContNode.setAngularMovement(omega)
            self.player2BulletCharContNode.setLinearMovement(speed, True)

    def motionDetection(self, task):

        # cap = cv2.VideoCapture('Test Video 4.mp4')

        self.ourScreenshot2 = self.camera_one_buffer.getActiveDisplayRegion(0).getScreenshot()
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

        arrayContour = contours

        if len(self.savedContours)>0 and len(arrayContour)>0:
            for item in self.savedContours:
                for sub in item:
                    for con in contours:
                        if sub.all() == con.all():
                            print("Found Something Similar")
                        else:
                            print("didnt find nothing")
                            self.savedContours.append(arrayContour)

        for contour in contours:

            (x, y, w, h) = cv2.boundingRect(contour)
            # print("x=" + str(x) + " y=" + str(y))
            if cv2.contourArea(contour) > 1500:
                cv2.drawContours(self.framecopy, contours, -1, (0, 255, 0), 2)
                cv2.rectangle(self.framecopy, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(self.framecopy, "Status: {}".format('Movement'), (10, 20), cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 0, 255), 3)
                self.yellowSquareImage.setPos(convertToScreen(self, x + w, y + h))
                self.yellowSquareImage2.setPos(convertToScreen(self, x, y))
                self.yellowSquareImage3.setPos(convertToScreen(self, x + w, y))
                self.yellowSquareImage4.setPos(convertToScreen(self, x, y + h))

                # self.RectangleOverObject.moveTo(self.convertToScreen(x, y))
                # self.RectangleOverObject.drawTo(self.convertToScreen(x + w, y + h))
                # self.RectangleOverObject.setThickness(4)
                # self.RectangleOverObjectNode = self.RectangleOverObject.create()
                # self.RectangleOverObjectNodeNP = NodePath(self.RectangleOverObjectNode)
                # self.RectangleOverObjectNodeNP.reparentTo(self.render)

                M = cv2.moments(contour)
                if M['m00'] != 0:
                    self.centerX = int(M["m10"] / M["m00"])
                    self.centerY = int(M["m01"] / M["m00"])
                    # draw the contour and center of the shape on the image
                    # cv2.drawContours(self.framecopy, [contour], -1, (0, 255, 0), 2)
                    cv2.circle(self.framecopy, (self.centerX, self.centerY), 7, (255, 255, 255), -1)
                    cv2.putText(self.framecopy, "center", (self.centerX - 20, self.centerY - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                    self.blackSquareImage.setPos(convertToScreen(self, self.centerX, self.centerY))




        self.previous_frame = self.current_frame
        cv2.imshow('OpenCV', self.framecopy)
        if cv2.waitKey(1) == ord('q'):
            cv2.destroyAllWindows()
            return

        return task.cont



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
