#!/usr/bin/env python3
"""Generate a deterministic catalog from the complete HEAD tree, not checksums.

Only small README/checksum blobs are read. Firmware is never opened or fetched.
"""
import argparse
import json
import os
import posixpath
import re
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path, PurePosixPath
from urllib.parse import quote, unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
SUFFIXES = {".tar.gz": "archive", ".tar.xz": "archive", ".tar.bz2": "archive",
            ".tar.zst": "archive", ".fd.enc": "encrypted", ".tgz": "archive",
            ".zip": "archive", ".tar": "archive", ".fd": "image",
            ".bin": "image", ".efi": "tool", ".iso": "tool"}
FW_RE = re.compile(r"(?<![A-Za-z0-9])[vV]\d+(?:\.\d+){2,}(?![.\d])")
REV_RE = re.compile(r"(?<![A-Za-z0-9])[vV]\d+\.(?:\d+|x)(?:-\d+)?(?![.\d])", re.I)
STAGE_RE = re.compile(r"(?<![A-Za-z0-9])(?:pre-beta|prestable|stable|beta|rc)\d+(?![A-Za-z0-9])", re.I)
DATE_RE = re.compile(r"(?<![A-Za-z0-9])(20\d{6}(?:\d{6})?)(?![A-Za-z0-9])")
SUPPORT_RE = re.compile(r"https://[^\s<>\"')]+/helpdesk_bios/?", re.I)


def git(root, *args):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_NO_LAZY_FETCH="1")
    # Only callers reading explicitly selected small text blobs may lazy-fetch.
    if args and args[0] == "show":
        env.pop("GIT_NO_LAZY_FETCH", None)
    return subprocess.run(["git", *args], cwd=root, env=env, check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          timeout=20).stdout.decode("utf-8", "replace")


def classify(path):
    for suffix in sorted(SUFFIXES, key=len, reverse=True):
        if path.lower().endswith(suffix):
            return SUFFIXES[suffix], suffix[1:]
    return None


def group_for(path):
    parts = PurePosixPath(path).parts
    if parts[0] == "MultiArchUefiSupport":
        return "/".join(parts[:4]) if len(parts) >= 5 else None
    if parts[0].endswith("Series"):
        return "/".join(parts[:3]) if len(parts) >= 4 else None
    if parts[0] in {"LoongArchVirtMachine", "Memtest86+", "LoongsonBackupOS", "tools", "Tools", "QEMU"}:
        return parts[0] if len(parts) >= 2 else None
    return None


def valid_date(token):
    try:
        return datetime.strptime(token, "%Y%m%d%H%M%S" if len(token) == 14 else "%Y%m%d").date().isoformat()
    except ValueError:
        return None


def parse_filename(filename):
    classification = classify(filename)
    if classification is None:
        raise ValueError("Unsupported artifact suffix: " + filename)
    kind, fmt = classification
    stem = filename[:-(len(fmt) + 1)]
    fw = FW_RE.search(stem)
    # A two-component revision must not be a truncated firmware version.
    rev = REV_RE.search(stem[:fw.start()] if fw else stem)
    stage = STAGE_RE.search(stem)
    baseline = re.match(r"(?:UDK\d+|EDK\d+(?:_\d{6})?)(?=[_-])", stem, re.I)
    build = re.search(r"(?:^|[_-])(dbg|debug|rel|release)(?=$|[_-])", stem, re.I)
    variants = re.findall(r"(?<![A-Za-z0-9])(?:NoGmem|Gmem|mainline-dvfs)(?![A-Za-z0-9])", stem, re.I)
    role = re.search(r"QEMU_(?:EFI|VARS)", stem, re.I)
    dates = [valid_date(m.group(1)) for m in DATE_RE.finditer(stem)]
    version = fw.group() if fw else None
    stage_text = stage.group() if stage else None
    if stage is not None:
        # Keep the spelling AND separator exactly as published.
        version = stem[fw.start():stage.end()] if fw and re.fullmatch(r"[_-]+", stem[fw.end():stage.start()]) else (version or stage_text)
    return {"kind": kind, "format": fmt, "version": version,
            "firmware_version": fw.group() if fw else None,
            "hardware_rev": rev.group() if rev else None,
            "baseline": baseline.group() if baseline else None,
            "rc_baseline": stage_text.lower() if stage_text else None,
            "variant": "+".join(variants) or None,
            "build": ({"debug": "dbg", "release": "rel"}.get(build[1].lower(), build[1].lower()) if build else None),
            "role": role.group().upper() if role else None,
            "build_date": next((d for d in dates if d), None)}


