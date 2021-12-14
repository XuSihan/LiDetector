from model.config import Config
from model.data_utils import CoNLLDataset, get_vocabs, UNK, NUM, \
    get_glove_vocab, write_vocab, load_vocab, get_char_vocab, \
    export_trimmed_glove_vectors, get_processing_word


def main():
    """Procedure to build data

    You MUST RUN this procedure. It iterates over the whole dataset (train,
    dev and test) and extract the vocabularies in terms of words, tags, and
    characters. Having built the vocabularies it writes them in a file. The
    writing of vocabulary in a file assigns an id (the line #) to each word.
    It then extract the relevant GloVe vectors and stores them in a np array
    such that the i-th entry corresponds to the i-th word in the vocabulary.


    Args:
        config: (instance of Config) has attributes like hyper-params...

    """
    '''
    !python D:\Python\_LicenseAnalysis\\NER\code\sequence_tagging\\build_data.py --tag23 0
    '''
    '''
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag23", default=None, type=int, required=True,help="0-22 one number")
    args = parser.parse_args()
    # get config and processing of words
    config = Config(load=False, TAG23=args.tag23)
    '''
    config = Config(load=False)
    #config = Config()
    #print("args.tag23: " + str(args.tag23)) # 这个不起作用 不知道为什么


    processing_word = get_processing_word(lowercase=True)

    # Generators
    print(config.filename_train)
    print(config.filename_dev)
    print(config.filename_test)
    dev   = CoNLLDataset(config.filename_dev, processing_word)
    print("dev: "+str(len(dev)))
    test  = CoNLLDataset(config.filename_test, processing_word)
    print("test: " + str(len(test)))
    train = CoNLLDataset(config.filename_train, processing_word)
    print("train: " + str(len(train)))

    # Build Word and Tag vocab
    vocab_words, vocab_tags = get_vocabs([train, dev, test])
    vocab_glove = get_glove_vocab(config.filename_glove)
    print(vocab_tags)

    vocab = vocab_words & vocab_glove
    vocab.add(UNK)
    vocab.add(NUM)

    # Save vocab
    write_vocab(vocab, config.filename_words)
    write_vocab(vocab_tags, config.filename_tags)

    # Trim GloVe Vectors
    vocab = load_vocab(config.filename_words)
    export_trimmed_glove_vectors(vocab, config.filename_glove,
                                config.filename_trimmed, config.dim_word)

    # Build and save char vocab
    train = CoNLLDataset(config.filename_train)
    vocab_chars = get_char_vocab(train)
    write_vocab(vocab_chars, config.filename_chars)


if __name__ == "__main__":
    main()
