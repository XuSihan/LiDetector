# -*- coding:utf-8 -*-
'''

从项目中抽取license相关信息

'''
import re
import os

rootDir = os.path.dirname(__file__) + "/"
unDir = rootDir + '/unzips/'
outputDir000 = rootDir + '/output/'
outputDir = rootDir + '/output/pros/'
DIR = outputDir


checked_repos_list = []
finished_pac_list = []
ex_pac_list = []

def acquire_run_history():

    with open(outputDir000 + "checked_repos_list.txt", 'r', encoding='utf-8')as fr:
        for line in fr.readlines():
            checked_repos_list.append(line.strip())
    print("checked_repos_list : "+str(len(checked_repos_list)))

    with open(outputDir000 + "finished_pac_list.txt", 'r', encoding='utf-8')as fr:
        for line in fr.readlines():
            finished_pac_list.append(line.strip())
    print("finished_pac_list : "+str(len(finished_pac_list)))

    with open(outputDir000 + "ex_pac_list.txt", 'r', encoding='utf-8')as fr:
        for line in fr.readlines():
            ex_pac_list.append(line.strip())
    print("ex_pac_list : "+str(len(ex_pac_list)))

    return


def checkLicenseFile(filename):
    if re.findall(r'^license$', filename, flags=re.IGNORECASE) or re.findall(r'^license\.[a-zA-Z]+', filename, flags=re.IGNORECASE) \
            or re.findall(r'^copying$', filename, flags=re.IGNORECASE) or re.findall(r'^copying\.[a-zA-Z]+', filename, flags=re.IGNORECASE):
        return True
    else:
        return False

def checkPackageImport1(filepath):
    try:
        imports = []
        with open(filepath, 'r', encoding="utf-8") as fr:
            for line in fr.readlines():
                if line.strip() and line.find('==') > -1:
                    imports.append(line.strip().split('==')[0])
        return imports
    except Exception:
        print(filepath)
        return []




REGEXP = [
    re.compile(r'^import (.+)$'),
    re.compile(r'^from ((?!\.+).*?) import (?:.*)$')
]

def checkPackageImport2(filepath):
    try:
        imports = []
        with open(filepath, 'r', encoding="utf-8") as fr:
            for line in fr.readlines():
                if "import " in line:
                    if "from" in line:
                        match = REGEXP[1].match(line.strip())
                        if match:
                            name = match.groups(0)[0]
                            for im in name.partition(' as ')[0].partition(','):
                                nm = im.strip().partition('.')[0].strip()
                                if len(nm) > 1:
                                    imports.append(nm)
                    else:
                        match = REGEXP[0].match(line.strip())
                        if match:
                            name = match.groups(0)[0]
                            for im in name.partition(' as ')[0].partition(','):
                                nm = im.strip().partition('.')[0].strip()
                                if len(nm) > 1:
                                    imports.append(nm)
        return imports
    except Exception:
        print(filepath)
        return []



def checkLicenseInline(filepath):
    '''
    安装ninka（需要在Linux上另外处理）
    使用其Comment extractor， Split sentences， Filter good sentences
    得到inline部分
    '''
    # return "" # 读取ninka对其处理结果文件

    '''
    为了简单测试，可以暂先使用下面的替代函数
    '''
    try:
        targetText = ""
        with open(filepath, 'r', encoding="utf-8") as fr:
            fg = False
            for line in fr.readlines():
                if line.strip().startswith("#"):
                    targetText += line.strip()[1:].strip() + ' '
                elif line.strip().startswith("\'\'\'") or line.strip().startswith("\"\"\""):
                    if not fg:
                        # start ...
                        if line.strip().endswith("\'\'\'", 3, len(line.strip())) or line.strip().endswith("\"\"\"", 3,
                                                                                                          len(
                                                                                                                  line.strip())):
                            targetText += line.strip()[3:-3].strip() + ' '
                        else:
                            targetText += line.strip()[3:].strip() + ' '
                            fg = True
                    else:
                        fg = False
                elif line.strip():
                    if fg:
                        targetText += line.strip() + ' '
                    else:
                        break
        if re.findall('license', targetText, flags=re.IGNORECASE):
            # print(filepath+str(len(targetText)))
            return targetText
        else:
            return ""
    except Exception:
        print(filepath)
        return ""