def order_artifacts(artifacts):
    """Newest repository changes first; never select or hide firmware versions."""
    ordered = sorted(artifacts, key=lambda a: (a.get("filename", a["path"]), a["path"]))
    ordered.sort(key=lambda a: datetime.fromisoformat(a["updated_at"]).timestamp()
                 if a.get("updated_at") else float("-inf"), reverse=True)
    return ordered


def read_text(root, path, warnings):
    local = root / path
    if local.is_file():
        return local.read_text(encoding="utf-8", errors="replace")
    try:
        return git(root, "show", "HEAD:" + path)
    except (subprocess.SubprocessError, OSError) as exc:
        warnings.append("Unable to read metadata blob: " + path + " (" + type(exc).__name__ + ")")
        return ""


def readme_image(text, readme, tracked):
    for ref in re.findall(r"!\[[^\]]*\]\(([^\s)]+)", text):
        ref = unquote(ref.strip("<>"))
        parsed = urlparse(ref)
        if parsed.scheme:
            # Only images belonging to this upstream repository, never arbitrary photos.
            if parsed.netloc not in {"github.com", "raw.githubusercontent.com"} or not parsed.path.startswith("/loongson/Firmware/"):
                continue
            match = re.search(r"/(Image/[^?#]+)$", parsed.path)
            path = match[1] if match else ""
        else:
            path = posixpath.normpath(posixpath.join(posixpath.dirname(readme), ref))
        if path.startswith("Image/") and path in tracked:
            return path
    return None


def generate(root, metadata=None):
    root = Path(root)
    metadata = metadata or {}
    warnings = []
    source = git(root, "rev-parse", "HEAD").strip()
    tracked = set(git(root, "ls-tree", "-r", "--name-only", "-z", "HEAD").split("\0")) - {""}
    raw = "https://raw.githubusercontent.com/loongson/Firmware/" + source + "/"
    blob = "https://github.com/loongson/Firmware/blob/" + source + "/"
    checksums = {}
    for path in sorted(tracked):
        if PurePosixPath(path).name == "SHA256SUMS.txt":
            for line in read_text(root, path, warnings).splitlines():
                match = re.match(r"^([0-9a-fA-F]{64})\s+\*?(.+?)\s*$", line)
                if match:
                    target = posixpath.normpath(posixpath.join(posixpath.dirname(path), match[2]))
                    if target in tracked:
                        checksums[target] = match[1].lower()
    shallow = git(root, "rev-parse", "--is-shallow-repository").strip() == "true"
    if shallow:
        warnings.append("Shallow history: updated_at is null; boundary commits are not reliable file update dates.")
    times = {}
    if not shallow:
        # One history walk, metadata only. Committer date is not a push/release date.
        try:
            history = git(root, "log", "--no-renames", "--format=CATALOG_DATE:%cI", "--name-only", "HEAD")
            stamp = None
            for line in history.splitlines():
                if line.startswith("CATALOG_DATE:"):
                    stamp = line[len("CATALOG_DATE:"):]
                elif line in tracked and line not in times:
                    times[line] = stamp
        except subprocess.SubprocessError:
            warnings.append("Git history unavailable: updated_at is null.")
    machine_meta = metadata.get("machines", {})
    groups = defaultdict(list)
    for path in sorted(tracked):
        group = group_for(path)
        if group and (classify(path) or PurePosixPath(path).name.upper().startswith("README")):
            groups[group].append(path)
    for group in machine_meta:
        groups.setdefault(group, [])
    machines = []
    for group, paths in sorted(groups.items()):
        meta = machine_meta.get(group, {})
        parts = group.split("/")
        multi = parts[0] == "MultiArchUefiSupport"
        is_board = len(parts) >= (4 if multi else 3)
        machine = {"id": group, "group_path": group, "model": meta.get("model", parts[-1]),
                   "series": parts[1 if multi else 0] if is_board else None,
                   "category": meta.get("category", parts[2 if multi else 1] if is_board else None),
                   "collection": parts[0] if multi or not is_board else None,
                   "image_url": None, "readme_url": None, "readme_zh_url": None,
                   "support_url": None, "upstream_url": meta.get("upstream_url"),
                   "updated_at": None, "artifacts": []}
        image = meta.get("image_path")
        support = meta.get("support_url")
        for name, field in (("README.md", "readme_url"), ("README_CN.md", "readme_zh_url"), ("README_ZH.md", "readme_zh_url")):
            path = group + "/" + name
            if path in tracked:
                machine[field] = blob + quote(path, safe="/")
                text = read_text(root, path, warnings)
                image = image or readme_image(text, path, tracked)
                found = SUPPORT_RE.search(text)
                support = support or (found.group() if found else None)
        if support and SUPPORT_RE.fullmatch(support):
            machine["support_url"] = support
        if image and image.startswith("Image/") and ".." not in PurePosixPath(image).parts:
            if image in tracked:
                machine["image_url"] = raw + quote(image, safe="/")
            elif (root / image).is_file():
                machine["image_url"] = "../" + quote(image, safe="/")
        if meta.get("image_url"):
            machine["image_url"] = meta["image_url"]
        if meta.get("hide_image"):
            machine["image_url"] = None
        for path in paths:
            if not classify(path):
                continue
            filename = PurePosixPath(path).name
            item = parse_filename(filename)
            overrides = metadata.get("artifacts", {}).get(path, {})
            item["rc_baseline"] = overrides.get("rc_baseline", item["rc_baseline"])
            item["edk2_baseline"] = overrides.get("edk2_baseline", metadata.get("upstream_baselines", {}).get((item["baseline"] or "").upper()))
            release = overrides.get("release_date")
            if release:
                try:
                    datetime.strptime(release, "%Y-%m-%d")
                except ValueError:
                    warnings.append("Invalid release_date metadata: " + path)
                    release = None
            item.update({"path": path, "filename": filename, "url": raw + quote(path, safe="/"),
                         "sha256": checksums.get(path), "size_bytes": None,
                         "release_date": release, "updated_at": times.get(path)})
            machine["artifacts"].append(item)
        machine["artifacts"] = order_artifacts(machine["artifacts"])
        stamps = [times[p] for p in paths if times.get(p)]
        machine["updated_at"] = max(stamps, key=datetime.fromisoformat) if stamps else None
        machine["external_only"] = bool(machine["support_url"] and not machine["artifacts"])
        machines.append(machine)
    release_notes = discover_release_notes(tracked, metadata, blob, warnings)
    return {"schema_version": "3.0", "source_commit": source, "machines": machines,
            "release_notes": release_notes, "warnings": warnings}


