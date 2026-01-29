import pygame as pg
import numpy as np
import numba
import random

screen_width, screen_height = 900, 900
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
        self.generate_population(20)
  
    @staticmethod
    @numba.njit()
    def cell_calc(cell_map, cell_map_buffer):
        PL = 0
        SO = 1
        LT = 2
        LIFETIME = 3
        SOIL_COST = 20
        NE_SOIL_SCALE = 1/2
        PLANT_LIMIT = 255
        SOIL_SCALE = 0.25
        MIN_PLANT_MATURITY = 64
        MIN_SOIL = 4
        for i in range(SIZE):
            for j in range(SIZE):
                cell = cell_map[i][j]
                neighboors  = [
                    (i-1, j-1), (i-1, j), (i-1, j+1),
                    (i, j-1), (i, j+1),
                    (i+1, j-1), (i+1, j), (i+1, j+1)
                ]
                if cell[PL] > 0 and cell[PL] <= PLANT_LIMIT and cell[LT] != 0 and cell[SO] > 0:
                    f = SOIL_SCALE
                    soil_calc = SOIL_COST * (f + (1-f) * cell[PL]/PLANT_LIMIT)
                    #soil_calc = SOIL_COST
                    cell_map_buffer[i][j][PL] += soil_calc
                    cell_map_buffer[i][j][SO] -= soil_calc
                
                if cell[SO] < 0 and 0:
                    cell_map_buffer[i][j][LT] = 0
                    
                if cell[LT] > 0:
                    cell_map_buffer[i][j][LT] -= 1
                
                if cell[LT] == 0:
                    cell_map_buffer[i][j][SO] += cell[PL]
                    cell_map_buffer[i][j][PL] = 0
                
                for ne in neighboors:
                    l, c = ne[0], ne[1]
                    if l < 0 or l > SIZE-1 or c < 0 or c > SIZE-1:
                        break
                    ne_cell = cell_map[l][c]
                    if ne_cell[SO] >= MIN_SOIL and ne_cell[PL] == 0 and cell[PL] >= MIN_PLANT_MATURITY:
                        cell_map_buffer[l][c][PL] += 1
                        cell_map_buffer[l][c][SO] -= 1
                        cell_map_buffer[l][c][LT] += LIFETIME * max(LIFETIME * (ne_cell[SO]//50), 0)
                    if cell[PL] > 0 and cell[PL] <= PLANT_LIMIT and ne_cell[SO] > 0 and ne_cell[LT] != 0:
                        #soil_calc = ne_cell[SO]/16
                        f = SOIL_SCALE
                        soil_calc = SOIL_COST*NE_SOIL_SCALE * (f + (1-f) * cell[PL]/PLANT_LIMIT)
                        cell_map_buffer[i][j][PL] += soil_calc
                        cell_map_buffer[l][c][SO] -= soil_calc
                
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
                self.cell_map[i][j][1] = random.randint(100, 168)
                self.cell_map[i][j][2] = 10
        for n in range(quantity):
            i, j = random.randint(0, self.size-1), random.randint(0, self.size-1)
            print(f"{i}, {j}")
            self.cell_map[i][j][0] = 128
            
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

        screen.fill(BG_COLOR)
        
        if counter > 2000:
            automata.cell_draw_transform(automata.cell_map, CAMERA.x, CAMERA.y, CAMERA.zoom) 
        
        pg.display.flip()
        
        print(counter)
        counter += 1
        clock.tick(500)



if __name__ == "__main__": 
    main()