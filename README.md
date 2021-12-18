# LiDetector

**LiDetector** , a hybrid method that automatically understands license texts and infers rights and obligations to detect license incompatibility in open-source software.   
For an open-source project as input, where licenses may appear in three forms: referenced, declared, and inline, the license texts are first extracted from the two forms for further incompatibility analysis. With  such a license set, the main components of LiDetector include:   
**(1) Preprocessing**, which filters out official licenses and feeds custom ones into the probabilistic model for automatic understandings of license texts.  
**(2) License term identification**, which aims to identify license terms relevant to rights and obligations;   
**(3) Right and obligation inference**, which infers the stated condition of software use defined by license terms;   
**(4) Incompatibility detection**,  which automatically analyzes incompatibility between multiple licenses within one project based on the regulations inferred from each license.  
![LiDetector Overview](https://drive.google.com/file/d/1Gl8fDaJdSr1sCab4JBytp15nKynGzVbb/view?usp=sharing)


# LiDetector


