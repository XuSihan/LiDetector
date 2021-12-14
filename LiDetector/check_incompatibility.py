# -*- coding:utf-8 -*-
'''
检查项目许可证的兼容性
'''
import os
import re
import pandas as pd
import numpy as np

import config
import checkIncom_functions as myFunctions

rootDir = os.path.dirname(__file__) + "/"

DIR = rootDir + '/output/pros/'
outputDir000 = rootDir + 'output/'
modelOutputCsv = rootDir + '/model/DetermAtti/predict.csv'
modelOutputIndex = rootDir + '/model/DetermAtti/checked-repos-list___.txt'



modelOutput_pro_indexs = {}
def split_modelOutputIndex():
    with open(modelOutputIndex, 'r', encoding="utf-8")as fr:
        for line in fr.readlines():
            if line.strip():
                idnStr = line.strip()
                pro = '__'.join(idnStr.split('__')[0:2])
                idn = idnStr.split('__')[2][:-4]
                if pro in modelOutput_pro_indexs.keys():
                    modelOutput_pro_indexs[pro].append(idn)
                else:
                    modelOutput_pro_indexs[pro] = []
                    modelOutput_pro_indexs[pro].append(idn)
    print("modelOutput_pro_indexs.keys() : "+str(len(modelOutput_pro_indexs.keys())))
    return


def check_incmp():


    tldr_212_details = pd.read_csv(os.path.join(rootDir, 'label-212.csv'))
    print(type(tldr_212_details[config.config['term_list'][5]][5]))

    modelOutput_details = pd.read_csv(modelOutputCsv)
    print(type(modelOutput_details))
    print(modelOutput_details.shape)

    fileNameList = []
    with open(modelOutputIndex, 'r', encoding='utf-8')as fr:
        for line in fr.readlines():
            if line.strip():
                file = line.strip()
                fileNameList.append(file)
    print("fileNameList : "+str(len(fileNameList)))

    #

    TermListSize = 23

    numm = 0
    summ = 0

    myFunctions.init()


    for pro in os.listdir(DIR):

        # every pro
        print(pro + "............................")

        # ref
        ref_212check = []
        with open(os.path.join(DIR, pro, "importedPackagesList-licenses.txt"), 'r', encoding="utf-8")as fr:
            for line in fr.readlines():
                if line.strip():
                    ref_212check.append(line.strip())
        print("ref_212check : "+str(len(ref_212check)))
        # dec, inline
        dec_indexs = []
        project_license_idn = "project-license-0"
        proLicenText = ""
        if pro in modelOutput_pro_indexs.keys():
            for idn in modelOutput_pro_indexs[pro]:
                if idn.startswith("declared-license-") or idn.startswith("inline2-license-"):
                    itsIdn = pro + "__" + idn + ".txt"
                    # print(list(modelOutput_details.loc[fileNameList.index(itsIdn)]))
                    if sum(list(modelOutput_details.loc[fileNameList.index(itsIdn)])[1:]) > 0:
                        dec_indexs.append(idn)

                    text = ""
                    with open(os.path.join(DIR, pro, idn + ".txt"), 'r', encoding='utf-8') as fr:
                        for line in fr.readlines():
                            if line.strip():
                                text += line.strip() + ' '

                else:
                    project_license_idn += '_'+idn[len("project-license-"):]

                    with open(os.path.join(DIR, pro, idn + ".txt"), 'r', encoding='utf-8') as fr:
                        for line in fr.readlines():
                            if line.strip():
                                proLicenText += line.strip() + ' '

        print("dec_indexs : " + str(len(dec_indexs)))

        # shape
        licensesIndexList = []
        licensesIndexList.extend(ref_212check)
        licensesIndexList.extend(dec_indexs)
        licensesIndexList.append(project_license_idn)
        print("licensesIndexList : " + str(len(licensesIndexList)))

        preArray = np.zeros((len(licensesIndexList), config.config['termList_size']))

        # merge
        for i in range(len(ref_212check)):
            itsL = licensesIndexList[i]
            for j in range(23):
                val = tldr_212_details[config.config['term_list'][j]][int(itsL)]
                preArray[i][j] = val

        for i in range(len(dec_indexs)):
            itsIdn = pro+"__"+dec_indexs[i]+".txt"
            for j in range(23):
                val = modelOutput_details.loc[fileNameList.index(itsIdn), config.config['term_list'][j]] ###
                preArray[i+len(ref_212check)][j] = val

        if len(project_license_idn) > len("project-license-0"):
            itsIdn = pro + "__" + "project-license-1.txt"
            for j in range(23):
                val = modelOutput_details.loc[fileNameList.index(itsIdn), config.config['term_list'][j]]  ###
                preArray[len(licensesIndexList)-1][j] = val

        '''
        
        '''

        # save info
        pre = pd.DataFrame(data=preArray, index=licensesIndexList, columns=config.config['term_list'])
        pre.to_csv(os.path.join(DIR, pro, "incompatibility_preArray_.csv"), sep=',')

        # check
        RES = myFunctions.isConflict_withCondInfo_2(pro, preArray, licensesIndexList, (len(ref_212check),len(dec_indexs)))

        if RES:
            summ += 1
            print(pro+" : 不兼容")

        numm += 1
        print(str(numm) + '/' + str(len(os.listdir(DIR))))

    print(str(summ) + '/' +  str(len(os.listdir(DIR))))

    return




if __name__ == "__main__":


    split_modelOutputIndex()
    check_incmp()
