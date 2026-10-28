
import os
import subprocess
import tempfile
from pathlib import Path


def compile_c_source(source_code: str) -> dict:
    """Compile C source and return compiler diagnostics."""

    with tempfile.TemporaryDirectory(prefix="ac_") as temp_dir:
        source_path = Path(temp_dir) / "input.c"
        output_path = Path(temp_dir) / "program.exe"

        source_path.write_text(source_code, encoding="utf-8")

        command = [
            "gcc",
            "-std=c11",
            "-Wall",
            "-Wextra",
            "-Wpedantic",
            str(source_path),
            "-o",
            str(output_path),
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return {
                "compiled": False,
                "return_code": None,
                "stdout": "",
                "stderr": "Compilation timed out.",
            }
        except OSError as exc:
            return {
                "compiled": False,
                "return_code": None,
                "stdout": "",
                "stderr": f"Compiler could not start: {exc}",
            }

        return {
            "compiled": result.returncode == 0,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
