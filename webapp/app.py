import os
import json
import shutil
import zipfile
import io, base64


from backend import main
from backend.model.config import config as term_config

from flask import Flask, render_template, request, make_response, jsonify, session
from flask_restful import Resource, Api
from flask_cors import CORS



''' 建立webapp对象 '''
app = Flask(__name__,
            template_folder="./frontend/dist",
            static_folder="./frontend/dist/static")


cors = CORS(app)

app.config['SECRET_KEY'] = os.urandom(24)



# 存放路径
data_slices_root = os.path.join(os.path.dirname(__file__), 'backend', 'data', 'upload_data_slices')
targetDIR_forBackend = os.path.join(os.path.dirname(__file__), 'backend', 'data', 'repos')
saveDIR = os.path.join(os.path.dirname(__file__), 'backend', 'data', 'repos_save')




# （先加载好ner模型）
from backend.model.LocateTerms.nermodel.ner_model import NERModel
from backend.model.LocateTerms.nermodel.config import Config
ner_config = Config()
ner_model = NERModel(ner_config)
ner_model.build()
ner_model.restore_session(ner_config.dir_model)
# （先加载好corenlp）
from stanfordcorenlp import StanfordCoreNLP
nlp = StanfordCoreNLP(os.path.join(os.path.dirname(__file__), 'backend', 'model', 'stanford-corenlp-4.2.0'))
## ld
from backend.LicenseDataset import Licensedataset
ld = Licensedataset()
ld.load_licenses_from_csv()











''' 分发路由 '''

# 主页面
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/upload', methods=["POST"])
def upload():
    upload_file = request.files['file']  ##### 获取data
    task = request.form.get('identifier')  # 获取文件唯一标识符
    filename = '%s' % (task)  ### 构成该分片唯一标识符

    print('上传文件 {} ， 保存在 {}'.format(filename, data_slices_root))
    ### 保存分片
    #upload_file.save('%s/%s' % (data_slices_root, filename))
    with open('%s/%s' % (data_slices_root, filename), 'ab')as fw:
        fw.write(upload_file.read())
    #
    result_text = {"statusCode": 200, "message": "文件上传成功"}
    response = make_response(jsonify(result_text))
    return response



# 解压缩.zip文件
def unzip_file(zip_file_name, destination_path):
    archive = zipfile.ZipFile(zip_file_name, mode='r') ## 可能会遇到报错 not zip file
    for file in archive.namelist():
        archive.extract(file, destination_path) # FileNotFoundError: [Errno 2] No such file or directory

@app.route('/analyze', methods=["POST", "GET"])
def analyze():
    form_reponame = request.json.get("form_reponame")
    print('form_reponame: ', form_reponame)

    # file = os.listdir(data_slices_root)[0] # 后面改...

    form_reponame = form_reponame.replace('.','')

    for file in os.listdir(data_slices_root):

        if '-'.join(file.split('-')[1:])[:-3] != form_reponame:
            continue

        repoName = '-'.join(file.split('-')[1:])[:-3]  # 除去label和zip

        shutil.copy(os.path.join(data_slices_root, file), os.path.join(targetDIR_forBackend, repoName + '.zip'))
        #os.remove(os.path.join(data_slices_root, file))  ####

        if not os.path.exists(os.path.join(targetDIR_forBackend, repoName)):
            os.mkdir(os.path.join(targetDIR_forBackend, repoName))
        unzip_file(zip_file_name=os.path.join(targetDIR_forBackend, repoName + '.zip'),
                   destination_path=os.path.join(targetDIR_forBackend, repoName))





        #
        # result_text = {"statusCode": 200, "message": repoName}
        # response = make_response(jsonify(result_text))
        # response = repoName
        # response = make_response(repoName)
        # return repoName
        res = {"repoName": repoName}
        return jsonify(res)

    res = {"status": "reponame error"}
    return jsonify(res)






