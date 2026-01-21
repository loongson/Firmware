#!/usr/bin/env python3
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List

ROOT = Path(__file__).resolve().parents[1]

LINE_RE = re.compile(r'^([0-9a-fA-F]{64})\s+\*?(\S+)$')
VERSION_RE = re.compile(r'V\d+(?:\.\d+)+')
BASE_RE = re.compile(r'^(UDK\d+|EDK\d+)', re.IGNORECASE)
BOARD_REV_RE = re.compile(r'V\d+\.(?:\d+|x)(?=$|[_-])', re.IGNORECASE)
BRACKET_RE = re.compile(r'\[([^\]]+)\]')
STAGE_TOKEN_RE = re.compile(r'^(beta\d+[a-z0-9]*|prestable\d+[a-z0-9]*|stable\d+[a-z0-9]*|rc\d+[a-z0-9]*)$',
                            re.IGNORECASE)


def get_git_timestamp(path: Path, cache: dict) -> Optional[int]:
    """Return last commit timestamp (unix seconds) for a file path."""
    key = str(path)
    if key in cache:
        return cache[key]
    rel = path.relative_to(ROOT)
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", str(rel)],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            universal_newlines=True,
            check=False,
        )
        out = result.stdout.strip()
        ts = int(out) if out.isdigit() else None
    except Exception:
        ts = None
    cache[key] = ts
    return ts


def parse_base(filename: str) -> Optional[str]:
    match = BASE_RE.match(filename)
    if match:
        return match.group(1).upper()
    token = filename.split('_')[0].split('-')[0]
    return token.upper() if token else None


def parse_versions(filename: str) -> List[str]:
    return VERSION_RE.findall(filename) or []


def parse_board_rev(filename: str, base: Optional[str] = None) -> Optional[str]:
    """Parse mainboard revision (e.g. V1.0, V0.x) from the board identifier part.

    This is *not* the firmware/RefCode version (e.g. V5.0.0344). We intentionally only
    match patterns like V<major>.<minor|x> that end before a third dot.
    """
    name = re.sub(r"\.(fd|bin|zip)$", "", filename, flags=re.IGNORECASE)
    if base and name.upper().startswith(base.upper()):
        name = name[len(base):].lstrip("_-")
    m = BOARD_REV_RE.search(name)
    return m.group(0) if m else None


def parse_build(filename: str) -> Optional[str]:
    lower = filename.lower()
    if "dbg" in lower or "debug" in lower:
        return "dbg"
    if "rel" in lower or "release" in lower:
        return "rel"
    return None


def derive_firmware_type(base: Optional[str]) -> Optional[str]:
    if not base:
        return None
    if base.upper().startswith("EDK"):
        return "UEFI"
    return base.upper()


def strip_platform_prefix(text: str) -> str:
    if not text:
        return text
    return re.sub(r'^(loongarch64|loongarch|loongson)[_-]+', '', text, flags=re.IGNORECASE)


def parse_stage_from_filename(filename: str, base: Optional[str] = None) -> Optional[str]:
    name = re.sub(r"\.(fd|bin|zip)$", "", filename, flags=re.IGNORECASE)
    if base and name.upper().startswith(base.upper()):
        name = name[len(base):].lstrip("_-")
    name = BRACKET_RE.sub("", name).strip("_-")
    name = re.sub(r"(_|-)?(dbg|debug|rel|release)$", "", name, flags=re.IGNORECASE).strip("_-")
    tokens = [t for t in re.split(r"[_-]+", name) if t]
    for token in reversed(tokens):
        if STAGE_TOKEN_RE.match(token):
            return token
    return None


