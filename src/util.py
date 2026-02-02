from PIL import Image
import os

#Saving the GIF
def main():
    os.chdir("../results")
    for d in [d for d in os.listdir() if os.path.isdir(d)]:
        print(d)
        images = []
        dir_files = os.listdir(f"./{d}")
        #Natural sort
        dir_files.sort(key=lambda x: int(x[:-4]))
        for f in dir_files:
            images.append(Image.open(f"./{d}/{f}"))
        images[0].save(f"{d}.gif", append_images=images[1::2], optimize=False)
    
    
    

if __name__ == "__main__":
    main()