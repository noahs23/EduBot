import json
import csv
import sys
 
def merge(recording_csv, checkpoints_json, output_csv):
    with open(recording_csv, "r") as f:
        reader = csv.reader(f)
        headers = [h.strip() for h in next(reader)]
        rows = []
        for row in reader:
            rows.append([v.strip() for v in row])
 
    time_col = headers.index("time")
    times = [float(r[time_col]) for r in rows]
 
    with open(checkpoints_json, "r") as f:
        checkpoints = json.load(f)
 
    cp_map = {}
    for cp in checkpoints:
        target = cp["time"]
        best_idx = 0
        best_diff = abs(times[0] - target)
        for i in range(1, len(times)):
            diff = abs(times[i] - target)
            if diff < best_diff:
                best_diff = diff
                best_idx = i
        cp_map[best_idx] = cp["label"]
 
    with open(output_csv, "w") as f:
        f.write(",".join(headers) + ",checkpoint\n")
        for i, row in enumerate(rows):
            label = cp_map.get(i, "")
            f.write(",".join(row) + "," + label + "\n")
 
    print("Merged " + str(len(checkpoints)) + " checkpoints into " + output_csv)
 
if __name__ == "__main__":
    recording = sys.argv[1] if len(sys.argv) > 1 else "envRecording.csv"
    cps       = sys.argv[2] if len(sys.argv) > 2 else "checkpoints.json"
    output    = sys.argv[3] if len(sys.argv) > 3 else "envRecording_merged.csv"
    merge(recording, cps, output)