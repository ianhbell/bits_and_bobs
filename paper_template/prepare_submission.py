"""
Note: https://tex.stackexchange.com/questions/574280/latexdiff-with-cite-commands-gives-output-with-apparently-mismatched-braces
"""
import re, os, subprocess, shutil, glob

def remakedir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)
remakedir('submission')

def clean(TeX):
    for ext in 'aux','bbl','blg','idx','log','nlo','out','spl','bib':
        for fn in glob.glob('submission/'+TeX+'_injected.'+ext):
            os.remove(fn)

def final_clean(TeX):
    clean(TeX)
    # for ext in ['aux']:
    #     for fn in glob.glob('submission/SI_'+TeX+'.'+ext):
    #         os.remove(fn)
    # After injection, don't need the bib files
    for fn in glob.glob('submission/*.bib'):
        os.remove(fn)

# Convert all PDF to PDF/A so that they will have a consistent colorspace
def convert_to_PDFA(folder):
    os.makedirs(folder+'/PDF',exist_ok=True)

    # Setup and run a docker instance to convert figures to PDF/A with ghostscript
    subprocess.check_call('docker build -t gs .', cwd='docker', shell=True)

    for PDF in glob.glob(folder+'/*.pdf'):
        filename = os.path.split(PDF)[1]
        new_PDF = 'PDF/' + filename # relative to folder
        shutil.move(PDF, folder+'/'+new_PDF)

        call = 'pdftops ' + new_PDF
        subprocess.check_call(call, shell=True, cwd=folder)
        old_PS = new_PDF.replace('.pdf', '.ps')

        # For debugging.....
        # call_fmt = 'docker run -v "%CWD%":/h ubuntu bash -c "cd /h/%folder% && ls'
        call_fmt = 'docker run -v "%CWD%":/h gs bash -c "cd /h/%folder% && gs -dPDFA -dBATCH -dNOPAUSE -dNOOUTERSAVE -sColorConversionStrategy=UseDeviceIndependentColor -sProcessColorModel=DeviceRGB -sDEVICE=pdfwrite -sPDFACompatibilityPolicy=1 -sOutputFile=%OUT% %IN%"'
        call = call_fmt.replace('%IN%', old_PS).replace('%OUT%', filename).replace('%CWD%', os.path.abspath(os.path.dirname(__file__))).replace('%folder%', folder)
        # print(call); quit()
        subprocess.check_call(call, shell=True, cwd=folder)
    shutil.rmtree(folder+'/PDF')

def check_duplicated_doi(bbl):

    contents = open(bbl).read()
    import collections
    
    thedois = []
    for match in re.finditer(r' {2,}\\BibitemOpen(.*?)\\BibitemShut', contents, re.MULTILINE | re.DOTALL):
        doiregex = r'(10.\d{4,9}\/[-._;()\/:A-Za-z0-9]+)' # https://www.crossref.org/blog/dois-and-matching-regular-expressions/
        # print(match.groups(1))
        dois = []
        for doimatch in re.finditer(doiregex, match.groups(1)[0], re.MULTILINE | re.DOTALL):
            dois.append(doimatch.groups(1,))
        thedois += list(set(dois))

    for item, count in collections.Counter(thedois).items():
        if count > 1:
            raise ValueError(f'Duplicated doi found: {item}')

def get_injected(TeX, *, ofnames, convert_PDFA=True):
    for matcher in  ['*.bib','*.bst','*.cls','*.bst']:
        for fname in glob.glob(matcher):
            shutil.copy2(fname, 'submission')

    def match_is_commented(matchobj):
        """ Work backwards from the start of the match.  If you find an EOL first, not commented; otherwise commented """
        istart = matchobj.start()
        while (istart >= 0):
            if contents[istart] == '%':
                return True
            elif contents[istart] == '\n':
                return False
            istart -= 1

    def repl_func(matchobj):
        # If the line is commented, don't do the injection
        if match_is_commented(matchobj):
            return matchobj.group(0)
        path = matchobj.group(1)
        with open(path if os.path.exists(path) else path+'.tex') as fp:
            return fp.read()

    def repl_figs(matchobj):
        # If the line is commented, don't do the injection
        if match_is_commented(matchobj):
            return matchobj.group(0)
        N = len(matchobj.groups())
        old_path = matchobj.group(N)
        new_path = matchobj.group(N)
        if '/' in new_path or '\\' in new_path:
            new_path = new_path.replace('\\','/').rsplit('/',1)[1]
        print(old_path, '-->', new_path, N, 'groups')
        if os.path.exists('figs/'+old_path):
            shutil.copy2('figs/'+old_path, 'submission/'+new_path+'.pdf')
        else:
            for extension in ['.pdf','.png']:
                old, new = 'figs/'+old_path+extension, 'submission/'+new_path+extension
                if os.path.exists(old):
                    shutil.copy2(old, new)

        return '\includegraphics[{w:s}]{{{f:s}}}'.format(w=matchobj.group(1) if N >= 2 else '', f=new_path)

    with open(TeX + '.tex') as fp:
        contents = fp.read()
        for i in range(100):
            contents = re.sub(r'\\input{(.+)}', repl_func, contents)
            contents = re.sub(r'\\include{(.+)}', repl_func, contents)
        contents = re.sub(r'\\includegraphics{(.+)}', repl_figs, contents)
        contents = re.sub(r'\\includegraphics\[(.+)\]{(.+)}', repl_figs, contents)

    # Write a file that contains the contents of the aux file for the SI
    # AIP submission does not like .aux files (doesn't allow them, but auto-generating this file on the fly seems to work)
    # Also, adding to injected file also causes problems in diff-ing.
    if '%$SI_AUX$%' in contents:
        contents = contents.replace('%$SI_AUX$%', r'\input{SI.aux.tex}')
        with open('submission/SI.aux.tex','w') as fp:
            fp.write(r'\begin{filecontents}{SI_'+TeX+'.aux}'+'\n'+open('submission/SI_'+TeX+'.aux').read()+r'\n\end{filecontents}')
        os.remove('submission/SI_'+TeX+'.aux')

    for ofname in ofnames:
        with open(ofname, 'w') as fp:
            fp.write(contents)

    if convert_PDFA:
        convert_to_PDFA('submission')

    for i in range(3):
        subprocess.check_call('pdflatex --quiet '+TeX+'_injected.tex', cwd='submission', shell=True)
    subprocess.call('bibtex '+TeX+'_injected', cwd='submission', shell=True)

    # Check that no doi appear more than once
    check_duplicated_doi('submission/'+TeX+'_injected.bbl')

    # Inject the bbl file that was generated
    with open('submission/'+TeX+'_injected.tex') as fp:
        contents = fp.read()
        contents = re.sub(r'\\bibliography{(.+)}', lambda r: open('submission/'+TeX+'_injected.bbl').read(), contents)
    with open('submission/'+TeX+'_injected.tex','w') as fp:
        fp.write(contents)

    def is_commented(m):
        if all([(line.strip().startswith('%') or line.strip() == "[H]") for line in m.split('\n')]):
            return True
        else:
            return False

    unlabeled_figures = 0
    for match in re.findall(r"\\begin\{figure[\*]?\}(.*?)\\end\{figure", contents, re.MULTILINE|re.DOTALL):
        if '\\label' in match or is_commented(match):
            pass
        else:
            print('No label:\n', match)
            unlabeled_figures += 1

    unlabeled_tables = 0
    for match in re.findall(r"\\begin\{table[\*]?\}(.*?)\\end\{table", contents, re.MULTILINE|re.DOTALL):
        if '\\label' in match or is_commented(match):
            pass
        else:
            print('No label:\n', match)
            unlabeled_tables += 1

    if unlabeled_tables or unlabeled_figures:
        raise ValueError(f"Some unlabeled tables ({unlabeled_tables}) or figures ({unlabeled_figures}) found")

