# _*_coding:utf-8_*_
'''
一个许可证 = n * 条款
'''

import json
import logging
import os
import re
import pandas as pd
import shutil


from backend.Term import Term
from backend import utils

from backend.model.PreprocessData import cleanData_intoTestDir
from backend.model.LocateTerms import ner_predict
from backend.model.DetermAtti import get_treeAtti
from backend.model.config import config as term_config

DIR = os.path.dirname(__file__)+'/'



class License:
    def __init__(self, name=None, termList=None, text=None, textNeedTE=None, matchedLnameList=None):
        '''
        过程中的被处理形式：期待是termList.
        :param name:
        :param termList:
        :param text:
        '''
        self.name = name
        self.termList = termList # termExtraction
        self.text = text # text. 经过条款提取进入termList

        self.textNeedTE = textNeedTE ##
        self.matchedLnameList = matchedLnameList ##

        self.sentTokens = []
        if self.sentTokens is None:
            self.sentTokens = []

        self.entity_mention_set = None

        if self.termList is None:
            self.termList = []

        # (条款细节抽取的相关)
        self.words = None
        self.labs = None
        self.entities_chunks = None
        self.jj_etChunkInx = None ##
        ##
        self.termRelatedList = None # 来源：extract_termRelated()
        # List[ TermRelated(Object) ]

    def printTermlist(self, base_termlist=None):

        if base_termlist:
            attiList = [term_config['attiType_label'][tt.atti] for tt in base_termlist]
        else:
            attiList = [term_config['attiType_label'][tt.atti] for tt in self.termList]
        return attiList


    def termExtraction(self, ner_model, nlp, ld):
        '''
        由self.text，进行条款提取；self.name当做data文件夹下的文件名
        填充其self.termList

        【这里的所有都只涉及到一个许可证(每次用NER预测一个)（不会被fname一样而影响）】

        【tree里的text一定要去检测CPS，有可能进行条款提取（根据标志位情况），所有ref的都放matchedLnameList去直接找label基础】
        '''

        ## 把matchedLnameList对应的label结果拿过来
        matchedLnameList = list(set(self.matchedLnameList))
        for mathedLiname in matchedLnameList:
            base_termlist = ld.give_termList_from_liname(mathedLiname)
            sentList = ld.give_sentList_from_liname(mathedLiname)
            self.sentTokens.extend(sentList)
            if base_termlist:
                self.setTermList(base_termlist)
                print('base_termlist', mathedLiname, ' '.join([str(k) for k in self.printTermlist(base_termlist=base_termlist)]))

        ''' 进行条款提取 '''
        print('self.textNeedTE:', self.textNeedTE)
        if self.textNeedTE:

            # 预处理
            with open(DIR + 'model/data/' + self.name + '.txt', 'w', encoding="utf-8") as fw:
                fw.write(self.text)
            fw.close()

            # 主体步骤
            cleanData_intoTestDir.main()
            ner_predict.main(model=ner_model)
            self.jj_etChunkInx = get_treeAtti.main(nlp=nlp)

            # 后处理
            modelOutput_details = pd.read_csv(DIR + "model/DetermAtti/predict.csv")  # 默认读第一行数据
            # （按顺序加进去的。）
            for j in range(23):
                content = term_config['term_list'][j]
                attiLabel = modelOutput_details.loc[0, term_config['term_list'][j]]
                atti = term_config['attiLabel_type'][attiLabel]  # 此时的还未set default... （还有很多0在里面）

                tt = Term(content=content, atti=atti)

                if self.existsTerm(content=content): ## 已有base

                    if tt.isMentioned(): # 1/2/3
                        self.updateTerm(tt) # 覆盖上去
                        print('     updateTerm:', tt.content, tt.atti, '【from text：】', self.text)

                else:
                    # 设置缺省认定值 （这里就都设成123 省的兼容性检测时不统一 导致bug）
                    tt.set_absentAtti()
                    ### 更新self.termList
                    self.addTerm(tt)  ###



            # 从NER结果（test-pre/） 得到self的words, labs, entities_chunks
            self.words, self.labs, self.entities_chunks = utils.get_entities(
                os.path.join(DIR + 'model/LocateTerms/data/test-pre/', self.name + '.txt'), clean=False)
            # 从NER结果（test-pre/），得到sentTokens
            sentList = utils.getSentTokens(
                os.path.join(DIR + 'model/LocateTerms/data/test-pre/', self.name + '.txt'), clean=False)
            self.sentTokens.extend(sentList)

            ##
            for d in [
                DIR + 'model/data/',
                DIR + 'model/PreprocessData/dataOOO/',
                DIR + 'model/LocateTerms/data/test/',
                DIR + 'model/LocateTerms/data/test-pre/',
            ]:
                if os.path.exists(d):
                    try:
                        shutil.rmtree(d)
                        os.mkdir(d)
                    except Exception as e:
                        print(e, d)
                        continue
            try:
                os.remove(DIR + "model/DetermAtti/checked-repos-list___.txt")
            except Exception as e:
                print(e, DIR + "model/DetermAtti/checked-repos-list___.txt")
            try:
                os.remove(DIR + "model/DetermAtti/predict.csv")
            except Exception as e:
                print(e, DIR + "model/DetermAtti/predict.csv")



        return




    def getName(self):
        return self.name

    def getTermList(self):
        # return self.termList
        tmp = []
        for tt in self.termList:
            tmp.append(tt.get())
        return tmp

    def setTermList(self, termList):
        self.termList = termList
        return


    def addTerm(self, term):
        self.termList.append(term)
        return

    def updateTerm(self, tt):
        for term in self.termList:
            if term.content == tt.content:
                term.atti = tt.atti
        return

    def existsTerm(self, content):
        for term in self.termList:
            if term.content == content:
                return True
        return False


    def isSatisNeed(self, termList):
        '''
        给定需求，判断此license对象是否满足. 【（准确符合这个需求）】
        （满足给定的条款集合即可，其他多余的条款不管）
        :param termList:
        :return:
        '''
        for tn in termList:
            fg = False
            for term in self.termList:
                if term.content == tn.content and term.atti == tn.atti:
                    fg = True
                    break
            if not fg:
                return False
        return True


    def isSatisNeed_2(self, termlist_need_fromChildren, termlist_need_fromParent):
        '''
        给定需求，判断此license对象是否满足. 【（满足这个范围要求）】
        '''
        for j in range(23):

            if not termlist_need_fromParent:
                if not self.termList[j].isMoreStrict(termlist_need_fromChildren[j]):
                    return False
            else:
                if not (self.termList[j].isMoreStrict(termlist_need_fromChildren[j]) and termlist_need_fromParent[j].isMoreStrict(self.termList[j])):
                    return False

        return True



