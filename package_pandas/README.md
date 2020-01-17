# Setup

N.B. Do not install matplotlib, pandas, and numpy via conda on windows because they will pull in the mkl dependency which is huge.

Conda setup (pulls the environment spec from ``environment.yml``)
```
conda env create && conda activate pyin 
```
Build & Test the built exe:
```
pyinstaller --noconfirm test_pandas.py && dist\test_pandas\test_pandas.exe
```
7-zip (optional, but recommended).  See https://superuser.com/a/340062 for a description of the controls on path
```
"C:\Program Files\7-Zip\7z.exe" a test_data.7z .\dist\test_pandas\*
```
Cleanup(optional):
```
conda deactivate && conda env remove -n pyin
```

Joining it all together, one-liner:
```
conda env create && conda activate pyin && pyinstaller --noconfirm test_pandas.py && dist\test_pandas\test_pandas.exe && "C:\Program Files\7-Zip\7z.exe" a test_data.7z .\dist\test_pandas\* && conda deactivate && conda env remove -n pyin
```