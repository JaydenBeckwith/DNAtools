import subprocess
import os
import argparse

def convert_annotated_vcf_to_maf(vcf_path, output_maf, ref_fasta):
    # Absolute paths
    vcf_path = os.path.abspath(vcf_path)
    output_maf = os.path.abspath(output_maf)
    ref_fasta = os.path.abspath(ref_fasta)

    # Docker mounting
    work_dir = os.path.dirname(vcf_path)
    ref_dir = os.path.dirname(ref_fasta)

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

    print("\nRunning command:")
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)
    print(f"Finished: {output_maf}")

def main():
    parser = argparse.ArgumentParser(description="Batch convert all VEP-annotated VCFs in a folder to MAFs.")
    parser.add_argument("--folder", required=True, help="Folder with VEP-annotated VCF files")
    parser.add_argument("--ref", required=True, help="Path to reference FASTA file")
    args = parser.parse_args()

    folder = os.path.abspath(args.folder)
    ref_fasta = os.path.abspath(args.ref)

    # Process all .vcf and .vcf.gz files
    for file in os.listdir(folder):
        if file.endswith(".subset_high.vcf"):
            input_vcf = os.path.join(folder, file)
            output_maf = os.path.join(folder, file.replace(".vcf.gz", "").replace(".vcf", "") + ".maf")
            print(f"\n Converting: {input_vcf}")
            convert_annotated_vcf_to_maf(input_vcf, output_maf, ref_fasta)

    print("\n All done. All MAF files are in:", folder)

if __name__ == "__main__":
    main()