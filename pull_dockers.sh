#!/bin/bash

echo "Pulling all required images."

# SpliceAI container
echo "Pulling stefpiatek/spliceai:1.2.1..."
docker pull stefpiatek/spliceai:1.2.1

# Bcftools (staphb)
echo "Pulling staphb/bcftools..."
docker pull staphb/bcftools
