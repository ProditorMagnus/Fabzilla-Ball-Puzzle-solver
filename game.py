import pyautogui
import time
from os import listdir
from os.path import isfile, join

pyautogui.PAUSE = 0.1


class game:
    def __init__(self):
        self.data = []
        for i in range(20):
            row = []
            for j in range(20):
                row.append("?")
            self.data.append(row)

    def show(self):
        for row in self.data:
            for cell in row:
                print(cell, end="")
            print()
    def setxy(self, x, y, s):
        if x<0 or y<0 or x>19 or y >19:
            #print("error", x, y, s)
            return
            fail()
        if self.data[y][x] != "?" and self.data[y][x]!=s:
            pass
            #print("overwrite",x,y, self.data[y][x], s)
        self.data[y][x]=s

    def filled(self):
        for i in range(20):
            for j in range(20):
                if self.data[i][j]=="?":
                    return False
        return True
    
    def solve(self):
        knownPositions = {}
        start = self.getAll("+")[0]
        goal = self.getAll("O")[0]
        knownPositions[start] = []

        queue = [start]
        print(knownPositions)
        
        while goal not in knownPositions and len(queue) > 0:
            #print("queue", queue)
            #print(knownPositions)
            active = queue.pop(0)
            print("take from queue", active)
            path = knownPositions[active]
            transitions = self.getTransitions(active)
            for direction in transitions:
                transition = transitions[direction]
                if transition is not None and transition not in knownPositions:
                    knownPositions[transition] = path + [direction]
                    print("add to queue", transition)
                    queue.append(transition)
                
                pass
        print("loop ended", knownPositions)
        if goal in knownPositions:
            print("win:", len(knownPositions[goal]), knownPositions[goal])
            input("go?")
            time.sleep(3)
            for direction in knownPositions[goal]:
                pyautogui.keyDown(direction)
                pyautogui.keyUp(direction)
                time.sleep(6)
            


    def getTransitions(self, fromPos):
        transitions = {"up":None, "down":None, "right":None, "left":None}
        
        for direction in ["up", "down", "left", "right"]:
            transitions[direction] = self.attemptMoveTo(direction, fromPos)
        
        #print(transitions)
        return transitions


    def attemptMoveTo(self, direction, fromPos):
        pos = fromPos
        portals = self.getAll("¤")
        xo = 0
        yo = 0
        oneWay = ""
        if direction == "down":
            xo = 1
            oneWay = "ˇ"
        elif direction == "up":
            xo = -1
            oneWay = "^"
        elif direction == "left":
            yo = -1
            oneWay = "<"
        elif direction == "right":
            yo = 1
            oneWay = ">"

        endPos = pos
        loopDetector = 0
        while loopDetector < 43:
            loopDetector +=1
            potentialPos = ((endPos[0]+xo)%20,(endPos[1]+yo)%20)
            nextSymbol = self.data[potentialPos[0]][potentialPos[1]]
            #print("next", nextSymbol, "at", potentialPos)
            if nextSymbol in [" ", oneWay, "+"]:
                endPos = potentialPos
                continue
            elif nextSymbol in ["#", "<", "^", "ˇ", ">"]:
                break
            elif nextSymbol == "¤":
                if portals[0][0] == potentialPos[0] and portals[0][1] == potentialPos[1]:
                    endPos = portals[1]
                else:
                    endPos = portals[0]
                potentialPos = endPos
                #print("next", nextSymbol, "at", potentialPos)
                continue
            elif nextSymbol == "O":
                print("WIN!", direction)
                return potentialPos
        if loopDetector > 40:
            #print("loop if moving", direction)
            return None
        else:
            #print("from", pos, "to", endPos, "if moving", direction)
            return endPos


    def getAll(self, symbol):
        result = []
        for i in range(20):
            for j in range(20):
                if self.data[i][j]==symbol:
                    result.append((i,j))
        return result
        

g = game()

def findOne(name):
    i = 0
    while True:
        i +=1
        try:
            return pyautogui.locateOnScreen(name)
        except:
            if i > 100:
                print(name)
                raise
            pass

def findAny(name):
    try:
        return list(pyautogui.locateAllOnScreen(name))
    except:
        return []


def close(actual, expected, leeway):
    return abs(actual-expected)<=leeway


def fillBoardPx():
    portalColor = {(255, 51, 0), (210, 2, 2), (255, 255, 0), (255, 153, 0), (255, 102, 0)}
    endColor = {(0, 204, 51), (0, 102, 51), (0, 51, 51), (0, 255, 51), (0, 153, 51)}
    startColor = {(255, 0, 0)}
    dirColor = {(255, 204, 255), (255, 102, 255), (255, 153, 255), (255, 51, 255), (219, 2, 219)}
    xC = []
    yC = []

    x0 = 420
    y0 = 54
    x19 = 1180
    y19 = 814

    for i in range(20):
        xC.append(x0+(x19-x0)//19*i)

    for i in range(20):
        yC.append(y0+(y19-y0)//19*i)

    for x in xC:
        for y in yC:
            xi = (x-x0)//40
            yi = (y-y0)//40
            px = pyautogui.pixel(x, y)
            if close(px.red, 91, 5) and close(px.green, 189, 5) and close(px.blue, 255, 5):
                g.setxy(xi, yi, " ")
            elif px.red == 0 and close(px.green, 150, 5) and close(px.blue, 255, 5):
                g.setxy(xi, yi, "#")
            else:
                
                colors = set()
                for i in range(20):
                    px = pyautogui.pixel(x, y)
                    colors.add((px.red,px.green,px.blue))
                    #print("unknown", px, xi, yi)
                    if colors == portalColor:
                        g.setxy(xi, yi, "¤")
                        break
                    if colors == endColor:
                        g.setxy(xi, yi, "O")
                        break
                if colors == portalColor or colors == endColor:
                    pass
                elif colors == startColor:
                    g.setxy(xi, yi, "+")
                    # static image, cant decide from color
                else:# colors == dirColor:
                    # create screenshots until it starts repeating, then commpare file
                    im = pyautogui.screenshot(region=(x-20,y-20, 40, 40))
                    direction = None

                    mypath = "gateToRight"
                    files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
                    for (folder, symbol) in [("gateToRight" , ">"), ("gateToDown", "ˇ"), ("gateToUp", "^"), ("gateToLeft", "<")]:
                        files = [f for f in listdir(folder) if isfile(join(folder, f))]
                        for f in files:
                            try:
                                pyautogui.locate(join(folder,f),im)
                                g.setxy(xi,yi,symbol)
                                direction = symbol
                                break
                            except:
                                pass

                    
                    if direction is None:
                        ts = time.time()
                        pyautogui.moveTo(x, y, duration=1)
                        direction = input("which direction ")
                        pyautogui.moveTo(300, 50, duration=0)
                        for i in range(100):
                            im = pyautogui.screenshot(region=(x-10,y-10, 16, 16))
                            if direction == ">":
                                im.save("gateToRight/"+str(ts)+"_"+str(i)+".png")
                            elif direction == "<":
                                im.save("gateToLeft/"+str(ts)+"_"+str(i)+".png")
                            elif direction == "^":
                                im.save("gateToUp/"+str(ts)+"_"+str(i)+".png")
                            elif direction == "ˇ":
                                im.save("gateToDown/"+str(ts)+"_"+str(i)+".png")
                            else:
                                fail()
                            g.setxy(xi,yi,direction)



fillBoardPx()
g.show()
g.solve()






