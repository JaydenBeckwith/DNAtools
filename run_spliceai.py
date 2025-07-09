import os
import subprocess
import gzip
import shutil
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

def run_spliceai(filename, data_dir, ref_dir, spliceai_dir, ref_fasta):
    input_vcf = f"/data/{filename}"
    output_basename = filename.replace("vep.vcf", "vep.spliceai.vcf")
    output_vcf = f"/spliceai/{output_basename}"
    local_output_path = os.path.join(spliceai_dir, output_basename)

    print(f"\n🚀 Running SpliceAI on {filename}")

    docker_cmd = [
        "docker", "run", "--rm",
        "-v", f"{data_dir}:/data",
        "-v", f"{ref_dir}:/ref",
        "-v", f"{spliceai_dir}:/spliceai",
        "stefpiatek/spliceai:1.2.1",
        "spliceai",
        "-I", input_vcf,
        "-O", output_vcf,
        "-R", ref_fasta,
        "-A", "grch38"
    ]
    print("Running:", " ".join(docker_cmd))
    subprocess.run(docker_cmd)

    if os.path.exists(local_output_path):
        print(f"Gzipping {local_output_path}")
        with open(local_output_path, 'rb') as f_in:
            with gzip.open(local_output_path + '.gz', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(local_output_path)
        return f"Finished {filename}"
    else:
        return f"Warning: SpliceAI did not create expected output for {filename}"

def main():
    # Arg parser
    parser = argparse.ArgumentParser(description="Run SpliceAI in parallel on VCF files using Docker.")
    parser.add_argument("--data-dir", required=True, help="Path to directory containing VCF files")
    parser.add_argument("--ref-dir", required=True, help="Path to directory containing FASTA")
    parser.add_argument("--max-workers", type=int, default=4, help="Number of parallel SpliceAI runs")
    args = parser.parse_args()

    data_dir = os.path.abspath(args.data_dir).replace("\\", "/")
    ref_dir = os.path.abspath(args.ref_dir).replace("\\", "/")
    ref_fasta = "/ref/primary_assembly.genome.fa"
    spliceai_dir = os.path.join(data_dir, "spliceai").replace("\\", "/")
    max_workers = args.max_workers

    os.makedirs(spliceai_dir, exist_ok=True)

    print(f"Input VCFs from: {data_dir}")
    print(f"FASTA from: {ref_dir}")
    print(f"SpliceAI outputs will be stored in: {spliceai_dir}")
    print(f"Running up to {max_workers} parallel SpliceAI jobs.")

    # List VCF files
    files = [f for f in os.listdir(data_dir) if f.endswith(".vep.vcf") and not f.startswith("._")]

    # Run in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(run_spliceai, f, data_dir, ref_dir, spliceai_dir, ref_fasta): f
            for f in files
        }
        for future in as_completed(future_to_file):
            print(future.result())

    print("\n Done! All SpliceAI outputs gzipped in:", spliceai_dir)

if __name__ == "__main__":
    main()