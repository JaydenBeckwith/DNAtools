import subprocess
import argparse
import os

def ensure_bgzip_and_index(input_vcf):
    input_dir = os.path.dirname(input_vcf).replace("\\", "/")
    input_basename = os.path.basename(input_vcf)

    if input_vcf.endswith(".vcf.gz"):
        index_file = os.path.join(input_dir, input_basename + ".tbi")
        if not os.path.exists(index_file):
            print("🚀 Indexing existing bgzipped VCF...")
            cmd = [
                "docker", "run", "--rm",
                "-v", f"{input_dir}:/data",
                "staphb/bcftools",
                "bcftools", "index",
                f"/data/{input_basename}"
            ]
            subprocess.run(cmd)
        else:
            print("✅ Already bgzipped and indexed.")
        return input_vcf
    else:
        # Use bcftools view -Oz to compress + index
        compressed_vcf = input_vcf + ".gz"
        docker_input = f"/data/{input_basename}"
        docker_output = f"/data/{os.path.basename(compressed_vcf)}"

        print("🚀 Compressing with bcftools view -Oz and indexing...")
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{input_dir}:/data",
            "staphb/bcftools",
            "bash", "-c",
            f'bcftools view -Oz -o {docker_output} {docker_input} && bcftools index {docker_output}'
        ]
        subprocess.run(cmd)
        if not os.path.exists(compressed_vcf):
            raise FileNotFoundError(f"⚠️ Did not create {compressed_vcf}")
        print(f"✅ Created {compressed_vcf} with index.")
        return compressed_vcf

def run_bcftools_and_write(input_vcf, output_tsv):
    input_dir = os.path.dirname(input_vcf).replace("\\", "/")
    input_basename = os.path.basename(input_vcf)
    docker_output = f"/data/{os.path.basename(output_tsv)}"

    cmd = [
        "docker", "run", "--rm",
        "-v", f"{input_dir}:/data",
        "staphb/bcftools",
        "bash", "-c",
        f"bcftools query -f '%CHROM\\t%POS\\t%REF\\t%ALT\\t%INFO/CSQ\\t%INFO/SpliceAI\\n' /data/{input_basename} "
        f"| awk -F'\\t' '{{ "
        f"split($6, f, \"|\"); "
        f"max=f[3]; if(f[4]>max) max=f[4]; if(f[5]>max) max=f[5]; if(f[6]>max) max=f[6]; "
        f"if (max > 0.5) "
        f"print $1, $2, $3, $4, $5, $6, f[3], f[4], f[5], f[6], max "
        f"}}' OFS='\\t' > {docker_output}"
    ]

    print("🚀 Running:", " ".join(cmd))
    subprocess.run(cmd)

    local_output = os.path.join(input_dir, os.path.basename(output_tsv))
    if not os.path.exists(local_output):
        raise FileNotFoundError(f"⚠️ Docker did not create file: {local_output}")
    print(f"✅ Filtered TSV written to: {local_output}")
    return local_output

def build_sites_file(tsv_file, sites_file):
    print(f"🚀 Building true VCF-style sites file from {tsv_file}")
    with open(tsv_file, 'r') as infile, open(sites_file, 'w') as outfile:
        # Minimal required VCF header
        outfile.write("##fileformat=VCFv4.2\n")
        outfile.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n")
        for line in infile:
            if line.strip() == "" or line.startswith("#"):
                continue
            fields = line.strip().split("\t")
            outfile.write(f"{fields[0]}\t{fields[1]}\t.\t{fields[2]}\t{fields[3]}\t.\t.\t.\n")
    print(f"✅ Sites file created at {sites_file}")

def subset_vcf(input_vcf, sites_file, subset_vcf):
    input_dir = os.path.dirname(input_vcf).replace("\\", "/")
    input_basename = os.path.basename(input_vcf)
    docker_output = f"/data/{os.path.basename(subset_vcf)}"

    cmd = [
        "docker", "run", "--rm",
        "-v", f"{input_dir}:/data",
        "staphb/bcftools",
        "bcftools", "view",
        "-R", f"/data/{os.path.basename(sites_file)}",
        f"/data/{input_basename}",
        "-Ov", "-o", docker_output
    ]

    print("🚀 Running:", " ".join(cmd))
    subprocess.run(cmd)

    local_output = os.path.join(input_dir, os.path.basename(subset_vcf))
    if not os.path.exists(local_output):
        raise FileNotFoundError(f"⚠️ Docker did not create file: {local_output}")
    print(f"✅ Subset VCF written to: {local_output}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input VCF file (.vcf or .vcf.gz)")
    args = parser.parse_args()

    input_vcf = os.path.abspath(args.input).replace("\\", "/")
    input_dir = os.path.dirname(input_vcf)

    # Ensure bgzip + index
    processed_vcf = ensure_bgzip_and_index(input_vcf)

    # File names
    output_tsv = os.path.join(input_dir, os.path.basename(processed_vcf).replace(".vcf.gz", ".high.tsv"))
    sites_file = os.path.join(input_dir, "exact_sites.vcf")
    subset_output_vcf = os.path.join(input_dir, os.path.basename(processed_vcf).replace(".vcf.gz", ".subset_high.vcf"))

    # Pipeline
    run_bcftools_and_write(processed_vcf, output_tsv)
    build_sites_file(output_tsv, sites_file)
    subset_vcf(processed_vcf, sites_file, subset_output_vcf)

    print("\n✅ All done! Filtered VCF:", subset_output_vcf)

if __name__ == "__main__":
    main()
