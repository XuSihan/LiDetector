# -*- coding:utf-8 -*-
'''
（检查兼容性的具体规则）
'''
import os
import re
import pandas as pd
import numpy as np

import config


######################################################################################################################################################

TermListSize = 23
RightList = []
ObligList = []


def init():
    for i in range(len(config.config['absentAtti'])):  # 0-22
        if config.config['absentAtti'][i] == 2:
            RightList.append(i)
        else:
            ObligList.append(i)
    ObligList.append(-1)
    return


#################################################################################################################################################
# 极性赋予, and, 改变格式
def fuzhi_2(attiList, INFO_details):
    assert len(RightList) == 11 and len(ObligList) == 13

    INFO_details_1 = np.zeros((TermListSize, TermListSize + 2))

    for i in range(TermListSize):
        INFO_details_1[i][i] = attiList[i]  # {0,1,2,3}

    for j in range(len(ObligList) - 1):
        for i in range(len(RightList)):
            if INFO_details.iat[i, j] != 0:
                INFO_details_1[RightList[i]][ObligList[j]] = attiList[ObligList[j]]  #
                INFO_details_1[ObligList[j]][RightList[i]] = attiList[RightList[i]]  #

    return INFO_details_1  # (23,25)


# (整理)
def get_CondWithAttiInfo_2(pro, preArray, licensesIndexList, tuple_num1_num2):
    isHasProL = True
    condInfo212Dir = os.path.join(os.path.dirname(__file__), "condInfo", "condInfo_212")
    condInfotheseDir = os.path.join(os.path.dirname(__file__), "condInfo", "condInfo_these")

    AllInfoList = []

    # load `related` condInfo

    # first part
    for k in range(tuple_num1_num2[0]):
        fileIdn = str(int(licensesIndexList[k]) + 1) + '.csv'
        INFO_details = pd.read_csv(os.path.join(condInfo212Dir, fileIdn))
        # print(INFO_details) # (8,17) 多余第一列
        # print(INFO_details.shape)
        INFO_details_1 = fuzhi_2(preArray[k], INFO_details.iloc[:, 1:])  ##
        # print(INFO_details)
        # print(INFO_details.shape)

        # print(INFO_details.as_matrix())
        # print(INFO_details.as_matrix().shape)
        AllInfoList.append(INFO_details_1)

    # second part
    for k in range(tuple_num1_num2[1]):
        fileIdn = pro + '__' + licensesIndexList[tuple_num1_num2[0] + k] + '.csv'
        INFO_details = pd.read_csv(os.path.join(condInfotheseDir, fileIdn))
        INFO_details_1 = fuzhi_2(preArray[tuple_num1_num2[0] + k], INFO_details.iloc[:, 1:])  ##
        AllInfoList.append(INFO_details_1)

    # third part (project license)
    if len(licensesIndexList[-1]) > len("project-license-0"):
        fileIdn = pro + "__" + "project-license-1.csv"
        INFO_details = pd.read_csv(os.path.join(condInfotheseDir, fileIdn))
        INFO_details_1 = fuzhi_2(preArray[-1], INFO_details.iloc[:, 1:])  ##
        AllInfoList.append(INFO_details_1)
    else:
        fileIdn = pro + "__" + "project-license-0.csv"
        DefaultPre = np.zeros((TermListSize, TermListSize + 2))
        AllInfoList.append(DefaultPre)
        isHasProL = False

    # 提交
    print("AllInfoList : " + str(len(AllInfoList)))
    return np.array(AllInfoList), isHasProL


