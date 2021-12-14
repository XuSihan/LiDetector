# -*- coding:utf-8 -*-
'''
[许可证条款de极性判别]
（在已经NER条款抽取的基础上）
'''
import re
import pandas as pd
import numpy as np
import config
import os
from nltk.tree import Tree
import re



from stanfordcorenlp import StanfordCoreNLP
nlp = StanfordCoreNLP('../stanford-corenlp-4.3.2')



ALLstc_nodePaths = {}
tooLongStce = []

# 关键词
KWS = [
    [['not','misrepresented','without','notwithstanding','refuse','disallowed','against','delete','decline','declining','prohibited','prohibiting','remove'],
     ['don\'t','no','nothing','free of charge','void','nor','non-sublicenseable']],

    [['must','should'],
     ['as long as','so long as','provided that','ensuring that','ensure that','ask that','have to','shall']]
]
# 词性 (情态动词 介词 副词 动词)
ATTIPOS = ['MD', 'IN','RB','RBR','RBS','VB','VBD','VBG','VBN','VBP','VBZ']



def MultiTreePaths(root):
    def helper(root, path, res):
        if type(root)==str:
            res.append(path +str(root))
            return
        l=len(root)
        for i in range(l):
            if len(root)>=i:
                if root[i]:
                    helper(root[i], path +str(root.label()) +'->', res)
    if root is None:
        return []
    l = []
    helper(root, '', l)
    return l

def putIn():

    for root, dirs, files in os.walk('tmp/'):
        for file in files:
            with open('tmp/'+file, 'r', encoding="utf-8")as fr:
                sqc = ""
                tmp = []
                i = 0
                for line in fr.readlines():
                    i += 1
                    if i == 1:
                        sqc += line.strip()
                    elif line.strip():
                        tmp.append(line.strip())
                if tmp:
                    ALLstc_nodePaths[sqc] = tmp
    print('ALLstc_nodePaths:'+str(len(ALLstc_nodePaths)))
    return


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

def innerHave(entity):
    for per in KWS:
        for ty in per:
            for kw in ty:
                if re.findall(kw, entity, flags=re.IGNORECASE):
                    return True
    return False

def getInnerHave(entity):
    attilist = []
    for per in KWS:
        for ty in per:
            for kw in ty:
                if re.findall(kw, entity, flags=re.IGNORECASE):
                    attilist.append(kw)
    return attilist


def getAttiWords(kId, sqc):

    if sqc in ALLstc_nodePaths:
        allPaths0 = ALLstc_nodePaths[sqc]
    else:
        try:
            zhi = nlp.parse(sqc)
        except Exception:
            '''
            with open('tooLongStce.txt','a',encoding="utf-8")as fw:
                fw.write(sqc+'\n')
            print("！！！！！！！！！！！")
            print(sqc)
            '''
            return []
        tree = Tree.fromstring(zhi)
        allPaths0 = MultiTreePaths(tree)  # 每个叶子结点的全路径
        ALLstc_nodePaths[sqc] = allPaths0
        #
        with open('tmp/'+str(len(ALLstc_nodePaths))+'.txt', 'w', encoding="utf-8")as fw:
            fw.write(sqc+'\n\n')
            for path in allPaths0:
                fw.write(path+'\n')

    attiList = []

    allPath = []

    for path in allPaths0:
        allPath.append(path.split('->'))

    try:
        obj = allPath[kId] ###
    except Exception:
        '''
        print(sqc)
        print(kId)
        print(str(len(allPath)))
        print(str(len(ALLstc_nodePaths)))
        print("***********************************************************")
        '''
        print()
        # 发现了 出现这个问题：句子too长，parse只会给出前面句子的语法树

    try:
        for path in allPath:
            ST = 1
            i = 0
            while i < len(path):
                if ST == 1:
                    if path[i] != obj[i]:
                        ST = 2
                        i -= 1
                elif ST == 2:
                    if i < len(path) - 1:
                        if not path[i] in ATTIPOS:
                            break
                    else:
                        attiList.append(path[i])
                i += 1
    except Exception:
        print()

    return attiList


def getItsSequence(words, entity_chunk):
    SSList = ['.','!','?']
    beginIdx, endIdx = entity_chunk[1], entity_chunk[2] - 2
    for i in range(entity_chunk[1] - 1, -1, -1):  # backward ...
        beginIdx -= 1
        if words[beginIdx] in SSList:
            break
    for i in range(entity_chunk[2] - 1, len(words), 1):  # forward ...
        endIdx += 1
        if words[endIdx] in SSList:
            break
    return beginIdx,' '.join(words[beginIdx:endIdx])


def getOuterHave(words, entity_chunk):
    # 找到此实体所在的句子
    idx, sqc = getItsSequence(words, entity_chunk)
    # 去找语法谓词列表
    attilist = getAttiWords(idx, sqc.upper())

    for per in KWS:
        for grp in per[1]:
            if re.findall(grp, sqc, flags=re.IGNORECASE):
                attilist.append(grp)

    return attilist


### 判断2/3/1
def getAtti(attilist):

    NEGwords = KWS[0][0] + KWS[0][1]
    MUSTwords = KWS[1][0] + KWS[1][1]

    V = 1
    for w in attilist:
        if w.lower() in NEGwords:
            V *= -1

    if V == -1:
        return 2 # cannot
    else:
        for w in attilist:
            if w.lower() in MUSTwords:
                return 3 # must
        return 1 # can


#############################################################
#############################################################
def main():

    putIn()

    testDataDir = "..\\LocateTerms\\data\\test-pre\\"

    fileNameList = []
    # 按checked-repos-list.txt的顺序来（csv亦然）
    with open(r"checked-repos-list___.txt", 'r', encoding='utf-8')as fr:
        for line in fr.readlines():
            if line.strip():
                file = line.strip()
                fileNameList.append(file)

    preArray = np.zeros((len(fileNameList), config.config['termList_size']))

    sum1 = 0
    for file in fileNameList:
        print("--------------------------" + file)
        i = fileNameList.index(file)
        # 找到所有实体
        words, labs, entities_chunks = get_entities(testDataDir + file)
        for entity_chunk in entities_chunks:
            ###############
            # 考察每一个实体
            j = int(entity_chunk[0])
            attilist = []
            entity_text = ' '.join(words[entity_chunk[1]:entity_chunk[2]])
            # 实体内部含有任何极性词
            if innerHave(entity_text):
                attilist = getInnerHave(entity_text)  # 极性词列表
            # 去找实体外部
            else:
                attilist = getOuterHave(words, entity_chunk)  # 谓词列表
            # 得到这个实体所映射的条款极性
            # print(attilist)
            if preArray[i][j] == 0:
                if attilist:
                    preArray[i][j] = getAtti(attilist)
                else:
                    preArray[i][j] = 1
        sum1 += 1
        print(str(sum1) + '/' + str(len(fileNameList)))



    ### 保存结果
    pre = pd.DataFrame(data=preArray, index=fileNameList,columns=config.config['term_list'])
    pre.to_csv("..\\DetermAtti\\predict.csv", sep=',')




if __name__ == "__main__":

    main()






