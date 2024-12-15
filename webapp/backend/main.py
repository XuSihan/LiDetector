#coding=utf-8
import os
import gc
from backend import LicenseIncomDetection, utils

def analyzeOSS(repo, ner_model, nlp, ld):
    # # （先加载好ner模型）
    # from backend.model.LocateTerms.nermodel.ner_model import NERModel
    # from backend.model.LocateTerms.nermodel.config import Config
    # ner_config = Config()
    # ner_model = NERModel(ner_config)
    # ner_model.build()
    # ner_model.restore_session(ner_config.dir_model)
    # # （先加载好corenlp）
    # from stanfordcorenlp import StanfordCoreNLP
    # nlp = StanfordCoreNLP(os.path.join(os.path.dirname(__file__), 'model', 'stanford-corenlp-4.2.0'))
    # ## ld
    # from backend.LicenseDataset import Licensedataset
    # ld = Licensedataset()
    # ld.load_licenses_from_csv()

    '''
    执行主函数 对OSS数据集进行扫描检测、建模、兼容性分析。
    '''

    # repo = 'christabor___flask_jsondash'

    lr = LicenseIncomDetection.runLicenseIncomDetection(repo, ner_model, nlp, ld)
    ''' （可以获取lr的各种属性） '''

    # # （关闭corenlp）
    # nlp.close()

    return lr