def parse_board_id_and_special(filename: str, base: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """Extract board identifier and optional special tag.

    Naming rule (from spec):
      固件类型_主板标识_[特殊标识]_版本号_产品阶段/版本代号
    """
    name = re.sub(r"\.(fd|bin|zip)$", "", filename, flags=re.IGNORECASE)

    if base and name.upper().startswith(base.upper()):
        name = name[len(base):].lstrip("_-")
    mv = VERSION_RE.search(name)
    mid = name[:mv.start()] if mv else name

    special = None
    bm = BRACKET_RE.search(mid)
    if bm:
        special = bm.group(1)
        mid = BRACKET_RE.sub("", mid)
        mid = re.sub(r"__+", "_", mid).strip("_-")
    if not mv:
        mid = re.sub(r"(_|-)?(dbg|debug|rel|release)$", "", mid, flags=re.IGNORECASE).strip("_-")
        tokens = [t for t in re.split(r"[_-]+", mid) if t]
        if tokens and STAGE_TOKEN_RE.match(tokens[-1]):
            mid = "-".join(tokens[:-1]).strip("_-")
    board_id = strip_platform_prefix(mid.strip("_-")) or None
    return board_id, special


def parse_fw_version_and_stage(refcode_base: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """Split RefCode base into firmware version + stage/variant."""
    if not refcode_base:
        return None, None
    base = refcode_base.strip("_-")
    mv = VERSION_RE.search(base)
    if not mv:
        return None, base or None
    version = mv.group(0)
    rest = (base[mv.end():] or "").strip("_-")
    stage = rest or None
    return version, stage


def normalize_stage(stage: Optional[str]) -> Optional[str]:
    if not stage:
        return None
    s = stage.strip("_-")
    m = re.match(r"^(stable)(\d{6})$", s, flags=re.IGNORECASE)
    if m:
        # stableYYYYMM -> stableYYMM
        return f"{m.group(1)}{m.group(2)[-4:]}"
    return s

def normalize_fw_version(ver: Optional[str]) -> Optional[str]:
    if not ver:
        return None
    v = ver.strip()
    # If already has 4 numeric components like V5.0.0.343, keep as-is.
    if re.match(r"^V\d+\.\d+\.\d+\.\d+$", v, flags=re.IGNORECASE):
        return v
    m = re.match(r"^V(\d+)\.(\d+)\.(\d+)$", v, flags=re.IGNORECASE)
    if not m:
        return v
    a, b, c = m.group(1), m.group(2), m.group(3)
    # If last component is 4 digits (e.g. 0343), split to 0.343
    if len(c) == 4 and c.isdigit():
        return f"V{a}.{b}.{c[0]}.{c[1:]}"
    return v

def make_version_full(fw_version: Optional[str], stage: Optional[str]) -> Optional[str]:
    v = normalize_fw_version(fw_version)
    s = normalize_stage(stage)
    if v and s:
        return f"{v}_{s}"
    return v or s

def parse_refcode_base(filename: str, board_rev: Optional[str], base: Optional[str] = None) -> Optional[str]:
    """RefCode Base / UEFI base version string."""
    name = re.sub(r"\.(fd|bin|zip)$", "", filename, flags=re.IGNORECASE)

    if base and name.upper().startswith(base.upper()):
        name = name[len(base):].lstrip("_-")
    cut_idx = None
    if board_rev:
        i = name.find(board_rev)
        if i != -1:
            cut_idx = i + len(board_rev)
    if cut_idx is None:
        j = name.find('_')
        cut_idx = j + 1 if j != -1 else 0

    tail = name[cut_idx:].strip("_-")
    tail = BRACKET_RE.sub("", tail).strip("_-")
    tail = re.sub(r"(_|-)?(dbg|debug|rel|release)$", "", tail, flags=re.IGNORECASE).strip("_-")
    if not VERSION_RE.search(tail):
        return None
    return tail or None


def parse_date_key(text: str) -> Optional[Tuple[int, int, int]]:
    match = re.search(r"(20\d{6})", text)
    if match:
        val = match.group(1)
        return (int(val[0:4]), int(val[4:6]), int(val[6:8]))
    match = re.search(r"(20\d{4})", text)
    if match:
        val = match.group(1)
        return (int(val[0:4]), int(val[4:6]), 0)
    match = re.search(r"(\d{2})(\d{2})[_-]?(\d{2})(\d{2})", text)
    if match:
        yy, mm, dd1, dd2 = match.groups()
        day = int(dd1 + dd2)
        return (2000 + int(yy), int(mm), day)
    match = re.search(r"(?<!\d)(\d{2})(\d{2})(?!\d)", text)
    if match:
        yy, mm = match.groups()
        return (2000 + int(yy), int(mm), 0)
    return None


def version_key(version: Optional[str]) -> Tuple[int, ...]:
    if not version:
        return ()
    nums = re.findall(r"\d+", version)
    return tuple(int(n) for n in nums)


def sort_key(artifact: dict) -> tuple:
    # Prefer filesystem timestamp if available, else fall back to date-like tokens in refcode/path.
    ts = artifact.get("timestamp") or 0
    text = f"{artifact.get('refcode_base') or ''} {artifact.get('path') or ''}"
    date_key = parse_date_key(text) or (0, 0, 0)
    return (ts, date_key, version_key(artifact.get("refcode_base")), artifact.get("edk") or "", artifact.get("build") or "")


def main() -> None:
    sha_files = sorted(ROOT.rglob("SHA256SUMS.txt"))
    machines = []
    git_ts_cache = {}

    for sha_path in sha_files:
        rel_dir = sha_path.parent.relative_to(ROOT)
        parts = rel_dir.parts

        collection = None
        series = None
        category = None
        model = None

        if len(parts) >= 1 and parts[0] == "MultiArchUefiSupport":
            collection = parts[0]
            if len(parts) >= 2:
                series = parts[1]
            if len(parts) >= 3:
                category = parts[2]
            if len(parts) >= 4:
                model = parts[3]
        elif len(parts) >= 3 and parts[0].endswith("Series"):
            series = parts[0]
            category = parts[1]
            model = parts[2]
        else:
            model = parts[-1] if parts else str(rel_dir)

        artifacts = []
        with sha_path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                match = LINE_RE.match(line)
                if not match:
                    continue
                sha256, filename = match.groups()
                artifact_path = str(rel_dir / filename)

                edk = parse_base(filename)
                firmware_type = derive_firmware_type(edk)
                board_rev = parse_board_rev(filename, edk)
                refcode_base = parse_refcode_base(filename, board_rev, edk)
                build = parse_build(filename)
                board_id, special_tag = parse_board_id_and_special(filename, edk)
                fw_version, stage = parse_fw_version_and_stage(refcode_base)
                if not stage:
                    stage = parse_stage_from_filename(filename, edk)

                # File mtime (best-effort) for sorting
                file_path = (ROOT / rel_dir / filename)
                try:
                    ts = int(file_path.stat().st_mtime)
                    dt = datetime.fromtimestamp(ts).isoformat(timespec='seconds')
                except Exception:
                    ts = 0
                    dt = None

                git_ts = get_git_timestamp(file_path, git_ts_cache)
                git_dt = datetime.fromtimestamp(git_ts).isoformat(timespec='seconds') if git_ts else None

                artifacts.append(
                    {
                        # New semantic fields (schema v2)
                        "edk": edk,
                        "edk2_baseline": edk,
                        "firmware_type": firmware_type,
                        "version_full": make_version_full(fw_version, stage),
                        "board_rev": board_rev,
                        "refcode_base": refcode_base,
                        "build": build,
                        "board_id": board_id,
                        "special_tag": special_tag,
                        "fw_version": fw_version,
                        "stage": stage,
                        "timestamp": ts,
                        "datetime": dt,
                        "git_timestamp": git_ts or 0,
                        "git_datetime": git_dt,
                        # Existing fields kept for backward compatibility
                        "base": edk,
                        "version": board_rev,
                        "release_tag": refcode_base,
                        "secure_boot": None,
                        "gmem": None,
                        "path": artifact_path,
                        "sha256": sha256.lower(),
                        "checksum_source": str(sha_path.relative_to(ROOT)),
                    }
                )

        latest = []
        if artifacts:
            latest_map = {}
            for artifact in artifacts:
                key = (artifact.get("edk"), artifact.get("board_rev"), artifact.get("build"))
                if key not in latest_map or sort_key(artifact) > sort_key(latest_map[key]):
                    latest_map[key] = artifact
            latest = list(latest_map.values())
            latest.sort(key=lambda a: (a.get("edk") or "", a.get("board_rev") or "", a.get("build") or ""))

        machines.append(
            {
                "collection": collection,
                "series": series,
                "category": category,
                "model": model,
                "group_path": str(rel_dir),
                "latest": latest,
                "artifacts": artifacts,
            }
        )

    manifest = {
        "schema_version": "2.0",
        "coverage": "full",
        "generated_from": "SHA256SUMS.txt",
        "latest_rule": "date_desc_then_refcode_desc",
        "machines": machines,
    }

    out_path = ROOT / "manifest.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=False)
        f.write("\n")

    web_path = ROOT / "web" / "manifest.json"
    if web_path.parent.exists():
        with web_path.open("w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, sort_keys=False)
            f.write("\n")


if __name__ == "__main__":
    main()