def checkPro(repo):

    repoDir = unDir + repo.split('/')[0] + "__" + repo.split('/')[1] + '/'
    repoOutputDir = outputDir + repo.split('/')[0] + "__" + repo.split('/')[1] + '/'

    # imported package names >>> importedPackagesList.txt
    # license files and license inline >>> (each into one txt) license-x.txt
    # check and tag ... >>> project-license-x.txt (maybe not exists)

    if not os.path.exists(repoOutputDir):
        os.makedirs(repoOutputDir)

    num_packages = 0
    num_packages000 = 0
    num_files = 0
    num_inline = 0
    num_prolicense = 0


    fileNum = 0
    packages = []

    for root, dirs, files in os.walk(repoDir):
        for file in files:

            if checkLicenseFile(file):
                #
                try:
                    text = ""
                    with open(os.path.join(root, file), 'r', encoding="utf-8")as fr:
                        for line in fr.readlines():
                            if line.strip():
                                text += line.strip() + ' '
                    # print(file+str(len(text)))
                    fileNum += 1
                    with open(os.path.join(repoOutputDir, "declared-license-" + str(fileNum) + ".txt"), 'w', encoding="utf-8")as fw:
                        fw.write(text)
                    num_files += 1
                except Exception:
                    print(file)

            elif re.findall("^requirements.txt$", file, flags=re.IGNORECASE):
                # some imported
                packages.extend(checkPackageImport1(os.path.join(root,file)))

            elif file.endswith(".py"):
                # some imported
                packages.extend(checkPackageImport2(os.path.join(root,file)))
                # license inline
                inline = checkLicenseInline(os.path.join(root,file))
                #print(file+str(len(inline)))
                if inline:
                    fileNum += 1
                    with open(os.path.join(repoOutputDir, "inline-license-" + str(fileNum) + ".txt"), 'w',
                              encoding="utf-8")as fw:
                        fw.write(inline)
                    num_inline += 1


    num_packages000 = len(packages)
    dependency_list = list(set(packages))
    num_packages = len(dependency_list)
    with open(os.path.join(repoOutputDir,"importedPackagesList.txt"), 'w', encoding='utf-8') as fw:
        for pac in dependency_list:
            fw.write(pac+'\n')

    # project-license 在license-x里面也是有的，
    fileNum2 = 0
    if len(os.listdir(repoDir)) == 1:
        masterDir = os.path.join(repoDir,os.listdir(repoDir)[0])
        for file in os.listdir(masterDir):
            if checkLicenseFile(file):
                try:
                    text = ""
                    with open(os.path.join(masterDir, file), 'r', encoding="utf-8")as fr:
                        for line in fr.readlines():
                            if line.strip():
                                text += line.strip() + ' '
                    fileNum2 += 1
                    with open(os.path.join(repoOutputDir, "project-license-" + str(fileNum2) + ".txt"), 'w',
                              encoding="utf-8")as fw:
                        fw.write(text)
                    num_prolicense += 1
                except Exception:
                    print(file)



    return num_packages, num_packages000, num_files, num_inline, num_prolicense




def get_licenses():
    num1 = len(finished_pac_list) + len(ex_pac_list)
    num2 = len(finished_pac_list)

    for repo in checked_repos_list:

        if repo not in finished_pac_list and repo not in ex_pac_list:

            print(repo + " ...")

            num_packages, num_packages000, num_files, num_inline, num_prolicense = checkPro(repo)
            print(str(num_packages) + '\t'+str(num_packages000) + '\t'+ str(num_files) + '\t'+str(num_inline) + '\t'+str(num_prolicense))

            with open(outputDir000 + 'collectNumbers.csv', 'a', encoding="utf-8")as fw:
                fw.write(repo + ',' + str(num_packages) + ','+str(num_packages000) + ','+ str(num_files) + ','+str(num_inline) + ','+str(num_prolicense) + '\n')

            finished_pac_list.append(repo)
            with open(outputDir000 + 'finished_pac_list.txt', 'a', encoding="utf-8")as fw:
                fw.write(repo + '\n')

            num2 += 1
            num1 += 1
            print(str(num1) + '/' + str(len(checked_repos_list)))
            print(str(num2) + '/' + str(len(checked_repos_list)))
            print()

    return







def cleanIt(text):

    text = re.sub('!/usr/bin/env python',' ',text)
    text = re.sub('! /usr/bin/env python', ' ', text)
    text = re.sub('!/usr/bin/python', ' ', text)
    text = re.sub('! /usr/bin/python', ' ', text)
    text = re.sub('-\*- coding: utf-8 -\*-', ' ', text)
    text = re.sub('-\*-coding:utf-8-\*-', ' ', text)
    text = re.sub('coding utf-8', ' ', text)
    text = re.sub('=+', ' ', text)
    text = re.sub('-+', ' ', text)
    text = re.sub('#+', ' ', text)
    text = re.sub('\*+', ' ', text)
    text = re.sub('~+', ' ', text)
    text = re.sub(' +', ' ', text)

    legalCharSet = [
        '(', ')', '[', ']', ':', ';', '-', '"', ',', '.',' '
    ]
    ww = ""
    for c in text.lower():
        if (c >= 'a' and c <= 'z') or c in legalCharSet:
            ww += c
    ww = re.sub(' +', ' ', ww)

    return ww


