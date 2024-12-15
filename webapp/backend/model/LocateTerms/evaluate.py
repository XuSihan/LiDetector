'''
[许可证条款抽取]の训练时的评测
'''
from .nermodel.data_utils import CoNLLDataset
from .nermodel.ner_model import NERModel
from .nermodel.config import Config
import numpy as np
import os


def align_data(data):
    """Given dict with lists, creates aligned strings

    Adapted from Assignment 3 of CS224N

    Args:
        data: (dict) data["x"] = ["I", "love", "you"]
              (dict) data["y"] = ["O", "O", "O"]

    Returns:
        data_aligned: (dict) data_align["x"] = "I love you"
                           data_align["y"] = "O O    O  "

    """
    spacings = [max([len(seq[i]) for seq in data.values()])
                for i in range(len(data[list(data.keys())[0]]))]
    data_aligned = dict()

    # for each entry, create aligned string
    for key, seq in data.items():
        str_aligned = ""
        for token, spacing in zip(seq, spacings):
            str_aligned += token + " " * (spacing - len(token) + 1)

        data_aligned[key] = str_aligned

    return data_aligned



def interactive_shell(model):
    """Creates interactive shell to play with model

    Args:
        model: instance of NERModel

    """
    model.logger.info("""
This is an interactive mode.
To exit, enter 'exit'.
You can enter a sentence like
input> I love Paris""")

    while True:
        try:
            # for python 2
            sentence = raw_input("input> ")
        except NameError:
            # for python 3
            sentence = input("input> ")

        words_raw = sentence.strip().split(" ")

        if words_raw == ["exit"]:
            break

        #####
        preds = model.predict(words_raw)
        to_print = align_data({"input": words_raw, "output": preds})

        for key, seq in to_print.items():
            model.logger.info(seq)


#########################################################################
def printPred(config, model):

    print(config.filename_dir_test)
    print(config.filename_dir_pre)
    if not os.path.exists(config.filename_dir_pre):
        os.makedirs(config.filename_dir_pre)

    print("phase 1 - LicenseTerm predict --------------------------------------- ")

    kk = 0
    for root, dirs, files in os.walk(config.filename_dir_test):
        for file in files:
            kk += 1
            print(str(kk)+'/80 : '+file)
            fw = open(config.filename_dir_pre+file, 'w', encoding="utf-8")

            tmp = []
            with open(config.filename_dir_test+file, 'r', encoding="utf-8")as fr:
                for line in fr.readlines():
                    word = line.strip().split(' ')[0]
                    if word == '.':
                        tmp.append(word)
                        words_raw = tmp
                        ##
                        preds = model.predict(words_raw)
                        for wd, pre in zip(words_raw, preds):
                            fw.write(wd + ' ' + pre + '\n')

                        tmp.clear()
                    else:
                        tmp.append(word)
            fr.close()

            fw.close()


def get_chunks2(labs):
    '''
    :param labs: [O,O,O,O,B-X,I-X,I-X,O,O,O...]
    :return:
    [tag,start,end]  左闭右开
    [["X", 0, 2], ["Y", 3, 4]...]

    '''
    TMP = []
    tmp0 = ()
    tmp = []
    for i in range(len(labs)):
        la = labs[i]
        '''
        if la.startswith("B-"):
            tmp.append(la.split('-')[1])
            tmp.append(i)
            tmp.append(i+1)
        if la.startswith("I-"):
            tmp[2] += 1
            if labs[i+1] == 'O':
                TMP.append(tmp)
                tmp.clear()
        '''
        if la.split('-')[0]=='B' or la.split('-')[0]=='I':
            if i==0 or labs[i-1]=='O' or labs[i-1].split('-')[1] != la.split('-')[1]:
                tmp.append(la.split('-')[1])
                tmp.append(i)
                tmp.append(i + 1)
                # print("--------")
                # print(str(i))
                # print(tmp)
            else:
                tmp[2] += 1
            if i==len(labs)-1 or labs[i+1]=='O' or labs[i+1].split('-')[1] != la.split('-')[1]:
                tmp2 = tuple(tmp)
                TMP.append(tmp2)
                # print(str(i))
                # print(tmp2)
                # print("--------")
                tmp.clear()

    return TMP

