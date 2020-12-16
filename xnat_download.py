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
import pdb


def connect_xnat(url, usr, password):

    session = xnat.connect(url, user=usr, password=password)
    return session


def query_dicom(project_name, session, pj_path, dicom_query, download_root):

    files_paths = []    
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
                    if value_check(dicom_tag, df, dv): 
                        files_paths.append(file_path)
                        download_path = os.path.join(download_root, SL, EL, SCL)
                        if (os.path.isdir(download_path)):
                            exps.scans[SCL].download_dir(download_path)
                        else: 
                            os.makedirs(download_path) 
                            exps.scans[SCL].download_dir(download_path) 
                    else:
                        print('field exist, value did not match')    
                else:
                    print('query field did not exist')
    return files_paths    
    
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
    query_v = []
    for i in df:
        query_v.append(str(dicom_tag[i].value).lower())  
    if query_v == list_value: 
       out = True
    else:
       out = False
    return out   


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