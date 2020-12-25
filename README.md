# xnat


prerequisite

xnatpy module
https://xnat.readthedocs.io/en/latest/

將檔案load_config, xnatconfig.ini, xnat_download.py置於同一個folder下並加入路徑



xnat_download.py 模組
xnat_export.ipynb 如何以dicom tag query影像範例


dicom Query 說明

聯集是default的形式

Case A 
field A必須存在 而且 case-sensitive
x必須存在, 但 word-sensitive
dicom_query['A'] = 'x'


Case A & B & C
field A, B, and C 均必須存在 而且 case-sensitive
x,y,z 均必須存在, 但 word-sensitive
dicom_query['A'] = 'x'
dicom_query['B'] = 'y'
dicom_query['C'] = 'z'


Case A | B 
請個別query
dicom_query['A'] = 'x'
然後
dicom_query['B'] = 'y'
再pool_data

e.g. field A = x | field B = x, pooling dicom_query['A'] = 'x', dicom_query['B'] = 'x' 
