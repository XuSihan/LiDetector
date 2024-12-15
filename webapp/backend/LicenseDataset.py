# _*_coding:utf-8_*_
'''
数据库= n * 许可证
'''

import json
import logging
import os
import re
import pandas as pd
import pickle

from backend.Term import Term
from backend.License import License
from backend import utils




class Licensedataset:
    def __init__(self, licenseList=None):
        self.licenseList = licenseList

        self.licenses = None # dict(name:text). 未经结构化的许可证数据库（原始的若干个许可证文本）
        self.sentBertIdsDataset = None # list的list。 （若干个句子的ids）（各个许可证的句子ids，总体再消重）对应roberta-base的。

        if self.licenseList is None:
            self.licenseList = []

    def printLicenseList(self):
        for ll in self.licenseList:
            print(ll.getName(), ll.getTermList())
        return


    def addLicense(self, license):
        self.licenseList.append(license)
        return


    def load_licenses_from_csv(self):
        '''
        直接读取 已经结构化的许可证 数据库
        :return:
        '''

        df = pd.read_csv(os.path.dirname(__file__)+"/data/tldr-licenses-forSpdx.csv")
        contentList = list(df.columns)[1:]

        for row in df.itertuples():
            # 每行是一个许可证
            license = License(name=row[1])
            for i, atti in enumerate(row[2:]):
                # 某许可证的一个条款with极性

                tt = Term(content=contentList[i], atti=atti)
                # 设置缺省认定值 （这里就都设成123 省的兼容性检测时不统一 导致bug）
                tt.set_absentAtti()
                ### 更新self.termList
                license.addTerm(tt)

            self.addLicense(license)

        return self.licenseList

    def give_termList_from_liname(self, name):
        for li in self.licenseList:
            kk = li.name.split('___')
            for k in kk:
                if k==name:
                    return li.termList
        print('【这个matchedLiName竟然在ld里面找不到对应的】,,,,,', name)
        return []




    def give_sentList_from_liname(self, name):
        for i in range(len(self.licenseList)):
            li = self.licenseList[i]
            kk = li.name.split('___')
            for k in kk:
                if k==name:
                    ###
                    return utils.getSentTokens(
                        os.path.dirname(__file__)+"/data/termEntityTagging/"+str(i+1)+'.txt', clean=False)
        return []




    def read_licenses(self, dataDir):
        '''
        读取原始的若干个许可证文本；
        文本预处理；
        :return:
        '''
        licenses = {}
        for file in os.listdir(dataDir):
            with open(os.path.join(dataDir, file), 'r', encoding="utf-8")as fr:
                text = ' '.join([line.strip() for line in fr.readlines()])
            text = utils.cleanText(text)
            fr.close()
            # print(text)
            licenses[file[:-4]] = text
        self.licenses = licenses
        print('self.licenses', len(self.licenses))
        return self.licenses



    def isNeedSatisfied(self,termList):
        '''
        判断本数据库中 是否存在满足此需求的许可证 【（准确符合这个需求）】
        输出license对象的列表
        :return:
        '''
        abled = []
        for ll in self.licenseList:
            if ll.isSatisNeed(termList):
                abled.append(ll)
        return abled

    def isNeedSatisfied_2(self,termlist_need_fromChildren, termlist_need_fromParent):
        '''
        判断本数据库中 是否存在满足此需求的许可证 【（满足这个范围要求）】
        输出license对象的列表
        :return:
        '''
        abled = []
        for ll in self.licenseList:
            if ll.isSatisNeed_2(termlist_need_fromChildren, termlist_need_fromParent):
                abled.append(ll)
                print(ll.name, ' '.join([str(k) for k in ll.printTermlist()]))
        return abled








'''
ld = Licensedataset()
ld.printLicenseList()

license = License(name="GYL")
license.addTerm(Term(content="Distribute",atti="cannot"))
ld.addLicense(license)
ld.printLicenseList()
'''

'''
ld = Licensedataset()
ld.load_licenses_from_csv()
ld.printLicenseList()
'''






