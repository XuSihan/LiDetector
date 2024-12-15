'''
[许可证条款抽取]の模型训练
'''
from .nermodel.data_utils import CoNLLDataset
from .nermodel.ner_model import NERModel
from .nermodel.config import Config


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
    model.build() ##### 从这里开始
    # model.restore_session("results/crf/model.weights/") # optional, restore weights
    # model.reinitialize_weights("proj")

    # create datasets
    print(config.filename_train)
    print(config.filename_dev)
    dev   = CoNLLDataset(config.filename_dev, config.processing_word,
                         config.processing_tag, config.max_iter)
    train = CoNLLDataset(config.filename_train, config.processing_word,
                         config.processing_tag, config.max_iter)

    # train model
    model.train(train, dev)

if __name__ == "__main__":
    main()
