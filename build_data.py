"""Build data.json for NGO Operations Database from OCHA Pakistan 5W XLSX.
Source: HDX "Pakistan: Who does What, Where, When and for Whom (5W)" (OCHA Pakistan)
Resource: PAK_5W_24072025.xlsx, snapshot 2026-07-24, downloaded 2026-10-02.
License: CC BY-IGO.
"""
import openpyxl, json, collections, datetime

SRC = '/tmp/ngo5w/pak_5w.xlsx'
OUT = '/home/hatch/workspace/projects/ngo-operations-database/data/data.json'

PROV = {'punjab':'Punjab','khyber pakhtunkhwa':'Khyber Pakhtunkhwa','sindh':'Sindh',
        'balochistan':'Balochistan','gilgit baltistan':'Gilgit-Baltistan','azad kashmir':'Azad Kashmir'}
SECTOR = {'education':'Education','health - srh':'Health - SRH','nutrition':'Nutrition',
  'protection - gbv':'Protection - GBV','food security and livelihood':'Food Security and Livelihood',
  'wash':'WASH','shelter/nfi':'Shelter/NFI','health':'Health','multipurpose cash':'Multipurpose Cash',
  'protection - child protection':'Protection - Child Protection','drr':'DRR','protection':'Protection'}

def norm(s): return ' '.join((s or '').strip().split())
def title(s): return ' '.join(w.capitalize() if w not in ('/',) else w for w in norm(s).split())

wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
ws = wb['Overall (2)']
rows = list(ws.iter_rows(min_row=2, values_only=True))
raw_n = len(rows)

groups = collections.defaultdict(list)
for r in rows:
    org = norm(r[1]).split(' - ')[0]
    prov = PROV.get(norm(r[4]).lower(), title(r[4]))
    dist = title(r[5])
    sec = SECTOR.get(norm(r[10]).lower(), title(r[10]))
    groups[(org, dist, sec, norm(r[11]))].append(r)

def num(v):
    try: return int(float(str(v).replace(',','').strip()))
    except: return 0

recs = []
for (org, dist, sec, act), rs in groups.items():
    tehsils = sorted({title(r[6]) for r in rs if norm(r[6])})
    desc = max((norm(r[12]) for r in rs), key=len, default='')
    mods = sorted({title(r[13]) for r in rs if norm(r[13])})
    inds = sum(num(r[20]) for r in rs); hh = sum(num(r[14]) for r in rs)
    starts = [str(r[30])[:10] for r in rs if r[30]]; ends = [str(r[31])[:10] for r in rs if r[31]]
    statuses = {norm(r[32]).lower() for r in rs if norm(r[32])}
    status = 'Ongoing' if 'ongoing' in statuses else ('Completed' if 'completed' in statuses else ('Planned' if 'planned' in statuses else 'Unknown'))
    provs = sorted({PROV.get(norm(r[4]).lower(), title(r[4])) for r in rs})
    resps = sorted({norm(r[0]) for r in rs if norm(r[0])})
    recs.append({'org':org,'dist':dist,'prov':'/'.join(provs),'sector':sec,'act':act,
                 'desc':desc[:280],'tehsils':tehsils[:8],'mods':mods,'inds':inds,'hh':hh,
                 'start':min(starts) if starts else '','end':max(ends) if ends else '',
                 'status':status,'resp':resps[0] if resps else ''})
recs.sort(key=lambda x:(x['dist'],x['org'],x['sector']))

orgs = sorted({r['org'] for r in recs})
districts = sorted({(r['prov'],r['dist']) for r in recs})
sectors = sorted({r['sector'] for r in recs})

meta = {
 'dataset_title':'Pakistan: Who does What, Where, When and for Whom (5W)',
 'dataset_url':'https://data.humdata.org/dataset/pakistan-who-does-what-where-when-and-for-whom-5w',
 'publisher':'OCHA Pakistan (via Humanitarian Data Exchange - HDX)',
 'license':'CC BY-IGO (Creative Commons Attribution for Intergovernmental Organisations)',
 'license_url':'https://creativecommons.org/licenses/by/3.0/igo/',
 'resource_file':'PAK_5W_24072025.xlsx','snapshot_date':'2026-07-24','downloaded_date':'2026-10-02',
 'raw_rows':raw_n,'unique_activities':len(recs),'org_count':len(orgs),'district_count':len(districts),
 'note':'Data snapshot, not live. Operational picture changes daily. Reported by clusters/organizations; gaps may reflect under-reporting, not absence of need.'
}
json.dump({'meta':meta,'orgs':orgs,'districts':[{'prov':p,'dist':d} for p,d in districts],
           'sectors':sectors,'rows':recs}, open(OUT,'w',encoding='utf-8'),
          ensure_ascii=False, separators=(',',':'))
import os; print("rows:",len(recs),"| size:",os.path.getsize(OUT),"bytes")
