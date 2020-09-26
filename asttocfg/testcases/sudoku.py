import pygame
import pygame.freetype
from pprint import pprint

class Grid:
    WIDTH = 270
    HEIGHT = 270
    CELL = WIDTH // 9

    def __init__(self):
        pygame.init()
        pygame.display.set_caption('sudoku')
        self.surface = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.writer = pygame.freetype.SysFont("Arial", 24)
    
    def color_cell(self, row, col, num, color = (0,200,0,0.25)):
        if num == 0:
            pygame.draw.rect(self.surface, (0,200,0, 0.25), (col*self.CELL+1, row*self.CELL+1, self.CELL-1, self.CELL-1))
            return
        pygame.draw.rect(self.surface, color, (col*self.CELL+1, row*self.CELL+1, self.CELL-1, self.CELL-1))
        self.writer.render_to(self.surface, (col*self.CELL + self.CELL/2, row*self.CELL + self.CELL//3), str(num), (0, 0, 0))
        pygame.display.update()
        pygame.time.delay(10)

    def draw_grid(self):
        cols = self.WIDTH // self.CELL
        rows = self.HEIGHT // self.CELL
        x, y = 0, 0

        self.surface.fill((255,255,255))
        
        for i in range(cols+1):
            pygame.draw.line(self.surface, (125,125,125), (x, 0), (x, self.HEIGHT ))
            x += self.CELL
        
        for i in range(rows+1):
            pygame.draw.line(self.surface, (125,125,125), (0, y), (self.WIDTH, y))
            y += self.CELL

class Sudoku:
    def __init__(self, mat, g):
        self.mat = mat
        self.g = g
        self.num_set = {1,2,3,4,5,6,7,8,9}
        self.init_grid()
        
    def init_grid(self):
        if self.g == None:
            return

        for i in range(0,9):
            for j in range(0,9):
                self.g.color_cell(i,j, self.mat[i][j],(255,255,255))

    def find_all_row(self, i):
        el_set = set()
        for j in range(0,9):
            el_set.add(self.mat[i][j])
        
        return self.num_set - el_set

    def find_all_col(self, j):
        el_set = set()
        for i in range(0,9):
            el_set.add(self.mat[i][j])
        
        return self.num_set - el_set

    def find_all_box(self, i,j):
        boxX, boxY = (i - i%3), (j - j%3)

        el_set = set()
        for i in range(0,3):
            for j in range(0,3):
                el_set.add(self.mat[boxX + i][boxY + j])
        
        return self.num_set - el_set

    def find_all_values(self, i,j):
        row_set = self.find_all_row(i)
        col_set = self.find_all_col(j)
        box_set = self.find_all_box(i,j)

        return row_set.intersection(col_set.intersection(box_set))

    def solve(self, out = True):
        empty_indices = []
        pos_stack = []
        # find all empty indices
        for i in range(0,9):
            for j in range(0,9):
                if self.mat[i][j] == 0:
                    empty_indices.append((i,j))
        # print(empty_indices)

        tstack_cache = {}
        while len(empty_indices) > 0:
            i,j = empty_indices.pop()
            tstack = self.find_all_values(i,j)
            tstack_cache[(i,j)] = tstack
            # print(tstack_cache)
            # bactrack if stuck
            if len(tstack) == 0:
                empty_indices.append((i,j))
                self.mat[i][j] = 0
                if out:
                    self.g.color_cell(i,j,0)
                while(len(tstack) == 0):
                    i,j = pos_stack.pop()
                    tstack = tstack_cache[(i,j)]
                    if len(tstack) == 0:
                        self.mat[i][j] = 0
                        if out:
                            self.g.color_cell(i,j,0)
                        empty_indices.append((i,j))
                    else:
                        pos_stack.append((i,j))

                # print(f"backtrack done: {tstack}")
            else:
                pos_stack.append((i,j))

            val = tstack.pop()
            self.mat[i][j] = val
            if out:
                    self.g.color_cell(i,j,val)
        
    def verify(self):
        for i in range(0,9):
            print(f"{self.mat[i][:]} : {sum(self.mat[i][:])}")

puzzle = [  
            [3, 0, 6, 5, 0, 8, 4, 0, 0],  
            [5, 2, 0, 0, 0, 0, 0, 0, 0],  
            [0, 8, 7, 0, 0, 0, 0, 3, 1],  
            [0, 0, 3, 0, 1, 0, 0, 8, 0],  
            [9, 0, 0, 8, 6, 3, 0, 0, 5],  
            [0, 5, 0, 0, 9, 0, 6, 0, 0],  
            [1, 3, 0, 0, 0, 0, 2, 5, 0],  
            [0, 0, 0, 0, 0, 0, 0, 7, 4],  
            [0, 0, 5, 2, 0, 6, 3, 0, 0]
        ]

def generator():
    """
        generate a sudoku puzzle, by solving an empty puzzle

        TODO: difficulty adjustment, randomization
    """
    empty_puzzle = [[0]*9 for i in range(9)]
    s = Sudoku(empty_puzzle, None)
    s.solve(out=False)
    pprint(s.mat)

def solver():
    """
    pygame visualization of sudoku solving.
    """
    g = Grid()
    done = False
    clock = pygame.time.Clock()
    g.draw_grid()
    s = Sudoku(puzzle, g)
    
    while not done:
        pygame.time.delay(50)
        clock.tick(10)
        s.solve()
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                done = True

solver()