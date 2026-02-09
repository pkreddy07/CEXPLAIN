import re

def parse_diagnostics(raw_stderr) :
    pattern = r"^(.*?):(\d+):(\d+):\s+(error|warning):\s+(.*)$"
    errors = []

    for line in raw_stderr.splitlines() :
        match = re.match(pattern, line)

        if match :
            errors.append({
                "file": match.group(1),
                "line": int(match.group(2)),
                "column": int(match.group(3)),
                "severity": match.group(4),
                "message": match.group(5)
            })
    
    return errors