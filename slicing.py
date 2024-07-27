import subprocess
import re
import json
import datetime
from collections import defaultdict

def generate_timestamp_filename(prefix='data', extension='.json'):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}{extension}"

    return filename

def parse_metrics(output):
    
    ue_metrics = defaultdict(lambda: {
        "DRB.RlcSduDelayDl": [],
        "DRB.UEThpDl": [],
        "DRB.UEThpUl": [],
        "RRU.PrbTotDl": [],
        "RRU.PrbTotUl": []
        })
    ue_id = None

    patterns = {
        "ue_id": re.compile(r"ran_ue_id = (\d+)"),
        "DRB.RlcSduDelayDl": re.compile(r"DRB.RlcSduDelayDl = ([0-9\.]+) \[μs\]"),
        "DRB.UEThpDl": re.compile(r"DRB.UEThpDl = ([0-9\.]+) \[kbps\]"),
        "DRB.UEThpUl": re.compile(r"DRB.UEThpUl = ([0-9\.]+) \[kbps\]"),
        "RRU.PrbTotDl": re.compile(r"RRU.PrbTotDl = ([0-9]+) \[PRBs\]"),
        "RRU.PrbTotUl": re.compile(r"RRU.PrbTotUl = ([0-9]+) \[PRBs\]")
    }

    for line in output:
        ue_id_match = patterns["ue_id"].search(line)
        if ue_id_match:
            ue_id = ue_id_match.group(1)

        if ue_id:
            for key, pattern in patterns.items():
                if key != "ue_id":
                    matched = pattern.search(line)
                    if matched:
                        ue_metrics[ue_id][key].append(float(matched.group(1)))

    return ue_metrics

def calculate_delay_average(delay_list):
    average = sum(delay_list)/len(delay_list)
    return average

def collect_metrics(executable_path):
    process = subprocess.Popen(executable_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    stdout, stderr = process.communicate()

    return stdout

def save_dict_as_json(data, filename):
    data = {k: dict(v) for k, v in data.items()}
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)


# Somente um UE terá delay observado para fim de fatiamento
def trigger_qos(avg_delay, threshold):
    if avg_delay > threshold:
        result = subprocess.run(["docker", "exec", "oai-spgwu", "ps", "aux"], capture_output=True, text=True)
        if not "scapy-emulate-delay" in result.stdout:
            subprocess.run(["docker", "exec", "oai-spgwu", "scripts/iptables-rules.sh"])
            subprocess.Popen(["docker", "exec", "oai-spgwu", "python3", "scripts/scapy-emulate-delay.py", "0"])


import time

def monitor_loop(executable_path):
    n = 1
    while True:
        stdout = collect_metrics(executable_path)
        metrics = parse_metrics(stdout.splitlines())
        filename = generate_timestamp_filename(prefix='ue_metrics', extension='.json')
        save_dict_as_json(metrics, filename)

        delay_averages = {ue_id: calculate_delay_average(metrics[ue_id]["DRB.RlcSduDelayDl"]) for ue_id in metrics}
        
        trigger_qos(delay_averages['1'], 500)
        n = n + 1
        print("Começando outra rodada ", n)
        time.sleep(5)


executable_path = "./xapp_kpm_moni"

monitor_loop(executable_path)
