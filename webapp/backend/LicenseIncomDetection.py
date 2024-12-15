# _*_coding:utf-8_*_
'''

许可证问题de具体修复方案

'''

import json
import logging
import os
import re
import pandas as pd
from itertools import product

from treelib import Tree, Node

from backend.model.config import config as term_config
from backend.Term import Term
from backend.License import License
from backend.LicenseDataset import Licensedataset
from backend import utils

rootDir = os.path.dirname(__file__)

class LicenseIncomDetection:
    def __init__(self, licenseTree=None, nid_filepath=None, hasPL=None, nid_textNeedTE=None, nid_matchedLnameList=None, nid_licenseOriginType=None):

        self.licenseTree = licenseTree # 树结构（节点的索引、内容、层次、）
        self.nid_filepath = nid_filepath # dict {nid: str}
        self.nid_textNeedTE = nid_textNeedTE
        self.nid_matchedLnameList = nid_matchedLnameList
        self.nid_licenseOriginType = nid_licenseOriginType

        self.hasPL = hasPL

        self.nid_license = {}  # dict {nid: LicenseObject}


        self.nid_termListFromChildren = {} #（保存一下这个信息）
        self.incomNid_termLists = {} # dict {部分nid: [list[TermObject], list[TermObject]] } # 下界和上界 # 比下界更紧and比上界更松。
        self.incomNid_filepathLists = {}
        # (和上面格式一致，只是对应换成 对应的term的对应极性的filepath。) # 一个atti对应的filepath可能是多个，用|来连接。...好复杂
        # 其实不用放 filepath from parent need。（反正exception的文本中不用涉及父节点。）
        # {nid: list[ dict{atti: str-filepaths} ]} 不用str-filepaths 只写nid即可 （list[nid]）（然后简化成了一个nid）



    def show_licenseTree(self):
        self.licenseTree.show()
        return


    def getShortPath(self,nid,repoName):
        return self.nid_filepath[nid][len(os.path.join(rootDir, 'data', 'repos', repoName)+'/'):]

    def collect_preprocess_results(self, keyList,repoName,):
        '''

        :return:
        '''
        ld = Licensedataset()
        ld.load_licenses_from_csv()

        itemList = []
        for nid in self.licenseTree.expand_tree(mode=Tree.DEPTH, sorting=False):
            if nid == 1:
                continue
            item = {}
            if 'id' in keyList:
                item['id'] = str(nid)
            if 'filepath' in keyList:
                # item['filepath'] = self.nid_filepath[nid]
                item['filepath'] = self.getShortPath(nid,repoName)
            if 'licenseOriginType' in keyList:
                item['licenseOriginType'] = self.nid_licenseOriginType[nid]
            if 'matchedLicenses' in keyList:
                item['matchedLicenses'] = str(self.nid_matchedLnameList[nid])
            if 'text' in keyList:
                if not self.nid_license[nid].text:
                    textaa = ""
                    matchedLnameList = list(set(self.nid_license[nid].matchedLnameList))
                    for mathedLiname in matchedLnameList:
                        textaa += utils.read_text(os.path.join(os.path.join(rootDir,'data', 'licenses', mathedLiname + '.txt')))
                    item['text'] = textaa
                else:
                    item['text'] = self.nid_license[nid].text

            itemList.append(item)
        return itemList


    def collect_termExtraction_results(self):
        '''

        :return:
        '''
        sentList = []
        for nid in self.licenseTree.expand_tree(mode=Tree.DEPTH, sorting=False):
            if nid == 1:
                continue
            sentList.extend(self.nid_license[nid].sentTokens)
        return sentList



    def collect_attiInfer_results(self, keyList):
        '''

        :return:
        '''
        itemList = []
        for nid in self.licenseTree.expand_tree(mode=Tree.DEPTH, sorting=False):
            if nid == 1:
                continue
            item = {}
            if 'id' in keyList:
                item['id'] = str(nid)
            attiList = self.nid_license[nid].printTermlist() # list[int]
            assert len(keyList)==1+23
            for i, key in enumerate(keyList[1:]):
                # item[key] = term_config['attiLabel_type'][attiList[i]]
                item[key] = attiList[i]
            ####
            itemList.append(item)
        return itemList



    def collect_incomReport_results(self, repoName):
        '''

        :return:
        '''
        infoDict = {}

        infoDict['numm'] = str(len(self.nid_filepath))

        infoDict['ispl'] = self.hasPL

        if self.hasPL:
            infoDict['ispl'] = "YES"
        else:
            infoDict['ispl'] = "NO"

        if len(self.incomNid_termLists)>0:
            infoDict['isincom'] ="YES"
        else:
            infoDict['isincom'] = "NO"

        '''
        incom_tt_j_list = []
        if self.hasPL:
            termlist_need_fromChildren = self.incomNid_termLists[2][0]
            termlist_real = self.nid_license[2].termList
            for j, tt in enumerate(termlist_real):
                if tt.atti != termlist_need_fromChildren[j].atti:
                    # incom_tt_j_list.append(j)
                    incom_tt_j_list.append(term_config['term_list'][j])
        else:
            termlist_need_fromChildren = self.incomNid_termLists[-1][0]
            if self.isConflictNeed2(termList=termlist_need_fromChildren):
                conf_tt_j_list = self.getConflictNeed2(termList=termlist_need_fromChildren)
                for j in conf_tt_j_list:
                    incom_tt_j_list.append(term_config['term_list'][j])
        infoDict['incomterms'] = incom_tt_j_list
        '''


        '''
        '''
        reportList = []
        if self.hasPL:
            termlist_PL = self.nid_license[2].termList
            for nid in self.licenseTree.expand_tree(mode=Tree.DEPTH, sorting=False):
                if nid <= 2:
                    continue
                termlist_CLi = self.nid_license[nid].termList
                ##
                tmp_j_list = []
                for j in range(23):
                    if not termlist_PL[j].isMoreStrict(termlist_CLi[j]): ##
                        #tmp_j_list.append(j)
                        tmp_j_list.append(term_config['term_list'][j])
                if tmp_j_list:
                    sent = {}
                    sent['A'] = self.getShortPath(nid=2,repoName=repoName)
                    sent['B'] = self.getShortPath(nid=nid, repoName=repoName)
                    sent['incomterms'] = ', '.join(tmp_j_list)
                    reportList.append(sent)
        else:
            print()
            cids = []
            for nid in self.licenseTree.expand_tree(mode=Tree.DEPTH, sorting=False):
                if nid == 1:
                    continue
                cids.append(nid)
            for d1 in range(0,len(cids)):
                for d2 in range(d1+1, len(cids)):
                    termlist_CL1 = self.nid_license[cids[d1]].termList
                    termlist_CL2 = self.nid_license[cids[d2]].termList
                    ##
                    tmp_j_list = []
                    for j in range(23):
                        if not termlist_CL1[j].isTwoOccurConflict(termlist_CL2[j]): ##
                            # tmp_j_list.append(j)
                            tmp_j_list.append(term_config['term_list'][j])
                    if tmp_j_list:
                        sent = {}
                        sent['A'] = self.getShortPath(nid=cids[d1], repoName=repoName)
                        sent['B'] = self.getShortPath(nid=cids[d2], repoName=repoName)
                        sent['incomterms'] = ', '.join(tmp_j_list)
                        reportList.append(sent)
        infoDict['reportList'] = reportList


        return infoDict




    def turn_into_licenseObjects(self, ner_model, nlp, ld):
        '''
        填充了self.nid_license
        '''
        for nid in self.licenseTree.expand_tree(mode=Tree.DEPTH, sorting=False):
            if nid == 1:
                continue

            print('（条款提取）', nid, '/', len(self.licenseTree.nodes.keys()))

            ntag = self.licenseTree[nid].tag
            nname = self.nid_filepath[nid].split('\\')[-1].replace(':','.')
            ###
            li = License(name=nname,text=ntag, textNeedTE=self.nid_textNeedTE[nid], matchedLnameList=self.nid_matchedLnameList[nid])
            li.termExtraction(ner_model, nlp, ld)
            self.nid_license[nid] = li

        return


    def isConflictNeed2(self, termList):
        '''
        （这个版本是针对于 termList放的是 某条款只放一次 只不过极性冲突的已经用'conflict'来表示了）
        '''
        for tt in termList:
            if tt.isconflict2():
                return True
        return False

    def getConflictNeed2(self, termList):
        conf_tt_j_list = []
        for j, tt in enumerate(termList):
            if tt.isconflict2():
                conf_tt_j_list.append(j)
        return conf_tt_j_list




    def isCompatible_real_for_needs(self, nid, needtermlist):
        '''
        比较两个termlist（一个节点上的，本身VS被需求）

        输入：两个termlist
        输出：是否。

        》》每个term.content上 本身atti 应该比 被需求atti 一样or更加严格。
        '''

        realTermlist = self.nid_license[nid].termList

        '''
        （暂时简化成按顺序直接就term.content已经对应了）
        '''
        #print(nid, [tt.atti for tt in realTermlist], [tt.atti for tt in needtermlist])

        for j in range(23):

            if not realTermlist[j].isMoreStrict(needtermlist[j]):
                #print(j, realTermlist[j].atti, needtermlist[j].atti)
                return False

        return True


    def get_oneNode_needs_from_its_childern(self, termlists_of_cid):
        '''
        得到此节点的低层需求termlist，从其所有子节点的termlist。
        输入：若干个termlist
        输出：一个termlist。

        》》每个term.content上 找其中最严格的那种atti。
        若“最严格们”冲突 则atti='conflict'（下游直接就不兼容了）
        '''
        termlist = []
        attiCidsList = []

        for j in range(23):

            terms_sameCont_diffAtti = []
            corr_cid = []
            for cid in termlists_of_cid.keys():
                termlist_tmp = termlists_of_cid[cid]
                # （这里暂时简化了 原本应该写函数去寻找哪些term的content是一样的）
                # （这里直接按顺序来的 因为当时nid_license就是按顺序放进去的）
                tt = termlist_tmp[j]
                # 设置缺省认定值 （改成最初就都设成123 省的兼容性检测时不统一 导致bug）
                # tt.set_absentAtti()
                terms_sameCont_diffAtti.append(tt)
                corr_cid.append(cid)
            # 找其中最严格的那种atti
            mostStrictOne, atti_cids = terms_sameCont_diffAtti[0].find_mostStrictAtti(terms_sameCont_diffAtti, corr_cid)
            termlist.append(mostStrictOne)
            attiCidsList.append(atti_cids)

        return termlist, attiCidsList


    def upward_get_allNodes_needs_from_childern(self):
        '''
        逐层向上，对于非叶子结点，得到各自的低层需求termlist。

        找非叶子节点，
        按深度排序，
        （保证在计算它时，它的所有子节点已经计算过）
        （遍历其所有子节点的termlist：其中若为叶子则使用其本身termlist/若为非叶子则用其需求termlist。）

        按深度排序then依次计算。《《《《 先这样写。
        or
        写一个递归函数
        '''
        nid_termListFromChildren = {}
        nid_attiCidsListFromChildren = {}

        nids_of_leaves = [nd.identifier for nd in self.licenseTree.leaves()]
        nids_of_not_leaves = set(list(self.licenseTree.nodes.keys())) - set(list([1])) - set(nids_of_leaves) ###
        nid_level = dict(zip(nids_of_not_leaves, [self.licenseTree.level(nid) for nid in nids_of_not_leaves]))
        sorted_nid_level = sorted(nid_level.items(), key=lambda d:d[1], reverse=True)

        for nid, nlevel in sorted_nid_level:
            # 找到所有子节点
            childrenList = self.licenseTree.is_branch(nid)

            termlists_of_cid = {}
            # 找到子节点的termlist（若为叶子则使用其本身termlist/若为非叶子则用其需求termlist）
            for cid in childrenList:
                # 每一个子节点：
                assert cid in nids_of_leaves or cid in nid_termListFromChildren.keys()
                if cid in nids_of_leaves:
                    termlists_of_cid[cid] = self.nid_license[cid].termList
                else:
                    termlists_of_cid[cid] = nid_termListFromChildren[cid]

                ############################
                # if nid in [4,48,51]:


                ###########################


            # 更新nid_termListFromChildren
            termlist_from_children, attiCidsList_from_children = self.get_oneNode_needs_from_its_childern(termlists_of_cid)
            nid_termListFromChildren[nid] = termlist_from_children
            nid_attiCidsListFromChildren[nid] = attiCidsList_from_children

        '''
        （但为了get_PL_needs_from_childern万一从叶子，》》nid_termListFromChildren也放入叶子的本身。）
        '''
        for nid  in nids_of_leaves:
            nid_termListFromChildren[nid] = self.nid_license[nid].termList


        return nid_termListFromChildren, nid_attiCidsListFromChildren


    def get_PL_needs_from_childern(self):
        '''
        在项目不含PL时(self.hasPL=False):
            填充 self.incomNid_termList[-1] 和 incomNid_filepathLists[-1]
        （此时已经计算完了全OSS的层次化兼容性检测，在此基础上，找第一层 for PL）
        '''
        termlists_of_cid = {}
        for nid in self.nid_termListFromChildren.keys():
            if self.licenseTree.level(nid) == 1:
                termlists_of_cid[nid] = self.nid_termListFromChildren[nid]

        termlist_from_children, attiCidsList_from_children = self.get_oneNode_needs_from_its_childern(termlists_of_cid)
        self.incomNid_termLists[-1] = [termlist_from_children, []]
        self.incomNid_filepathLists[-1] = attiCidsList_from_children

        return




    def get_incomNodes_needs_from_parent(self, nid):
        '''
        对那些不兼容的位置，只向上看一层，
        》》其实实际编程时 这个就简单了，父节点最多一个，那“高层需求”基本就是复制父节点的termlist，，，
        '''
        nParid = self.licenseTree.parent(nid).identifier
        termlist_from_parent = self.nid_license[nParid].termList

        return termlist_from_parent


    def detect_incompatibility_hierarchically(self):
        '''
        从最内层向外 汇总当前位置被内层导致的需求 判断当前位置是否发生了不兼容
        （以一个项目即一个子树为单位）

        使用：self.licenseTree，self.nid_license；self.nid_filepath。

        最终结果：【填充self.incomNid_termList】和incomNid_filepathLists。

        1. 逐层向上，得到各自的低层需求termlist。（非叶子结点）（但为了get_PL_needs_from_childern万一从叶子，》》nid_termListFromChildren也放入叶子的本身。）
        2. 比较各自的需求termlist和本身termlist，得到发生不兼容的点。（不兼容and非叶子节点）
        3. 逐层向下只向上看一层，对那些不兼容的位置 根据其高层需求得到各自的高层需求termlist。（“只为了修复时不至于产生新的冲突”）  （不兼容and非叶子结点and非根节点）

        '''
        # 1
        self.nid_termListFromChildren, nid_attiCidsListFromChildren = self.upward_get_allNodes_needs_from_childern()

        # 2
        for nid, needtermlist in self.nid_termListFromChildren.items():
            if not self.isCompatible_real_for_needs(nid, needtermlist):
                self.incomNid_termLists[nid] = [needtermlist] # 添加下界
                self.incomNid_filepathLists[nid] = nid_attiCidsListFromChildren[nid]
        print(self.incomNid_termLists.keys())
        print(self.incomNid_filepathLists)

        # 3
        for icNid in self.incomNid_termLists.keys():
            if self.licenseTree.level(icNid) > 1:
                termlist_from_parent = self.get_incomNodes_needs_from_parent(icNid)
                self.incomNid_termLists[icNid].append(termlist_from_parent) # 添加上界
            else:
                self.incomNid_termLists[icNid].append([])


        return




    def get_incom_and_fixable_places(self):
        '''
        填充self.incomAndFixable_nid，列表
        '''
        incom_nids = self.incomNid_termLists.keys()
        fixable_nids = self.fixable_nid

        self.incomAndFixable_nid = list(set(incom_nids) & set(fixable_nids))
        return





