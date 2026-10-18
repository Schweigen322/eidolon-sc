import ast
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import server

class PanelTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = server.DB, server.CHARACTERS, server.BACKUPS
        root = Path(self.tmp.name)
        server.DB = root / 'test.db'
        server.BACKUPS = root / 'devtools-backups'
        server.CHARACTERS = root / 'characters'
        server.CHARACTERS.mkdir()
        (server.CHARACTERS / 'sheets').mkdir()
        (server.CHARACTERS / 'sheets/a.md').write_text('Original', 'utf-8')
        (server.CHARACTERS / 'characters.toml').write_text('[[characters]]\nid="a"\nname="A"\nsheet="sheets/a.md"\n', 'utf-8')
        (server.CHARACTERS / 'gifts.toml').write_text('[[gifts]]\nid="cake"\nname="Cake"\n', 'utf-8')
        repo = Path(__file__).resolve().parents[1]
        with sqlite3.connect(server.DB) as db:
            db.execute('CREATE TABLE users(id TEXT PRIMARY KEY,name TEXT)')
            db.executemany('INSERT INTO users VALUES(?,?)', [('u', 'User'), ('other', 'Other')])
            for name in ('affinity', 'gifts'):
                tree = ast.parse((repo / f'backend/src/eidolon/{name}.py').read_text('utf-8'))
                node = next(n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == '_SCHEMA' for t in n.targets))
                db.executescript(ast.literal_eval(node.value))
    def tearDown(self):
        server.DB, server.CHARACTERS, server.BACKUPS = self.old
        self.tmp.cleanup()
    def change(self, **kwargs):
        return server.mutate({'user': 'u', **kwargs})
    def test_selective_restore(self):
        self.change(action='affinity', character='a', value=0)
        before = self.change(action='gift', gift='cake', count=99)['backup']
        self.change(action='affinity', character='a', value=80)
        self.change(action='balances', draws=7, cards=10)
        server.mutate({'user': 'other', 'action': 'gift', 'gift': 'cake', 'count': 4})
        self.change(action='restore', backup=before)
        data = server.state('u')
        self.assertEqual(data['affinities'][0]['value'], 0)
        self.assertEqual(data['affinities'][0]['cooling'], 1)
        self.assertEqual(data['gift_backpacks'], [])
        self.assertEqual(server.state('other')['gift_backpacks'][0]['count'], 4)
    def test_validation(self):
        for args in [dict(action='gift', gift='cake', count=-1), dict(action='gift', gift='missing', count=2), dict(action='affinity', character='a', value=float('nan')), dict(action='affinity', character='missing', value=50), dict(action='balances', draws=8, cards=0), dict(action='restore', backup='../test.db')]:
            with self.assertRaises(ValueError): self.change(**args)
        self.assertFalse(server.BACKUPS.exists())
    def test_clear_cooldown(self):
        self.change(action='affinity', character='a', value=0)
        self.change(action='affinity', character='a', value=80)
        self.assertEqual(server.state('u')['affinities'][0]['cooling'], 0)
    def test_http_and_sheet_backup(self):
        http = server.HTTPServer(('127.0.0.1', 0), server.Handler)
        thread = threading.Thread(target=http.serve_forever, daemon=True)
        thread.start()
        url = f'http://127.0.0.1:{http.server_port}'
        def request(path, headers, body=None):
            return urlopen(Request(url + path, headers=headers, data=json.dumps(body).encode() if body else None))
        try:
            with self.assertRaises(HTTPError) as err: request('/', {'Host': 'evil.example'})
            self.assertEqual(err.exception.code, 403)
            h = {'Host': 'localhost:8766', 'X-Devtools-Token': server.TOKEN}
            with self.assertRaises(HTTPError) as err: request('/api/sheet', h, {'character': 'a', 'text': 'Changed'})
            self.assertEqual(err.exception.code, 403)
            h['Origin'] = 'http://localhost:8766'
            with request('/api/sheet', h, {'character': 'a', 'text': 'Changed'}) as r: self.assertEqual(r.status, 200)
            self.assertEqual(server.sheet_path('a').read_text(), 'Changed')
            self.assertEqual(next((server.BACKUPS / 'sheets').glob('*.md')).read_text(), 'Original')
        finally:
            http.shutdown(); http.server_close(); thread.join()

if __name__ == '__main__': unittest.main()
