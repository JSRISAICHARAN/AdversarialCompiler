
import re


RULES = [
    {
        "rule_id": "AC101",
        "pattern": re.compile(r"\bgets\s*\("),
        "severity": "critical",
        "title": "Unsafe input function",
        "message": "gets() does not limit input length and can cause a buffer overflow.",
        "recommendation": "Use fgets() with the destination buffer size.",
        "cwe": "CWE-120",
    },
    {
        "rule_id": "AC102",
        "pattern": re.compile(r"\bstrcpy\s*\("),
        "severity": "high",
        "title": "Unbounded string copy",
        "message": "strcpy() does not check whether the destination buffer is large enough.",
        "recommendation": "Validate input length and destination capacity before copying.",
        "cwe": "CWE-120",
    },
    {
        "rule_id": "AC103",
        "pattern": re.compile(r"\bstrcat\s*\("),
        "severity": "high",
        "title": "Unbounded string concatenation",
        "message": "strcat() can exceed the destination buffer capacity.",
        "recommendation": "Check available capacity and use a bounded string-handling approach.",
        "cwe": "CWE-120",
    },
    {
        "rule_id": "AC104",
        "pattern": re.compile(r"\bsprintf\s*\("),
        "severity": "high",
        "title": "Unbounded formatted output",
        "message": "sprintf() does not limit the number of characters written to its destination.",
        "recommendation": "Consider snprintf() and check its return value and buffer size.",
        "cwe": "CWE-120",
    },
    {
        "rule_id": "AC105",
        "pattern": re.compile(r"\bsystem\s*\("),
        "severity": "medium",
        "title": "Operating-system command execution",
        "message": "system() invokes a command interpreter and may be dangerous with untrusted input.",
        "recommendation": "Avoid shell execution when possible; never concatenate untrusted input into commands.",
        "cwe": "CWE-78",
    },
    {
        "rule_id": "AC106",
        "pattern": re.compile(r'\bscanf\s*\(\s*"[^"]*%s'),
        "severity": "medium",
        "title": "Potentially unbounded string input",
        "message": "The scanf format appears to use %s without a field width.",
        "recommendation": "Specify a maximum field width that fits the destination buffer.",
        "cwe": "CWE-120",
    },
    {
        "rule_id": "AC107",
        "pattern": re.compile(
            r"""(?i)\b(password|passwd|api[_-]?key|secret|token)"""
            r"""\s*=\s*["'][^"']{4,}["']"""
        ),
        "severity": "medium",
        "title": "Possible hardcoded secret",
        "message": "A credential-like variable appears to contain a hardcoded string.",
        "recommendation": "Use a secure configuration mechanism or secret manager.",
        "cwe": "CWE-798",
    },
]

BIDI_CONTROLS = {
    "\u202a", "\u202b", "\u202c", "\u202d", "\u202e",
    "\u2066", "\u2067", "\u2068", "\u2069",
}


def analyze_source(source_code: str) -> dict:
    findings = []

    for line_number, line in enumerate(source_code.splitlines(), start=1):
        for rule in RULES:
            if rule["pattern"].search(line):
                findings.append({
                    "rule_id": rule["rule_id"],
                    "severity": rule["severity"],
                    "title": rule["title"],
                    "message": rule["message"],
                    "recommendation": rule["recommendation"],
                    "line_number": line_number,
                    "cwe": rule["cwe"],
                    "evidence": line.strip()[:200],
                })

        if any(char in BIDI_CONTROLS for char in line):
            findings.append({
                "rule_id": "AC108",
                "severity": "high",
                "title": "Unicode bidirectional control character",
                "message": (
                    "This line contains a Unicode control character "
                    "that can make source-code text appear misleading."
                ),
                "recommendation": (
                    "Inspect the character and remove it unless its use "
                    "is explicitly required and understood."
                ),
                "line_number": line_number,
                "cwe": "CWE-451",
                "evidence": f"Line {line_number} contains a bidirectional control character.",
            })

    counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    for finding in findings:
        severity = finding["severity"]
        if severity in counts:
            counts[severity] += 1

    return {
        "findings": findings,
        "total_findings": len(findings),
        "severity_counts": counts,
        "analysis_method": "Rule-based static analysis",
        "limitations": (
            "Heuristic checks only. Findings may include false positives, "
            "and the absence of findings does not prove code is safe. "
            "Rules currently inspect individual source lines."
        ),
    }
