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
