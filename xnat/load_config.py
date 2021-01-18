#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 14:39:54 2020

@author: anpo
"""

import configparser
import os.path 
import xnat_download

config = configparser.ConfigParser()
config.read('xnatconfig.ini')


server_data_root_path = os.path.join(config['default']['url'],'xnat-docker-compose/xnat-data/archive')
url = config['default']['url'] # xnat ip
#usr = config['default']['usr'] # 
#password = config['default']['password']# your password

def load(project_name, usr, password):

    print(usr)
    print(password)
    # create server connection object
    session = xnat_download.connect_xnat(url, usr, password)
    
    # list project, here I assumed querying files based on dicom tag is not cross projects
    #proj_obj = session.projects
    proj_path = os.path.join(server_data_root_path, project_name)
    
    return session, proj_path

