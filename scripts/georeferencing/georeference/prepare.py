"""CV preparation: inner map frames, bounded corner details and cross candidates."""
import cv2
import numpy as np
from PIL import Image, ImageDraw
from .catalog import CACHE, pilot_records, read, save
from .acquire import ImageCache, region_request, original_point


def overview(record):
    evidence = read(CACHE / 'work' / record['inventoryNumber'] / 'overview.json')
    return evidence, cv2.imread(str(CACHE / 'images' / (evidence['id'] + '.jpg')))


def frame_lines(image, number):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 30, 90)
    h, w = gray.shape
    lines = cv2.HoughLinesP(edges, 1, np.pi/1800, 80, minLineLength=250, maxLineGap=25)
    horizontal = []
    vertical = []
    for x1,y1,x2,y2 in lines[:,0]:
        if abs(y2-y1) < abs(x2-x1)*.025:
            horizontal.append([int(x1),int(y1),int(x2),int(y2)])
        if abs(x2-x1) < abs(y2-y1)*.025:
            vertical.append([int(x1),int(y1),int(x2),int(y2)])
    # Search windows describe the film layout, not geographic orientation.
    def choose(lines, axis, low, high, inner_max):
        candidates = [l for l in lines if low < (l[axis]+l[axis+2])/2 < high]
        if not candidates:
            raise ValueError(f'Missing frame for {number}')
        return (max if inner_max else min)(candidates, key=lambda l:(l[axis]+l[axis+2])/2)
    top = choose(horizontal,1,.18*h,.25*h,True)
    bottom = choose(horizontal,1,.75*h,.81*h,False)
    if number == '947':
        left = choose(vertical,0,.05*w,.10*w,True)
        right = [w-1,0,w-1,h]
    elif number == '948':
        left = [0,0,0,h]
        right = choose(vertical,0,.46*w,.51*w,False)
    else:
        left = choose(vertical,0,.12*w,.16*w,True)
        right = choose(vertical,0,.83*w,.87*w,False)
    def intersection(a,b):
        p=np.cross(np.cross([a[0],a[1],1],[a[2],a[3],1]),np.cross([b[0],b[1],1],[b[2],b[3],1]))
        return (p[:2]/p[2]).tolist()
    return [intersection(top,left),intersection(top,right),intersection(bottom,right),intersection(bottom,left)]


def prepare(offline=False, inventory=None):
    cache = ImageCache(offline=offline)
    for r in pilot_records():
        n=r['inventoryNumber']
        if inventory and n not in inventory: continue
        ev,img=overview(r)
        frame=frame_lines(img,n)
        original=[original_point(p,ev) for p in frame]
        work=CACHE/'work'/n
        save(work/'frame-candidate.json', {'overviewFrame':frame,'resourceFrame':original,'method':'Canny/Hough inner-frame line intersections','reviewStatus':'unreviewed'})
        preview=Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
        ImageDraw.Draw(preview).line([tuple(p) for p in frame+[frame[0]]],fill='red',width=2)
        preview.save(work/'frame-preview.jpg')
        evidence=[]
        for corner,p in zip(['tl','tr','br','bl'],original):
            x=p[0]-180 if corner.endswith('l') else p[0]-1620
            y=p[1]-160 if corner.startswith('t') else p[1]-840
            result,path=cache.get(r,*region_request(r,[x,y,1800,1000]))
            evidence.append({'corner':corner,'evidence':result})
        save(work/'corners.json', evidence)
        print(n, 'prepared', flush=True)
    print({'networkRequests':cache.network_requests,'cacheHits':cache.cache_hits})
