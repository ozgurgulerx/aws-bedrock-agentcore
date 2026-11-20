import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('library', Path(__file__).with_name('library.py'))
lib = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lib)
URL = 'https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime.html'
HTML = '''<html><head><title>Runtime</title><meta name="date" content="2026-10-01"></head><body><nav>noise</nav><div id="main-content"><h1 id="runtime">Runtime</h1><p>Agent runtime identity and memory documentation with enough text for validation.</p><h2 id="code">Example</h2><pre><code>x = 1\nprint(x)</code></pre><table><tr><th>Key</th><th>Value</th></tr><tr><td>Runtime</td><td>Secure</td></tr></table><a href="memory.html">Memory</a></div></body></html>'''
ITEM = {'url': URL, 'product': 'agentcore', 'topics': ['runtime']}

class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root/'sources.json').write_text(json.dumps([ITEM]))
    def tearDown(self): self.temp.cleanup()
    def fake_fetch(self, item): return {**item, **lib.extract(HTML, item['url']), 'url': item['url']}
    def test_extract(self):
        doc = lib.extract(HTML, URL)
        self.assertIn('```\nx = 1\nprint(x)\n```', doc['body'])
        self.assertIn('| Key | Value |', doc['body'])
        self.assertIn('https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html', doc['body'])
        self.assertNotIn('noise', doc['body'])
        self.assertEqual(doc['source_modified'], '2026-10-01')
        self.assertEqual(doc['title'], 'Runtime')
    def test_reject_empty(self):
        for html in ['<html>landing</html>', '<main id="main-content"><h1>Empty</h1></main>']:
            with self.assertRaises(ValueError): lib.extract(html, URL)
    def test_source_validation(self):
        for url in ['http://docs.aws.amazon.com/a', 'https://evil.com/a', 'https://docs.aws.amazon.com/']:
            with self.assertRaises(ValueError): lib.validate_source({**ITEM, 'url': url})
        with self.assertRaises(ValueError): lib.validate_source({**ITEM, 'product': '../x'})
        self.assertEqual(lib.validate_source(ITEM), ITEM)
    def test_fetch_and_redirect(self):
        from subprocess import CompletedProcess
        good = CompletedProcess([], 0, HTML+'\n'+URL, '')
        with patch.object(lib.subprocess, 'run', return_value=good):
            self.assertIn('body', lib.fetch(ITEM))
        bad = CompletedProcess([], 0, HTML+'\nhttps://docs.aws.amazon.com/', '')
        with patch.object(lib.subprocess, 'run', return_value=bad):
            self.assertIn('error', lib.fetch(ITEM))
        fail = CompletedProcess([], 22, '', 'HTTP 404')
        with patch.object(lib.subprocess, 'run', return_value=fail):
            self.assertIn('404', lib.fetch(ITEM)['error'])
    def test_refresh_unchanged_changed_failure_and_search(self):
        with patch.object(lib, 'fetch', side_effect=self.fake_fetch):
            self.assertEqual(lib.refresh(self.root), 0)
            manifest = lib.read_json(self.root/'manifest.json', [])
            target = self.root/manifest[0]['path']
            stamp = target.stat().st_mtime_ns
            self.assertEqual(lib.refresh(self.root), 0)
            self.assertEqual(target.stat().st_mtime_ns, stamp)
        changed = {**self.fake_fetch(ITEM), 'body': self.fake_fetch(ITEM)['body']+'\nChanged new policy.\n'}
        with patch.object(lib, 'fetch', return_value=changed): self.assertEqual(lib.refresh(self.root), 0)
        self.assertTrue(list((self.root/'backups').rglob('*.diff')))
        previous = target.read_text()
        with patch.object(lib, 'fetch', return_value={**ITEM, 'error': 'offline'}):
            self.assertEqual(lib.refresh(self.root), 1)
        self.assertEqual(target.read_text(), previous)
        self.assertEqual(lib.read_json(self.root/'manifest.json', [])[0]['status'], 'stale')
        rows = lib.search(self.root, 'runtime', product='agentcore', topic='runtime')
        self.assertTrue(rows)
        self.assertIn(URL, rows[0][4])
        with self.assertRaises(ValueError): lib.search(self.root, '')
    def test_failure_without_previous_and_lock(self):
        with patch.object(lib, 'fetch', return_value={**ITEM, 'error': 'offline'}):
            self.assertEqual(lib.refresh(self.root), 1)
        self.assertEqual(lib.read_json(self.root/'manifest.json', []), [])
        with lib.lock(self.root):
            with self.assertRaises(RuntimeError):
                with lib.lock(self.root): pass
    def test_native_markdown_and_representation_change(self):
        from subprocess import CompletedProcess
        native = '# Runtime\n\n' + 'Runtime native documentation. ' * 10
        response = CompletedProcess([], 0, native+'\n'+URL[:-5]+'.md', '')
        with patch.object(lib.subprocess, 'run', return_value=response):
            result = lib.fetch(ITEM)
        self.assertEqual(result['representation'], 'native-markdown')
        with patch.object(lib, 'fetch', side_effect=self.fake_fetch): lib.refresh(self.root)
        with patch.object(lib, 'fetch', return_value=result): lib.refresh(self.root)
        self.assertEqual(lib.read_json(self.root/'refresh-report.json', {})['counts']['representation-changed'], 1)
    def test_cli_and_invalid_registry(self):
        self.assertEqual(lib.main(['search', '', '--root', str(self.root)]), 1)
        with patch.object(lib, 'fetch', side_effect=self.fake_fetch):
            self.assertEqual(lib.main(['refresh', '--root', str(self.root)]), 0)
        self.assertEqual(lib.main(['reindex', '--root', str(self.root)]), 0)
        self.assertEqual(lib.main(['search', 'runtime', '--root', str(self.root)]), 0)
        (self.root/'sources.json').write_text('[]')
        self.assertEqual(lib.main(['refresh', '--root', str(self.root)]), 1)
    def test_bad_markdown_falls_back_to_html(self):
        from subprocess import CompletedProcess
        good = CompletedProcess([], 0, HTML+'\n'+URL, '')
        for response in ['not markdown\n'+URL[:-5]+'.md', HTML+'\nhttps://docs.aws.amazon.com/']:
            with patch.object(lib.subprocess, 'run', side_effect=[CompletedProcess([], 0, response, ''), good]) as run:
                result = lib.fetch(ITEM)
                self.assertEqual(result['representation'], 'html-converted')
                self.assertEqual(run.call_count, 2)
    def test_missing_body_with_different_representation(self):
        old = {URL: {**ITEM, 'representation': 'web-extract'}}
        entry, outcome = lib.merge_result(self.root, self.fake_fetch(ITEM), old, '2026-11-04')
        self.assertEqual(outcome, 'added')
        self.assertTrue((self.root/entry['path']).exists())
    def test_invalid_registry_entry_fails_before_writes(self):
        for item in [None, {}, {**ITEM, 'url': None}, {**ITEM, 'product': 1},
                     {k: v for k, v in ITEM.items() if k != 'topics'}, {**ITEM, 'topics': [1]}]:
            with self.assertRaises(ValueError): lib.validate_source(item)
            (self.root/'sources.json').write_text(json.dumps([item]))
            self.assertEqual(lib.main(['refresh', '--root', str(self.root)]), 1)
            self.assertFalse((self.root/'manifest.json').exists())
    def test_sections_fenced(self):
        parts = lib.sections('# Start\nHi\n```\n# code\n```\n## End\nbye')
        self.assertEqual(len(parts), 2)
        self.assertIn('# code', parts[0][1])

if __name__ == '__main__': unittest.main()
