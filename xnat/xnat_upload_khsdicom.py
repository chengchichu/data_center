#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 13 15:11:11 2021

@author: anpo
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 13:19:30 2021

@author: anpo
"""



import os, os.path
import zipfile
import xnat
import pyxnat
from pydicom import dcmread
import pandas as pd
import glob
import pdb
import numpy as np

# https://xnat.readthedocs.io/en/latest/static/tutorial.html

def connect_xnat(url, usr, password):
    session = xnat.connect(url, user=usr, password=password)
    return session

# 把所有輸入路徑zip為單一個file
def zipit(folders, zip_filename):
    zip_file = zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED)

    for folder in folders:
        for dirpath, dirnames, filenames in os.walk(folder):
            for filename in filenames:
                zip_file.write(
                    os.path.join(dirpath, filename),
                    os.path.relpath(os.path.join(dirpath, filename), os.path.join(folders[0], '../..')))

    zip_file.close()


def img_uploader(root_path, session, project_name, patient_ID, exp, pidn):
    
    # 根據accession number 來當exp/session的號碼, 但如果一個folder裡面的圖片有兩個不同的號碼, 會衝突
    # 傳不上去, 利用upload assistant解決
    for exp_id in exp['img'].unique():   
        archive_name = 'myZipFile.zip'
        archive_path = os.path.join(root_path, patient_ID, archive_name)
        fs_one_exp = exp['fs'][exp['img'] == exp_id]       
        zipit(fs_one_exp.tolist(), archive_path)

        experiment = session.services.import_(archive_path,
                                          project=project_name,
                                          subject=pidn,
                                          experiment=exp_id)
                                         
        os.remove(archive_path)
    return experiment


def get_DICOM_info(root_path, patient_ID):        
    imgs = []
    fs = []
    for root, dirs, files in os.walk(os.path.join(root_path, patient_ID)):
        if files:
            if files[0].endswith('.dcm'):
                head_info = dcmread(os.path.join(root, files[0]), stop_before_pixels=True, force=True)
              #  pdb.set_trace()
                # p_ID = head_info.data_element('PatientID').value
                image_No = head_info['AccessionNumber'].value
                if not image_No:
                    image_No = head_info['StudyID'].value 
                # print(image_No)    
                imgs.append(image_No)        
                fs.append(root)                
    imgs = np.array(imgs)
    fs = np.array(fs)
    a = np.concatenate((imgs.reshape(-1,1),fs.reshape(-1,1)),axis = 1)            
    exp_table = pd.DataFrame(data = a, columns = ['img','fs'])
    return exp_table
    

def get_img_report(img_reports, image_No):
    try:
        return img_reports[img_reports.image_no == image_No].CONTENT.values[0]
    except Exception:
        return ''


# def report_uploader(session, experiment, img_report_set, image_No):
#     report_text = get_img_report(img_report_set, image_No)
#     if report_text != '':
#         with open("report.txt", "w") as text_file:
#             text_file.write(report_text)
#         ext = session.create_object(experiment.uri)
#         resource = ext.resources.get('Report', None)
#         # If resource doesn't exist, just create it
#         if resource is None:
#             resource = session.classes.ResourceCatalog(parent=ext, label='Report')
#         resource.upload(os.path.realpath(text_file.name), 'report.txt')
#         # resource.upload_dir('/output/currsub')
#         os.remove(os.path.realpath(text_file.name))



if __name__ == '__main__':

    xlslist = pd.read_csv('/home/anpo/Desktop/pyscript/2AI_data_20210518.csv')
    xlslist_re = xlslist.rename(columns={'gender':'G-code', 'Unnamed: 4':'Gender', 'his':'HIS', 'dicom_pidn':'PIDN', 'birthday': 'Birthday'})
    xlslist2 = pd.read_csv('/home/anpo/Desktop/pyscript/ai-missing-20210524.csv')
    
    cnt = 0
    for i in xlslist2['Birthday']:
        xlslist2.at[cnt,'Birthday'] = i.replace('-','/')        
        cnt+=1
   
    xlslist_re.at[17,'Birthday'] = xlslist_re.at[17,'Birthday'].replace('-','/')

    pd.concat((xlslist_re,xlslist2))
    xlist_all = pd.concat((xlslist_re,xlslist2))
    
    project_name = 'BRS-KHS-1'
    session = xnat.connect('http://10.30.223.96:8080', user='anpo', password='espesp043')
    pyxnatobj = pyxnat.Interface('http://10.30.223.96:8080','anpo','espesp043')
    root_path = '/media/anpo/Backup Plus/DICOM_from_KHS_2021'
    datalist = next(os.walk('/media/anpo/Backup Plus/DICOM_from_KHS_2021/'))[1]
      
    complete = [] 
    fails = []
    meta = {}
    for patient_ID in datalist:
        # image_No = get_DICOM_info(root_path, patient_ID)
        
        print(patient_ID)
        patient_ID_ = patient_ID.replace(' ', '')
        image_No = patient_ID_.split('-')[1]
        pidn = xlist_all['PIDN'][xlist_all['HIS'] == int(image_No)].values[0]       
        gender = xlist_all['Gender'][xlist_all['HIS'] == int(image_No)].values
        info = {} 

        info['gender'] = gender[0]
        
        BD = xlist_all['Birthday'][xlist_all['HIS'] == int(image_No)].values
        info['YOB'] = BD[0].split('/')[0]
        info['dob'] = BD[0].replace('/','-')
        info['handedness'] = 'unknown'
        meta[str(pidn)] = info
        
        if pidn.size:
           print(str(pidn))
           try:              
               exp_table = get_DICOM_info(root_path, patient_ID)
               experiment = img_uploader(root_path, session, project_name, patient_ID, exp_table, pidn)
               complete.append(patient_ID)             
           except:              
               print('fail')
               fails.append(patient_ID)
               
  # metadata 
for pidn, j in meta.items():
    if int(pidn) not in [4315,1432]:
        session.projects[project_name].subjects[str(pidn)].demographics.handedness = j['handedness']
        session.projects[project_name].subjects[str(pidn)].demographics.gender = j['gender']
        my_project = pyxnatobj.select.project(project_name)
        my_subject = my_project.subject(str(pidn))
        my_subject.attrs.mset({'xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/YOB': j['YOB']})
        my_subject.attrs.mset({'xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/dob': j['dob']})


#
# import os
# import pandas as pd
# import numpy as np

# # for dirpath, dirName, filename in os.walk('/media/anpo/Backup Plus/DICOM_from_KHS_2021/'):
# #     print(dirpath)
#     # for f in filename:
#     #     print(os.path.join(dirpath, f))

# datalist = next(os.walk('/media/anpo/Backup Plus/DICOM_from_KHS_2021/'))[1]
# his = xlslist['his'].values
# his2 = np.array([int(x.split('-')[1]) for x in datalist])
# np.setdiff1d(his2,his)


