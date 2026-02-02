from PIL import Image
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as clr

#Saving the GIF
def gif():
    for d in [d for d in os.listdir() if os.path.isdir(d)]:
        print(d)
        images = []
        dir_files = os.listdir(f"./{d}")
        #Natural sort
        dir_files.sort(key=lambda x: int(x[:-4]))
        for f in dir_files:
            images.append(Image.open(f"./{d}/{f}"))
        images[0].save(f"{d}.gif", append_images=images[1::2], optimize=False)
  


   
#soil_color_low = (241, 218, 198)
#soil_color_high = (94, 56, 23)
#plant_color_low = (172, 220, 186)
#plant_color_high = (35, 83, 49)
def graph_save(d, f):
    veg_map = clr.LinearSegmentedColormap("grad", 
                                          {"red": [(0, 172/255, 172/255), (1, 35/255, 35/255)], 
                                           "green": [(0, 220/255, 220/255), (1, 83/255, 83/255)], 
                                           "blue": [(0, 186/255, 186/255), (1, 49/255, 49/255)]})
    soil_map = clr.LinearSegmentedColormap("grad", 
                                          {"red": [(0, 241/255, 241/255), (1, 94/255, 94/255)], 
                                           "green": [(0, 218/255, 218/255), (1, 56/255, 56/255)], 
                                           "blue": [(0, 198/255, 198/255), (1, 23/255, 23/255)]})
    image = plt.imread(f"{d}/{f}")
    plt.figure(figsize=(8, 8))

    plt.axis("off")
    plt.title(d)
    plt.imshow(image, vmin=0, vmax=1, cmap=veg_map)
    plt.colorbar(label="Plant", orientation="horizontal", shrink=0.6, pad=0)
    plt.imshow(image, vmin=0, vmax=1, cmap=soil_map) 
    plt.colorbar(label="Soil", orientation="horizontal", shrink=0.6, pad=0.05)
    plt.tight_layout(pad=0)
    plt.savefig(f"{d}.png")


def graph():
    for d in [d for d in os.listdir() if os.path.isdir(d)]:
        print(d)
        graph_save(d, "10000.png")

def main():
    os.chdir("../results")
    i = input("1: gif | 2: graph\n")
    if i == "1":
        gif()
    elif i == "2":
        graph()
    else:
        "invalid option"
    

if __name__ == "__main__":
    main()