#!/usr/bin/env python3
from __future__ import annotations
import argparse, collections, json, struct
from pathlib import Path


def dec(data: bytes, encs):
    data=data.rstrip(b'\0')
    for enc in encs:
        try:return data.decode(enc)
        except UnicodeDecodeError:pass
    return data.decode('latin1','replace')

def dec_omw(b): return dec(b,('utf-8-sig','utf-8','cp1252','latin1'))
def dec_cp(b): return dec(b,('cp949','utf-8-sig','utf-8','cp1252','latin1'))

def iter_records(blob: bytes):
    pos=0; idx=0
    while pos<len(blob):
        rt=blob[pos:pos+4]; size=struct.unpack_from('<I',blob,pos+4)[0]; rest=blob[pos+8:pos+16]
        end=pos+16+size; q=pos+16; subs=[]
        while q<end:
            st=blob[q:q+4]; ss=struct.unpack_from('<I',blob,q+4)[0]; p=blob[q+8:q+8+ss]
            subs.append((st,p)); q+=8+ss
        yield idx,rt,rest,subs
        idx+=1; pos=end

def get(subs,key):
    for s,p in subs:
        if s==key:return p
    return None

def find(root: Path, suffix: str, prefer='ReTranslation'):
    xs=[p for p in root.rglob('*'+suffix) if p.is_file()]
    ys=[p for p in xs if prefer.lower() in p.name.lower()]
    xs=ys or xs
    return sorted(xs,key=lambda p:(len(str(p)),str(p)))[0]

def base_id(rt,subs,decoder):
    if rt==b'SCPT': return decoder((get(subs,b'SCHD') or b'')[:32].split(b'\0',1)[0])
    if rt in (b'MGEF',b'SKIL'):
        p=get(subs,b'INDX'); return p.hex() if p else ''
    p=get(subs,b'NAME')
    return decoder(p) if p else ''

def indexed(records,decoder):
    out={}; ords=collections.Counter(); skipped=collections.Counter()
    for idx,rt,rest,subs in records:
        if rt in (b'TES3',b'INFO',b'DIAL',b'CELL'):
            skipped[rt.decode('ascii','replace')]+=1; continue
        ident=base_id(rt,subs,decoder)
        if not ident:
            skipped[rt.decode('ascii','replace')]+=1; continue
        k0=(rt,ident); n=ords[k0]; ords[k0]+=1
        out[(rt,ident,n)]={'index':idx,'type':rt,'id':ident,'ordinal':n,'subs':subs}
    return out,skipped

SAFE={(b'GMST',b'STRV'),(b'BOOK',b'TEXT')}
SAFE_SUBS={b'FNAM',b'DESC'}

def sublists(subs):
    d=collections.defaultdict(list)
    for s,p in subs:d[s].append(p)
    return d

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--openmw-root',type=Path,required=True); ap.add_argument('--cp949-root',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
    omw=find(a.openmw_root,'.esp'); cp=find(a.cp949_root,'.esp')
    A=list(iter_records(omw.read_bytes())); B=list(iter_records(cp.read_bytes()))
    MA,skipA=indexed(A,dec_omw); MB,skipB=indexed(B,dec_cp)
    common=set(MA)&set(MB); onlyA=set(MA)-set(MB); onlyB=set(MB)-set(MA)
    report={'record_count_openmw':len(A),'record_count_cp949':len(B),'mapped_openmw':len(MA),'mapped_cp949':len(MB),'mapped_common':len(common),'only_openmw':len(onlyA),'only_cp949':len(onlyB),'skipped_openmw':dict(skipA),'skipped_cp949':dict(skipB)}
    counts=collections.Counter(); samples=[]; focus=[]
    for key in sorted(common,key=lambda k:(k[0],k[1],k[2])):
        aa,bb=MA[key],MB[key]; ra=aa['type']; ida=aa['id']
        da,db=sublists(aa['subs']),sublists(bb['subs'])
        for st in set(da)&set(db):
            if not (((ra,st) in SAFE) or st in SAFE_SUBS): continue
            for n,(pa,pb) in enumerate(zip(da[st],db[st])):
                ta,tb=dec_omw(pa),dec_cp(pb)
                if ta==tb: continue
                label=f'{ra.decode()}/{st.decode()}'; counts[label]+=1
                row={'type':ra.decode(),'field':st.decode(),'occurrence':n,'id':ida,'record_ordinal':aa['ordinal'],'openmw':ta,'cp949':tb}
                if len(samples)<1200:samples.append(row)
                low=(ida+' '+ta+' '+tb).lower()
                if any(k in low for k in ('chargen','class','quiz','job','직업','지역','region','seyda','bitter coast','ascadian','grazelands','ashlands','question','generate')):
                    focus.append(row)
    report['safe_display_diff_counts']=dict(counts); report['safe_display_diff_total']=sum(counts.values()); report['samples']=samples; report['focus_samples']=focus[:500]
    report['only_openmw_samples']=[{'type':k[0].decode(),'id':k[1],'ordinal':k[2]} for k in sorted(onlyA,key=lambda k:(k[0],k[1],k[2]))[:100]]
    report['only_cp949_samples']=[{'type':k[0].decode(),'id':k[1],'ordinal':k[2]} for k in sorted(onlyB,key=lambda k:(k[0],k[1],k[2]))[:100]]
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('record_count_openmw','record_count_cp949','mapped_openmw','mapped_cp949','mapped_common','only_openmw','only_cp949','safe_display_diff_counts','safe_display_diff_total')},ensure_ascii=False,indent=2))
    print('FOCUS SAMPLES')
    for row in report['focus_samples'][:160]:print(json.dumps(row,ensure_ascii=False))
if __name__=='__main__':main()
