#!/bin/bash

echo "Pulling all required images."

# SpliceAI container
echo "Pulling stefpiatek/spliceai:1.2.1..."
docker pull stefpiatek/spliceai

# Bcftools (staphb)
echo "Pulling staphb/bcftools..."
docker pull staphb/bcftools

# vcf2maf
echo "Pulling opengenomics/vcf2maf..."
docker pull opengenomics/vcf2maf