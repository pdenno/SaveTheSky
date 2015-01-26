#!/usr/bin/python3

import tkinter as tk
import random
import os
import getpass

os.chdir("/home/{0}/SkySwitch/source".format(getpass.getuser()))

GAME = False
TILE_X_SIZE = 52  # Width of tiles in pixels
TILE_Y_SIZE = 52  # Length of tiles in pixels
START_MOVES = 5   # Moves the user is allowed

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

    def class_name(self):
        self.__class__.__name__
    
    def draw(self):
        "Place the widget on the screen."
        #"Drawing {0} at x = {1}, y={2}".format(self,TILE_X_SIZE*((self.col)-1),TILE_Y_SIZE*((self.row)-1))
        #"Drawing {0}, self.state = {1}".format(self,self.state)
        if self.state == 0:
            self.widget.configure(image = self.off_image)
            self.widget.place_forget()
            self.widget.place(x=TILE_X_SIZE*(self.col), y=TILE_Y_SIZE*(self.row))
        elif self.state == 1:
            "Tile ({0},{1}) state is {2}.".format(self.row, self.col, self.state)
            self.widget.configure(image = self.on_image)
            self.widget.place_forget()
            self.widget.place(x=TILE_X_SIZE*(self.col), y=TILE_Y_SIZE*(self.row))
            
    def drop(self):
        "Slowly drop the widget downward one row."
        self.widget.place_forget()
        self._drop_position = self._drop_position + 4
        self.widget.place(x=TILE_X_SIZE*(self.col), y=TILE_Y_SIZE*(self.row-1) + self._drop_position)
        self._drop_job_id = GAME.root.after(60, self.drop) # Change for faster drop
        if self._drop_position >= TILE_Y_SIZE:
            GAME.root.after_cancel(self._drop_job_id)
            self._drop_position = 0
            
    def buttonPress(self):
        "If off, turn on. If on, turn off by changing state and image."
        "\n\nStart button press {0}, self.state = {1}".format(self,self.state)        
        if self.state == 0:
            self.state = 1
            self.draw()
            self.maybeSwap() 
            for item in GAME.three_in_a_row():
                GAME.deleteTiles(item)
                GAME.dropTiles(item)
            if GAME.moves <= 0:
                GAME.root.wait_window(EndOfGameDialog(GAME.root).top)
        else:
            self.state = 0 
            self.draw()
            "End button press {0}, self.state = {1}".format(self,self.state)

    def forget(self):
        "Remove the tile. Destroy it's widget."
        self.state = -1
        self.widget.pack_forget()
        self.widget.destroy()
            
    def maybeSwap(self):
        '''Check tiles next to self. If ON, then swap and turn both off'''
        near_me = self.neighbors()
        "neighbors = {0}".format(near_me)
        for near in near_me:
            if near.state == 1:
                if GAME.moves > 0:
                    GAME.moves = GAME.moves - 1
                GAME.movesText.set("Moves\n{0}".format(GAME.moves))
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
        "r = {0} c = {1}".format(r, c)
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
        else: # everything that isn't a corner or edge looks like this:
            n = [GAME.grid[r][c-1],GAME.grid[r+1][c],GAME.grid[r][c+1],GAME.grid[r-1][c]]
        return n

# Each of these calls the superclass constructor (Tile) to set the row and column
# that the game item is to appear on, and sets the 'off' and 'on' images.
class Bird(Tile):
    def __init__(self,irow,icol):
        super(Bird,self).__init__(irow,icol,"../images/bird52OFF.gif", "../images/bird52ON.gif")

class Cloud(Tile):
    def __init__(self,irow,icol):
        super(Cloud,self).__init__(irow,icol,"../images/cloud52OFF.gif","../images/cloud52ON.gif")

class Snow(Tile): 
    def __init__(self,irow,icol):
        super(Snow,self).__init__(irow,icol,"../images/snow52OFF.gif","../images/snow52ON.gif")

class Rain(Tile): 
    def __init__(self,irow,icol):
        super(Rain,self).__init__(irow,icol,"../images/rain52OFF.gif","../images/rain52ON.gif")

class Sun(Tile): 
    def __init__(self,irow,icol):
        super(Sun,self).__init__(irow,icol,"../images/sun52OFF.gif","../images/sun52ON.gif")

        