def build_SI(SI_TeX):
    for i in range(2):
        subprocess.check_call('pdflatex --quiet -shell-escape '+SI_TeX+'.tex', cwd='.', shell=True)
    subprocess.call('bibtex '+SI_TeX+'', cwd='.', shell=True)
    for i in range(2):
        subprocess.check_call('pdflatex --quiet -shell-escape '+SI_TeX+'.tex', cwd='.', shell=True)
    shutil.copy2(SI_TeX+'.aux','submission')
    shutil.copy2(SI_TeX+'.pdf','submission')

def make_diff(TeX):
    def clean():
        for ext in 'aux','bbl','blg','idx','log','nlo','out','spl','bib','synctex.gz':
            for fn in glob.glob('diff.'+ext):
                os.remove(fn)

    # See https://stackoverflow.com/a/41489151
    call_fmt = 'docker run --mount type=bind,source="%CWD%",target=/h gs bash -c "cd /h && latexdiff --allow-spaces --encoding=ascii \\"0. submission/submission/%TeX%_injected.tex\\" submission/%TeX%_injected.tex > diff.tex"'
    call = call_fmt.replace('%TeX%', TeX).replace('%CWD%', os.path.abspath(here).replace("\\",'/'))
    # print(call)#; quit()
    subprocess.check_call(call, shell=True, cwd='.')

    # See https://tex.stackexchange.com/a/579662
    # See https://tex.stackexchange.com/questions/574280/latexdiff-with-cite-commands-gives-output-with-apparently-mismatched-braces
    with open('diff.tex') as fp:
        new = fp.read().replace('\\hspace{0pt}','\\hskip0pt')
    with open('diff.tex','w') as fp:
        fp.write(new)

    for i in range(3):
        subprocess.check_call('xelatex --quiet diff', cwd='.', shell=True)
    subprocess.call('bibtex diff', cwd='.', shell=True)
    for i in range(2):
        subprocess.check_call('xelatex --quiet diff', cwd='.', shell=True)
    clean()
    os.remove('diff.tex')

TeX = 'paper'
SI_TeX = 'SI_' + TeX
resubmission = False
has_SI = True

# Build SI
if has_SI:
    build_SI(SI_TeX)

# Build injected manuscript, embedding the BibTeX and updating figure paths
get_injected(TeX, ofnames=['submission/' + TeX + '_injected.tex'])

# Cleanup again
clean(TeX)

# Compile, check no errors
for i in range(3):
    subprocess.check_call('pdflatex --quiet '+TeX+'_injected', cwd='submission', shell=True)

# Cleanup again
clean(TeX)

if resubmission:
    make_diff(TeX)

final_clean(TeX)

os.makedirs('submission/submission', exist_ok=True)
# os.makedirs('submission/implementation', exist_ok=True)
for fname in glob.glob('submission/*.*'):
    shutil.move(fname, 'submission/submission')

# Copy back the files we want to not zip
keepers = [TeX+'_injected.pdf']
if has_SI:
    keepers.append(SI_TeX+'.pdf')
for fname in keepers:
    shutil.move('submission/submission/'+fname, 'submission')
shutil.move('submission/'+TeX+'_injected.pdf', 'submission/'+TeX+'.pdf')

if resubmission:
    shutil.move('diff.pdf','submission')
shutil.make_archive('submission/submission', 'zip', 'submission/submission')
# shutil.make_archive('submission/implementation', 'zip', 'submission/implementation')