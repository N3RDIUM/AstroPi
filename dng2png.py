import imageio
import rawpy
with rawpy.imread("./0.dng") as raw:
    rgb = raw.postprocess()
imageio.imsave(f"./0.png", rgb)