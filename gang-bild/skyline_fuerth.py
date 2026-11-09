# Stylised Fürth skyline: Altstadt gable houses, St. Michael, Rathaus tower, St. Paul
DARK=(12,4,18,255); FAR=(55,14,48,255); BLK=(0,0,0,255)
WIN=[(255,200,70,255)]*4+[(255,60,120,255)]
def windows(d,x0,y0,x1,y1,p=0.4,step=(22,28),sz=(10,14)):
    for wy in range(int(y0),int(y1)-sz[1],step[1]):
        for wx in range(int(x0),int(x1)-sz[0],step[0]):
            if random.random()<p: d.rectangle([wx,wy,wx+sz[0],wy+sz[1]],fill=random.choice(WIN))
def gable_house(d,x,w,h,base=1000,col=DARK,win=True):
    y0=base-h; roof=w*0.55
    d.polygon([(x,y0),(x+w/2,y0-roof),(x+w,y0),(x+w,base+100),(x,base+100)],fill=col,outline=BLK)
    if win:
        windows(d,x+10,y0+14,x+w-6,base-6,p=0.42)
        d.rectangle([x+w/2-6,y0-roof*0.55,x+w/2+5,y0-roof*0.55+12],fill=random.choice(WIN))
    for wx in [x+w*0.3]: d.rectangle([wx,y0-roof*0.75-26,wx+12,y0-roof*0.4],fill=col,outline=BLK)  # chimney
def church_tower(d,cx,base,tw,body_top,spire_top,col=DARK,oct_h=60):
    d.rectangle([cx-tw/2,body_top,cx+tw/2,base+100],fill=col,outline=BLK,width=4)
    ow=tw*0.75
    d.rectangle([cx-ow/2,body_top-oct_h,cx+ow/2,body_top],fill=col,outline=BLK,width=4)
    for k in (-1,1): d.polygon([(cx+k*tw/2,body_top),(cx+k*ow/2,body_top-12),(cx+k*ow/2,body_top)],fill=col)
    d.polygon([(cx-ow/2-4,body_top-oct_h),(cx,spire_top),(cx+ow/2+4,body_top-oct_h)],fill=col,outline=BLK)
    d.line([(cx,spire_top),(cx,spire_top-30)],fill=col,width=5); d.line([(cx-10,spire_top-20),(cx+10,spire_top-20)],fill=col,width=5)
    for i in range(2): d.rounded_rectangle([cx-ow/2+8+i*(ow/2-4),body_top-oct_h+14,cx-ow/2+8+i*(ow/2-4)+ow/2-16,body_top-12],radius=8,fill=(255,200,70,255))
    d.ellipse([cx-14,body_top+30,cx+14,body_top+58],fill=(255,230,150,255),outline=BLK,width=3)
    windows(d,cx-tw/2+10,body_top+80,cx+tw/2-4,base-10,p=0.3,step=(20,40),sz=(8,20))
def rathaus(d,cx,base,top):
    tw=66
    # main hall
    d.rectangle([cx-170,base-190,cx+120,base+100],fill=DARK,outline=BLK,width=4)
    d.polygon([(cx-178,base-190),(cx-150,base-225),(cx+100,base-225),(cx+128,base-190)],fill=DARK,outline=BLK)
    for wy in (base-170,base-120,base-70):
        for wx in range(cx-158,cx+110,26):
            if abs(wx-cx)>tw/2+4 and random.random()<0.6: d.rounded_rectangle([wx,wy,wx+12,wy+28],radius=5,fill=random.choice(WIN))
    # tower shaft
    shaft_top=top+120
    d.rectangle([cx-tw/2,shaft_top,cx+tw/2,base],fill=DARK,outline=BLK,width=4)
    for wy in range(shaft_top+70,base-200,46): d.rounded_rectangle([cx-7,wy,cx+7,wy+22],radius=6,fill=(255,200,70,255))
    # clock
    d.ellipse([cx-22,shaft_top+14,cx+22,shaft_top+58],fill=(255,235,170,255),outline=BLK,width=4)
    d.line([(cx,shaft_top+36),(cx,shaft_top+22)],fill=BLK,width=3); d.line([(cx,shaft_top+36),(cx+11,shaft_top+40)],fill=BLK,width=3)
    # corbelled gallery + battlements
    gw=tw+18
    d.rectangle([cx-gw/2,shaft_top-14,cx+gw/2,shaft_top],fill=DARK,outline=BLK,width=3)
    for i in range(6): d.rectangle([cx-gw/2+i*gw/6+2,shaft_top-26,cx-gw/2+i*gw/6+gw/12+2,shaft_top-14],fill=DARK)
    # open belfry with arches
    bw_=tw-8
    d.rectangle([cx-bw_/2,top+30,cx+bw_/2,shaft_top-14],fill=DARK,outline=BLK,width=4)
    for i in range(2):
        ax=cx-bw_/2+8+i*(bw_/2-4); d.rounded_rectangle([ax,top+44,ax+bw_/2-16,shaft_top-30],radius=10,fill=(255,170,60,255))
        d.line([(ax+(bw_/2-16)/2,top+44),(ax+(bw_/2-16)/2,shaft_top-30)],fill=DARK,width=3)
    # crown battlements + cap
    d.rectangle([cx-bw_/2-6,top+18,cx+bw_/2+6,top+30],fill=DARK,outline=BLK,width=3)
    for i in range(5): d.rectangle([cx-bw_/2-6+i*(bw_+12)/5+2,top+6,cx-bw_/2-6+i*(bw_+12)/5+(bw_+12)/10+2,top+18],fill=DARK)
    d.polygon([(cx-18,top+8),(cx,top-34),(cx+18,top+8)],fill=DARK,outline=BLK)
    d.line([(cx,top-34),(cx,top-60)],fill=DARK,width=4); d.polygon([(cx,top-60),(cx+18,top-54),(cx,top-48)],fill=(220,30,50,255))

sk=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(sk)
# far layer
x=-20
while x<W:
    w=random.randint(70,120); gable_house(d,x,w,random.randint(200,300),base=990,col=FAR,win=False); x+=w-4
church_tower(d,640,990,50,760,640,col=FAR,oct_h=50)   # Unsere Liebe Frau (far)
# near layer
for (x,w,h) in [(-10,95,170),(80,80,210),(330,90,150),(410,70,200),(560,85,170),(640,100,215),(735,90,180),(820,95,200),(910,100,160),(1000,100,190)]:
    gable_house(d,x,w,h)
church_tower(d,215,1000,62,760,600)                     # St. Michael
d.rectangle([250,880,340,1100],fill=DARK,outline=BLK,width=4); d.polygon([(250,880),(295,830),(340,880)],fill=DARK,outline=BLK)
rathaus(d,505,1000,590)                                   # Rathaus tower
bg.alpha_composite(sk,(0,-75))
# label
lb=Image.new('RGBA',(W,H),(0,0,0,0)); ld=ImageDraw.Draw(lb)
