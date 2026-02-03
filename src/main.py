import pygame as pg
import os
import numpy as np
import numba
import random

screen_width, screen_height = 800, 800
screen = pg.display.set_mode((screen_width, screen_height))
pg.display.set_caption("Some cells")
BG_COLOR = (0, 0, 0)
SEED = 42
SAVE = False

SIZE = 200
PL = 0
SO = 1
LT = 2
LIFETIME_MEAN = 20
LIFETIME_SIGMA = 2
SOIL_COST = 0.2
NE_SOIL_SCALE = 1/4
PLANT_LIMIT = 1
SOIL_SCALE = 0.25
MIN_PLANT_MATURITY = 0.25
MIN_SOIL = 0.0625
RAIN_INTERVAL = 400
RAIN_AMOUNT_PER_TICK = 0.0002
PLANT_DECAY = 0.0002
SOIL_DECAY = 0.0012


class Camera:
    def __init__(self, x: int = 0, y: int = 0, zoom: float = 1.0):
        self.x: int = x
        self.y: int = y
        self.zoom: float = zoom

CAMERA = Camera(zoom=4)


class Automata:
    def __init__(self, size):
        self.size = size
        self.cell_map = np.zeros(shape=(size, size, 3))
        self.cell_map_buffer = np.empty_like(self.cell_map)
        self.soil_range: tuple[float, float] = (0.4, 0.6)
        self.generate_population(5)
        self.counter = 0
  
    @staticmethod
    @numba.njit()
    def cell_calc(cell_map, cell_map_buffer, counter, soil_decay): 
        
        for i in range(SIZE):
            for j in range(SIZE):
                if counter % RAIN_INTERVAL == 0:
                    cell_map_buffer[i][j][SO] += RAIN_AMOUNT_PER_TICK * RAIN_INTERVAL
                cell = cell_map[i][j]
                fertilized = False
                neighboors  = [
                    (i-1, j-1), (i-1, j), (i-1, j+1),
                    (i, j-1), (i, j+1),
                    (i+1, j-1), (i+1, j), (i+1, j+1)
                ]
                #Alive
                if cell[PL] > 0:
                    if cell[LT] > 0:
                        cell_map_buffer[i][j][PL] = max(0, cell_map_buffer[i][j][PL] - PLANT_DECAY)
                        if cell[PL] <= PLANT_LIMIT and cell[SO] > 0:
                            #f = SOIL_SCALE
                            #soil_calc = SOIL_COST * (f + (1-f) * cell[PL]/PLANT_LIMIT)
                            a = SOIL_SCALE
                            b = 1
                            t = cell[PL]/PLANT_LIMIT
                            lerp = (1 - t)*a + t*b
                            soil_calc = SOIL_COST * lerp
                            cell_map_buffer[i][j][PL] += soil_calc
                            cell_map_buffer[i][j][SO] -= soil_calc
                    else:
                        cell_map_buffer[i][j][SO] += cell_map_buffer[i][j][PL]
                        cell_map_buffer[i][j][PL] = 0
                elif cell[SO] > 0:
                    cell_map_buffer[i][j][SO] -= soil_decay
                
                for ne in neighboors:
                    l, c = ne[0], ne[1]
                    if l < 0 or l > SIZE-1 or c < 0 or c > SIZE-1:
                        break
                    ne_cell = cell_map[l][c]
                    #Root spread rule
                    if ne_cell[PL] > 0 and ne_cell[PL] <= PLANT_LIMIT and cell[SO] > 0:
                        #f = SOIL_SCALE
                        #soil_calc = SOIL_COST*NE_SOIL_SCALE * (f + (1-f) * ne_cell[PL]/PLANT_LIMIT)
                        a = SOIL_SCALE
                        b = 1
                        t = cell[PL]/PLANT_LIMIT
                        lerp = (1 - t)*a + t*b
                        soil_calc = SOIL_COST*NE_SOIL_SCALE*lerp

                        cell_map_buffer[l][c][PL] += soil_calc
                        cell_map_buffer[i][j][SO] -= soil_calc
                    #Valid fertilization rule
                    if not fertilized and cell[SO] >= MIN_SOIL and cell[PL] == 0 and ne_cell[PL] >= MIN_PLANT_MATURITY:
                        fertilized = True
                
                #Creation
                if fertilized:
                    cell_map_buffer[i][j][PL] += 0.004
                    cell_map_buffer[i][j][SO] -= 0.004
                    cell_map_buffer[i][j][LT] += random.gauss(LIFETIME_MEAN, LIFETIME_SIGMA)
                    #cell_map_buffer[i][j][LT] += LIFETIME + int(max(LIFETIME * cell[SO]*10, 0))


                #Lifetime tick
                if cell[LT] > 0:
                    cell_map_buffer[i][j][LT] -= 1
                
    @staticmethod
    def cell_draw_transform(cell_map, camera_x, camera_y, camera_zoom):
        soil_color_low = (241, 218, 198)
        soil_color_high = (94, 56, 23)
        plant_color_low = (172, 220, 186)
        plant_color_high = (35, 83, 49)
        
        for i in range(len(cell_map)):
            for j in range(len(cell_map)):
                cell = (j, i, cell_map[i][j])
                rect_dim = ((cell[0]-camera_x)*camera_zoom, (cell[1]-camera_y)*camera_zoom, camera_zoom, camera_zoom)
                c_val = cell[2]
                cell_color = (0, 0, 0)
                if c_val[0] == 0:
                    soil_factor = max(min(1, c_val[1]), 0)
                    cell_color = tuple([int(cl + soil_factor*(ch-cl)) for cl, ch in zip(soil_color_low, soil_color_high)])
                elif c_val[0] > 0:
                    plant_factor = min(1, c_val[0])
                    cell_color = tuple([int(cl + plant_factor*(ch-cl)) for cl, ch in zip(plant_color_low, plant_color_high)])
                elif c_val[0] < 0:
                    cell_color = (255, 0, 0)
                try:
                    pg.draw.rect(screen, cell_color, rect_dim, width=int(camera_zoom))
                except Exception as e:
                    print(c_val)
                    print(cell_color)
                    input()

    def generate_population(self, quantity=5, start_strength=0.5, start_lifetime=10):
        for i in range(self.size):
            for j in range(self.size):
                self.cell_map[i][j][1] = random.uniform(*self.soil_range)
        for n in range(quantity):
            i, j = random.randint(0, self.size-1), random.randint(0, self.size-1)
            print(f"{i}, {j}")
            self.cell_map[i][j][0] = start_strength
            self.cell_map[i][j][2] = start_lifetime
            
    def tick(self):
        self.counter += 1
        self.cell_map_buffer = np.copy(self.cell_map)
        self.cell_calc(self.cell_map, self.cell_map_buffer, self.counter, SOIL_DECAY)
        self.cell_map = self.cell_map_buffer



