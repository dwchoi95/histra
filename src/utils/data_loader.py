import os, json, sys


class DataLoader:
    @staticmethod
    def parse(data):
        problem = data["problem"]
        meta_raw = data.get("meta", {})
        if isinstance(meta_raw, str):
            try:
                meta = json.loads(meta_raw)
            except Exception:
                meta = {}
        else:
            meta = meta_raw if isinstance(meta_raw, dict) else {}
        pid = meta.get("problem_id", None)
        timeout = meta.get("time_limit_ms", 2000) / 1000.0
        tests = []
        for i, t in enumerate(data["tests"]):
            tests.append({"id": i, "input": t["input"], "output": t["output"]})
        traj = {}
        refs = {}
        for t in data["trajectories"]:
            user_id = t["user_id"]
            subs = t["submissions"]
            was = []
            for s in subs:
                if s["verdict"] == "Accepted":
                    refs[user_id] = s["code"]
                else:
                    was.append(s["code"])
            traj[user_id] = was
        return pid, problem, timeout, traj, refs, tests

    @classmethod
    def get_problem(cls, pdir):
        data = {}
        for fname in ["problem.html", "meta.json", "trajectories.jsonl", "tests.jsonl", ]:
            if not os.path.exists(os.path.join(pdir, fname)):
                raise ValueError(f"Missing required file '{fname}' in problem directory: {pdir}")
            file = os.path.join(pdir, fname)
            base = os.path.splitext(fname)[0]
            data[base] = open(file, encoding="utf-8").read() if base != "trajectories" and base != "tests" else [json.loads(ln) for ln in open(file, encoding="utf-8")]
        return data

    @classmethod
    def run(cls, dataset_path):
        problems = []
        if os.path.isdir(dataset_path):
            for pid in os.listdir(dataset_path):
                pdir = os.path.join(dataset_path, pid)
                if os.path.isdir(pdir):
                    data = cls.get_problem(pdir)
                    problems.append(data)
            if not problems:
                data = cls.get_problem(dataset_path)
                problems.append(data)
        else:
            raise ValueError("Dataset path must be a directory or a JSON file containing problem IDs")
        return problems