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
exec(open('skyline_fuerth.py').read())
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

def bill(sc=1.0):
    w,h=int(170*sc),int(82*sc); b=Image.new('RGBA',(w,h),(0,0,0,0)); dd=ImageDraw.Draw(b)
    dd.rectangle([0,0,w-1,h-1],fill=(30,30,30)); dd.rectangle([3,3,w-4,h-4],fill=(110,190,100))
    dd.rectangle([10,10,w-11,h-11],outline=(40,110,50),width=max(2,int(3*sc)))
    cx_,cy_=w//2,h//2; rr=int(26*sc)
    dd.ellipse([cx_-rr,cy_-rr,cx_+rr,cy_+rr],fill=(170,225,150),outline=(40,110,50),width=3)
    dd.text((cx_,cy_+2),'$',font=F(int(40*sc)),fill=(20,80,30),anchor='mm')
    for (x,y) in [(22*sc,20*sc),(w-22*sc,h-20*sc)]: dd.text((x,y),'100',font=F(int(20*sc)),fill=(20,80,30),anchor='mm')
    return pad(b,8)
def scatter(spots):
    for (x,y,sc,rot) in spots:
        b=bill(sc).rotate(rot,resample=Image.BICUBIC,expand=True)
        shadow(bg,b,(x,y),off=(8,10),alpha=150,blur=4); bg.alpha_composite(b,(x,y))
scatter([(60,70,0.8,25),(830,60,0.9,-30),(870,300,0.7,15),(40,420,0.75,-20),(600,540,0.6,40),(360,470,0.6,-15)])
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
alpha=np.array(car)[:,:,3]
car=Image.fromarray(np.dstack([q,alpha]),'RGBA')
car=outline(pad(car,12),5,(0,0,0,255))
cpos=(10,1160-car.height); bg.alpha_composite(car,cpos)
# headlight flare
fl=Image.new('RGBA',(W,H),(0,0,0,0)); fd=ImageDraw.Draw(fl)
for (x,y) in [(cpos[0]+12+int(0.37*cw),cpos[1]+12+int(0.49*(car.height-24)))]:
    fd.ellipse([x-70,y-16,x+70,y+16],fill=(200,240,255,150))
bg.alpha_composite(fl.filter(ImageFilter.GaussianBlur(18)))

# ---------- gangster Homer ----------
P=90
hc=np.array(Image.open('homer_cut.png').convert('RGBA')).astype(int)
r_,g_,b_=hc[:,:,0],hc[:,:,1],hc[:,:,2]
yy_,xx_=np.mgrid[0:hc.shape[0],0:hc.shape[1]]
yellow=(r_>190)&(g_>150)&(b_<110)&(r_-g_<48)
region=(xx_>=28)&(xx_<=168)&(yy_>=160)&(yy_<=322)
keep=((xx_<=130)&(yy_>=228)&yellow)|(xx_<=40)
pink=(b_>120)&(r_>120)&(g_<200)
hc[region&(~keep|pink),3]=0
hc[(xx_>=124)&(xx_<=182)&(yy_>=200)&(yy_<=345)&~yellow&(r_+g_+b_<600),3]=0
am=(hc[:,:,3]>40).astype(np.uint8); n_,lab_,st_,_=cv2.connectedComponentsWithStats(am)
big_=1+np.argmax(st_[1:,cv2.CC_STAT_AREA]); hc[lab_!=big_,3]=0
ho=pad(Image.fromarray(hc.astype(np.uint8),'RGBA'),P); d=ImageDraw.Draw(ho)
def s(x,y): return (x+P,y+P)
# joint (cone from fist up-right)
import math as _m
bx,by=s(92,262); tx,ty=s(52,140)
ang=_m.atan2(ty-by,tx-bx); nx,ny=-_m.sin(ang),_m.cos(ang)
w0,w1=8,14
poly=[(bx+nx*w0,by+ny*w0),(tx+nx*w1,ty+ny*w1),(tx-nx*w1,ty-ny*w1),(bx-nx*w0,by-ny*w0)]
d.polygon(poly,fill=(250,245,232),outline=(0,0,0))
d.line([poly[0],poly[1]],fill=(0,0,0),width=4); d.line([poly[3],poly[2]],fill=(0,0,0),width=4)
for k in (0.35,0.62): # paper twist lines
    px_,py_=bx+(tx-bx)*k,by+(ty-by)*k; ww=w0+(w1-w0)*k
    d.line([(px_+nx*ww,py_+ny*ww),(px_-nx*ww+6,py_-ny*ww+4)],fill=(170,160,140),width=2)
