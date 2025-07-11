# DNAtools
This is a collection of Python scripts for variant analysis pipelines, with a focus on identifying and visualising predicted splice-disrupting mutations.  

This toolkit allows you to run SpliceAI on VCF files, filter variants based on predicted splice impact, and convert results into MAF format for downstream visualization (e.g. with `maftools` in R).


## Workflow Overview

This pipeline processes DNA variant data in three main steps:

1. **SpliceAI annotation (`run_spliceai.py`)**  
   Annotates your input VCF with SpliceAI scores predicting splice disruption.

2. **Filtering for high SpliceAI delta (`subset_splice_vcf.py`)**  
   Filters variants to retain only those with SpliceAI delta > 0.5, enriching for likely splice-altering mutations.

3. **Conversion to MAF format (`vcftomaf.py`)**  
   Converts filtered VCF files into MAF format, ready for downstream visualization (e.g. oncoplots in `maftools`).

---

## Usage

### Pull Docker Containers

```bash
./pull_dockers.sh
```

### Run SpliceAI
Runs SpliceAI on your VCF to predict splicing impact.

```bash
python3 spliceai.py \
    --input input.vcf \
    --output annotated.vcf \
    --reference hg38.fa
```

## Subset to highly predicted Splice Sites

```bash
python3 subset_splice_vcf.py \
    --folder /folder_containing_vcfs
```

## vcf to maf conversion

```bash
python3 vcftomaf.py \
    --folder /folder_containing_subsets \
    --ref hg38.fa
```