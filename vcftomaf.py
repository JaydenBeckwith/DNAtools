import subprocess
import os
import argparse

def convert_annotated_vcf_to_maf(vcf_path, output_maf, ref_fasta):
    # Get absolute paths
    vcf_path = os.path.abspath(vcf_path)
    output_maf = os.path.abspath(output_maf)
    ref_fasta = os.path.abspath(ref_fasta)

    # Get directories
    work_dir = os.path.dirname(vcf_path)
    ref_dir = os.path.dirname(ref_fasta)

    # Build Docker command
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{work_dir}:/data",
        "-v", f"{ref_dir}:/ref",
        "ghcr.io/mskcc/vcf2maf/vcf2maf:v1.6.18",
        "perl", "vcf2maf.pl",
        "--input-vcf", f"/data/{os.path.basename(vcf_path)}",
        "--output-maf", f"/data/{os.path.basename(output_maf)}",
        "--ref-fasta", f"/ref/{os.path.basename(ref_fasta)}",
        "--filter-vcf", "0",
        "--inhibit-vep"
    ]

    # Run command
    print("Running command:")
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert pre-annotated VEP VCF to MAF using vcf2maf.pl inside Docker.")
    parser.add_argument("--vcf", required=True, help="Path to input VEP-annotated VCF file")
    parser.add_argument("--maf", required=True, help="Path to output MAF file")
    parser.add_argument("--ref", required=True, help="Path to reference FASTA file")

    args = parser.parse_args()
    convert_annotated_vcf_to_maf(args.vcf, args.maf, args.ref)