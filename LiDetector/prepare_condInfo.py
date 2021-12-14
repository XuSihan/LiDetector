# -*- coding:utf-8 -*-
'''
抽取条款之间condition关系
（在已经NER条款抽取的基础上）
'''
import re
import pandas as pd
import numpy as np
import config
import os

rootDir = os.path.dirname(__file__)




def get_chunks2(labs):
    # 得到实体列表 [('X',3,4), (), () ...]
    TMP = []
    tmp = []
    for i in range(len(labs)):
        la = labs[i]
        if la.split('-')[0]=='B' or la.split('-')[0]=='I':
            if i==0 or labs[i-1]=='O' or labs[i-1].split('-')[1] != la.split('-')[1]:
                tmp.append(la.split('-')[1])
                tmp.append(i)
                tmp.append(i + 1)
            else:
                tmp[2] += 1
            if i==len(labs)-1 or labs[i+1]=='O' or labs[i+1].split('-')[1] != la.split('-')[1]:
                tmp2 = tuple(tmp)
                TMP.append(tmp2)
                tmp.clear()
    return TMP

def get_entities(filename):
    words = []
    labs = []
    with open(filename, 'r', encoding="utf-8")as fr:
        for line in fr.readlines():
            if line.strip():
                line = line.strip()
                words.append(line.split(' ')[0])
                labs.append(line.split(' ')[1])
    entities_chunks = get_chunks2(labs)

    return words, labs, entities_chunks


def getItsSequence(words, entity_chunk):
    SSList = ['.', '!', '?']
    beginIdx, endIdx = entity_chunk[1], entity_chunk[2]-2
    for i in range(entity_chunk[1]-1, -1, -1): # backward ...
        beginIdx -= 1
        if words[beginIdx] in SSList:
            break
    for i in range(entity_chunk[2]-1, len(words), 1): # forward ...
        endIdx += 1
        if words[endIdx] in SSList:
            break
    return (beginIdx, endIdx)




#############################################################

def getCondInfo_inOneLicense(testDataDir, file, outputDir):
    NUM_Right = config.config['absentAtti'].count(2)
    NUM_Oblig = config.config['absentAtti'].count(1) + 1
    RightList = []
    ObligList = []
    MergeList = [0]*23 # 0~22 : 在8和15中的idx
    for i in range(len(config.config['absentAtti'])): # 0-22
        if config.config['absentAtti'][i] == 2:
            RightList.append(i)
            MergeList[i] = len(RightList)-1
        else:
            ObligList.append(i)
            MergeList[i] = len(ObligList) - 1
    ObligList.append(-1)
    assert len(RightList)==NUM_Right and len(ObligList)==NUM_Oblig

    ###
    preArray = np.zeros( (NUM_Right, NUM_Oblig) )

    #### 找condition关系

    # 所有实体
    words, labs, entities_chunks = get_entities(os.path.join(testDataDir, file))

    # 每个实体,先分个类,
    RightEntityList = []
    RightEntityInSentList = []
    ObligEntityList = []
    ObligEntityInSentList = []
    for entity_chunk in entities_chunks:
        j = int(entity_chunk[0]) # j: 0-22
        if j in RightList:
            RightEntityList.append(entity_chunk)
            RightEntityInSentList.append(getItsSequence(words, entity_chunk))
        else:
            ObligEntityList.append(entity_chunk)
            ObligEntityInSentList.append(getItsSequence(words, entity_chunk))

    #找关系
    isAmongL1 = [0]*len(RightEntityList)
    isAmongL2 = [0]*len(ObligEntityList)

    for m in range(len(RightEntityList)):

        for n in range(len(ObligEntityList)):
            if RightEntityInSentList[m] == ObligEntityInSentList[n]:
                thisSent = ' '.join(words[RightEntityInSentList[m][0]:RightEntityInSentList[m][1]+1])
                thisSent = thisSent.lower()
                if thisSent.find("provided that ") > -1 or thisSent.find(" condition ") > -1 or thisSent.find(" conditions ") > -1 or thisSent.find("if ") > -1 or thisSent.find("when ") > -1:
                    ##
                    preArray[MergeList[int(RightEntityList[m][0])]][MergeList[int(ObligEntityList[n][0])]] = 1
                    isAmongL1[m] = 1
                    isAmongL2[n] = 1
                    preArray[MergeList[int(RightEntityList[m][0])]][NUM_Oblig-1] = 1

    for m in range(len(RightEntityList)):
        if isAmongL1[m] == 0:
            preArray[MergeList[int(RightEntityList[m][0])]][NUM_Oblig - 1] = 1
            '''
            for n in range(len(ObligEntityList)):
                if isAmongL2[n] == 0:
                    ##
                    preArray[MergeList[int(RightEntityList[m][0])]][MergeList[int(ObligEntityList[n][0])]] = 1
            '''

    ### 保存结果
    pre = pd.DataFrame(data=preArray, index=RightList, columns=ObligList)
    pre.to_csv(os.path.join(outputDir, file[:-4]+".csv"), sep=',')

    return


def main():


    testDataDir = os.path.join(rootDir, "model", "LocateTerms", "data", "test-pre")
    outputDir = os.path.join(os.path.dirname(__file__), "condInfo", "condInfo_these")

    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    fileNameList = []
    with open(os.path.join(rootDir, "model", "DetermAtti", "checked-repos-list___.txt"), 'r', encoding='utf-8')as fr:
        for line in fr.readlines():
            if line.strip():
                file = line.strip()
                fileNameList.append(file)

    sum1 = 0
    for file in fileNameList:
        print("--------------------------" + file)
        i = fileNameList.index(file)

        getCondInfo_inOneLicense(testDataDir, file, outputDir)

        sum1 += 1
        print(str(sum1) + '/' + str(len(fileNameList)))









if __name__ == "__main__":


    main()