def main(max_steps = -1, save_iter=False):
    automata = Automata(SIZE)
    
    running = True
    clock = pg.time.Clock()
    counter = 0
    REALTIME = False
    RENDER_INTERVAL = 100
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_r:
                    REALTIME = not REALTIME
                if event.key == pg.K_a:
                    RENDER_INTERVAL -= 10
                if event.key == pg.K_d:
                    RENDER_INTERVAL += 10
        
        RENDER_INTERVAL = max(10, RENDER_INTERVAL)
        if REALTIME or counter % RENDER_INTERVAL == 0:
            screen.fill(BG_COLOR)
            automata.cell_draw_transform(automata.cell_map, CAMERA.x, CAMERA.y, CAMERA.zoom) 
            if save_iter:
                pg.image.save(screen, f"./results/{SOIL_DECAY}/{counter}.png")
                
        automata.tick()
        
        pg.display.flip()
        
        print(f"\rtick: {counter} | Render interval: {RENDER_INTERVAL}      ", end='')
        
        counter += 1
        if max_steps != -1 and counter > max_steps:
            running = False
        clock.tick(500)



if __name__ == "__main__": 
    if SAVE:
        #0.0006 #Full
        #0.0012 #Holes
        #0.0025 #Maze
        #0.004 #Spots
        soil_list = [0.0006, 0.0012, 0.0025, 0.004]
        os.chdir("../")
        #Result loop
        for s in soil_list:
            random.seed(SEED)
            if str(s) not in os.listdir("results"):
                os.mkdir(f"./results/{s}") 
            SOIL_DECAY = s
            main(max_steps=10000, save_iter=True)
    else:
        random.seed(SEED)
        main()