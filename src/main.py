import pygame as pg
import numpy as np
import numba
import random

screen_width, screen_height = 800, 800
screen = pg.display.set_mode((screen_width, screen_height))
pg.display.set_caption("Some cells")
BG_COLOR = (0, 0, 0)
SEED = 42
SIZE = 200
random.seed(SEED)

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
        self.soil_range: tuple[int, int] = (100, 160)
        self.generate_population(5)
  
    @staticmethod
    @numba.njit()
    def cell_calc(cell_map, cell_map_buffer):
        PL = 0
        SO = 1
        LT = 2
        LIFETIME = 3
        SOIL_COST = 20
        NE_SOIL_SCALE = 1/4
        PLANT_LIMIT = 255
        SOIL_SCALE = 0.25
        MIN_PLANT_MATURITY = 128
        MIN_SOIL = 16
        
        for i in range(SIZE):
            for j in range(SIZE):
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
                        if cell[PL] <= PLANT_LIMIT and cell[SO] > 0:
                            f = SOIL_SCALE
                            soil_calc = SOIL_COST * (f + (1-f) * cell[PL]/PLANT_LIMIT)
                            cell_map_buffer[i][j][PL] += soil_calc
                            cell_map_buffer[i][j][SO] -= soil_calc
                    else:
                        cell_map_buffer[i][j][SO] += cell[PL]
                        cell_map_buffer[i][j][PL] = 0
                
                for ne in neighboors:
                    l, c = ne[0], ne[1]
                    if l < 0 or l > SIZE-1 or c < 0 or c > SIZE-1:
                        break
                    ne_cell = cell_map[l][c]
                    #Root spread rule
                    if ne_cell[PL] > 0 and ne_cell[PL] <= PLANT_LIMIT and ne_cell[LT] != 0 and cell[SO] > 0:
                        f = SOIL_SCALE
                        soil_calc = SOIL_COST*NE_SOIL_SCALE * (f + (1-f) * ne_cell[PL]/PLANT_LIMIT)
                        cell_map_buffer[l][c][PL] += soil_calc
                        cell_map_buffer[i][j][SO] -= soil_calc
                    #Valid fertilization rule
                    if not fertilized and cell[SO] >= MIN_SOIL and cell[PL] == 0 and ne_cell[PL] >= MIN_PLANT_MATURITY:
                        fertilized = True
                
                #Creation
                if fertilized:
                    cell_map_buffer[i][j][PL] += 1
                    cell_map_buffer[i][j][SO] -= 1
                    cell_map_buffer[i][j][LT] += LIFETIME + max(LIFETIME * (int(cell[SO]*0.02)), 0) 

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
                    soil_factor = max(min(1, c_val[1]/255), 0)
                    cell_color = tuple([int(cl + soil_factor*(ch-cl)) for cl, ch in zip(soil_color_low, soil_color_high)])
                elif c_val[0] > 0:
                    plant_factor = min(1, c_val[0]/255)
                    cell_color = tuple([int(cl + plant_factor*(ch-cl)) for cl, ch in zip(plant_color_low, plant_color_high)])
                elif c_val[0] < 0:
                    cell_color = (255, 0, 0)
                try:
                    pg.draw.rect(screen, cell_color, rect_dim, width=int(camera_zoom))
                except Exception as e:
                    print(c_val)
                    print(cell_color)
                    input()

    def generate_population(self, quantity=5):
        for i in range(self.size):
            for j in range(self.size):
                self.cell_map[i][j][1] = random.randint(*self.soil_range)
                self.cell_map[i][j][2] = 0
        for n in range(quantity):
            i, j = random.randint(0, self.size-1), random.randint(0, self.size-1)
            print(f"{i}, {j}")
            self.cell_map[i][j][0] = 128
            self.cell_map[i][j][2] = 10
            
    def tick(self):
        self.cell_map_buffer = np.copy(self.cell_map)
        self.cell_calc(self.cell_map, self.cell_map_buffer)
        self.cell_map = self.cell_map_buffer



def main():
    automata = Automata(SIZE)
    
    running = True
    clock = pg.time.Clock()
    counter = 0
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        
        
        automata.tick()

        
        if 0 or counter % 50 == 0:
            screen.fill(BG_COLOR)
            automata.cell_draw_transform(automata.cell_map, CAMERA.x, CAMERA.y, CAMERA.zoom) 
        
        pg.display.flip()
        
        print(counter)
        counter += 1
        clock.tick(500)



if __name__ == "__main__": 
    main()