#!/usr/bin/python3
#from time import sleep
from calendar import timegm
from time import gmtime
from pprint import pprint
import sys
RECLIMIT = 500 #sys.getrecursionlimit() - 1
MAXTIME = 10 #how much time to spend searching for an answer

def timenow():
    return timegm(gmtime()) #current time since epoch, in seconds

class Camelot:
    def __init__(self, color, debug=False):
        self.hu_color = color
        self.co_color = 'B' if color == 'W' else 'W'
        self.p_set = {'B': list(), 'W': list()} #lists to hold piece coordinates for each color
        self.board = list()
        for j in [3,4]: #adding pieces to their lists
            for i in [4,5]:
                self.p_set['W'].append((i,j))
                self.p_set['B'].append((i+4,j)) 
        for j in [2,5]: #adding pieces to their lists
            self.p_set['W'].append((4,j))
            self.p_set['B'].append((9,j))
        self._repaint_board() #paints the background and pieces into the board
        if debug: #testing only: add corner case scenarios here
            self.hu_color = 'W'
            self.board[4][2], self.board[7][2] = self.board[7][2], self.board[4][2]
            self.p_set['W'].remove((4,2))
            self.p_set['W'].append((7,2))
            self.board[4][3], self.board[12][4] = self.board[12][4], self.board[4][3]
            self.p_set['W'].remove((4,3))
            self.p_set['W'].append((12,4))

    def printboard(self, board=None):
        if board is None:
            board = self.board
        def horizrule(): #to print numbers for coordinates
            print('  ', end=' ') #formatting
            for i in range(8):
                print(' %i' % i, end=' ')
            print()
        horizrule()
        for rownum, row in enumerate(board):
            if rownum < 10: #for neatness
                print(' %i' % rownum, end=' ')
            else:
                print('%i' % rownum, end=' ') #note the lack of leading space
            for elem in row:
                print(elem, end=' ') #print board elements
            print(rownum)
        horizrule()
        
    def _isonboard(self, px, py): #check if a location is on the board or not. Static, doesn't depend on game state.
        if px >= 0 and px <= 13 and py >= 0 and py <= 7:
            return self.board[px][py] != '  ' #if within the board coordinates, return whether the space is on the board or not (corner)
        else:
            return False
        
    def _get_moves(self, px, py, pcolor, board=None):
        if board is None:
            board = self.board
        simplemoves = [(i,j) \
                 for i in range(px-1, px+2) \
                 for j in range(py-1, py+2) \
                 if (i != px or j != py) and \
                    self._isonboard(i,j) and \
                    (board[i][j] == '__' or board[i][j][1] == 'C') #target destination should be empty or a castle
                ] #list comprehension magic!
        
        cantermoves = list()
        for i,j in [(-2,2), (0,2), (2,2), (2,0), (2,-2), (0,-2), (-2,-2), (-2,0)]: #two hops
            if self._isonboard(px+i, py+j):
                if (board[px+i][py+j] == '__' or board[px+i][py+j][1] == 'C') \
                and board[px+int(i/2)][py+int(j/2)] == pcolor + 'P': #if canter target is blank or a castle and in between lies own piece
                    cantermoves.append((px+i, py+j))
        return simplemoves + cantermoves
    
    def detect_win(self, board=None): #are the castles filled with enemies? if yes, who won?
        if board is None:
            board = self.board
        return 'B' if board[0][3] == 'BP' and board[0][4] == 'BP' else \
            'W' if board[13][3] == 'WP' and board[13][4] == 'WP' else \
                None

    def _repaint_board(self):
        self.board = [['__']*8 for _ in range(14)] #blank tiles
        for i in range(3):
            for j in range(3-i): #top-left: not part of the board
                self.board[i][j] = '  '
            for j in range(i+5, 8): #top-right: not part of the board
                self.board[i][j] = '  '
            for j in range(i+1): #bottom-left: not part of the board
                self.board[i+11][j] = '  '
            for j in range(2-i, 3): #bottom-right: not part of the board
                self.board[i+11][j+5] = '  '
        for j in [3,4]: #castles
            self.board[0][j] = 'WC'
            self.board[13][j] = 'BC'
        for c in ['B', 'W']:
            for x, y in self.p_set[c]: #pieces
                self.board[x][y] = c + 'P'

    def _get_utility(self, pcolor, board, p_set): #utility function for use by AI
        DISTMUL = 2
        ENEMMUL = -5
        ocolor = 'B' if pcolor == 'W' else 'W'
        castley = 13 if ocolor == 'B' else 0
        if board[castley][3] == pcolor + 'P' and board[castley][4] == pcolor + 'P':
            castlescore = 1000 #if both castle positions are occupied by the player
        elif board[castley][3] == pcolor + 'P' or board[castley][4] == pcolor + 'P':
            castlescore = 500 #if one castle position is occupied by the player
        else:
            castlescore = 0
        #print('Castle score: %i' % castlescore)
        distancescore = sum([DISTMUL*(abs(px - castley)) for px, py in p_set[pcolor]]) #distance from castle for each player piece
        #print('Distance score: %i' % distancescore)
        enemyscore = ENEMMUL*len(p_set[ocolor]) #penalty for number of enemy pieces
        #print('Enemy piece score: %i' % enemyscore)
        return castlescore + distancescore + enemyscore
        #Utility = 500*(no of castles occupied by self) + (DISTMUL* sum of distances from enemy castle) \
                #+ (ENEMMUL* number of enemy pieces on board)

    def _detect_captures(self, pcolor, board=None, p_set=None): #detect capture possibilities
        if board is None or p_set is None:
            board = self.board
            p_set = self.p_set
        capmoves = list() #re-initialize so that old capture possibilities aren't reused
        target  = 'B' if pcolor == 'W' else 'W'
        for (px, py) in p_set[pcolor]:
            for i,j in [(-2,2), (0,2), (2,2), (2,0), (2,-2), (0,-2), (-2,-2), (-2,0)]: #possible post-capture destinations
                if self._isonboard(px+i, py+j):
                    if board[px+i][py+j] == '__' and board[px+int(i/2)][py+int(j/2)] == target + 'P': #if there's an empty spot to jump to and an enemy piece to jump over
                        capmoves.append((i,j, px, py))
        return capmoves

    def hu_makemove(self):
        capmoves = self._detect_captures(self.hu_color) #find if we can make any captures
        if len(capmoves) == 0: #no captures; play regular move
            for idx, elem in enumerate(self.p_set[self.hu_color]):
                print('*** %i: %s' % (idx, elem))
            choice1 = -1
            while choice1 not in range(6):
                choice1 = input('Select your piece from the above: ')
                if not choice1.isdigit():
                    print('Bad choice, try again. ', end='')
                else:
                    choice1 = int(choice1)
                    if choice1 not in range(6):
                        print('Bad choice, try again. ', end='')
            px, py = self.p_set[self.hu_color][choice1]
            moves = self._get_moves(px, py, self.hu_color)
            for idx, elem in enumerate(moves):
                print('*** %i: %s' % (idx, elem))
            choice2 = -1
            while choice2 not in range(len(moves)):
                choice2 = input('Select your move from the above: ')
                if not choice2.isdigit():
                    print('Bad choice, try again. ', end='')
                else:
                    choice2 = int(choice2)
                    if choice2 not in range(len(moves)):
                        print('Bad choice, try again. ', end='')
            fx, fy = moves[choice2]
            self.p_set[self.hu_color][choice1] = (fx, fy)
            self._repaint_board()
            #self.board[fx][fy] = self.board[px][py]
            #self.board[px][py] = '__'
        else: #captures are obligatory
            print('Playing capture move.')
            print('Select a capture move (options are listed as X-offset, Y-offset, X-start, Y-start)')
            for idx, piece in enumerate(capmoves):
                print('*** %i: ' % idx, end='')
                print(piece)
            choice = -1
            while choice not in range(len(capmoves)):
                choice = input('Select the move: ')
                if not choice.isdigit():
                    print('Bad selection, try again.')
                else:
                    choice = int(choice)
                    if choice not in range(len(capmoves)):
                        print('Bad selection, try again.')
            i, j, px, py = capmoves[choice]
            #capmoves.remove((i, j, px, py))
            fx, fy = px+i, py+j #post-capture destination
            ex, ey = px+int(i/2), py+int(j/2) #enemy location
            idx = self.p_set[self.hu_color].index((px, py)) #which piece are we moving?
            self.p_set[self.hu_color][idx] = (fx, fy) #move the piece
            self.p_set[self.co_color].remove((ex, ey)) #remove the enemy piece
            self._repaint_board() #repaint the board

    def _enum_moves(self, board, p_set, pcolor, origactions): #returns a dictionary of actions ready for alphabeta's use
        origmoves = [] if origactions is None else origactions.keys()
        moves = self._detect_captures(pcolor, board, p_set)
        if len(moves) == 0: #if no captures, look at regular moves
            moves = list()
            for px, py in p_set[pcolor]:
                fullmoves = self._get_moves(px, py, pcolor)
                moves += [(fx-px, fy-py, px, py) for fx, fy in fullmoves] #converting from destination,piece to offset,piece
        actions = {x:0 for x in moves if x not in origmoves} #converting to dictionary
        return actions
    
    def _alphabeta(self, pcolor, board, p_set, stupid=False, debug=False):
        actions = self._enum_moves(board, p_set, self.co_color, None)
        if len(actions) == 1: #if only 1 possible action, why even go into min/max calculations
            return actions.keys()[0]
        if stupid: #stupid algorithm: pick a random move (just for testing move sanity)
            from random import choice
            return choice(list(actions.keys()))
        maxv, finalactions = self._minmaxval(pcolor, board, p_set, actions, \
                                             float('-inf'), float('inf'), timenow(), depth=0, ismax=True, \
                                             debug=debug) #here's the alpha-beta algorithm
        if debug:
            print('Max value: %i, actions: ' % maxv, end='')
            print(finalactions)
        for action, v in finalactions.items(): #find which action to return
            if v == maxv:
                return action

    def _minmaxval(self, pcolor, board, p_set, actions, alpha, beta, starttime, depth, ismax, debug):
        if (self.detect_win(board) is not None) or (timenow() - starttime >= MAXTIME) or (depth == RECLIMIT):
            #if a win is detected, time exceeded, or depth limit reached, return the final utility and the dict of actions with scores
            return self._get_utility(pcolor, board, p_set), actions
        v = float('-inf') if ismax else float('inf') #set v to -inf or inf depending on whether the iteration is max or min
        ocolor = 'B' if pcolor == 'W' else 'W'
        for i, move in enumerate(actions.keys()):
            if debug:
                print('Move to play: %i/' % i, end='')
                print(ismax, end=' ')
                print(move)
            board2 = board.copy() #make copy of board and piece lists for each move possibility
            p_set2 = p_set.copy()
            ix, iy, px, py = move
            ###########begin: play the move
            if abs(ix) == 2 or abs(iy) == 2: #jumping over a piece
                ex, ey = px+int(ix/2), py+int(iy/2)
                if (ex, ey) in p_set[ocolor]: #board2[ex][ey] == ocolor + 'P': #capture
                    board2[ex][ey] = '__'
                    if debug:
                        print('Enemy piece: %i, %i' % (ex, ey), file=sys.stderr)
                        print('Set of enemy pieces: ', end='', file=sys.stderr)
                        print(p_set[ocolor], file=sys.stderr)
                    p_set2[ocolor].remove((ex,ey))
            board2[px+ix][py+iy], board2[px][py] = board2[px][py], board2[px+ix][py+iy]
            ###########end: play the move
            newactions = self._enum_moves(board2, p_set2, ocolor, actions) #get new action possibilities
            if ismax:
                v2, _ = self._minmaxval(ocolor, board2, p_set2, newactions, alpha, beta, starttime, depth+1, ismax=False, debug=debug) #call min
                v = max(v, v2)
                actions[move] += v
                if v >= beta:
                    return v, actions
                alpha = max(alpha, v)
            else:
                v2, _ = self._minmaxval(ocolor, board2, p_set2, newactions, alpha, beta, starttime, depth+1, ismax=True, debug=debug) #or call max
                v = min(v, v2)
                actions[move] += v
                if v >= alpha:
                    return v, actions
                beta = min(beta, v)
        return v, actions

    def co_makemove(self): #computer move playing function
        print('Thinking...')
        move = self._alphabeta(self.co_color, self.board.copy(), self.p_set.copy(), stupid=False, debug=False)
        self._repaint_board() #prepare to play move
        print('Computer move: ', end='')
        print(move)
        ix, iy, px, py = move
        if move is None:
            print('Error: computer generated empty move.', file=sys.stderr)
            exit(1)
        if abs(ix) == 2 or abs(iy) == 2: #is it a capture/canter?
            ex, ey = px+int(ix/2), py+int(iy/2)
            if self.board[ex][ey] == self.hu_color + 'P': #jumping to capture?
                self.board[ex][ey] = '__' #clear the enemy piece from the board
                self.p_set[self.hu_color].remove((ex,ey)) #delete the enemy piece from enemy's piece list
        self.board[px+ix][py+iy], self.board[px][py] = self.board[px][py], self.board[px+ix][py+iy] #move the computer piece from origin to destination
        idx = self.p_set[self.co_color].index((px, py)) #which piece was it?
        self.p_set[self.co_color][idx] = (px+ix, py+iy) #update the computer piece list with new location
        

if __name__ == '__main__':
    while True:
        color = input('Select your color (W/B): ')
        if color not in {'W', 'B'}:
            print('Bad input, try again.')
        else:
            break
    game = Camelot(color, debug=False)
    game.printboard()
    if color == 'W': #white goes first
        game.hu_makemove()
        game.printboard()
    while game.detect_win() is None:
        if game.detect_win() is None:
            game.co_makemove()
            game.printboard()
        if game.detect_win() is None:
            game.hu_makemove()
            game.printboard()
    if game.detect_win() == game.hu_color:
        print('You won!')
    else:
        print('Wow, you lost!')