class Game (object):
    def __init__(self,rows=5,cols=7):
        global GAME
        GAME = self  
        self.nrows = rows
        self.ncols = cols
        self.grid = []
        self.start_gui()

    def start_gui (self):
        "Do basic window setup."
        self.root = tk.Tk()
        self.root.geometry("480x320+0+0") # Size of our Raspberry Pi screen
        self.canvas = tk.Canvas(self.root, width = 480, height = 320, bg = 'LightBlue')
        self.canvas.pack()
        self.new_game()

    def new_game(self):
        "Start or restart with new tiles."
        if len(self.grid) > 0: # If tiles from old game, get rid of them.
            for i in range(len(self.grid)):
                for j in range(len(self.grid[i])):
                    self.grid[i][j].forget()
        self.grid = []

        self.moves = START_MOVES
        self.movesText = tk.StringVar()
        self.movesText.set("Moves\n{0}".format(self.moves))

        self.score = 0
        self.scoreText = tk.StringVar()
        self.scoreText.set("Score\n{0}".format(self.score))

        for i in range(self.nrows): # Walk through the rows
            row = []
            for j in range(self.ncols): # Walk through the columns
                row.append(self.new_random_tile(i,j))
            self.grid.append(row)
        # Where there are three in a row of some tile, break it up by placing another kind of tile.
        while len(self.three_in_a_row()) > 0:
            for end_tile in self.three_in_a_row():
                i = end_tile.row
                j = end_tile.col-2 # change the tile two tiles to the left
                self.grid[i][j] =  self.new_random_tile(i,j,not_class=end_tile.class_name())
        self.redraw()
            
    def redraw(self):
        'Redraw the whole board'
        for i in range(self.nrows):
            for j in range(self.ncols):
                self.grid[i][j].draw()

        self.moves_widget = tk.Label(self.canvas, textvariable=self.movesText, bg="LightBlue", font=("",20))
        self.moves_widget.place(x=390, y=10)

        self.score_widget = tk.Label(self.canvas, textvariable=self.scoreText, bg="LightBlue", font=("",20))
        self.score_widget.place(x=390, y=110)

        self.new_game_button = tk.Button(self.canvas, text="New Game", command=self.new_game)
        self.new_game_button.place(x=390, y=250)
        self.root.mainloop()

    def new_random_tile(self, i, j, not_class='any'):
        'Return a new random tile at row I, column J.'
        while True:
            ipick = random.randint(1,5)
            if   ipick == 1 and not_class != 'Bird':
                return(Bird(i,j))
            elif ipick == 2 and not_class != 'Cloud':
                return(Cloud(i,j))
            elif ipick == 3 and not_class != 'Rain':
                return(Rain(i,j))
            elif ipick == 4 and not_class != 'Snow':
                return(Snow(i,j))
            elif ipick == 5 and not_class != 'Sun':
                return(Sun(i,j))

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
        '''Remove this item, add to score. If the tile to its right is the same type, call this again to remove it too.'''
        tile.forget()
        GAME.score = GAME.score + 100
        GAME.scoreText.set("Score\n{0}".format(GAME.score))
        if (tile.col > 0):
            on_left = GAME.grid[tile.row][tile.col-1]
            if type(tile) == type(on_left):
                self.deleteTiles(on_left)
                
    def dropTiles(self,start_tile):
        '''Drop tiles above the start_tile and every tile of its type to the left.
        all the way to the top row. Then fill in top row with new tiles.'''
        irow = start_tile.row
        icol = start_tile.col
        len = 3
        if icol-3 >= 0 and self.grid[irow][icol-3].state == -1:
            len = 4
        if icol-4 >= 0 and self.grid[irow][icol-4].state == -1:
            len = 5
        for i in range (irow-1,-1,-1):
            for j in range(icol,icol-len,-1):
                " \n Dropping into ({0},{1}), state = {2}".format(i+1, j, self.grid[i+1][j].state)
                self.grid[i][j].row = i+1
                self.grid[i+1][j] = self.grid[i][j]
                self.grid[i+1][j].drop()
        # Now fill the top row with new tiles
        for j in range (icol,icol-len,-1):
            self.grid[0][j] = GAME.new_random_tile(0,j)
            GAME.root.after(1500,self.grid[0][j].drop)


class EndOfGameDialog:
    def __init__(self, parent):
        top = self.top = tk.Toplevel(parent)
        tk.Label(top, text="Game Over", bg="LightGreen", font=("",20)).pack()
        b = tk.Button(top, text="New Game", command=self.ok)
        b.pack(pady=5)
        top.geometry("+%d+%d" % (parent.winfo_rootx()+50, parent.winfo_rooty()+50))
    def ok(self):
        global GAME
        self.top.destroy()
        GAME.new_game()

#Start the game!
Game()
