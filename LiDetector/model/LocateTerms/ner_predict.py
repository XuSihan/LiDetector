'''
[许可证条款抽取]の测试数据の正式预测
'''
from model.data_utils import CoNLLDataset
from model.ner_model import NERModel
from model.config import Config
import numpy as np
import os



def printPred(config, model):
    print("---------------------------------")

    print(config.filename_dir_test)
    print(config.filename_dir_pre)
    if not os.path.exists(config.filename_dir_pre):
        os.makedirs(config.filename_dir_pre)

    for root, dirs, files in os.walk(config.filename_dir_test):
        for file in files:
            print(file)
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

            fw.close()

####################################################


def main():

    '''

    :return:
    '''
    config = Config()

    # build model
    model = NERModel(config)
    model.build()
    model.restore_session(config.dir_model)

    # 就这里每次都输出文件存储test/的预测结果吧
    printPred(config, model)





if __name__ == "__main__":

    main()