d.ellipse([tx-12,ty-12,tx+12,ty+12],fill=(60,40,30),outline=(0,0,0),width=3)
d.ellipse([tx-8,ty-8,tx+8,ty+8],fill=(255,90,20)); d.ellipse([tx-4,ty-5,tx+3,ty+2],fill=(255,230,120))
# smoke puffs
for i,(ox,oy,rr) in enumerate([(-6,-24,11),(8,-50,15),(-12,-82,19),(6,-118,23),(-14,-156,27)]):
    cx_,cy_=tx+ox,ty+oy
    d.ellipse([cx_-rr-3,cy_-rr-3,cx_+rr+3,cy_+rr+3],fill=(40,40,50))
    d.ellipse([cx_-rr,cy_-rr,cx_+rr,cy_+rr],fill=(225,225,235))
    d.ellipse([cx_-rr*0.6,cy_-rr*0.7,cx_-rr*0.1,cy_-rr*0.25],fill=(255,255,255))
# fist blob closing the hand over the joint base
d.rounded_rectangle([s(30,240),s(128,318)],radius=34,fill=(255,217,15),outline=(0,0,0),width=4)
for fy in (262,284,304):
    d.arc([s(78,fy-14),s(124,fy+12)],270,90,fill=(0,0,0),width=4)
d.arc([s(36,232),s(112,290)],200,330,fill=(0,0,0),width=4)
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

scatter([(40,1040,0.7,-8)])
# ---------- 3 x 1kg packages ----------
def brick(x,y,d,w=150,h=58,dep=34,rot=0):
    top=[(x,y),(x+w,y),(x+w+dep,y-dep*0.6),(x+dep,y-dep*0.6)]
    side=[(x+w,y),(x+w+dep,y-dep*0.6),(x+w+dep,y+h-dep*0.6),(x+w,y+h)]
    d.polygon([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],fill=(196,160,104),outline=(0,0,0),width=4)
    d.polygon(top,fill=(226,194,140),outline=(0,0,0),width=4)
    d.polygon(side,fill=(150,118,72),outline=(0,0,0),width=4)
    for k in (0.28,0.72):  # tape bands
        d.line([(x+w*k,y+2),(x+w*k,y+h-2)],fill=(120,90,50),width=8)
        d.line([(x+w*k+dep*0.5,y-dep*0.3),(x+w*k,y)],fill=(120,90,50),width=8)
    d.rectangle([x+w*0.36,y+12,x+w*0.64,y+h-12],fill=(250,250,245),outline=(0,0,0),width=3)
    d.text((x+w/2,y+h/2+1),'1KG',font=F(24),fill=(0,0,0),anchor='mm')
    d.text((x+w*0.14,y+h/2),'76',font=F(20),fill=(200,20,30),anchor='mm')
pk=Image.new('RGBA',(W,H),(0,0,0,0)); pd=ImageDraw.Draw(pk)
brick(372,1188,pd); brick(530,1196,pd,w=140); brick(450,1130,pd)
shadow(bg,pk,(0,0),off=(10,12),alpha=170,blur=5); bg.alpha_composite(pk)
# ---------- title ----------
tl=Image.new('RGBA',(W,H),(0,0,0,0)); td=ImageDraw.Draw(tl)
td.text((40,1250),'76er',font=F(170),fill=(255,214,40),stroke_width=9,stroke_fill=(0,0,0),anchor='ls')
td.text((48,1312),'NO LOVE IN SPRINGFIELD',font=F(46),fill=(255,255,255),stroke_width=5,stroke_fill=(0,0,0),anchor='ls')
tl=tl.rotate(3,resample=Image.BICUBIC,center=(300,1250))
sh=Image.new('RGBA',(W,H),(0,0,0,0)); sh.putalpha(tl.split()[3]); bg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(2)),(8,10)); bg.alpha_composite(tl)

# ---------- finish: vignette + comic frame ----------
yy,xx=np.mgrid[0:H,0:W]; v=np.clip((np.hypot((xx-W/2)/(W*0.7),(yy-H/2)/(H*0.7))-0.55)*1.6,0,0.75)
vig=Image.fromarray(np.dstack([np.zeros((H,W,3),np.uint8),(v*255).astype(np.uint8)]),'RGBA'); bg.alpha_composite(vig)
fr=ImageDraw.Draw(bg); fr.rectangle([0,0,W-1,H-1],outline=(255,255,255),width=22); fr.rectangle([22,22,W-23,H-23],outline=(0,0,0),width=8)
bg.convert('RGB').save('76gang.png'); bg.convert('RGB').resize((540,675)).save('preview.png')
