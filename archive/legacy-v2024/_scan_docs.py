import os, re, json
from pathlib import Path
from PyPDF2 import PdfReader

BASE = Path('docs/raw_docs_legacy')
KEYWORDS = [
  'Frazer', 'Frazer Brookes', 'Frazer Method', 'Frazers Method',
  'Dashboard', 'Kundekort', 'pipeline', 'Pipeline', 'DMO', 'Invite', 'Show', 'Keep Talking',
  'reminder', 'Reminder', 'no-show', 'No-Show', 'NBA', 'Next Best', 'event', 'Event', 'webhook', 'CAPI'
]

results = {
  'summary': {},
  'files': [],
  'pdfs': [],
  'events_schema': [],
  'pipelines': {},
}

# Parse events schema
try:
  import json as _json
  sch_path = BASE / 'frazer_method_blueprints' / 'schemas' / 'events.json'
  if sch_path.exists():
    data = _json.loads(sch_path.read_text(encoding='utf-8', errors='ignore'))
    # collect enum if present
    enum = []
    for k,v in data.get('properties',{}).items():
      if k=='event_name' and isinstance(v, dict):
        enum = v.get('enum', [])
    results['events_schema'] = enum
except Exception as e:
  results['events_schema_error'] = str(e)

# Parse pipelines
try:
  p_path = BASE / 'frazer_method_blueprints' / 'crm' / 'pipelines.json'
  if p_path.exists():
    pdata = json.loads(p_path.read_text(encoding='utf-8', errors='ignore'))
    results['pipelines'] = pdata
except Exception as e:
  results['pipelines_error'] = str(e)

# Walk all files
for root, _, files in os.walk(BASE):
  for fn in files:
    fp = Path(root)/fn
    ext = fp.suffix.lower()
    entry = {'path': str(fp).replace('\\','/'), 'ext': ext}
    try:
      if ext in ['.md','.markdown','.txt','.json','.yaml','.yml','.js','.py','.sql']:
        txt = fp.read_text(encoding='utf-8', errors='ignore')
        # First heading or first line
        m = re.search(r'^(#.+)$', txt, re.M)
        title = m.group(1) if m else txt.splitlines()[0][:120] if txt else ''
        hits = {}
        lower = txt.lower()
        for kw in KEYWORDS:
          c = lower.count(kw.lower())
          if c:
            hits[kw] = c
        # snippets: first 2 matches lines for a few key terms
        snippets = []
        for kw in ['Frazer','Dashboard','Kundekort','NBA','reminder','no-show','pipeline']:
          pat = re.compile(r'.{0,60}'+re.escape(kw)+r'.{0,60}', re.I|re.S)
          sm = pat.search(txt)
          if sm:
            snippets.append({'kw': kw, 'snippet': sm.group(0).replace('\n',' ')[:180]})
        entry.update({'title': title, 'hits': hits, 'snippets': snippets})
        results['files'].append(entry)
      elif ext == '.pdf':
        pdf_info = {'path': entry['path']}
        try:
          r = PdfReader(str(fp))
          pdf_info['pages'] = len(r.pages)
          text = ''
          for i in range(min(2, len(r.pages))):
            text += r.pages[i].extract_text() or ''
          pdf_info['snippet'] = (text[:400] or '').replace('\n',' ')
        except Exception as e:
          pdf_info['error'] = str(e)
        results['pdfs'].append(pdf_info)
    except Exception as e:
      entry['error'] = str(e)
      results['files'].append(entry)

# Summaries
from collections import Counter
ext_counts = Counter(Path(f['path']).suffix.lower() for f in results['files'])
results['summary']['counts_by_ext'] = dict(ext_counts)

# Keyword totals
kw_totals = Counter()
for f in results['files']:
  for k,v in f.get('hits',{}).items():
    kw_totals[k]+=v
results['summary']['keyword_totals'] = dict(kw_totals)

outdir = Path('docs/plan/_concordance')
outdir.mkdir(parents=True, exist_ok=True)
(outdir/'report.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
print('OK report at', str(outdir/'report.json'))
