from PIL import Image, ImageDraw, ImageFont
import math, os

OUT = "pwa_assets"
FONT = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"

# app gradient stops: #6a5cff -> #ff5d8f -> #ff9d3d
C1=(106,92,255); C2=(255,93,143); C3=(255,157,61)

def lerp(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))

def grad(size):
    img=Image.new("RGB",(size,size))
    px=img.load()
    for y in range(size):
        for x in range(size):
            # diagonal 0..1
            t=(x+y)/(2*(size-1))
            if t<0.5:
                c=lerp(C1,C2,t/0.5)
            else:
                c=lerp(C2,C3,(t-0.5)/0.5)
            px[x,y]=c
    return img

def draw_text(img, scale=1.0):
    size=img.width
    d=ImageDraw.Draw(img)
    # main "70.3"
    fs=int(size*0.40*scale)
    f=ImageFont.truetype(FONT,fs)
    txt="70.3"
    bb=d.textbbox((0,0),txt,font=f)
    w=bb[2]-bb[0]; h=bb[3]-bb[1]
    x=(size-w)/2-bb[0]
    y=(size-h)/2-bb[1]+int(size*0.04)
    # subtle shadow
    d.text((x+size*0.012,y+size*0.012),txt,font=f,fill=(40,30,80,90))
    d.text((x,y),txt,font=f,fill=(255,255,255))
    # small label above
    fs2=int(size*0.105*scale)
    f2=ImageFont.truetype(FONT,fs2)
    lab="IRONMAN"
    bb2=d.textbbox((0,0),lab,font=f2)
    w2=bb2[2]-bb2[0]
    x2=(size-w2)/2-bb2[0]
    y2=y-int(size*0.16)
    d.text((x2,y2),lab,font=f2,fill=(255,255,255))
    return img

def save_square(size, name, scale=1.0):
    img=grad(size)
    draw_text(img, scale)
    img.save(os.path.join(OUT,name))
    print("wrote",name,size)

# standard icons (full-bleed; platforms mask/round)
save_square(192,"icon-192.png",1.0)
save_square(512,"icon-512.png",1.0)
save_square(180,"apple-touch-icon.png",1.0)
save_square(32,"favicon-32.png",1.0)

# maskable: keep content inside safe ~80% zone -> scale text down
img=grad(512); draw_text(img,0.8); img.save(os.path.join(OUT,"icon-512-maskable.png")); print("wrote maskable")