# 设置absent, and, 情形扩充
def setSelfAbsentValue_andTwoOccasion(AllInfoNP):
    NUM_licenses = AllInfoNP.shape[0]

    AllInfoList = []

    for k in range(NUM_licenses):

        INFO_details = AllInfoNP[k]  # 23*25

        for i in range(TermListSize):

            if INFO_details[i][i] == 0:
                VAL = 0
                if i in RightList:
                    VAL = config.config['absent'][0]
                else:
                    VAL = config.config['absent'][1]
                # 设置absent
                INFO_details[i][i] = VAL
                # 情形扩充
                INFO_details[i][TermListSize] = i
                INFO_details[i][TermListSize + 1] = VAL

            else:
                # 情形扩充
                FG = False

                if INFO_details[i][i] == 1:
                    INFO_details[i][TermListSize] = i
                    INFO_details[i][TermListSize + 1] = 2
                    FG = True

                if not FG:
                    for j in range(TermListSize):
                        if INFO_details[i][j] == 1:  #
                            INFO_details[i][TermListSize] = j
                            INFO_details[i][TermListSize + 1] = 2
                            FG = True
                            break

                '''
                if not FG:
                    INFO_details[i][TermListSize] = i
                    INFO_details[i][TermListSize + 1] = INFO_details[i][i]
                    FG = True

                '''
                if not FG:
                    for j in range(TermListSize):
                        if INFO_details[i][j] == 2:  #
                            INFO_details[i][TermListSize] = j
                            INFO_details[i][TermListSize + 1] = 1
                            FG = True
                            break

                if not FG:
                    for j in range(TermListSize):
                        if INFO_details[i][j] == 3:  #
                            INFO_details[i][TermListSize] = j
                            INFO_details[i][TermListSize + 1] = 2
                            FG = True
                            break

                assert FG == True

            # ()
            for j in range(TermListSize):
                if i != j and INFO_details[i][j] == 0:
                    VAL = 0
                    if j in RightList:
                        VAL = config.config['absent'][0]
                    else:
                        VAL = config.config['absent'][1]
                    # 设置absent
                    INFO_details[i][j] = VAL

        AllInfoList.append(INFO_details)

    return np.array(AllInfoList)


def isCon_PLCL(overall0, component0):
    overall = int(overall0)
    component = int(component0)
    if overall == 1 and (component == 2 or component == 3):
        return True
    elif overall == 2 and (component == 3):
        return True
    elif overall == 3 and (component == 2):
        return True
    return False


def detectIncom_PLCL(AllInfoNP):
    RES = False

    NUM_CL = AllInfoNP.shape[0] - 1
    PL_details = AllInfoNP[-1]  # 23*25
    for k in range(NUM_CL):

        CL_details = AllInfoNP[k]  # 23*25

        TwentyThreeResults = []
        for i in range(TermListSize):

            # 比较PL_details[i]和CL_details[i]
            FourResults = []
            # 1, 串VS串
            FG = "Com"
            for j in range(TermListSize):
                if isCon_PLCL(PL_details[i][j], CL_details[i][j]):
                    FG = "InCom"
            FourResults.append(FG)
            # 2, 串VS反
            FG = "Com"
            TT = int(CL_details[i][TermListSize])
            if isCon_PLCL(PL_details[TT][TT], CL_details[i][TermListSize + 1]):
                FG = "InCom"
            FourResults.append(FG)
            # 3, 反VS串
            FG = "Com"
            TT = int(PL_details[i][TermListSize])
            if isCon_PLCL(PL_details[i][TermListSize + 1], CL_details[TT][TT]):
                FG = "InCom"
            FourResults.append(FG)
            # 4, 反VS反
            FG = "Com"
            if PL_details[i][TermListSize] == CL_details[i][TermListSize]:
                if isCon_PLCL(PL_details[i][TermListSize + 1], CL_details[i][TermListSize + 1]):
                    FG = "InCom"
            else:
                TT = int(CL_details[i][TermListSize])
                if isCon_PLCL(PL_details[TT][TT], CL_details[i][TermListSize + 1]):
                    FG = "InCom"
                '''
                TT = int(PL_details[i][TermListSize])
                if isCon_PLCL(PL_details[i][TermListSize + 1],CL_details[TT][TT]):
                    FG = "InCom"
                '''
            FourResults.append(FG)

            # (现已得到FourResults)
            if FourResults.count("InCom") >= 1:
                # return True  ## .. !
                TwentyThreeResults.append("InCom")
            else:
                TwentyThreeResults.append("Com")

        # (现已得到TwentyThreeResults)
        if TwentyThreeResults.count("InCom") >= 1:
            RES = True

    return RES




