#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 13:10:59 2020

@author: anpo
"""

#from ismember import ismember
import os, os.path
import xnat
import numpy as np
# import pdb


def connect_xnat(url, usr, password):

    session = xnat.connect(url, user=usr, password=password)
    return session


def query_dicom(project_name, session, pj_path, dicom_query, download_root):

    files_paths = [] 
    query_result = []
    scans_obj = []
    download_paths = []
    pj = session.projects[project_name]    
    for subject in pj.subjects.values():
        SL = subject.label
        subs = pj.subjects[SL]
        for experiment in subs.experiments.values():
            EL = experiment.label
            exps = subs.experiments[EL]
            for iscan in exps.scans.keys():                
                SCL = iscan 
                dicom_tag = exps.scans[SCL].read_dicom()                                     
                file_path = os.path.join(pj_path, SL, EL, SCL)
                df, dv = dict_keys(dicom_query)  
                #pdb.set_trace() % careful dicom_tag.dir not list all?
                if all(ismember0(df, dicom_tag.dir())):                   
                    out, query_out = value_check(dicom_tag, df, dv)
                    if out : 
                        files_paths.append(file_path)
                        download_paths.append(os.path.join(download_root, SL, EL, SCL))
                        query_result.append(query_out)
                        scans_obj.append(exps.scans[SCL])
                #     else:
                #         print('field exist, value did not match')    
                # else:
                #     print('query field did not exist')
                
    return files_paths, query_result, scans_obj, download_paths  

def select_files(download_paths, query_result, selector):

    assert(len(query_result[0]) == len(selector))
   
    selected = [query_result[i] == selector for i in range(len(query_result))]
    paths_to_download = [i for i, j in zip(download_paths, selected) if j == True]
   
    return paths_to_download   


def download_files(scans_obj, download_paths): 
   
    assert(len(scans_obj) == len(download_paths))
    
    try:
        cnt = 0
        for ifile in scans_obj:
            if (os.path.isdir(download_paths[cnt])):
                ifile.download_dir(download_paths[cnt])
            else: 
                os.makedirs(download_paths[cnt]) 
                ifile.download_dir(download_paths[cnt])
            cnt+=1
    except:
        print('download error')  
    
    print('{} total files, {} files sucessfully download'.format(len(scans_obj),cnt))
    
def ismember0(a,b):
    
    B_unique_sorted, B_idx = np.unique(a, return_index=True)
    B_in_A_bool = np.in1d(B_unique_sorted, b, assume_unique=True)
    return B_in_A_bool

    
def dict_keys(dicom_query):
    df = []
    dv = []
    for i in dicom_query.keys():    
        df.append(i)
        fv = dicom_query[i]
        if type(fv) == str: 
           fv = fv.lower()
        dv.append(fv)
    return df, dv


def value_check(dicom_tag,df,list_value):
    out = np.zeros(len(df),dtype=bool)
    dicom_values = []
    cnt = 0
    for i in df:        
        dicom_v = str(dicom_tag[i].value).lower()
        dicom_values.append(dicom_v)
        # 一個個比對, 但有tolerance
        # print(dicom_v)
        # print(list_value)
        # print(list_value[cnt])
        if len(dicom_v) >= len(list_value[cnt]):
           short_one = list_value[cnt]
           long_one = dicom_v
        else:
           short_one = dicom_v
           long_one = list_value[cnt] 
        # print(out)   
        if short_one in long_one:              
           out[cnt] = True
                
        cnt+=1
    out = all(out) 
        
    return out, dicom_values    


# test2_pj = session.projects["test_pj2"]

# test2_pj.subjects

# subject0 = test2_pj.subjects["1_2_528_1_1001_200_10_4201_11781_257665444_20201117070526579"]

# for subject in test2_pj.subjects.values():
#     print(subject.label)
    
    
# subject0.download_dir('/home/anpo/Desktop/DataForDBtest/test_sub_Download')

# subject0.experiments

# exp = subject0.experiments['147A32011X01']

# exp.fields # custom variable

# exp.scans['Scout']

# exp.scans['Scout'].dicom_dump()

# dicom_tag = exp.scans['Scout'].read_dicom()

# dicom_tag['Modality'].value


# # import xnat
# import argparse
# import re


# def get_files(connection, project, subject, session, scan):
#     xnat_project = connection.projects[project]
#     xnat_subject = xnat_project.subjects[subject]
#     xnat_experiment = xnat_subject.experiments[session]
#     xnat_scan = xnat_experiment.scans[scan]
#     files = xnat_scan.files.values()
#     return files


# def filter_files(xnat_files, regex):
#     filtered_files = []
#     regex = re.compile(regex)
#     for file in xnat_files:
#         found = regex.match(file.name)
#         if found:
#             filtered_files.append(file)
#     return filtered_files


# def main():
#     parser = argparse.ArgumentParser(description='Prints all files from a certain scan.')
#     parser.add_argument('--xnathost', type=unicode, required=True, help='xnat host name')
#     parser.add_argument('--project', type=unicode, required=True, help='Project id')
#     parser.add_argument('--subject', type=unicode, required=True, help='subject')
#     parser.add_argument('--session', type=unicode, required=True, help='session')
#     parser.add_argument('--scan', type=unicode, required=True, help='scan')
#     parser.add_argument('--filter', type=unicode, required=False, default='.*', help='regex filter for file names')
#     args = parser.parse_args()

#     with xnat.connect(args.xnathost) as connection:
#         xnat_files = get_files(connection, args.project, args.subject, args.session, args.scan)
#         xnat_files = filter_files(xnat_files, args.filter)
#         for file in xnat_files:
#             print('{}'.format(file.name))


# if __name__ == '__main__':
#     main()