def cleanInlineLicenses():
    numm = 0
    for pro in os.listdir(DIR):
        # every pro
        for file in os.listdir(os.path.join(DIR, pro)):
            if file.startswith("inline-license-"):
                # every text
                text = ""
                with open(os.path.join(DIR, pro, file), 'r', encoding='utf-8') as fr:
                    for line in fr.readlines():
                        if line.strip():
                            text += line.strip() + ' '

                # clean the inline text ...
                # 尽可能地去躁
                text1 = cleanIt(text)
                with open(os.path.join(DIR, pro, file.replace("inline-","inline2-")), 'w', encoding='utf-8') as fw:
                    fw.write(text1)

        numm += 1
        print(str(numm) + '/' + str(1846))


library_license = {}

license_check = {}
license_name = {}
def get212LincenseCheck():
    with open(outputDir000+"filter-exclude-list.txt", 'r', encoding='utf-8') as f:
        for li in f.readlines():
            li = li.strip()
            if li:
                name = ' '.join(li.split(' ')[2:])
                name_list = []
                if re.findall("\(", name):
                    name_list.append(name.split(' ')[-1][1:-1])
                    name_list.append(' '.join(name.split(' ')[:-1]))
                else:
                    name_list.append(name)
                license_name[li.split(' ')[0]] = ' '.join(li.split(' ')[2:])
                license_check[li.split(' ')[0]] = name_list
    return


def get_import_licenseNameList():
    numm = 0
    lib_difficult = []
    for pro in os.listdir(DIR):
        # every pro
        licenses0 = []
        with open(os.path.join(DIR,pro,"importedPackagesList.txt"), 'r', encoding='utf-8') as fr:
            for line in fr.readlines():
                if line.strip():
                    library = line.strip()
                    if library in library_license.keys():
                        licenses0.append(library_license[library])
                    else:
                        lib_difficult.append(library)
                        # print(library + ", to add it！")
        licenses = list(set(licenses0))
        with open(os.path.join(DIR,pro,"importedPackagesList-li.txt"), 'w', encoding="utf-8")as fw:
            for li in licenses:
                fw.write(li + '\n')
        numm += 1
        print(str(numm) + '/' + str(1846))

    # print(str(len(list(set(lib_difficult))))+"!!!!!!!!!!!!")
    return


def checkLicenses(include_license_list):
    license_list = []
    for license in include_license_list:
        FLAG222 = False
        for i in range(212):
            filter_list = license_check[str(i + 1)]

            for kk in filter_list:
                FLAG = True
                for word in kk.split(' '):
                    if license.upper().find(word.upper()) == -1:
                        FLAG = False
                        break
                if FLAG == True:
                    license_list.append(str(i))
                    FLAG222 =True
                    break
            if FLAG222 == True:
                break
    result_license_list = list(set(license_list))
    return result_license_list


def get_import_licensesCheckList():

    get_import_licenseNameList()

    numm = 0

    for pro in os.listdir(DIR):
        # every pro
        licenseNameList = []
        with open(os.path.join(DIR,pro,"importedPackagesList-li.txt"), 'r', encoding='utf-8') as fr:
            for line in fr.readlines():
                if line.strip():
                    licenseNameList.append(line.strip())
        licensesCheckList = checkLicenses(licenseNameList)
        # print(str(len(licensesCheckList)))
        with open(os.path.join(DIR,pro,"importedPackagesList-licenses.txt"), 'w', encoding="utf-8")as fw:
            for li in licensesCheckList:
                fw.write(li + '\n')
        numm += 1
        print(str(numm) + '/' + str(1846))

    return





if __name__ == '__main__':

    '''
    
    '''
    if not os.path.exists(outputDir000 + "finished_pac_list.txt"):
        with open(outputDir000 + 'finished_pac_list.txt', 'w', encoding="utf-8")as fw:
            fw.write('')
        print("create finished_pac_list.txt ...")

    if not os.path.exists(outputDir000 + "ex_pac_list.txt"):
        with open(outputDir000 + 'ex_pac_list.txt', 'w', encoding="utf-8")as fw:
            fw.write('')
        print("create ex_pac_list.txt ...")

    if not os.path.exists(outputDir000 + "collectNumbers.csv"):
        with open(outputDir000 + 'collectNumbers.csv', 'w', encoding="utf-8")as fw:
            fw.write(
                "repoName" + ',' + "num_packages" + ',' + "num_packages000" + ',' + "num_files" + ',' + "num_inline" + ',' + "num_prolicense" + '\n')
        print("create collectNumbers.csv ...")

    with open(outputDir000 + "library_license.txt", 'r', encoding='utf-8')as fr:
        for line in fr.readlines():
            if line.strip():
                line = line.strip()
                library_license[line.split(" ::::: ")[0]] = line.split(" ::::: ")[1]
    print("library_license: " + str(len(library_license)))

    get212LincenseCheck()


    acquire_run_history()

    #######
    get_licenses()


    '''
    
    '''
    cleanInlineLicenses()

    '''
    
    '''
    get_import_licensesCheckList()


