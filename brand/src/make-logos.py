# Makes the logo SVGs. Needs the Anybody variable font from github.com/google/fonts (ofl/anybody).
# usage: uv run --with fonttools python make-logos.py "Anybody[wdth,wght].ttf" ..
import sys
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
OUT=sys.argv[2]
f=instantiateVariableFont(TTFont(sys.argv[1]),{'wdth':150,'wght':800})
gs=f.getGlyphSet(); cm=f.getBestCmap(); hm=f['hmtx']
def line(text,x0,base,s):
    # x0 = left edge of first glyph's ink, s = px per font unit
    bp=BoundsPen(gs); gs[cm[ord(text[0])]].draw(bp); lsb=bp.bounds[0]
    pen=SVGPathPen(gs, ntos=lambda v: ('%.2f'%v).rstrip('0').rstrip('.'))
    x=x0-lsb*s; right=0
    for c in text:
        g=cm[ord(c)]
        if c!=' ':
            gs[g].draw(TransformPen(pen,(s,0,0,-s,x,base)))
            b=BoundsPen(gs); gs[g].draw(b); right=x+b.bounds[2]*s
        x+=hm[g][0]*s
    return pen.getCommands(), right
NIGHT,LIME,ULTRA,TEXT='#0B0D12','#C8F031','#4D5BFF','#F1EDE4'
KNOT='M12 40 H18 C16 30 20 22 28 22 C30 18 38 18 40 22 C48 22 50 32 46 36 C50 42 42 48 36 44 C32 48 24 46 24 40 C20 38 22 32 28 32 C30 28 36 28 36 34'
def seal(bg=LIME,wire=NIGHT,spark=ULTRA,sw=3):
    return (f'<circle cx="32" cy="32" r="30" fill="{bg}"/><path d="{KNOT}" fill="none" stroke="{wire}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle cx="12" cy="40" r="3.2" fill="{spark}"/><circle cx="36" cy="34" r="3.2" fill="{spark}"/>')
def svg(vb,w,h,body): return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{w}" height="{h}">{body}</svg>\n'
def save(n,s): open(f'{OUT}/phygital-memory-{n}.svg','w').write(s)
save('mark',svg('0 0 64 64',64,64,seal()))
save('mark-night',svg('0 0 64 64',64,64,seal(bg=NIGHT,wire=LIME)))
def wire(wc,sc,sw=3.4):
    return svg('7 14 48 38',64,51,f'<path d="{KNOT}" fill="none" stroke="{wc}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/><circle cx="12" cy="40" r="3.2" fill="{sc}"/><circle cx="36" cy="34" r="3.2" fill="{sc}"/>')
save('wire-lime',wire(LIME,ULTRA))
save('wire-ink',wire(NIGHT,ULTRA))
# favicon: thicker wire, simpler knot (one loop) so it reads at 16px
FAV='M12 40 H18 C16 30 20 22 28 22 C30 18 38 18 40 22 C48 22 50 32 46 36 C50 42 42 48 36 44 C32 48 24 46 24 40 C20 38 22 32 28 32 C30 28 36 28 36 34'
save('favicon',svg('0 0 64 64',64,64,f'<circle cx="32" cy="32" r="31" fill="{LIME}"/><path d="{FAV}" fill="none" stroke="{NIGHT}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="12" cy="40" r="4.6" fill="{ULTRA}"/><circle cx="36" cy="34" r="4.6" fill="{ULTRA}"/>'))
# wordmark: same metrics as Phygital Brain (cap 24.6, baseline 44.3, ink starts 82.57)
s=24.6/1350
d,r=line('PHYGITAL MEMORY',82.57,44.3,s); W=round(r+8.9)
for n,c in (('wordmark',TEXT),('wordmark-ink',NIGHT)):
    save(n,svg(f'0 0 {W} 64',W*2,128,seal()+f'<path d="{d}" fill="{c}"/>'))
# stacked: mark x1.9, two lines cap 40 at baselines 170 and 226
s=40/1350
d1,r1=line('PHYGITAL',4.18,170,s); d2,r2=line('MEMORY',4.18,226,s); W=round(max(r1,r2)+4.18)
for n,c in (('stacked',TEXT),('stacked-ink',NIGHT)):
    save(n,svg(f'0 0 {W} 228',W*2,456,f'<g transform="scale(1.9)">{seal()}</g><path d="{d1}{d2}" fill="{c}"/>'))
print('ok',W)
