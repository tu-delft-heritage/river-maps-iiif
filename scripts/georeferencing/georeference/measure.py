"""Local cross-arm ridge localization, independently of geographic residuals."""
import cv2
import numpy as np
from scipy.ndimage import map_coordinates
from scipy.optimize import minimize


def refine_cross(image,seed,directions):
    gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY).astype(float)
    x,y=seed
    # Local dark contrast. A symmetric short template ignores the longer arrow tips.
    cx,cy=int(round(x)),int(round(y))
    patch=gray[max(0,cy-24):cy+25,max(0,cx-24):cx+25]
    origin=np.array([max(0,cx-24),max(0,cy-24)])
    ink=cv2.GaussianBlur(patch,(0,0),5)-cv2.GaussianBlur(patch,(0,0),.65)
    angles=[np.arctan2(d[1],d[0]) for d in directions]
    t=np.r_[np.linspace(-8,-2.5,12),np.linspace(2.5,8,12)]
    def objective(parameters):
        centre=np.array(parameters[:2])-origin
        score=0
        for angle in angles:
            a=angle+parameters[2]
            p=centre[:,None]+np.array([np.cos(a),np.sin(a)])[:,None]*t
            score+=map_coordinates(ink,[p[1],p[0]],order=1,mode='nearest').mean()
        return -score
    result=minimize(objective,[x,y,0],method='Powell',bounds=[(x-3,x+3),(y-3,y+3),(-.06,.06)],
                    options={'xtol':1e-4,'ftol':1e-5})
    point=np.array(result.x[:2])
    boundary=bool(np.max(np.abs(point-seed))>2.9)
    return (list(seed) if boundary else point.tolist()), {
        'method':'symmetric short cross-arm dark-ridge template; bounded subpixel search',
        'seed':list(seed),'candidate':point.tolist(),'shiftPixels':float(np.linalg.norm(point-seed)),
        'accepted':not boundary,'reason':'search boundary; retain reviewed seed' if boundary else 'within 3 px seed window',
        'score':float(-result.fun)}
