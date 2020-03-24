import shutil, subprocess, re, itertools, glob

shutil.copy2(r'D:\Code\alex\Alexandria.bib',r'Alexandria.bib')
subprocess.check_call('activate py37 && python -c "import CoolProp; CoolProp.copy_BibTeX_library()"',shell=True)

import pybtex, os
from pybtex.database import parse_file

bib_data = parse_file('Alexandria.bib')
path_dict = {}
for key in bib_data.entries:
    entry = bib_data.entries[key].fields
    if 'file' in entry:
        oldpath = entry['file'].replace('\\:',':/').lstrip(':').rsplit(':',1)[0]
        if os.path.exists(oldpath):
            # print(key, oldpath)
            path_dict[key] = oldpath

def get_keys(bblfile):
    if not os.path.exists(bblfile):
        return []
    else:
        with open(bblfile, 'r') as fp:
            contents = fp.read()
            patterns = [r'\\bibitem\s*\[.*?\]{(.*?)}', r'\\bibitem\s*{(.*?)}']
            results = [re.findall(regex, contents, re.MULTILINE | re.DOTALL) for regex in patterns]
            return list(itertools.chain.from_iterable(results))

if os.path.exists('lit'):
    shutil.rmtree('lit')
os.mkdir('lit')

items = []
for bbl in glob.glob('*.bbl'):
    items += get_keys(bbl)

missing = []
for item in items:
    if item in path_dict:
        shutil.copy2(path_dict[item], 'lit')
        bib_data.entries[item].fields['file'] = 'lit/'+os.path.basename(path_dict[item])
    else:
        missing.append(item)
for m in sorted(set(missing)):
    print('Missing:', m)

with open('Alexandria.bib','w') as fp:
    fp.write(bib_data.to_string('bibtex').replace(r'\\textasciitilde',r'\~'))