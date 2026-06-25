import os, json, sys


class DataLoader:
    @classmethod
    def _read(cls, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    @classmethod
    def get_problem(cls, pdir):
        meta_path = os.path.join(pdir, "meta.json")
        tests_path = os.path.join(pdir, "tests.jsonl")
        traj_path = os.path.join(pdir, "trajectories.jsonl")
        
        meta = json.loads(cls._read(meta_path))
        timeout = meta.get("timeout", 2000.0) / 1000.0  # Convert ms to seconds
        tests = [json.loads(line) for line in cls._read(tests_path).splitlines()]
        trajactories = [json.loads(line) for line in cls._read(traj_path).splitlines()]
        trajs = {}
        refs = {}
        for t in trajactories:
            user_id = t["user_id"]
            subs = t["submissions"]
            was = []
            for s in subs:
                if s["verdict"] == "Accepted":
                    refs[user_id] = s["code"]
                else:
                    was.append(s["code"])
            trajs[user_id] = was
        return timeout, tests, trajs, refs

    @classmethod
    def run(cls, dataset_path):
        problems = []
        if os.path.isdir(dataset_path):
            for pid in os.listdir(dataset_path):
                pdir = os.path.join(dataset_path, pid)
                if os.path.isdir(pdir):
                    data = cls.get_problem(pdir)
                    problems.append((pid,) + data)
            if not problems:
                pid = os.path.basename(os.path.normpath(dataset_path))
                data = cls.get_problem(dataset_path)
                problems.append((pid,) + data)
        else:
            raise ValueError("Dataset path must be a directory or a JSON file containing problem IDs")
        return problems