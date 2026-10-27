import sys, glob, io, itertools, imagehash
from PIL import Image
d=sys.argv[1]; files=sorted(glob.glob(d+"/*.png"))
H={f.split("/")[-1][:-4]: imagehash.phash(Image.open(f)) for f in files}
pairs=sorted((H[a]-H[b],a,b) for a,b in itertools.combinations(H,2))
print("memes:",len(H),"closest distinct pairs:",pairs[:3])
im=Image.open(files[0]).convert("RGB"); w,h=im.size
im=im.crop((20,20,w-20,h-20)).resize((540,675)); b=io.BytesIO(); im.save(b,"JPEG",quality=60)
print("re-saved, cropped, shrunk copy of",files[0].split("/")[-1],"distance:",imagehash.phash(Image.open(b))-H[files[0].split("/")[-1][:-4]])
