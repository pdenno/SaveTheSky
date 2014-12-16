#!/usr/bin/python

import Tkinter as tk
import random
import os

GAME = False
TILE_X_SIZE = 60
TILE_Y_SIZE = 60

class Thing(object): # "New style objects"
    pass

# A Tile is a rectangular things with a position and a state. 
# The subclasses of Tile are Bird, Cloud, Snow, Rain, and Sun
class Tile(Thing):
    def __init__(self, irow, icol, off_file, on_file):
        global GAME # There is only one of these.
        self.row = irow
        self.col = icol
        self.state = 0 # 0 means not pressed. 1 means pressed.
        self.off_image = tk.PhotoImage(file=off_file) # file to show when button is 'on'.
        self.on_image = tk.PhotoImage(file=on_file)   # file to show when button is 'off'.
        self.widget = tk.Button(GAME.canvas, image=self.off_image, borderwidth=0, command=self.buttonPress)
        self._drop_position = 0
        
    def __repr__(self):
        return "<%s (%s %s)>" % (self.__class__.__name__, self.row, self.col)
    
    def draw(self):
        "Place the widget on the screen."
        #print "Drawing {0} at x = {1}, y={2}".format(self,TILE_X_SIZE*((self.col)-1),TILE_Y_SIZE*((self.row)-1))
        #print "Drawing {0}, self.state = {1}".format(self,self.state)
        if self.state == 0:
            self.widget.configure(image = self.off_image)
            self.widget.place_forget()
            self.widget.place(x=TILE_X_SIZE*(self.col), y=TILE_Y_SIZE*(self.row))
        else:  #  self.state == 1
            print "Tile ({0},{1}) state is {2}.".format(self.row, self.col, self.state)
            self.widget.configure(image = self.on_image)
            self.widget.place_forget()
            self.widget.place(x=TILE_X_SIZE*(self.col), y=TILE_Y_SIZE*(self.row))
    def drop(self):
        "Slowly drop the widget downward one row."
        self.widget.place_forget()
        self._drop_position = self._drop_position + 1
        self.widget.place(x=TILE_X_SIZE*(self.col), y=TILE_Y_SIZE*(self.row-1) + self._drop_position)
        self._drop_job_id = GAME.root.after(3, self.drop)
        if self._drop_position >= TILE_Y_SIZE:
            GAME.root.after_cancel(self._drop_job_id)
            self._drop_position = 0
            
    def buttonPress(self):
        "If off, turn on. If on, turn off by changing state and image."
        print "\n\nStart button press {0}, self.state = {1}".format(self,self.state)        
        if self.state == 0:
            self.state = 1
            self.draw()
            self.maybeSwap() 
            for item in GAME.three_in_a_row():
                GAME.deleteTiles(item)
                GAME.dropTiles(item)
        else:
            self.state = 0 
            self.draw()
            print "End button press {0}, self.state = {1}".format(self,self.state)
            
    def maybeSwap(self):
        '''Check tiles next to self. If ON, then swap and turn both off'''
        print 'check for swap'
        near_me = self.neighbors()
        print "neighbors = {0}".format(near_me)
        for near in near_me:
            if near.state == 1:
                hold_row = self.row
                hold_col = self.col
                self.row = near.row
                self.col = near.col
                near.row = hold_row
                near.col = hold_col
                near.state = 0
                self.state = 0
                self.draw()
                near.draw()
                GAME.grid[self.row][self.col] = self
                GAME.grid[near.row][near.col] = near
                break
            
    def neighbors(self):
        n = False
        r = self.row
        c = self.col
        print "r = {0} c = {1}".format(r, c)
        last_row = GAME.nrows-1
        last_col = GAME.ncols-1
        # first see if it is a corner...
        if r == 0 and c == 0:   # upper-left corner
            n = [GAME.grid[0][1], GAME.grid[1][0]]
        elif r == last_row and c == 0: # lower-left corner
            n = [GAME.grid[last_row][1], GAME.grid[last_row-1][0]]
        elif r == 0 and c == last_col: # upper-right corner
            n = [GAME.grid[0][last_col-1], GAME.grid[1][last_col]]
        elif r == last_row and c == last_col: # lower-right corner
            n = [GAME.grid[last_row][last_col-1], GAME.grid[last_row-1][last_col]]
        # ...else see if it is an edge
        elif r == 0: # top edge
            n = [GAME.grid[0][c-1], GAME.grid[0][c+1], GAME.grid[1][c]]
        elif c == last_col: # right edge
            n = [GAME.grid[r-1][last_col], GAME.grid[r+1][last_col], GAME.grid[r][last_col-1]]
        elif r == last_row: # bottom edge
            n = [GAME.grid[last_row][c-1], GAME.grid[last_row][c+1], GAME.grid[last_row-1][c]]
        elif c == 0: # left edge
            n = [GAME.grid[r-1][0],GAME.grid[r+1][0],GAME.grid[r][1]]
        # It is not a corner or and edge...
        else: # everything that isn't a corder or edge looks like this
            n = [GAME.grid[r][c-1],GAME.grid[r+1][c],GAME.grid[r][c+1],GAME.grid[r-1][c]]
        return n

