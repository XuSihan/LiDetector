# LiDetector

**LiDetector** is a hybrid method that automatically understands license texts and infers rights and obligations to detect license incompatibilities in open-source software. For an open-source project as input, where licenses may appear in three forms: referenced, declared, and inline, the license texts are first extracted from these forms for further incompatibility analysis. With such a license set, the main components of LiDetector include:

1. **Preprocessing**: This filters out official licenses and feeds custom ones into the probabilistic model for automatic understanding of license texts.
2. **License Term Identification**: This aims to identify license terms relevant to rights and obligations.
3. **Right and Obligation Inference**: This infers the stated conditions of software use defined by license terms.
4. **Incompatibility Detection**: This automatically analyzes incompatibility between multiple licenses within one project based on the regulations inferred from each license.

<p align="center">
    <img src="overview.jpg" width="800">
</p>

# Code

## How to Start
Run the Python scripts in the following order:

1. `extract_licenseRelated_fromPros.py`
2. `collect_files_for_model.py`
3. `model/PreprocessData/cleanData_intoTestDir.py`
4. `model/LocateTerms/ner_predict.py`
5. `model/DetermAtti/get_treeAtti.py`
6. `prepare_condInfo.py`
7. `check_incompatibility.py`

## Directories and Files

Some directories and files are explained here:

```
+-- unzips: OSS projects to be tested
+-- extract_licenseRelated_fromPros.py: Extracts licenses from OSS projects
+-- output: Licenses extracted in three forms
+-- model: License comprehension
|   +-- data: Test data for term identification
|   +-- PreprocessData: Preprocess for test data
|   +-- LocateTerms: Term identification
|       +-- data: Data for term identification (train, dev, test)
|       +-- model: Sequence labeling model
|       +-- results: The trained model
|       +-- build_data, train, evaluate: For model training
|       +-- ner_predict: Predict terms for test data based on the trained model
|   +-- DetermAtti: Right and obligation inference
+-- prepare_condInfo: Extract license condition relationships
+-- condInfo: License conditions extracted
+-- check_incompatibility: Check license compatibility of OSS projects based on results above
+-- checkIncom_functions: Regulations of license compatibility
```

## Other Requirements

### Ninka
Ninka is required in the `checkLicenseInline` function on line 101 of `extract_licenseRelated_fromPros.py`. This part needs to be run separately because Ninka is based on Linux to read the extracted inline license words of code.
[Ninka](https://github.com/dmgerman/ninka)

### CoreNLP
CoreNLP is needed to help parse the syntax tree of license sentences. You can download it and place it at the pre-set path `./model/stanford-corenlp-4.3.2`.
[CoreNLP](https://stanfordnlp.github.io/CoreNLP/)

# Knowledge

## License Terms and Descriptions
In this paper, a license term refers to a formal and unified description of a certain right or obligation (e.g., commercial use). In our License Term Identification phase, we aim to identify license terms. The 23 license terms and their descriptions are shown below:
<p align="center">
    <img src="terms.jpg" width="800">
</p>

## Keyword Patterns for Regular Matching
In the evaluation stage of the License Term Identification phase, this paper implements Regular Matching as one of our baselines. We predefined a set of keyword patterns to guide license term identification. 72 patterns were found for 23 license terms, which can be downloaded from the following link:
[Keyword Patterns](https://drive.google.com/uc?id=1FpA6_n7__nb5Dm64FRuA9fzDP6bgpSEe&export=download)

## Representative Sentences for Semantic Similarity
In the evaluation stage of the License Term Identification phase, this paper implements Semantic Similarity as one of our baselines. We manually analyzed license sentences and collected a set of representative sentences relevant to each license term. 51 representative sentences for 23 license terms were found, which can be downloaded from the following link:
[Representative Sentences](https://drive.google.com/uc?id=1YCrKGC5QIbu7KB17DnXCSCr5xM1Cf2UL&export=download)

# Dataset

## Term Entity Tagging for the Term Identification Phase
We tagged license term entities on 400 licenses for training and testing the sequence labeling model in the Term Identification phase. These data can be downloaded from the following link:
[Term Entity Tagging Dataset](https://drive.google.com/uc?id=1V8IiM2XuQ9oQFXJf1OYmmQdL75eu506J&export=download)

## Testing Dataset for Overall License Comprehension
In the evaluation stage of the License Term Identification phase, Right and obligation inference phase, and overall License Comprehension (i.e., the overall performance of the previous two phases), this paper employed 80 licenses as the testing dataset, after randomly splitting 400 samples aforementioned into training and testing datasets by a 4:1 ratio. These licenses are equipped with their attitudes towards 23 terms, which can be downloaded from the following link:
[Testing Dataset](https://drive.google.com/uc?id=1TWeDJJeUsD8AY0sQgA7SYSfjEcHD-D2z&export=download)

## Dataset for Official Licenses
In this paper, *official licenses* refer to licenses from the Software Package Data Exchange (SPDX). We collect and annotate these licenses for their rights, obligations, and conditions.

## Dataset for Empirical Study
We crawled 1,846 GitHub projects for motivating study and Empirical Study, in which each OSS project has a high number of stars. They were extracted by their inline licenses, declared licenses, referenced licenses, and identified by ID from 1 to 1,846, which can be downloaded from the following link:
[Empirical Study Dataset](https://drive.google.com/uc?id=1TQS_UmX0wpTvq5dj5b6CdGc20v9qd4JP&export=download)

## Test Dataset for Incompatibility Detection Phase
We randomly selected 200 projects from the above 1,846 GitHub projects and constructed a ground-truth dataset by manual analysis on whether this project has a license incompatibility situation. The testing list can be downloaded from the following link:
[Test Dataset](https://drive.google.com/uc?id=1e91pG_EGvqUxtNiLbeKPj-WxRTByOzrp&export=download)
