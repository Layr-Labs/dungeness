"""Run a supplied official Linux ARM64 CLI in an offline disposable container."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path, help="Official archive matching cli-release.json")
    parser.add_argument("--image", required=True, help="Locally installed Linux ARM64 image with Python 3 and glibc")
    args = parser.parse_args()
    source = Path(__file__).resolve().parent
    release = json.loads((source / "cli-release.json").read_text())
    archive = args.archive.resolve()
    with archive.open("rb") as handle:
        digest = hashlib.file_digest(handle, "sha512").hexdigest()
    if digest != release["sha512"]:
        raise SystemExit("CLI archive does not match the pinned official release.")
    info = json.loads(subprocess.check_output(
        ["docker", "image", "inspect", "--", args.image], text=True,
    ))[0]
    if info["Os"] != "linux" or info["Architecture"] != "arm64":
        raise SystemExit("Select a locally installed Linux ARM64 image.")
    with tempfile.TemporaryDirectory(prefix="openrsi-agy-probe-") as temporary:
        binary = Path(temporary) / "agy"
        with tarfile.open(archive, "r:gz") as package:
            # Copy one regular ELF file, never extract archive paths or symlinks.
            candidates = [entry for entry in package if entry.isfile()]
            executables = []
            for entry in candidates:
                with package.extractfile(entry) as handle:
                    if handle.read(4) == b"\x7fELF":
                        executables.append(entry)
            if len(executables) != 1 or executables[0].size > 512 * 1024 * 1024:
                raise SystemExit("Expected exactly one bounded native CLI executable.")
            with package.extractfile(executables[0]) as handle:
                binary.write_bytes(handle.read())
        binary.chmod(0o755)
        cidfile = Path(temporary) / "container-id"
        command = [
            "docker", "run", "--rm", "--pull", "never", "--platform", "linux/arm64",
            "--cidfile", str(cidfile),
            "--network", "none", "--read-only", "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges", "--pids-limit", "128",
            "--memory", "1g", "--user", "10001:10001",
            "--tmpfs", "/tmp:rw,nosuid,nodev,size=512m,mode=1777",
            "--mount", f"type=bind,src={binary},dst=/usr/local/bin/agy,readonly",
            "--mount", f"type=bind,src={source},dst=/probe,readonly",
            "-e", "OPENRSI_OFFLINE_AGY_PROBE=1",
            "--entrypoint", "python", info["Id"], "/probe/probe.py",
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=125)
        finally:
            if cidfile.exists():
                # Only remove the container this invocation created.
                subprocess.run(
                    ["docker", "rm", "-f", cidfile.read_text().strip()],
                    capture_output=True, timeout=10,
                )
        if result.returncode:
            raise SystemExit(result.stderr[-2000:] or f"Probe container exited {result.returncode}")
        report = json.loads(result.stdout)
        report["cli_version"] = release["version"]
        report["archive_sha512"] = digest
        report["container_image_id"] = info["Id"]
        print(json.dumps(report, indent=2))
        # A completed probe can still demonstrate incompatibility.
        if (not report["probe_completed"] or not report["complete_usage_observed"]
                or not report["undeclared_shell_rejected"]):
            raise SystemExit(2)


if __name__ == "__main__":
    main()
