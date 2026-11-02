#!/usr/bin/env python3
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('stage', Path(__file__).with_name('stage-web-images.py'))
assert spec is not None and spec.loader is not None
stage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stage)

class StageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root/'Image').mkdir()
        (self.root/'web').mkdir()
        self.manifest = self.root/'web/manifest.json'

    def save(self, machines):
        self.manifest.write_text(json.dumps({'machines': machines}))

    def test_local_photo_and_js_output(self):
        (self.root/'Image/board.webp').write_bytes(b'fixture')
        self.save([{'image_url':'https://raw.githubusercontent.com/loongson/Firmware/main/Image/board.webp'}])
        stage.stage(self.manifest, self.root)
        self.assertEqual((self.root/'web/assets/Image/board.webp').read_bytes(), b'fixture')
        result=json.loads(self.manifest.read_text())
        self.assertEqual(result['machines'][0]['image_url'], 'assets/Image/board.webp')
        js=self.manifest.with_suffix('.js').read_text()
        self.assertEqual(json.loads(js.removeprefix('window.FIRMWARE_CATALOG = ').rstrip(';\n')),result)

    def test_missing_image_is_placeholder(self):
        self.save([{'image_url':'https://raw.githubusercontent.com/loongson/Firmware/main/Image/absent.jpg'}])
        stage.stage(self.manifest,self.root)
        self.assertIsNone(json.loads(self.manifest.read_text())['machines'][0]['image_url'])

    def test_path_traversal_rejected(self):
        self.save([{'image_path':'Image/../../secret','image_url':None}])
        with self.assertRaises(ValueError):stage.stage(self.manifest,self.root)

if __name__=='__main__':unittest.main()