def get_interactSet(labs1, labs2):
    interList = []
    for la1 in labs1:
        fg = False
        for la2 in labs2:
            if la1[0]==la2[0]:
                for i in range(la1[1],la1[2]):
                    if i>=la2[1] and i<la2[2]:
                        interList.append(la1)
                        fg = True
                        break
            if fg:
                break
    return interList


# 评测
def evaluate2(config):

    print("--------------------------------------- ")

    accs = []
    correct_preds, total_correct, total_preds = 0., 0., 0.

    for root, dirs, files in os.walk(config.filename_dir_test):
        for file in files:
            print(file)
            # （把一篇文本看做一个大的句子）
            words = []
            labs = []
            lab_preds = []
            with open(config.filename_dir_test+file, 'r', encoding="utf-8")as fr:
                for line in fr.readlines():
                    if line.strip():
                        words.append(line.strip().split(' ')[0])
                        labs.append(line.strip().split(' ')[1])
            fr.close()
            with open(config.filename_dir_pre+file, 'r', encoding="utf-8")as fr:
                for line in fr.readlines():
                    if line.strip():
                        lab_preds.append(line.strip().split(' ')[1])
            fr.close()
            # 基于标签de
            accs += [a == b for (a, b) in zip(labs, lab_preds)]
            # 基于实体de
            lab_chunks = set(get_chunks2(labs))
            lab_pred_chunks = set(get_chunks2(lab_preds))
            correct_preds += len(get_interactSet(lab_pred_chunks, lab_chunks))
            total_preds += len(lab_pred_chunks)
            total_correct += len(lab_chunks)

    p = correct_preds / total_preds if correct_preds > 0 else 0
    r = correct_preds / total_correct if correct_preds > 0 else 0
    f1 = 2 * p * r / (p + r) if correct_preds > 0 else 0
    acc = np.mean(accs)

    '''
    
    '''
    print("correct_preds: " + str(correct_preds))
    print("total_correct: " + str(total_correct))
    print("total_preds: " + str(total_preds))

    return {"acc": 100 * acc, "p": 100 * p, "r": 100 * r, "f1": 100 * f1}




####################################################


def main():

    '''

    :return:
    '''
    '''
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag23", default=None, type=int, required=True, help="0-22 one number")
    args = parser.parse_args()
    # create instance of config
    config = Config(TAG23=args.tag23)
    '''
    config = Config()

    # build model
    model = NERModel(config)
    model.build()
    model.restore_session(config.dir_model)

    ##### 在text上做评测
    '''
    
    '''
    test = CoNLLDataset(config.filename_test, config.processing_word, config.processing_tag, config.max_iter)
    model.evaluate(test)

    #####交互模式： 循环输入句子 输出预测
    # interactive_shell(model)


    # 就这里每次都输出给文件：存储预测结果吧
    # printPred(config, model) ###################

    '''
    # 用test文件和pre文件来评测
    metrics = evaluate2(config)
    msg = " - ".join(["{} {:04.2f}".format(k, v)
                      for k, v in metrics.items()])
    '''

    # print("phase 1 - LicenseTerm predict ----- FINISH ! ")
    #print(msg)


if __name__ == "__main__":

    main()

    # 测试
    '''
    TMP = get_chunks2([ 'O', 'O', 'O', 'O', 'O', 'B-3', 'I-3', 'I-3', 'O', 'O', 'I-5', 'B-11', 'I-11', 'I-22'])
    print(TMP)
    for tmp in TMP:
        print(tmp)
    TMP2 = get_chunks2(['O', 'O', 'O', 'O', 'B-3', 'B-3', 'O', 'O', 'O', 'I-5', 'I-5', 'I-5', 'O', 'I-11'])
    print(TMP2)
    for tmp in TMP2:
        print(tmp)
    TMP3 = get_interactSet(set(TMP),set(TMP2))
    print(TMP3)
    print(str(len(TMP3)))
    '''

