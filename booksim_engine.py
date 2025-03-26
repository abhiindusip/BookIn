import os
import subprocess
import datetime

# === Paths ===

BASE_DIR = os.path.dirname(__file__)
BOOKSIM_BINARY = os.path.join(BASE_DIR, "booksim2", "src", "booksim")

# === Save full GPT-generated config string to a temp file ===

def save_generated_config(config_str: str) -> str:
    os.makedirs("temp_configs", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    config_path = f"temp_configs/generated_{timestamp}.cfg"

    with open(config_path, "w") as f:
        f.write(config_str)

    return config_path

# === Run the Booksim simulation ===

def run_simulation(config_path: str) -> dict:
    process = subprocess.run(
        [BOOKSIM_BINARY, config_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False
    )

    output = process.stdout
    errors = process.stderr
    returncode = process.returncode

    # Save full output to log file
    os.makedirs("logs", exist_ok=True)
    basename = os.path.basename(config_path).replace("_temp", "").replace(".cfg", "")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/{basename}_{timestamp}.log"

    with open(log_filename, "w") as log_file:
        log_file.write(output)

    # Extract metrics
    metrics = extract_metrics_from_output(output) if returncode == 0 else {}

    return {
        "returncode": returncode,
        "stdout": output,
        "stderr": errors,
        "metrics": metrics,
        "log_file": log_filename
    }

# === Extract metrics from Booksim output ===

def extract_metrics_from_output(output: str) -> dict:
    metrics = {}
    for line in output.splitlines():
        line = line.strip()
        if "Packet latency average" in line:
            metrics["avg_latency"] = _extract_last_float(line)
        elif "Network latency average" in line:
            metrics["avg_network_latency"] = _extract_last_float(line)
        elif "Injected packet rate average" in line:
            metrics["injected_packet_rate"] = _extract_last_float(line)
        elif "Accepted packet rate average" in line:
            metrics["accepted_packet_rate"] = _extract_last_float(line)
        elif "Injected packet length average" in line:
            metrics["injected_packet_length"] = _extract_last_float(line)
        elif "Accepted packet length average" in line:
            metrics["accepted_packet_length"] = _extract_last_float(line)
        elif "Hops average" in line:
            metrics["avg_hops"] = _extract_last_float(line)
    return metrics

# === Helper to pull last float in a line ===

def _extract_last_float(line: str) -> float:
    try:
        return float(line.split("=")[-1].strip())
    except ValueError:
        return -1.0