def discover_release_notes(tracked, metadata, blob, warnings):
    """Discover language-suffixed documents; explicit entries resolve exceptions."""
    pattern = re.compile(r"^docs/changelist_(V\d+(?:\.\d+){2,})-((?:pre-beta|prestable|stable|beta|rc)\d+)-(CN|EN)\.md$", re.I)
    entries = {}
    conflicts = set()
    for path in sorted(tracked):
        match = pattern.fullmatch(path)
        if not match:
            continue
        version, baseline, language = match.groups()
        baseline, language = baseline.lower(), {"cn": "zh", "en": "en"}[language.lower()]
        key = (baseline, version.lower())
        entry = entries.setdefault(key, {"baseline": baseline, "version": version,
                                        "title": version + "-" + baseline, "documents": {}})
        collision = (key, language)
        if language in entry["documents"] or collision in conflicts:
            entry["documents"].pop(language, None)
            conflicts.add(collision)
            warnings.append("Ambiguous release notes language: " + path)
        else:
            entry["documents"][language] = path
    for override in metadata.get("release_notes", []):
        baseline = override["baseline"]
        version_match = FW_RE.search(override.get("title", ""))
        version = override.get("version", version_match.group() if version_match else None)
        key = (baseline, version.lower() if version else None)
        entry = entries.setdefault(key, {"baseline": baseline, "version": version, "documents": {}})
        entry["title"] = override["title"]
        entry["default"] = bool(override.get("default", False))
        entry["documents"].update(override.get("documents", {}))
    result = []
    for entry in entries.values():
        documents = {}
        for language, path in entry["documents"].items():
            if language not in {"zh", "en"} or not path.startswith("docs/") or path not in tracked:
                warnings.append("Release notes document unavailable: " + path)
                continue
            documents[language] = blob + quote(path, safe="/")
        if documents:
            result.append({**entry, "documents": documents})
    result.sort(key=lambda e: (e["baseline"], e["title"]))
    result.sort(key=lambda e: tuple(int(n) for n in e["version"][1:].split("."))
                if e["version"] else (), reverse=True)
    return result



def write_outputs(manifest, output):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    output.write_text(text, encoding="utf-8")
    output.with_suffix(".js").write_text("window.FIRMWARE_CATALOG = " + text.rstrip().replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029") + ";\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--metadata", type=Path)
    args = parser.parse_args()
    metadata_path = args.metadata or args.root / "scripts/catalog-metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
    manifest = generate(args.root, metadata)
    output = args.output or args.root / "web/manifest.json"
    write_outputs(manifest, output)
    print(json.dumps({"output": str(output), "javascript": str(output.with_suffix('.js')),
                      "machines": len(manifest["machines"]),
                      "artifacts": sum(len(m["artifacts"]) for m in manifest["machines"]),
                      "warnings": manifest["warnings"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
