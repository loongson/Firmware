#!/usr/bin/env python3
"""Copy repository board images into the static site; never download firmware.

An optional image root is useful for previewing a pending documentation patch.
Missing photos remain placeholders, rather than triggering broken remote images.
"""
import argparse
import json
import shutil
from pathlib import Path
from urllib.parse import unquote, urlsplit


def stage(manifest_path, image_root):
    manifest_path = Path(manifest_path)
    image_root = Path(image_root).resolve()
    data = json.loads(manifest_path.read_text(encoding='utf-8'))
    copied = set()
    missing = []
    for machine in data['machines']:
        image_url = machine.get('image_url')
        image_path = machine.get('image_path')
        if not image_path and image_url:
            path = unquote(urlsplit(image_url).path)
            if '/Image/' in path:
                image_path = 'Image/' + path.split('/Image/', 1)[1]
        if not image_path:
            continue
        source = (image_root / image_path).resolve()
        if not source.is_relative_to(image_root / 'Image'):
            raise ValueError(f'Image outside repository Image/: {image_path}')
        if not source.is_file():
            missing.append(image_path)
            machine['image_url'] = None
            continue
        target = manifest_path.parent / 'assets' / image_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        machine['image_url'] = 'assets/' + image_path
        copied.add(image_path)
    payload = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    manifest_path.write_text(payload, encoding='utf-8')
    manifest_path.with_suffix('.js').write_text(
        'window.FIRMWARE_CATALOG = ' + payload.replace('<', '\\u003c').rstrip() + ';\n',
        encoding='utf-8',
    )
    print(f'Staged {len(copied)} board photos; {len(set(missing))} unavailable.')
    for path in sorted(set(missing)):
        print(f'  Missing photo (placeholder): {path}')


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=root / 'web/manifest.json')
    parser.add_argument('--image-root', type=Path, default=root)
    args = parser.parse_args()
    stage(args.manifest, args.image_root)
