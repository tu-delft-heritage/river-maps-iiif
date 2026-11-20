"""Offline, compact native-evidence packs for human/vision review of CV proposals."""
import cv2
import numpy as np
from PIL import Image,ImageDraw
from .catalog import CACHE,read,save
from .batch import batch_dir
from .pilot import evidence_for
from .acquire import original_point
from .geometry import adjust


def cross_candidate(image,seed,directions):
    # Bounded image-only proposal search. Approval and final 3px localization are separate.
    gray=cv2.cvtColor(np.array(image),cv2.COLOR_RGB2GRAY).astype(np.float32)
    x,y=np.round(seed).astype(int);r=83
    patch=gray[max(0,y-r):y+r+1,max(0,x-r):x+r+1]
    if patch.shape!=(167,167):return list(seed)
    ink=cv2.GaussianBlur(patch,(0,0),5)-cv2.GaussianBlur(patch,(0,0),.7)
    kernel=np.zeros((21,21),np.float32)
    for d in directions:
        d=np.array(d)/np.linalg.norm(d)
        for t in np.r_[np.arange(-8,-2,.25),np.arange(2,8,.25)]:
            p=np.round(10+d*t).astype(int);kernel[p[1],p[0]]=1
    score=cv2.filter2D(ink,-1,kernel/kernel.sum())
    # Slight preference for nearby marks, unrelated to geographic residuals.
    xx,yy=np.meshgrid(np.arange(167),np.arange(167));score-=.003*((xx-83)**2+(yy-83)**2)
    roi=score[8:159,8:159];py,px=np.unravel_index(np.argmax(roi),roi.shape)
    return [int(x+px+8-83),int(y+py+8-83)]


def frame_candidate(image,seed):
    gray=np.asarray(image.convert('L'),float);x,y=seed;h,w=gray.shape
    # Continuous printed neatline wins over text and map detail. Local proposal only.
    xlo,xhi=max(0,int(x)-200),min(w,int(x)+200)
    ylo,yhi=max(0,int(y)-200),min(h,int(y)+200)
    if xhi<=xlo or yhi<=ylo:return list(seed)
    ink=255-gray
    xs=ink[100:min(h,800),xlo:xhi].mean(axis=0)
    ys=ink[ylo:yhi,300:min(w,1500)].mean(axis=1)
    return [int(xlo+np.argmax(xs)),int(ylo+np.argmax(ys))]


def packs(name):
    folder=batch_dir(name);proposals=read(folder/'registration-proposals.json');seeds={}
    out=CACHE/'batch-review';out.mkdir(exist_ok=True)
    for n,p in proposals.items():
        ev=evidence_for(n);images={k:Image.open(CACHE/'images'/(e['id']+'.jpg')).convert('RGB') for k,e in ev.items()}
        control=[q for q in p['points'] if len(q)==5]
        fit=adjust([q[3:5] for q in control],[original_point(q[1:3],ev[q[0]]) for q in control]);directions=np.array(fit['linear']).T
        q={**p,'frameCorners':[frame_candidate(images[k],xy) for k,xy in zip(['tl','tr','br','bl'],p['frameCorners'])],'points':[[a[0],*cross_candidate(images[a[0]],a[1:3],directions),*a[3:]] for a in p['points']]};seeds[n]=q
        canvas=Image.new('RGB',(1800,1550),'white');draw=ImageDraw.Draw(canvas)
        draw.text((10,4),n+' REFERENCE '+p['referenceInventory']+' (UNVERIFIED values '+p['referenceCrs']+')',fill='black')
        # Horizontal border strips and rotated vertical border strips, all 1:1 pixels.
        for i,k in enumerate(['tl','tr','br','bl']):
            fx,fy=q['frameCorners'][i];im=images[k];top=k.startswith('t');left=k.endswith('l')
            strip=im.crop((0,fy-65 if top else fy+4,1800,fy-5 if top else fy+64));canvas.paste(strip,(0,25+i*65))
            v=im.crop((fx-65 if left else fx+5,0,fx-5 if left else fx+65,1000)).rotate(90,expand=True)
            canvas.paste(v,(0,300+i*65));draw.text((1050,315+i*65),k+' border',fill='red')
            corner=im.crop((fx-45,fy-45,fx+45,fy+45)).resize((180,180));canvas.paste(corner,(i*200,580))
            dc=ImageDraw.Draw(canvas);dc.ellipse((i*200+86,666,i*200+94,674),outline='red',width=1)
        for i,pt in enumerate(q['points']):
            k,x,y,*_=pt;tile=images[k].crop((x-30,y-30,x+31,y+31)).resize((183,183));canvas.paste(tile,(i*260,1000));draw.ellipse((i*260+87,1087,i*260+95,1095),outline='red',width=1)
            draw.text((i*260,1190),str(i+1)+' '+str(pt[3:]),fill='black')
        if 'titleNotch' in p:
            k,x,y=p['titleNotch'];im=images[k];tile=im.crop((x-80,y-70,x+700 if k=='br' else x+80,y+270)) if k=='br' else im.crop((x-700,y-70,x+80,y+270));canvas.paste(tile,(900,560))
        overview=images['overview'].copy();d=ImageDraw.Draw(overview);sx=ev['overview']['decodedSize'][0]/ev['overview']['region'][2];sy=ev['overview']['decodedSize'][1]/ev['overview']['region'][3]
        vertices=[original_point(v,ev[k]) for v,k in zip(q['frameCorners'],['tl','tr','br','bl'])];vertices=[(x*sx,y*sy) for x,y in vertices];d.line(vertices+[vertices[0]],fill='red',width=2)
        overview.thumbnail((440,315));canvas.paste(overview,(1350,1230));canvas.save(out/(n+'-proposal.jpg'))
    save(folder/'cross-proposals.json',seeds)


def frame_lines_native(image,corner):
    gray=np.array(image.convert('L'));edges=cv2.Canny(gray,55,140)
    lines=cv2.HoughLinesP(edges,1,np.pi/1800,threshold=150,minLineLength=450,maxLineGap=25)
    horizontal=[];vertical=[]
    if lines is None:return None
    for x1,y1,x2,y2 in lines[:,0]:
        dx=x2-x1;dy=y2-y1
        if abs(dx)>900 and abs(dy/dx)<.025:
            a=dy/dx;b=y1-a*x1;y=a*900+b
            if (y<400 if corner.startswith('t') else y>600):horizontal.append((a,b,y))
        if abs(dy)>550 and abs(dx/dy)<.025:
            a=dx/dy;b=x1-a*y1;x=a*500+b
            if (x<400 if corner.endswith('l') else x>1400):vertical.append((a,b,x))
    if not horizontal or not vertical:return None
    h=sorted(horizontal,key=lambda p:p[2],reverse=corner.startswith('t'))[0]
    v=sorted(vertical,key=lambda p:p[2],reverse=corner.endswith('l'))[0]
    x=(v[0]*h[1]+v[1])/(1-v[0]*h[0]);y=h[0]*x+h[1]
    return [x,y]
