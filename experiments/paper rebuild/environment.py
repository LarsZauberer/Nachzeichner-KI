import os
import random
import numpy as np
import math as ma

class ShapeDraw(object):
    def __init__(self, sidelength, patchsize, referenceData):
        self.s = sidelength
        self.p = patchsize #sidelength of patch (local Input). must be odd
        
        #Input gloabal stream
        self.referenceData = referenceData
        self.canvas = np.full((self.s, self.s), 1)
        self.distmap = np.zeros((self.s, self.s))
        self.colmap = np.zeros((self.s, self.s))
        
        #Input local stream
        self.ref_patch = np.zeros((self.p, self.p))
        self.canvas_patch = np.zeros((self.p, self.p))

        #possible outputs
        self.n_actions= self.p*self.p*2

        #initializes rest
        self.lastSim = 0
        self.reference = referenceData[0]
        self.curRef = 0
        self.agentPos = [0,0]
        self.isDrawing = 0 # 0 = not Drawing, 1 = Drawing (not bool because NN)
        self.set_agentPos([random.randrange(0, self.s), random.randrange(0, self.s)])

    def step(self, agent_action):
        action = [0,0]
        self.isDrawing = 1
        
        x = agent_action % self.p
        y = agent_action // self.p
        if y >= self.p:
            y -= self.p
            self.isDrawing = 0
        
        action = [x,y]
        if self.move_isLegal(action):
            self.set_agentPos(action)
        else:
            self.isDrawing = False
        
        reward = self.reward() if self.isDrawing else 0

        return [self.reference, self.canvas, self.distmap, self.colmap], [self.ref_patch, self.canvas_patch], reward

    def set_agentPos(self, pos):
        if self.isDrawing:
            self.canvas = drawline(self.agentPos, pos, self.canvas)
        self.agentPos = pos
        self.update_distmap()
        self.update_patch()
        self.update_colmap()
        
    def update_distmap(self):
        x0 = self.agentPos[0]
        y0 = self.agentPos[1]
        for y in range(self.s):
            for x in range(self.s):
                dist =  ma.sqrt((x-x0)**2 + (y-y0)**2)/self.s
                self.distmap[y][x] = dist

    def update_colmap(self):
        for y in range(self.s):
            for x in range(self.s):
                self.colmap[y][x] = self.isDrawing
    
    def update_patch(self):
        patchX = int(self.agentPos[0]-(self.p-1)/2)
        patchY = int(self.agentPos[1]-(self.p-1)/2)
        for y in range(self.p):
            for x in range(self.p):
                yInd = 0 if patchY+y >= len(self.reference) else patchY+y
                xInd = 0 if patchX+x >= len(self.reference[0]) else patchX+x
                self.ref_patch[y][x] = self.reference[yInd][xInd]
                self.canvas_patch[y][x] = self.canvas[yInd][xInd]

    def reward(self):
        reward
        similarity = 0
        for i in range(self.s):
            for j in range(self.s):
                similarity += (self.canvas[i][j] - self.reference[i][j])**2
        similarity = similarity/(self.s**2)
        reward = similarity - self.lastSim
        self.lastSim = similarity

        return reward # Add on (from paper): Reward big steps

    def move_isLegal(self, action):
        if action[0] >= len(self.canvas[0]) or action[0] < 0:
            return False
        if action[1] >= len(self.canvas) or action[1] < 0:
            return False
        return True

    def reset(self):
        self.curRef += 1
        self.reference = self.referenceData[self.curRef]
        self.canvas = np.full((self.s, self.s), 1)
        self.set_agentPos(random.randrange(0, self.s), random.randrange(0, self.s))
        return [self.reference, self.canvas, self.distmap, self.colmap], [self.ref_patch, self.canvas_patch]
    

#draws Line directly on bitmap to save convert
def drawline(setpos, pos, canvas):
    weight = 1
    dx = pos[0] - setpos[0] 
    dy = pos[1] - setpos[1] 
    linePix = []

    if dx == 0 and dy == 0:
        return

    if abs(dx) > abs(dy):
        inc = int(ma.copysign(1,dx))
        for i in range(0, dx+inc, inc):
            linePix.append([setpos[0]+i, 0])
        
        step = dy/(abs(dx)+1)
        sign = int(ma.copysign(1,dy))
        move = 0
        res = 0
        for i in range((abs(dx)+1)):
            res += step
            if sign*res >= 0.5:
                move += sign
                res -= sign
            linePix[i][1] = setpos[1]+move

        for pix in linePix:
            canvas[pix[1]][pix[0]-weight] = 0
            canvas[pix[1]][pix[0]+weight] = 0
            canvas[pix[1]][pix[0]] = 0
    else:
        inc = int(ma.copysign(1,dy))
        for i in range(0, dy+inc, inc):
            linePix.append([0, setpos[1]+i])
        
        step = dx/(abs(dy)+1)
        sign = int(ma.copysign(1,dx))
        move = 0
        res = 0
        for i in range((abs(dy)+1)):
            res += step
            if sign*res >= 0.5:
                move += sign
                res -= sign
            linePix[i][0] = setpos[0]+move

        for pix in linePix:
            canvas[pix[1]][pix[0]+weight] = 0
            canvas[pix[1]][pix[0]-weight] = 0
            canvas[pix[1]][pix[0]] = 0
    
    return canvas