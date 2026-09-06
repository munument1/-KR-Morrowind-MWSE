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

def rid(rt,subs,decoder):
    if rt==b'SCPT': return decoder((get(subs,b'SCHD') or b'')[:32].split(b'\0',1)[0])
    if rt in (b'MGEF',b'SKIL'):
        p=get(subs,b'INDX'); return p.hex() if p else ''
    p=get(subs,b'NAME')
    return decoder(p) if p else ''

SAFE={(b'GMST',b'STRV'),(b'BOOK',b'TEXT')}
SAFE_SUBS={b'FNAM',b'DESC'}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--openmw-root',type=Path,required=True); ap.add_argument('--cp949-root',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
    omw=find(a.openmw_root,'.esp'); cp=find(a.cp949_root,'.esp')
    A=list(iter_records(omw.read_bytes())); B=list(iter_records(cp.read_bytes()))
    report={'record_count_openmw':len(A),'record_count_cp949':len(B),'record_type_sequence_equal':[x[1] for x in A]==[x[1] for x in B]}
    counts=collections.Counter(); samples=[]; identity_mismatch=[]; chargen=[]
    for (ia,ra,_,sa),(ib,rb,_,sb) in zip(A,B):
        if ra!=rb: continue
        ida=rid(ra,sa,dec_omw); idb=rid(rb,sb,dec_cp)
        if ra not in (b'INFO',b'DIAL',b'CELL') and ida!=idb:
            identity_mismatch.append({'index':ia,'type':ra.decode('ascii','replace'),'openmw_id':ida,'cp949_id':idb})
        # Compare occurrence-by-occurrence for safe display subrecords.
        by_a=collections.defaultdict(list); by_b=collections.defaultdict(list)
        for s,p in sa: by_a[s].append(p)
        for s,p in sb: by_b[s].append(p)
        for st in set(by_a)&set(by_b):
            if not (((ra,st) in SAFE) or st in SAFE_SUBS): continue
            for n,(pa,pb) in enumerate(zip(by_a[st],by_b[st])):
                ta,tb=dec_omw(pa),dec_cp(pb)
                if ta==tb: continue
                key=f'{ra.decode()}/{st.decode()}'
                counts[key]+=1
                row={'index':ia,'type':ra.decode(),'field':st.decode(),'occurrence':n,'id':ida or idb,'openmw':ta,'cp949':tb}
                if len(samples)<400: samples.append(row)
                low=(ida+' '+ta+' '+tb).lower()
                if any(k in low for k in ('chargen','class','quiz','직업','지역','region','seyda','bitter coast','ascadian','grazelands','ashlands')):
                    chargen.append(row)
    report['safe_display_diff_counts']=dict(counts)
    report['safe_display_diff_total']=sum(counts.values())
    report['identity_mismatch_count']=len(identity_mismatch)
    report['identity_mismatch_samples']=identity_mismatch[:100]
    report['samples']=samples
    report['chargen_region_samples']=chargen[:250]
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('record_count_openmw','record_count_cp949','record_type_sequence_equal','safe_display_diff_counts','safe_display_diff_total','identity_mismatch_count')},ensure_ascii=False,indent=2))
    print('CHARGEN/REGION SAMPLES')
    for row in report['chargen_region_samples'][:80]:
        print(json.dumps(row,ensure_ascii=False))
if __name__=='__main__': main()
