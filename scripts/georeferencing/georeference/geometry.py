"""Affine adjustment in the observation (pixel) space, and simple polygon checks."""
import numpy as np
from scipy.stats import chi2


def area(p):
    p=np.asarray(p,float)
    return float(np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1))/2)


def validate_mask(p, size):
    a=np.asarray(p,float)
    if a.ndim != 2 or a.shape[1] != 2 or len(a)<3 or not np.isfinite(a).all():
        raise ValueError('Invalid polygon coordinates')
    if len(set(map(tuple,a)))!=len(a) or area(a)<=0:
        raise ValueError('Mask must have unique clockwise vertices and positive area')
    if np.any(a<0) or np.any(a>np.asarray(size)):
        raise ValueError('Mask outside image')
    def orient(a,b,c): return float((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))
    def touches(a,b,c,d):
        o=[orient(a,b,c),orient(a,b,d),orient(c,d,a),orient(c,d,b)]
        if o[0]*o[1]<0 and o[2]*o[3]<0:return True
        for v,p,x,y in [(o[0],c,a,b),(o[1],d,a,b),(o[2],a,c,d),(o[3],b,c,d)]:
            if abs(v)<1e-8 and np.all(p>=np.minimum(x,y)) and np.all(p<=np.maximum(x,y)):return True
        return False
    for i in range(len(a)):
        for j in range(i+1,len(a)):
            if j==i+1 or (i==0 and j==len(a)-1):continue
            if touches(a[i],a[(i+1)%len(a)],a[j],a[(j+1)%len(a)]):
                raise ValueError('Self-intersecting mask')
    return True


def adjust(rd, pixels, sigma=2.0):
    rd,pixels=np.asarray(rd,float),np.asarray(pixels,float)
    if rd.shape!=pixels.shape or rd.ndim!=2 or rd.shape[1]!=2 or len(rd)<3 or not np.isfinite(rd).all() or not np.isfinite(pixels).all():
        raise ValueError('Need at least three finite pairs')
    centre=rd.mean(axis=0); scale=np.std(rd,axis=0)
    if np.any(scale<1e-9):raise ValueError('Collinear coordinates')
    A=np.column_stack([np.ones(len(rd)),(rd-centre)/scale])
    weights=np.broadcast_to(np.asarray(sigma,float),(len(rd),))
    if np.any(weights<=0):raise ValueError('Positive uncertainties required')
    Aw=A/weights[:,None]
    beta,_,rank,singular=np.linalg.lstsq(Aw,pixels/weights[:,None],rcond=None)
    condition=float(singular[0]/singular[-1])
    if rank<3 or condition>1000:raise ValueError('Rank deficient or poorly conditioned grid')
    linear=(beta[1:]/scale[:,None]).T
    if abs(np.linalg.det(linear))<1e-10:raise ValueError('Singular image transform')
    intercept=beta[0]-linear@centre
    predicted=A@beta
    residual=pixels-predicted
    dof=2*len(rd)-6
    weighted=float(np.sum((residual/weights[:,None])**2))
    cofactor=np.linalg.inv(Aw.T@Aw)
    hat=np.diag(Aw@cofactor@Aw.T)
    standard=residual/(weights[:,None]*np.sqrt(np.maximum(1-hat[:,None],1e-12)))
    return {'model':'affine-rd-to-image','linear':linear.tolist(),'intercept':intercept.tolist(),
            'normalization':{'centre':centre.tolist(),'scale':scale.tolist()},
            'normalizedParameters':beta.tolist(),'parameterCovariancePerAxis':cofactor.tolist(),
            'covarianceBasis':'assumed independent 2 px per coordinate; not empirically calibrated',
            'controlCount':len(rd),'degreesOfFreedom':dof,'condition':condition,
            'residualPixels':residual.tolist(),'residualMetres':(residual@np.linalg.inv(linear).T).tolist(),
            'rmsPixels':float(np.sqrt(np.mean(np.sum(residual**2,axis=1)))),
            'rmsMetres':float(np.sqrt(np.mean(np.sum((residual@np.linalg.inv(linear).T)**2,axis=1)))),
            'leverage':hat.tolist(),'standardizedResiduals':standard.tolist(),
            'weightedResidualStatistic':weighted,
            'chiSquareUpperTailAssumingSigma':float(chi2.sf(weighted,dof)) if dof else None,
            'statisticalPass':None,'uncertaintyStatus':'uncalibrated',
            'minimalControl':dof==0}


def to_pixel(fit,rd):
    return np.asarray(rd)@np.asarray(fit['linear']).T+fit['intercept']


def to_rd(fit,pixels):
    return (np.asarray(pixels)-fit['intercept'])@np.linalg.inv(fit['linear']).T


def predict_uncertainty(fit,rd):
    a=np.r_[1,(np.asarray(rd)-fit['normalization']['centre'])/fit['normalization']['scale']]
    return float(np.sqrt(a@np.asarray(fit['parameterCovariancePerAxis'])@a))
