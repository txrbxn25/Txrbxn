import cv2, numpy as np, random, math
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
random.seed(76)
W,H=1080,1350
BANG='fonts/Bangers.ttf'
def F(s): return ImageFont.truetype(BANG,s)

def outline(img,px,color,blur=0):
    a=np.array(img.split()[3]); k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*px+1,2*px+1))
    d=cv2.dilate(a,k); o=Image.new('RGBA',img.size,color); o.putalpha(Image.fromarray(d))
    if blur: o=o.filter(ImageFilter.GaussianBlur(blur))
    o.alpha_composite(img); return o
def pad(img,p):
    n=Image.new('RGBA',(img.width+2*p,img.height+2*p),(0,0,0,0)); n.paste(img,(p,p)); return n
def shadow(base,img,xy,off=(14,18),alpha=170,blur=6):
    s=Image.new('RGBA',img.size,(0,0,0,0)); s.putalpha(img.split()[3].point(lambda v:v*alpha//255))
    base.alpha_composite(s.filter(ImageFilter.GaussianBlur(blur)),(xy[0]+off[0],xy[1]+off[1]))

# ---------- background ----------
bg=Image.new('RGBA',(W,H)); px=np.zeros((H,W,3),np.float32)
t=np.linspace(0,1,H)[:,None]
top=np.array([40,6,60]); mid=np.array([150,10,40]); bot=np.array([20,4,20])
grad=np.where(t<0.55, top+(mid-top)*(t/0.55), mid+(bot-mid)*((t-0.55)/0.45))
px[:]=grad[:,None,:].reshape(H,1,3)
bg=Image.fromarray(px.astype(np.uint8)).convert('RGBA')
# sunburst
rays=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(rays); cx,cy=540,560
for i in range(36):
    a0=i*2*math.pi/36; a1=a0+math.pi/36
    d.polygon([(cx,cy),(cx+2000*math.cos(a0),cy+2000*math.sin(a0)),(cx+2000*math.cos(a1),cy+2000*math.sin(a1))],fill=(255,190,60,38))
bg.alpha_composite(rays)
# halftone dots (stronger toward edges)
ht=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ht)
for y in range(0,H,16):
    for x in range((y//16)%2*8,W,16):
        r=min(1,math.hypot(x-cx,y-cy)/750)*5.5
        if r>0.6: d.ellipse([x-r,y-r,x+r,y+r],fill=(0,0,0,120))
bg.alpha_composite(ht)
# skyline
sk=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(sk); x=-20
while x<W:
    bw=random.randint(60,140); bh=random.randint(140,360); y0=1000-bh
    d.rectangle([x,y0,x+bw,1100],fill=(12,4,18,255),outline=(0,0,0,255),width=4)
    for wy in range(y0+16,990,26):
        for wx in range(x+12,x+bw-14,22):
            if random.random()<0.35: d.rectangle([wx,wy,wx+10,wy+14],fill=(255,200,70,255) if random.random()<0.8 else (255,60,120,255))
    if random.random()<0.3: d.rectangle([x+bw//2-3,y0-50,x+bw//2+3,y0],fill=(12,4,18,255))
    x+=bw+random.randint(-10,6)
bg.alpha_composite(sk)
# street
st=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(st)
d.rectangle([0,995,W,H],fill=(18,14,22,255)); d.line([(0,995),(W,995)],fill=(0,0,0,255),width=6)
for i in range(-6,14): d.line([(540,995),(540+i*180-540, H)],fill=(40,30,50,255),width=3)
bg.alpha_composite(st)
glow=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(glow).ellipse([20,1080,820,1230],fill=(190,40,255,200))
bg.alpha_composite(glow.filter(ImageFilter.GaussianBlur(40)))

# ---------- 76 graffiti ----------
m=Image.open('tag_mask.png').convert('L')
tw=600; m=m.resize((tw,int(m.height*tw/m.width)),Image.LANCZOS)
g=np.zeros((m.height,m.width,4),np.uint8); tt=np.linspace(0,1,m.height)[:,None]
c1=np.array([255,236,90]); c2=np.array([255,120,0])
g[:,:,:3]=(c1+(c2-c1)*tt)[:,None,:].reshape(m.height,1,3); g[:,:,3]=np.array(m)
tag=Image.fromarray(g,'RGBA')
# highlight streaks
hl=Image.new('RGBA',tag.size,(0,0,0,0)); hd=ImageDraw.Draw(hl)
for i in range(0,tag.width+tag.height,70): hd.line([(i,0),(i-tag.height,tag.height)],fill=(255,255,255,70),width=14)
hl.putalpha(ImageChops.multiply(hl.split()[3],m)); tag.alpha_composite(hl)
tag=pad(tag,40); tag=outline(tag,10,(0,0,0,255)); tag=outline(tag,8,(255,255,255,255)); tag=outline(tag,6,(0,0,0,255))
tag=tag.rotate(7,resample=Image.BICUBIC,expand=True)
pos=((W-tag.width)//2-30,10); shadow(bg,tag,pos,off=(16,20),alpha=200,blur=3); bg.alpha_composite(tag,pos)

# ---------- car (comic filter) ----------
car=Image.open('car_cut.png').convert('RGBA'); cw=880; car=car.resize((cw,int(car.height*cw/car.width)),Image.LANCZOS)
rgb=cv2.cvtColor(np.array(car)[:,:,:3],cv2.COLOR_RGB2BGR)
for _ in range(3): rgb=cv2.bilateralFilter(rgb,9,60,60)
Z=rgb.reshape(-1,3).astype(np.float32)
_,lab,cent=cv2.kmeans(Z,10,None,(cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER,20,1),3,cv2.KMEANS_PP_CENTERS)
q=cent.astype(np.uint8)[lab.flatten()].reshape(rgb.shape)
gray=cv2.medianBlur(cv2.cvtColor(rgb,cv2.COLOR_BGR2GRAY),5)
edges=cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,9,4)
q=cv2.bitwise_and(q,q,mask=edges)
# subtle purple rim tint
q=cv2.cvtColor(q,cv2.COLOR_BGR2RGB).astype(np.float32); q=np.clip(q*0.95+np.array([10,0,22]),0,255).astype(np.uint8)
alpha=np.array(car)[:,:,3]; car=Image.fromarray(np.dstack([q,alpha]),'RGBA')
car=outline(pad(car,12),5,(0,0,0,255))
cpos=(10,1160-car.height); bg.alpha_composite(car,cpos)
# headlight flare
fl=Image.new('RGBA',(W,H),(0,0,0,0)); fd=ImageDraw.Draw(fl)
for (x,y) in [(cpos[0]+12+int(0.37*cw),cpos[1]+12+int(0.49*(car.height-24)))]:
    fd.ellipse([x-70,y-16,x+70,y+16],fill=(200,240,255,150))
bg.alpha_composite(fl.filter(ImageFilter.GaussianBlur(18)))

# ---------- gangster Homer ----------
P=90
ho=pad(Image.open('homer_cut.png').convert('RGBA'),P); d=ImageDraw.Draw(ho)
def s(x,y): return (x+P,y+P)
# gold chain
pts=[]
for i in range(41):
    tt_=i/40; a=(240,330); b=(300,470); c=(372,330)
    x=(1-tt_)**2*a[0]+2*(1-tt_)*tt_*b[0]+tt_**2*c[0]; y=(1-tt_)**2*a[1]+2*(1-tt_)*tt_*b[1]+tt_**2*c[1]; pts.append(s(x,y))
for i,(x,y) in enumerate(pts):
    r=7; d.ellipse([x-r,y-r,x+r,y+r],fill=(255,200,40),outline=(90,50,0),width=2)
mx,my=s(300,430); R=38
d.ellipse([mx-R-4,my-R-4,mx+R+4,my+R+4],fill=(0,0,0)); d.ellipse([mx-R,my-R,mx+R,my+R],fill=(255,205,40),outline=(150,90,0),width=4)
d.text((mx,my+2),'76',font=F(44),fill=(20,10,0),anchor='mm')
d.ellipse([mx-R+8,my-R+6,mx-R+22,my-R+16],fill=(255,255,230))
# shades
L=[s(176,146),s(254,142),s(250,198),s(196,204)]; Rr=[s(258,138),s(340,136),s(332,196),s(266,200)]
for poly in (L,Rr): d.polygon(poly,fill=(10,10,14),outline=(0,0,0)); 
d.line([s(250,152),s(260,150)],fill=(0,0,0),width=8); d.line([s(338,148),s(392,168)],fill=(0,0,0),width=7)
for (x0,y0) in [(190,154),(272,148)]:
    d.line([s(x0,y0+26),s(x0+26,y0)],fill=(255,255,255,200),width=6); d.line([s(x0+18,y0+32),s(x0+40,y0+10)],fill=(140,140,255),width=3)
# snapback cap (brim to the left)
d.pieslice([s(186,-36)[0],s(186,-36)[1],s(392,196)[0],s(392,196)[1]],180,360,fill=(16,16,20),outline=(0,0,0),width=5)
d.polygon([s(196,74),s(96,92),s(102,112),s(220,104),s(392,82)],fill=(16,16,20),outline=(0,0,0))
d.line([s(98,94),s(210,78)],fill=(255,200,40),width=4)
d.text(s(292,30),'76',font=F(58),fill=(255,205,40),anchor='mm',stroke_width=3,stroke_fill=(0,0,0))
d.ellipse([s(284,-38)[0],s(284,-38)[1],s(300,-26)[0],s(300,-26)[1]],fill=(16,16,20))
ho=ho.crop(ho.getbbox())
hh=900; ho=ho.resize((int(ho.width*hh/ho.height),hh),Image.LANCZOS)
ho=outline(pad(ho,20),7,(0,0,0,255)); ho=outline(ho,6,(255,255,255,255))
hpos=(W-ho.width+30,H-ho.height-15)
shadow(bg,ho,hpos,off=(-22,10),alpha=180,blur=8); bg.alpha_composite(ho,hpos)

# ---------- speech bubble ----------
b=Image.new('RGBA',(W,H),(0,0,0,0)); bd=ImageDraw.Draw(b)
bx0,by0,bx1,by1=40,560,470,760
tail=[(400,700),(470,740),(640,690)]
bd.ellipse([bx0-6,by0-6,bx1+6,by1+6],fill=(0,0,0)); bd.polygon([(t[0]+(6 if i==1 else 0),t[1]+(4 if i==1 else 0)) for i,t in enumerate(tail)],fill=(0,0,0))
bd.ellipse([bx0,by0,bx1,by1],fill=(255,255,255)); bd.polygon([(400,706),(460,728),(626,690)],fill=(255,255,255))
bd.text(((bx0+bx1)//2,(by0+by1)//2-22),'MMMH...',font=F(56),fill=(0,0,0),anchor='mm')
bd.text(((bx0+bx1)//2,(by0+by1)//2+34),'RS6!',font=F(74),fill=(220,20,40),anchor='mm',stroke_width=2,stroke_fill=(0,0,0))
b=b.rotate(-4,resample=Image.BICUBIC,center=(255,660)); bg.alpha_composite(b)

# ---------- title ----------
tl=Image.new('RGBA',(W,H),(0,0,0,0)); td=ImageDraw.Draw(tl)
td.text((40,1250),'76 GANG',font=F(150),fill=(255,214,40),stroke_width=9,stroke_fill=(0,0,0),anchor='ls')
td.text((48,1312),'NO LOVE IN SPRINGFIELD',font=F(46),fill=(255,255,255),stroke_width=5,stroke_fill=(0,0,0),anchor='ls')
tl=tl.rotate(3,resample=Image.BICUBIC,center=(300,1250))
sh=Image.new('RGBA',(W,H),(0,0,0,0)); sh.putalpha(tl.split()[3]); bg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(2)),(8,10)); bg.alpha_composite(tl)

# ---------- finish: vignette + comic frame ----------
yy,xx=np.mgrid[0:H,0:W]; v=np.clip((np.hypot((xx-W/2)/(W*0.7),(yy-H/2)/(H*0.7))-0.55)*1.6,0,0.75)
vig=Image.fromarray(np.dstack([np.zeros((H,W,3),np.uint8),(v*255).astype(np.uint8)]),'RGBA'); bg.alpha_composite(vig)
fr=ImageDraw.Draw(bg); fr.rectangle([0,0,W-1,H-1],outline=(255,255,255),width=22); fr.rectangle([22,22,W-23,H-23],outline=(0,0,0),width=8)
bg.convert('RGB').save('76gang.png'); bg.convert('RGB').resize((540,675)).save('preview.png')
