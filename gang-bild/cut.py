import cv2, numpy as np
from PIL import Image
# CAR via grabcut
car=cv2.imread('car_raw.png'); h,w=car.shape[:2]; print('car',w,h)
mask=np.zeros((h,w),np.uint8)
rect=(int(w*0.08),int(h*0.36),int(w*0.84),int(h*0.46))
bg=np.zeros((1,65),np.float64); fg=np.zeros((1,65),np.float64)
cv2.grabCut(car,mask,rect,bg,fg,8,cv2.GC_INIT_WITH_RECT)
m=np.where((mask==1)|(mask==3),255,0).astype(np.uint8)
n,lab,st,_=cv2.connectedComponentsWithStats(m)
big=1+np.argmax(st[1:,cv2.CC_STAT_AREA]); m=np.where(lab==big,255,0).astype(np.uint8)
m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
# fill holes
ff=m.copy(); cv2.floodFill(ff,None,(0,0),255); m=m|cv2.bitwise_not(ff)
m=cv2.GaussianBlur(m,(3,3),0)
rgba=cv2.cvtColor(car,cv2.COLOR_BGR2BGRA); rgba[:,:,3]=m
ys,xs=np.where(m>0); rgba=rgba[ys.min():ys.max()+1,xs.min():xs.max()+1]
cv2.imwrite('car_cut.png',rgba)
# HOMER: floodfill light-neutral from border
ho=cv2.imread('homer_raw.png'); h,w=ho.shape[:2]
hsv=cv2.cvtColor(ho,cv2.COLOR_BGR2HSV)
light=((hsv[:,:,1]<25)&(hsv[:,:,2]>185)).astype(np.uint8)
n,lab=cv2.connectedComponents(light)
border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
bgm=np.isin(lab,list(border))
a=np.where(bgm,0,255).astype(np.uint8)
n,lab,st,_=cv2.connectedComponentsWithStats(a)
big=1+np.argmax(st[1:,cv2.CC_STAT_AREA]); a=np.where(lab==big,255,0).astype(np.uint8)
a=cv2.erode(a,np.ones((2,2),np.uint8))
rgba=cv2.cvtColor(ho,cv2.COLOR_BGR2BGRA); rgba[:,:,3]=a
ys,xs=np.where(a>0); rgba=rgba[ys.min():ys.max()+1,xs.min():xs.max()+1]
cv2.imwrite('homer_cut.png',rgba)
# TAG: black strokes
tg=cv2.imread('tag_raw.png',0)
blk=(tg<90).astype(np.uint8)*255
n,lab,st,_=cv2.connectedComponentsWithStats(blk)
keep=np.zeros_like(blk)
for i in range(1,n):
    x,y,ww,hh,ar=st[i]
    if ar>2000 and y+hh<tg.shape[0]*0.9: keep[lab==i]=255
ys,xs=np.where(keep>0); keep=keep[ys.min():ys.max()+1,xs.min():xs.max()+1]
cv2.imwrite('tag_mask.png',keep)
# preview
prev=Image.new('RGB',(1500,700),(255,0,255))
x=0
for f in ['car_cut.png','homer_cut.png','tag_mask.png']:
    im=Image.open(f); im.thumbnail((500,700)); prev.paste(im,(x,0),im if im.mode=='RGBA' else None); x+=500
prev.save('check2.png')
