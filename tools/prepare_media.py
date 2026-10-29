"""One-time / occasional: make web-sized copies of photos & videos.
Usage: python3 tools/prepare_media.py <source file> <dest under assets/media/> [--max 1600] [--audio]
Images -> JPG (or PNG if transparent), longest side <= --max. Videos -> H.264 MP4, <=1280px wide, plus a poster JPG.
"""
import sys,os,subprocess
from PIL import Image,ImageOps
def image(src,dst,mx=1600):
    im=ImageOps.exif_transpose(Image.open(src)); im.thumbnail((mx,mx))
    if im.mode in('RGBA','LA','P') and 'A' in im.getbands() and im.getextrema()[-1][0]<255:
        dst=os.path.splitext(dst)[0]+'.png'; im.save(dst,optimize=True)
    else:
        dst=os.path.splitext(dst)[0]+'.jpg'; im.convert('RGB').save(dst,quality=82,optimize=True,progressive=True)
    return dst
def video(src,dst,audio=False,vf=None):
    dst=os.path.splitext(dst)[0]+'.mp4'
    f="scale='min(1280,iw)':-2"+(','+vf if vf else '')
    cmd=['ffmpeg','-v','error','-y','-i',src,'-vf',f,'-c:v','libx264','-preset','medium','-crf','22','-pix_fmt','yuv420p','-movflags','+faststart']
    cmd+=(['-c:a','aac','-b:a','96k'] if audio else ['-an'])
    subprocess.run(cmd+[dst],check=True)
    subprocess.run(['ffmpeg','-v','error','-y','-ss','1','-i',dst,'-frames:v','1','-q:v','4',os.path.splitext(dst)[0]+'-poster.jpg'],check=True)
    return dst
if __name__=='__main__':
    a=sys.argv[1:]; src,dst=a[0],a[1]; os.makedirs(os.path.dirname(dst),exist_ok=True)
    mx=int(a[a.index('--max')+1]) if '--max' in a else 1600
    if src.lower().endswith(('.mov','.mp4','.avi','.webm','.m4v')): print(video(src,dst,'--audio' in a))
    else: print(image(src,dst,mx))
