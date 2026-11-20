"""Repeat-edition image matching proposes locations only; never supplies accepted GCPs."""
import re
import cv2
import numpy as np
from PIL import Image,ImageDraw
from .catalog import DATA,CACHE,read,save
from .batch import batch_dir
from .pilot import evidence_for
from .acquire import original_point


def affine(source,target):
    cv2.setRNGSeed(0)
    sift=cv2.SIFT_create(nfeatures=10000)
    ka,da=sift.detectAndCompute(source,None);kb,db=sift.detectAndCompute(target,None)
    if da is None or db is None or len(db)<2:raise ValueError('Too few image features')
    pairs=cv2.BFMatcher().knnMatch(da,db,k=2)
    good=[a for a,b in pairs if a.distance < .65*b.distance]
    if len(good)<12:raise ValueError('Too few image matches')
    a=np.array([ka[m.queryIdx].pt for m in good]);b=np.array([kb[m.trainIdx].pt for m in good])
    matrix,inliers=cv2.estimateAffine2D(a,b,method=cv2.RANSAC,ransacReprojThreshold=2,maxIters=5000,confidence=.999)
    if matrix is None or inliers is None:raise ValueError('No reliable affine registration')
    keep=inliers.ravel().astype(bool)
    residual=b[keep]-(a[keep]@matrix[:,:2].T+matrix[:,2])
    if keep.sum()<12 or np.linalg.det(matrix[:,:2])<=0:raise ValueError('Unreliable registration')
    return matrix,{'matches':len(good),'inliers':int(keep.sum()),'rmsPixels':float(np.sqrt(np.mean(np.sum(residual**2,axis=1)))),'affine':matrix.tolist()}


def propose(name):
    folder=batch_dir(name);selection=read(folder/'selection.json');reviews=read(folder/'reviews.json')['maps']
    prior={}
    for path in [DATA/'reviews.json',*sorted((DATA/'batches').glob('*/reviews.json'))]:
        if path!=folder/'reviews.json':prior.update(read(path)['maps'])
    catalog=read(DATA/'selection.json')['records']
    def sheet_number(r):
        match=re.search(r'Blad\s*(?:no\.?|nr\.?)?\s*(\d+)',r['title'],re.I)
        if not match:raise ValueError(r['title'])
        return match[1]
    groups={};proposals={}
    for r in selection['records']:
        groups.setdefault(sheet_number(r),[]).append(r)
    for group in groups.values():
        ref=next((r for r in group if r['inventoryNumber'] in reviews),None)
        if ref is None:
            ref=next((r for r in reversed(catalog) if r['series']==group[0]['series'] and sheet_number(r)==sheet_number(group[0]) and r['inventoryNumber'] in prior),None)
        if ref is None:raise ValueError('No reviewed reference for sheet '+sheet_number(group[0]))
        rn=ref['inventoryNumber'];rev=reviews.get(rn,prior.get(rn));ev=evidence_for(rn)
        for r in group:
            n=r['inventoryNumber']
            if n in reviews:continue
            dest=evidence_for(n);matrices={};diagnostics={}
            for key in ['overview','tl','tr','br','bl']:
                a=cv2.imread(str(CACHE/'images'/(ev[key]['id']+'.jpg')),0);b=cv2.imread(str(CACHE/'images'/(dest[key]['id']+'.jpg')),0)
                try:matrices[key],diagnostics[key]=affine(a,b)
                except ValueError as e:
                    diagnostics[key]={'error':str(e)}
            def transform(key,xy):
                if key in matrices:return (matrices[key][:,:2]@xy+matrices[key][:,2]).tolist()
                if 'overview' not in matrices:raise ValueError(n+': no overview registration; direct review required')
                native=original_point(xy,ev[key]);ov=ev['overview'];p=np.array(native)*np.array(ov['decodedSize'])/np.array(ov['region'][2:]);q=matrices['overview'][:,:2]@p+matrices['overview'][:,2];native=original_point(q,dest['overview']);d=dest[key];return ((np.array(native)-d['region'][:2])*np.array(d['decodedSize'])/np.array(d['region'][2:])).tolist()
            points=[]
            for p in rev['points']:
                key=p[0]
                if key not in ['tl','tr','br','bl']:
                    native=original_point(p[1:3],ev[key]);key=min(['tl','tr','br','bl'],key=lambda k:np.linalg.norm(np.array(native)-np.array(ev[k]['region'][:2])-np.array([900,500])))
                    xy=(np.array(native)-ev[key]['region'][:2]).tolist()
                else:xy=p[1:3]
                points.append([key,*transform(key,xy),*p[3:]])
            frames=[]
            for i,key in enumerate(['tl','tr','br','bl']):
                xy=rev['frameCorners'][i]
                if str(i) in rev.get('frameNativeOverrides',{}):xy=(np.array(rev['frameNativeOverrides'][str(i)])-ev[key]['region'][:2]).tolist()
                frames.append(transform(key,xy))
            proposal={'referenceInventory':rn,'referenceCrs':rev['crs'],'points':points,'frameCorners':frames,'registration':diagnostics,'reviewStatus':'unreviewed; geographic values and frame locations are proposals only'}
            if 'titleNotch' in rev:
                title=rev['titleNotch'];proposal['titleNotch']=[title[0],*transform(title[0],title[1:])]
            if 'bottomTableNotchOverview' in rev:
                left,right,top=rev['bottomTableNotchOverview'];a=transform('overview',[left,top]);b=transform('overview',[right,top]);proposal['bottomTableNotchOverview']=[a[0],b[0],min(a[1],b[1])]
            proposals[n]=proposal
            print(n,'reference',rn,'inliers',[d.get('inliers',0) for d in diagnostics.values()],flush=True)
    save(folder/'registration-proposals.json',proposals)