# Each of these calls the superclass constructor (Tile) to set the row and column
# that the game item is to appear on, and sets the 'off' and 'on' images.
class Bird(Tile):
    def __init__(self,irow,icol):
        super(Bird,self).__init__(irow,icol,"images/bird60OFF.gif", "images/bird60ON.gif")

class Cloud(Tile):
    def __init__(self,irow,icol):
        super(Cloud,self).__init__(irow,icol,"images/cloud60OFF.gif","images/cloud60ON.gif")

class Snow(Tile): 
    def __init__(self,irow,icol):
        super(Snow,self).__init__(irow,icol,"images/snow60OFF.gif","images/snow60ON.gif")

class Rain(Tile): 
    def __init__(self,irow,icol):
        super(Rain,self).__init__(irow,icol,"images/rain60OFF.gif","images/rain60ON.gif")

class Sun(Tile): 
    def __init__(self,irow,icol):
        super(Sun,self).__init__(irow,icol,"images/sun60OFF.gif","images/sun60ON.gif")

        
class Game (object):
    def __init__(self,rows=5,cols=7):
        global GAME
        self.grid = []
        self.nrows = rows
        self.ncols = cols
        GAME = self
        self.start_gui()
    def start_gui (self):
        "Do basic window setup."
        os.chdir("/home/pdenno/new-projects/owen/saveTheSky")
        self.root = tk.Tk()
        self.root.geometry("480x320+200+200")
        self.canvas = tk.Canvas(self.root, width = 480, height = 320, bg = 'LightBlue')
        self.canvas.pack()
        self.empty_image = tk.PhotoImage(file="images/black.gif") # <=== all black for temporarily empty area
        for i in range(self.nrows): # Walk through the rows
            row = []
            for j in range(self.ncols): # Walk through the columns
                ipick = random.randint(1,5)
                if ipick == 1:
                    row.append(Bird(i,j))
                elif ipick == 2:
                    row.append(Cloud(i,j))
                elif ipick == 3:
                    row.append(Rain(i,j))
                elif ipick == 4:
                    row.append(Snow(i,j))
                elif ipick == 5:
                    row.append(Sun(i,j))
            self.grid.append(row)
        for i in range(self.nrows):
            for j in range(self.ncols):
                 self.grid[i][j].draw()
        print "grid = {0}".format(self.grid)
        self.root.mainloop()
    def three_in_a_row(self):
        '''Return a list of tiles that end a sequence of three or more in a row.'''
        g = self.grid # use a variable so you don't have to type self.grid all the time.
        found = []
        for i in range(0,self.nrows):
            type1 = type(g[i][0])
            count_same = 1
            for j in range(1,self.ncols):
                type2 = type(g[i][j])
                if type1 == type2:
                    count_same = count_same + 1
                    if count_same == 3:
                        found.append(g[i][j])
                    elif count_same > 3:
                        del found[-1]
                        found.append(g[i][j])
                else: # They are not equal. Start over.
                    type1 = type2
                    count_same = 1
        return found
    def deleteTiles(self,tile):
        '''Remove this item. If the tile to its right is the same type, call this again to remove it too.'''
        tile.widget.destroy()
        tile.state = -1
        if (tile.col > 0):
            on_left = GAME.grid[tile.row][tile.col-1]
            if type(tile) == type(on_left):
                self.deleteTiles(on_left)
    def dropTiles(self,start_tile):
        '''Drop tiles above the start_tile and every tile of its type to the left.
        all the way to the top row. Then fill in top row with new tiles.'''
        print "Dropping starting at {0}".format(start_tile)
        irow = start_tile.row
        icol = start_tile.col
        len = 3
        if icol-3 >= 0 and self.grid[irow][icol-3].state == -1:
            len = 4
        if icol-4 >= 0 and self.grid[irow][icol-4].state == -1:
            len = 5
        for i in range (irow-1,-1,-1):
            for j in range(icol,icol-len,-1):
                print "  Dropping into ({0},{1}), state = {2}".format(i+1, j, self.grid[i+1][j].state)
                self.grid[i][j].row = i+1
                self.grid[i+1][j] = self.grid[i][j]
                self.grid[i+1][j].drop()
            
    


