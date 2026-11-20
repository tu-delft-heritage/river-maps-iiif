"""Image matching produces tie candidates; @allmaps/attach is a separate solver."""
import cv2
import numpy as np
from .catalog import DATA,CACHE,read,save,pilot_records
from .acquire import ImageCache,original_point,region_request
from .prepare import overview
from PIL import Image, ImageDraw


def matches(a,b,mask_a=None,mask_b=None):
    sift=cv2.SIFT_create(nfeatures=12000,contrastThreshold=.025)
    ka,da=sift.detectAndCompute(a,mask_a);kb,db=sift.detectAndCompute(b,mask_b)
    candidates=[m for pair in cv2.BFMatcher().knnMatch(da,db,k=2) if len(pair)==2 for m,n in [pair] if m.distance<.65*n.distance]
    pa=np.float32([ka[m.queryIdx].pt for m in candidates]);pb=np.float32([kb[m.trainIdx].pt for m in candidates])
    cv2.setRNGSeed(2301)
    affine,ok=cv2.estimateAffine2D(pa,pb,method=cv2.RANSAC,ransacReprojThreshold=1.5,maxIters=4000,confidence=.999)
    if affine is None:raise ValueError('No reliable overlap')
    return [(pa[i].tolist(),pb[i].tolist(),float(m.distance)) for i,m in enumerate(candidates) if ok[i]],len(candidates),affine


def prepare_ties(offline=False):
    records={r['inventoryNumber']:r for r in pilot_records()}
    rasters=[];evs=[];masks=[]
    for n in ['947','948']:
        ev,img=overview(records[n]);evs.append(ev)
        gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY);rasters.append(gray)
        c=read(DATA/'maps'/(records[n]['id']+'.json'))
        scale=np.array(ev['decodedSize'])/ev['region'][2:]
        p=(np.array(c['mask']['resourceMask'])*scale).astype(np.int32)
        mask=np.zeros(gray.shape,np.uint8);cv2.fillPoly(mask,[p],255)
        mask=cv2.erode(mask,np.ones((15,15),np.uint8))
        masks.append(mask)
    pairs,count,affine=matches(*rasters,*masks)
    # Farthest-point selection gives coverage; descriptor distance breaks ties deterministically.
    pairs=sorted(pairs,key=lambda p:p[2]);chosen=[pairs[0]]
    while len(chosen)<6:
        best=max(pairs,key=lambda p:min(np.linalg.norm(np.array(p[0])-q[0]) for q in chosen))
        chosen.append(best)
    chosen.sort(key=lambda p:p[0][0])
    cache=ImageCache(offline=offline);ties=[]
    for i,(a,b,d) in enumerate(chosen):
        evidence=[];patches=[];original=[]
        for n,p,ev in zip(['947','948'],[a,b],evs):
            native=original_point(p,ev);original.append(native)
            e,path=cache.get(records[n],*region_request(records[n],[native[0]-200,native[1]-200,400,400]))
            evidence.append(e);patches.append(cv2.imread(str(path),cv2.IMREAD_GRAYSCALE))
        local,local_count,local_affine=matches(*patches)
        target=np.array(original[0])-evidence[0]['region'][:2]
        selected=min(local,key=lambda p:np.linalg.norm(np.array(p[0])-target))
        pixels=[original_point(p,e) for p,e in zip(selected[:2],evidence)]
        tie={'id':f'tie-{i+1}','role':'fit' if i%2==0 else 'check','mapIds':[records[n]['id'] for n in ['947','948']],
             'resourceCoords':pixels,'evidence':evidence,'overviewDescriptorDistance':d,
             'nativeMatchCount':len(local),'nativeDescriptorDistance':selected[2],
             'visualReview':'pending','matchingMethod':'SIFT ratio .65, affine RANSAC 1.5 pixels; local native SIFT refinement'}
        ties.append(tie)
        contact=Image.new('RGB',(800,430),'white');draw=ImageDraw.Draw(contact)
        for j,(patch,p) in enumerate(zip(patches,selected[:2])):
            im=Image.fromarray(patch).convert('RGB');di=ImageDraw.Draw(im)
            di.ellipse((p[0]-6,p[1]-6,p[0]+6,p[1]+6),outline='red',width=1)
            contact.paste(im,(j*400,25));draw.text((j*400+10,8),f'tie-{i+1} '+['947','948'][j],fill='black')
        contact.save(CACHE/'review'/f'tie-{i+1}.jpg')
    save(DATA/'tie-candidates.json',{'pair':['947','948'],'overviewCandidates':count,'overviewInliers':len(pairs),
        'overviewAffine':affine.tolist(),'ties':ties,'notes':'Same-sheet ties are correlated evidence; no extra geographic observations.'})
    print({'tiePairs':len(ties),'networkRequests':cache.network_requests,'cacheHits':cache.cache_hits})
