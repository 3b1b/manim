import subprocess


def capture(command, cwd=None):
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf8",
        cwd=cwd,
    )
    out, err = proc.communicate()
    return out, err, proc.returncode
