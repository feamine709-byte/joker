import json
import subprocess
import sys


def main() -> int:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return 0
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            return 0
    except Exception:
        return 0

    proc = subprocess.run(
        [
            "living_automaton_kernel.exe",
            "--data-dir",
            ".lak-data",
            "--rules",
            "presets/ai-agent.rules",
            "--hook",
        ],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.stdout:
        sys.stdout.write(proc.stdout)
        sys.stdout.flush()
    if proc.stderr:
        sys.stderr.write(proc.stderr)
        sys.stderr.flush()
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