'''模块案例测试'''
def runLicenseIncomDetection(repo, ner_model, nlp, ld,):
    '''
    输入：项目名 （默认其在文件夹./unzips/内）
    输出：修复结果，以及lr的一些属性统计数据，
    调试信息会适当地控制台输出
    '''
    print('repo: ', repo)


    # 生成许可证树
    # import projectLicenseTree
    from backend.projectLicenseTree import get_license_tree
    print('开始构建许可证树……')
    licenseTree, nid_filepath, hasPL, nid_textNeedTE, nid_matchedLnameList, nid_licenseOriginType = get_license_tree(repo=repo)  # nid_filepath 每个叶子结点所对应的文件路径。
    print('hasPL: ', hasPL)
    for key, val in nid_matchedLnameList.items():
        print(key, val)


    lr = LicenseIncomDetection(licenseTree=licenseTree, nid_filepath=nid_filepath, hasPL=hasPL,
                       nid_textNeedTE=nid_textNeedTE, nid_matchedLnameList=nid_matchedLnameList,
                               nid_licenseOriginType=nid_licenseOriginType)
    lr.show_licenseTree()

    # 遍历输出看一下 （确实是DFS的顺序）
    print('关于projectLicenseTree的一些遍历信息：')
    for nid in lr.licenseTree.expand_tree(mode=Tree.DEPTH, sorting=False):
        if nid == 1:
            continue
        # （试用一些个函数）
        ntag = lr.licenseTree[nid].tag
        nidd = lr.licenseTree[nid].identifier
        npath = lr.nid_filepath[nid]
        nlevel = lr.licenseTree.level(nid)  # PL的level=1.
        nparent = lr.licenseTree.parent(nid).identifier
        nchildren = lr.licenseTree.is_branch(nid)
        # print('\t'.join([str(key),val[len('D:\Python\OSSL2//unzips/'):]]))
        print('\t'.join([str(nid), str(nidd), str(nlevel), npath, str(nparent), str(nchildren)]))
    print('所有结点：', lr.licenseTree.nodes.keys())
    print('叶子结点：', [nd.identifier for nd in lr.licenseTree.leaves()])


    # (有可能一个许可证都没有，此时会导致root变成唯一的叶子结点》》最好趁早退出)
    if len(lr.licenseTree.leaves())==1 and lr.licenseTree.leaves()[0].identifier==1:
        return lr, lr.hasPL, 0, 0, 0, []



    # 每个许可证节点，生成对应的license对象
    # 条款提取 （填充self.nid_license）
    print('开始进行条款提取 都对应生成License对象……')
    lr.turn_into_licenseObjects(ner_model, nlp, ld)



    # 层次兼容性检测
    # （找到发生不兼容的位置 及其需求）（填充self.incomNid_termList）
    print('开始进行层次化的兼容性检测……')
    lr.detect_incompatibility_hierarchically()

    if not lr.hasPL:  # 需要计算得到'nid=-1'时的self.incomNid_termLists
        lr.get_PL_needs_from_childern()



    return lr









