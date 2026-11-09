# --- open driver door: carq is RGBA uint8 array (880 wide) ---
def open_door(carq):
    h,w=carq.shape[:2]
    door=np.array([(560,22),(650,20),(662,100),(687,262),(548,270),(550,105)],np.int32)
    src=np.float32([(560,22),(650,20),(687,262),(548,270)])
    dst=np.float32([(560,22),(452,58),(424,346),(548,270)])
    dm=np.zeros((h,w),np.uint8); cv2.fillPoly(dm,[door],255)
    dtex=carq.copy(); dtex[:,:,3]=np.minimum(dtex[:,:,3],dm)
    # interior where the door was
    out=carq.copy(); inner=Image.fromarray(out,'RGBA'); di=ImageDraw.Draw(inner)
    di.polygon([tuple(p) for p in door],fill=(22,18,28,255),outline=(0,0,0,255))
    di.polygon([(552,102),(662,98),(686,258),(550,266)],fill=(14,10,18,255))
    # ambient LED glow line + seat in side view (car faces left)
    di.line([(556,104),(660,100)],fill=(200,60,255,255),width=3)
    di.polygon([(634,234),(664,70),(704,74),(684,238)],fill=(160,26,40,255),outline=(0,0,0,255))   # backrest
    for k in range(3): di.line([(656+k*8,220),(682+k*7,84)],fill=(110,14,26,255),width=2)
    di.rounded_rectangle([664,42,704,72],radius=10,fill=(160,26,40,255),outline=(0,0,0,255),width=3) # headrest
    di.polygon([(588,214),(672,206),(678,236),(592,246)],fill=(140,22,34,255),outline=(0,0,0,255))   # cushion
    di.ellipse([566,96,592,172],outline=(70,70,82,255),width=7)  # steering wheel
    di.line([(586,134),(610,150)],fill=(70,70,82,255),width=6)
    di.line([(556,250),(684,244)],fill=(200,200,210,255),width=3)  # sill trim
    out=np.array(inner)
    # warp door outward
    M=cv2.getPerspectiveTransform(src,dst)
    wd=cv2.warpPerspective(dtex,M,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
    wd[:,:,:3]=(wd[:,:,:3]*0.85).astype(np.uint8)
    a=wd[:,:,3:].astype(np.float32)/255
    out[:,:,:3]=(out[:,:,:3]*(1-a)+wd[:,:,:3]*a).astype(np.uint8); out[:,:,3]=np.maximum(out[:,:,3],wd[:,:,3])
    # door outline
    dp=cv2.perspectiveTransform(door.reshape(-1,1,2).astype(np.float32),M).astype(np.int32)
    def P(pts): return cv2.perspectiveTransform(np.float32(pts).reshape(-1,1,2),M).reshape(-1,2).astype(np.int32)
    cv2.polylines(out,[P([(550,105),(662,100)])],False,(190,190,215,255),3,cv2.LINE_AA)        # belt line chrome
    cv2.polylines(out,[P([(560,22),(650,20),(662,100),(550,105)])],True,(20,20,26,255),7,cv2.LINE_AA)  # window frame
    cv2.polylines(out,[P([(552,190),(684,182)])],False,(150,150,175,255),2,cv2.LINE_AA)        # body crease
    cv2.fillPoly(out,[P([(640,136),(668,134),(668,142),(640,144)])],(200,200,215,255))      # handle
    cv2.polylines(out,[P([(560,22),(552,268)])],False,(40,40,48,255),5,cv2.LINE_AA)
    cv2.polylines(out,[dp],True,(0,0,0,255),4,cv2.LINE_AA)
    return out
