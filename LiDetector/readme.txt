
运行顺序：

extract_licenseRelated_fromPros.py
collect_files_for_model.py
model\PreprocessData\cleanData_intoTestDir.py
model\LocateTerms\ner_predict.py
model\DetermAtti\get_treeAtti.py
prepare_condInfo.py
check_incompatibility.py

============================

文件：

unzips文件夹：待分析项目源代码
extract_licenseRelated_fromPros：抽取license
output文件夹：抽取出的license相关信息
model文件夹：条款抽取和极性识别
	data：待抽取条款的数据
	PreprocessData：条款抽取前的预处理
	LocateTerms：条款抽取模块
		data：放置训练数据、测试数据等等
		model：NER的主要代码
		results：训练好的条款识别模型
		build_data, train, evaluate：用来训练
		ner_predict：对测试数据进行预测
	DetermAtti：极性识别模块
prepare_condInfo：从条款抽取结果来提取condition关系
condInfo文件夹：提取出的condition相关信息
check_incompatibility：利用条款抽取、极性识别、condition关系提取的结果，检查项目的许可证兼容性
checkIncom_functions：兼容性规则，供check_incompatibility调用

===========================

【注意】：需要另外安装ninka和corenlp工具配合运行。

1、ninka: 
在代码中具体出现在extract_licenseRelated_fromPros.py的101行checkLicenseInline函数，因为ninka需要Linux环境，所以这部分是另外分开运行的，在此函数中再去读取ninka处理结果的文件。
下载地址：https://github.com/dmgerman/ninka
【如果是直接简单测试，可以暂时用checkLicenseInline函数里面的一个替代函数】

2、corenlp (涉及到极性识别) : 
下载地址：https://stanfordnlp.github.io/CoreNLP/
【将其放到文件夹：./model/stanford-corenlp-4.3.2】