def isCompa_CLCL(component10, component20):
    component1 = int(component10)
    component2 = int(component20)
    if component1 == 1 and component2 == 1:
        return True
    if component1 == 2 and component2 == 2:
        return True
    if component1 == 3 and component2 == 3:
        return True
    return False


def detectIncom_CLCL(AllInfoNP):
    RES = False

    NUM_CL = AllInfoNP.shape[0]
    # print("@@@@@@@@@@"+str(NUM_CL))
    for k1 in range(0, NUM_CL - 1):
        for k2 in range(k1 + 1, NUM_CL):

            CL1_details = AllInfoNP[k1]  # 23*25
            CL2_details = AllInfoNP[k2]  # 23*25

            TwentyThreeResults = []
            for i in range(TermListSize):

                # 比较CL1_details[i]和CL2_details[i]
                FourResults = []
                # 1, 串VS串
                FG = "InCom"
                for j in range(TermListSize):
                    if isCompa_CLCL(CL1_details[i][j], CL2_details[i][j]):
                        FG = "Com"
                FourResults.append(FG)
                # 2, 串VS反
                FG = "InCom"
                TT = int(CL2_details[i][TermListSize])
                if isCompa_CLCL(CL1_details[TT][TT],
                                CL2_details[i][TermListSize + 1]):
                    FG = "Com"
                FourResults.append(FG)
                # 3, 反VS串
                FG = "InCom"
                TT = int(CL1_details[i][TermListSize])
                if isCompa_CLCL(CL1_details[i][TermListSize + 1],
                                CL2_details[TT][TT]):
                    FG = "Com"
                FourResults.append(FG)
                # 4, 反VS反
                FG = "InCom"
                if CL1_details[i][TermListSize] == CL2_details[i][TermListSize]:
                    if isCompa_CLCL(CL1_details[i][TermListSize + 1], CL2_details[i][TermListSize + 1]):
                        FG = "Com"
                else:
                    TT = int(CL2_details[i][TermListSize])
                    if isCompa_CLCL(CL1_details[TT][TT],
                                    CL2_details[i][TermListSize + 1]):
                        FG = "Com"
                    '''
                    TT = int(CL1_details[i][TermListSize])
                    if isCompa_CLCL(CL1_details[i][TermListSize + 1],
                                    CL2_details[TT][TT]):
                        FG = "Com"
                    '''
                FourResults.append(FG)

                # (现已得到FourResults)
                if FourResults.count("Com")>=1:
                    TwentyThreeResults.append("Com")
                else:
                    TwentyThreeResults.append("InCom")

            # (现已得到TwentyThreeResults)
            if TwentyThreeResults.count("Com") < 23:
                RES = True

    return RES



def detectIncompatibility__2(AllInfoNP, isHasProL):
    '''

    '''
    if isHasProL:
        return detectIncom_PLCL(AllInfoNP)
    else:
        return detectIncom_CLCL(AllInfoNP[:-1])


def isConflict_withCondInfo_2(pro, preArray, licensesIndexList, tuple_num1_num2):
    AllInfoNP, isHasProL = get_CondWithAttiInfo_2(pro, preArray, licensesIndexList, tuple_num1_num2)
    print("AllInfoNP : ")
    print(AllInfoNP.shape)

    AllInfoNP = setSelfAbsentValue_andTwoOccasion(AllInfoNP)

    RES = detectIncompatibility__2(AllInfoNP, isHasProL)

    return RES




