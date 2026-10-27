"""Run HISTRA (or an RQ3 variant) on the benchmark: output/approaches/histra.jsonl, or output/ablation/<MODE>.jsonl.
Usage: python run.py [PROBLEM ...] [-m MODE] [-j WORKERS]   (default: all problems; run p02686 alone with -j 4)"""
import argparse
import os
import sys

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="HISTRA: history-guided repair of student submissions")
    ap.add_argument("problems", nargs="*", help="problem ids under data/ (default: all)")
    ap.add_argument("-m", "--mode", default="min", help="min (HISTRA) or a variant of src/experiments/histra_eval.py")
    ap.add_argument("-j", "--workers", type=int, default=16)
    args = ap.parse_args()
    os.environ["ONLY"], os.environ["POOL"] = ",".join(args.problems), str(args.workers)
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "experiments"))
    import histra_eval
    histra_eval.main(args.mode)
