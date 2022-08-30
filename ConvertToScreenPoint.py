def convertToScreen(self, x, y):
    winWidth = self.win.getXSize()
    winHeight = self.win.getYSize()
    drWidth = self.camera_one_buffer.getActiveDisplayRegion(0).getPixelWidth()
    drHeight = self.camera_one_buffer.getActiveDisplayRegion(0).getPixelHeight()

    # print("winHeight=", winHeight, "winWidth= ", winWidth)
    # print("bufferHeight=", drHeight, "bufferWidth= ", drWidth)
    # print("cx=", self.cx, " cy=", self.cy)

    #  CALCULATING X VALUE
    OldMaxX = winWidth
    OldMinX = 0
    NewMaxX = 1.3333
    NewMinX = -1.3333
    OldValueX = x

    OldRangeX = (OldMaxX - OldMinX)
    NewRangeX = (NewMaxX - NewMinX)
    newXvalue = (((OldValueX - OldMinX) * NewRangeX) / OldRangeX) + NewMinX

    #  CALCULATING Y VALUE
    oldY = drHeight - y
    newYvalue = (oldY / (winHeight / 2)) - 1
    """dividing by 2 because if position is less than half the screen it needs to enter negative"""

    self.screenPoints = (newXvalue, 0, newYvalue)

    return self.screenPoints