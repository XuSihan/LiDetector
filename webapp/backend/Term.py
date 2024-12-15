# _*_coding:utf-8_*_
import json
import logging
import os
import re
from itertools import product

from backend.model.config import config as term_config

'''
一个条款 = 内容 + 极性
(内容是按23列表来固定的)
'''
class Term:
    def __init__(self, content=None, atti=None):
        self.content = content
        self.atti = atti

    def get(self):
        return self.content, self.atti

    def getAtti(self):
        return self.atti

    def set(self, content=None, atti=None):
        if content:
            self.content = content
        if atti:
            self.atti = atti
        return

    def set_absentAtti(self):
        '''
        权利cannot，义务can
        无返回值。直接修改自己。
        '''
        if self.atti==term_config['attiLabel_type'][0]:

            termId = term_config['term_list'].index(self.content)
            attiLabel = term_config['absentAtti'][termId]
            absentAtti = term_config['attiLabel_type'][attiLabel]
            self.atti = absentAtti

        return

    def isMentioned(self):
        if self.atti == term_config['attiLabel_type'][0]:
            return False
        return True


    def isconflict(self, termB):
        '''
        是否存在不一致(冲突)
        '''
        if self.content == termB.content and self.atti != termB.atti: # （这个规则，之后再斟酌吧，，）
            return True
        return False

    def isconflict2(self):
        '''
        ###
        :return:
        '''
        if self.atti == term_config['attiLabel_type'][4]:
            return True
        return False


    def isSameContent(self, termB):
        if self.content == termB.content : # （这个规则，之后再修改，，）
            return True
        return False

    def isMoreStrict(self, termB):
        '''
        self比termB 一样or更加严格
        （前置情况：他俩已经都非confilct了，都是1/2/3）
        '''
        if termB.atti == term_config['attiLabel_type'][4]:
            return False

        la1 = term_config['attiType_label'][self.atti]
        la2 = term_config['attiType_label'][termB.atti]
        la3 = term_config['atti_moreStrictTable'][la1 - 1][la2 - 1]
        # print(la1,la2,la3)
        if la3 == la1:
            return True
        else:
            return False

    def isTwoOccurConflict(self, termB):
        '''
        self比termB 冲突（CL和CL的那种）
        （前置情况：都是1/2/3.）
        '''
        la1 = term_config['attiType_label'][self.atti]
        la2 = term_config['attiType_label'][termB.atti]
        la3 = term_config['atti_moreStrictTable'][la1 - 1][la2 - 1]
        # print(la1,la2,la3)
        if la3 == 4:
            return True
        else:
            return False





    def find_mostStrictAtti(self, termList, corr_cid):
        '''
        找其中最严格的那种atti（不用管self，self是其中的一个。。。）
        (若“最严格们”冲突 则atti='conflict')

        输出： 这个term with mostStrictAtti
        '''
        assert len(set([tt.content for tt in termList]))==1

        mostStrictOne = Term(content=self.content)
        attis = list(set([tt.atti for tt in termList])) #####
        atti_cids = {} # {str:int}

        moreStrictAtti = attis[0]
        if len(attis)>1:

            for at in attis[1:]:
                la1 = term_config['attiType_label'][moreStrictAtti]
                la2 = term_config['attiType_label'][at]
                moreStrictAtti = term_config['attiLabel_type'][term_config['atti_moreStrictTable'][la1 - 1][la2 - 1]]

                if moreStrictAtti == term_config['attiLabel_type'][4]:# 已经出现conflict （各取一个代表file即可）
                    atti_cids[term_config['attiLabel_type'][la1]] = corr_cid[[tt.atti for tt in termList].index(term_config['attiLabel_type'][la1])]
                    atti_cids[term_config['attiLabel_type'][la2]] = corr_cid[[tt.atti for tt in termList].index(term_config['attiLabel_type'][la2])]
                    # break
                else:
                    atti_cids[moreStrictAtti] = corr_cid[[tt.atti for tt in termList].index(moreStrictAtti)]  #（取一个代表file即可）

        # elif len(attis)==1 and moreStrictAtti == term_config['attiLabel_type'][4]:
            # atti_cids[term_config['attiLabel_type'][4]] = corr_cid
        elif len(attis) == 1:
            atti_cids[attis[0]] = corr_cid[0] #（取一个代表file即可）



        mostStrictOne.set(atti=moreStrictAtti)

        return mostStrictOne, atti_cids









'''
term = Term()
term.set("Distribute","cannot")
print(term.get())
'''