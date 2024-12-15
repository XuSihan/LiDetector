# -*- coding:utf-8 -*-
'''
[许可证条款抽取model]の测试数据の预处理
'''
import os

ddir = os.path.dirname(os.path.dirname(__file__))

fromDir = ddir+"/data/" # 最初的数据
OOODIR = ddir+"/PreprocessData/dataOOO/" # 简单粗暴OOO
toDir = ddir+"/LocateTerms/data/test/" # 再次清洁，写入模型的预测数据位置
listText = ddir+"/DetermAtti/checked-repos-list___.txt"


#对英文做简单的数据清洗预处理
def cleanText(text):
    punctuation = """.,?!:;(){}[]"""
    text = text.lower().replace('\n', ' ')
    text = text.lower().replace('\t', ' ')
    text = text.replace('<br />', ' ')
    for c in punctuation:
        text = text.replace(c, ' %s ' % c)
    # corpus = [removeStopwords(z) for z in corpus]
    text = text.replace('  ', ' ')
    text = text.replace('  ', ' ')
    text = text.replace('  ', ' ')
    return text

def genOOOtxt():
    #print("---------------------------------")
    if not os.path.exists(OOODIR):
        os.makedirs(OOODIR)
    #print(fromDir)

    flist = open(listText,'w',encoding="utf-8")

    num = 0
    for root , dirs, files in os.walk(fromDir):
        for file in files:
            #print(file)
            flist.write(file+'\n')

            text = ""
            with open(fromDir+file, "r", encoding="utf-8")as fr:
                for line in fr.readlines():
                    if line.strip() != "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&":
                        text += line
            text = cleanText(text)
            fr.close()
            with open(OOODIR+file, "w", encoding="utf-8")as fw:
                for word in text.split(' '):
                    if word.strip():
                        fw.write(word.strip()+' '+"O"+'\n')
            fw.close()
            num += 1
            #print(str(num))

    flist.close()

    return



def cleanWord(word):
    legalCharSet = [
        '%','(',')','[',']','$',':',';','-','_','"','\'','+','@',
        '<','>','/','\\','{','}',',','.','?','!'
    ]
    ww = ""
    for c in word:
        if (c>='a'and c<='z') or c in legalCharSet:
            ww += c
    return ww

def checkFile():
    #print("---------------------------------")
    if not os.path.exists(OOODIR):
        os.makedirs(OOODIR)
    if not os.path.exists(toDir):
        os.makedirs(toDir)

    #print(OOODIR)
    num = 0
    for root, dirs, files in os.walk(OOODIR):
        for file in files:
            textList = []
            #print(file)
            with open(OOODIR + file, "r", encoding="utf-8")as fr:
                for line in fr.readlines():
                    if line.strip() and len(line.strip().split(' ')) == 2:
                        word = cleanWord(line.strip().split(' ')[0])
                        if word:
                            textList.append(word + ' ' + line.strip().split(' ')[1])
                    #else:
                        #print(line.strip())
            fr.close()
            with open(toDir + file, "w", encoding="utf-8")as fw:
                for line in textList:
                    fw.write(line + '\n')
            fw.close()
            num += 1
            #print(str(num))

    return


############################################################################################


def main():
    genOOOtxt()
    checkFile()