def getPreprocessInfos(repoName):
    # lr= main.analyzeOSS(repoName, ner_model, nlp, ld)
    # itemList = lr.collect_preprocess_results(['id', 'filepath', 'licenseOriginType', 'matchedLicenses', 'text'],repoName)

    ####
    lr = main.analyzeOSS(repoName, ner_model, nlp, ld)
    if not os.path.exists(os.path.join(saveDIR, repoName)):
        os.mkdir(os.path.join(saveDIR, repoName))

    itemList = lr.collect_preprocess_results(['id', 'filepath', 'licenseOriginType', 'matchedLicenses', 'text'],
                                             repoName)
    with open(os.path.join(saveDIR, repoName, 'preprocess.json'), 'w', encoding="utf-8") as fw:
        json.dump(itemList, fw)

    sentList = lr.collect_termExtraction_results()
    # 去重
    tmp = []
    for sent in sentList:
        ss = ' '.join([tk['word'] for tk in sent])
        tmp.append(ss)
    tmp = list(set(tmp))
    sentList2 = []
    for s in tmp:
        for sent in sentList:
            ss = ' '.join([tk['word'] for tk in sent])
            if ss == s:
                sentList2.append(sent)
                break
    with open(os.path.join(saveDIR, repoName, 'termExtraction.json'), 'w', encoding="utf-8") as fw:
        json.dump(sentList2, fw)

    term23List = term_config['term_list'][:23]
    keyList = ['id']
    keyList.extend(term23List)
    itemList = lr.collect_attiInfer_results(keyList)
    with open(os.path.join(saveDIR, repoName, 'attiInfer.json'), 'w', encoding="utf-8") as fw:
        json.dump(itemList, fw)

    itemDict = lr.collect_incomReport_results(repoName=repoName)
    itemDict['repoName'] = repoName
    with open(os.path.join(saveDIR, repoName, 'incomReport.json'), 'w', encoding="utf-8") as fw:
        json.dump(itemDict, fw)


    ######
    with open(os.path.join(saveDIR, repoName, 'preprocess.json'), 'r', encoding="utf-8") as fr:
        itemList = json.load(fr)


    # list[dict]
    #print(itemList)
    return itemList


@app.route('/result/preprocess', methods = ["POST", "GET"])
def handlePreprocess():
    repoName = request.json.get("repoName") #
    print('有请求来自preprocess-',repoName)
    res = getPreprocessInfos(repoName)
    return jsonify(res)






def getSentTokens(repoName):

    # lr = main.analyzeOSS(repoName, ner_model, nlp, ld)
    # sentList = lr.collect_termExtraction_results()
    #
    # # 去重
    # tmp = []
    # for sent in sentList:
    #     ss = ' '.join([tk['word'] for tk in sent])
    #     tmp.append(ss)
    #
    # tmp = list(set(tmp))
    #
    # sentList2 = []
    # for s in tmp:
    #
    #     for sent in sentList:
    #         ss = ' '.join([tk['word'] for tk in sent])
    #         if ss==s:
    #             sentList2.append(sent)
    #             break

    ######
    with open(os.path.join(saveDIR, repoName, 'termExtraction.json'), 'r', encoding="utf-8") as fr:
        sentList2 = json.load(fr)

    # list[list[dict]] 直接发送好像有点太复杂了吧
    # for sent in sentList:
    #     print(sent)
    return sentList2

@app.route('/result/termExtraction', methods = ["POST", "GET"])
def handleTermExtraction():
    repoName = request.json.get("repoName") #
    print('有请求来自termExtraction-',repoName)
    res = getSentTokens(repoName)
    return jsonify(res)




def getAttiList(repoName):

    # lr= main.analyzeOSS(repoName, ner_model, nlp, ld)
    # term23List = term_config['term_list'][:23]
    # keyList = ['id']
    # keyList.extend(term23List)
    # itemList = lr.collect_attiInfer_results(keyList)

    ######
    with open(os.path.join(saveDIR, repoName, 'attiInfer.json'), 'r', encoding="utf-8") as fr:
        itemList = json.load(fr)


    # list[dict]
    #print(itemList)
    return itemList


@app.route('/result/attiInference', methods = ["POST", "GET"])
def handleAttiInfer():
    repoName = request.json.get("repoName") #
    print('有请求来自attiInfer-',repoName)
    res = getAttiList(repoName)
    return jsonify(res)






def getIncomDetect(repoName):

    # lr = main.analyzeOSS(repoName, ner_model, nlp, ld)
    # itemDict = lr.collect_incomReport_results(repoName=repoName)
    # itemDict['repoName'] = repoName

    ######
    with open(os.path.join(saveDIR, repoName, 'incomReport.json'), 'r', encoding="utf-8") as fr:
        itemDict = json.load(fr)


    # dict
    # print(itemDict)
    return itemDict

@app.route('/result/incomReport', methods = ["POST", "GET"])
def handleIncomDetect():
    repoName = request.json.get("repoName") #
    print('有请求来自incomReport-',repoName)
    res = getIncomDetect(repoName)
    return jsonify(res)





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

    # （关闭corenlp）
    nlp.close()

