# -*- coding:utf-8 -*-
'''
输入到/model/data/的数据（进行条款抽取）
'''
import os
import shutil

rootDir = os.path.dirname(__file__) + "/"
DIR = rootDir + '/output/pros/'

outDir = rootDir + '/model/data/'

for pro in os.listdir(DIR):
    for file in os.listdir(os.path.join(DIR, pro)):

        if file.startswith("declared-license-"):
            shutil.copyfile(os.path.join(DIR, pro,file),os.path.join(outDir,pro+"__"+file))
        if file.startswith("inline2-license-"):
            shutil.copyfile(os.path.join(DIR, pro,file),os.path.join(outDir,pro+"__"+file))
        if file.startswith("project-license-"):
            shutil.copyfile(os.path.join(DIR, pro,file),os.path.join(outDir,pro+"__"+file))
