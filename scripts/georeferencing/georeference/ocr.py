"""Optional OCR proposals, kept separate from independently read visual labels."""
import subprocess
import cv2
from PIL import Image,ImageOps
from .catalog import CACHE,DATA,read,save,pilot_records
from .pilot import evidence_for


def propose_ocr():
    version=subprocess.run(['tesseract','--version'],capture_output=True,text=True,check=True).stdout.splitlines()[0]
    rows=[]
    for r in pilot_records():
        n=r['inventoryNumber'];ev=evidence_for(n)
        for side in ['tl','tr','br','bl']:
            e=ev[side];im=Image.open(CACHE/'images'/(e['id']+'.jpg')).convert('L')
            # Corner strips only. Try orthogonal text orientations, never alter source pixels.
            w,h=im.size
            regions=[(0,0,w,min(180,h))] if side[0]=='t' else [(0,max(0,h-170),w,h)]
            regions += [(0,0,min(180,w),h)] if side[1]=='l' else [(max(0,w-190),0,w,h)]
            for index,box in enumerate(regions):
                crop=ImageOps.autocontrast(im.crop(box))
                # Save all proposals, including empty or incorrect text; none assigns coordinates.
                texts=[]
                for rotation in [0,90,270]:
                    p=CACHE/'ocr-input.png';crop.rotate(rotation,expand=True).resize(tuple(2*x for x in crop.rotate(rotation,expand=True).size)).save(p)
                    result=subprocess.run(['tesseract',str(p),'stdout','--psm','11','-c','tessedit_char_whitelist=0123456789+-.'],capture_output=True,text=True,check=True)
                    texts.append({'rotationDegrees':rotation,'text':result.stdout.strip()})
                rows.append({'inventoryNumber':n,'evidenceId':e['id'],'regionInEvidence':box,'proposals':texts})
        print(n,'OCR proposals',flush=True)
    save(DATA/'ocr-proposals.json',{'engine':version,'status':'untrusted proposals; visual readings are authoritative',
      'limitations':'Only orthogonal rotations; oblique, faint and handwritten labels often fail. No automatic coordinate assignment.',
      'items':rows})
