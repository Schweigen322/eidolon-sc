"""Local companion for editing this deployment's play state; standard library only."""
import json
import math
import os
from pathlib import Path
import secrets
import sqlite3
from datetime import datetime, timezone, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
import tomllib

ROOT = Path(__file__).parent
DB = Path(os.environ.get('EIDOLON_DATABASE_PATH', '/data/eidolon.db'))
CHARACTERS = Path(os.environ.get('DEVTOOLS_CHARACTERS', '/characters'))
BACKUPS = DB.parent / 'devtools-backups'
TOKEN = secrets.token_urlsafe(32)
HOSTS = {'localhost:8766', '127.0.0.1:8766'}
TABLES = ('affinities', 'gift_balances', 'gift_backpacks')


def catalog():
    characters = tomllib.loads((CHARACTERS / 'characters.toml').read_text('utf-8'))['characters']
    gifts = tomllib.loads((CHARACTERS / 'gifts.toml').read_text('utf-8'))['gifts']
    return characters, gifts


def connect():
    db = sqlite3.connect(f'{DB.as_uri()}?mode=rw', uri=True, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    return db


def backup(db):
    BACKUPS.mkdir(exist_ok=True)
    name = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.db'
    with sqlite3.connect(BACKUPS / name) as dest:
        db.backup(dest)
    return name


def user_exists(db, user):
    if not db.execute('SELECT 1 FROM users WHERE id=?', (user,)).fetchone():
        raise ValueError('请选择有效用户')


def integer(value, high):
    if type(value) is not int or not 0 <= value <= high:
        raise ValueError(f'数量必须是 0 到 {high} 的整数')
    return value


def state(user=None):
    characters, gifts = catalog()
    with connect() as db:
        users = [dict(r) for r in db.execute('SELECT id,name FROM users ORDER BY name,id')]
        result = dict(users=users, characters=[{'id': c['id'], 'name': c['name']} for c in characters],
                      gifts=[{'id': g['id'], 'name': g['name']} for g in gifts],
                      backups=sorted([p.name for p in BACKUPS.glob('*.db')], reverse=True)[:30])
        if user:
            user_exists(db, user)
            for table in TABLES:
                result[table] = [dict(r) for r in db.execute(f'SELECT * FROM {table} WHERE user_id=?', (user,))]
        return result


def mutate(body):
    action, user = body.get('action'), body.get('user')
    chars, gifts = catalog()
    with connect() as db:
        user_exists(db, user)
        now = datetime.now(timezone.utc)
        day = now.astimezone(timezone(timedelta(hours=8))).date().isoformat()
        # Validate the entire change before taking a backup or writing anything.
        if action == 'affinity':
            char = body.get('character')
            if char not in {c['id'] for c in chars}:
                raise ValueError('无效角色')
            value = body.get('value')
            if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 100:
                raise ValueError('好感度必须在 0 到 100 之间')
        elif action == 'gift':
            gift = body.get('gift')
            if gift not in {g['id'] for g in gifts}:
                raise ValueError('无效礼物')
            count = integer(body.get('count'), 9999)
        elif action == 'balances':
            draws = integer(body.get('draws'), 7)
            cards = integer(body.get('cards'), 9999)
        elif action == 'restore':
            name = body.get('backup', '')
            if not isinstance(name, str) or Path(name).name != name or not (BACKUPS / name).is_file():
                raise ValueError('请选择现有备份')
            with sqlite3.connect(f'{(BACKUPS / name).as_uri()}?mode=ro', uri=True) as source:
                source.row_factory = sqlite3.Row
                restored = {t: [dict(r) for r in source.execute(f'SELECT * FROM {t} WHERE user_id=?', (user,))] for t in TABLES}
        else:
            raise ValueError('未知操作')
        saved = backup(db)
        db.execute('BEGIN IMMEDIATE')
        if action == 'affinity':
            db.execute('''INSERT INTO affinities(user_id,character_id,value,updated_at,cooling,gained_today,gained_on)
                VALUES(?,?,?,?,?,0,?) ON CONFLICT(user_id,character_id) DO UPDATE SET
                value=excluded.value,updated_at=excluded.updated_at,cooling=excluded.cooling,gained_today=0,gained_on=excluded.gained_on''',
                (user, char, value, now.isoformat(), int(value == 0), day))
        elif action == 'gift':
            db.execute('''INSERT INTO gift_backpacks(user_id,gift_id,count) VALUES(?,?,?)
                ON CONFLICT(user_id,gift_id) DO UPDATE SET count=excluded.count''', (user, gift, count))
        elif action == 'balances':
            db.execute('''INSERT INTO gift_balances(user_id,draws,given_on,reset_cards) VALUES(?,?,?,?)
                ON CONFLICT(user_id) DO UPDATE SET draws=excluded.draws,given_on=excluded.given_on,reset_cards=excluded.reset_cards''',
                (user, draws, day, cards))
        else:
            for table in TABLES:
                db.execute(f'DELETE FROM {table} WHERE user_id=?', (user,))
                for row in restored[table]:
                    cols = ','.join(row)
                    marks = ','.join('?' for _ in row)
                    db.execute(f'INSERT INTO {table} ({cols}) VALUES ({marks})', tuple(row.values()))
        return {'message': '已保存；刷新聊天页面查看。恢复只影响所选用户的好感度和背包。', 'backup': saved}


def sheet_path(character):
    chars, _ = catalog()
    entry = next((c for c in chars if c['id'] == character), None)
    if entry is None:
        raise ValueError('无效角色')
    path = (CHARACTERS / entry['sheet']).resolve()
    if not path.is_relative_to((CHARACTERS / 'sheets').resolve()):
        raise ValueError('无效人设路径')
    return path


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, data, mime='application/json; charset=utf-8'):
        encoded = data.encode('utf-8') if isinstance(data, str) else json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(encoded)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "frame-ancestors 'none'; default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'")
        self.end_headers()
        self.wfile.write(encoded)

    def allowed(self):
        return self.headers.get('Host') in HOSTS

    def do_GET(self):
        from urllib.parse import urlsplit, parse_qs
        if not self.allowed():
            return self.reply(403, {'error': '仅允许本机访问'})
        url = urlsplit(self.path)
        args = parse_qs(url.query)
        try:
            if url.path == '/':
                return self.reply(200, (ROOT / 'panel.html').read_text('utf-8').replace('__TOKEN__', TOKEN), 'text/html; charset=utf-8')
            if self.headers.get('X-Devtools-Token') != TOKEN:
                return self.reply(403, {'error': '请刷新开发者面板'})
            if url.path == '/api/state':
                return self.reply(200, state(args.get('user', [None])[0]))
            if url.path == '/api/sheet':
                p = sheet_path(args.get('character', [''])[0])
                return self.reply(200, {'text': p.read_text('utf-8')})
            self.reply(404, {'error': '不存在'})
        except (ValueError, OSError, sqlite3.Error) as e:
            self.reply(400, {'error': str(e)})

    def do_POST(self):
        if not self.allowed() or self.headers.get('Origin') not in {'http://' + h for h in HOSTS} or self.headers.get('X-Devtools-Token') != TOKEN:
            return self.reply(403, {'error': '来源校验失败，请从本机打开面板'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 262144:
                raise ValueError('请求大小无效')
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                raise ValueError('请求格式错误')
            if self.path == '/api/sheet':
                p = sheet_path(body.get('character'))
                content = body.get('text')
                if not isinstance(content, str) or not content.strip() or len(content) > 80000:
                    raise ValueError('人设不能为空，最多 80000 字符')
                folder = BACKUPS / 'sheets'
                folder.mkdir(parents=True, exist_ok=True)
                name = p.stem + '-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.md'
                (folder / name).write_text(p.read_text('utf-8'), 'utf-8')
                p.write_text(content, 'utf-8')
                return self.reply(200, {'message': '人设已保存并备份。点击“重启后端”启动器使修改生效，再新建对话测试。'})
            if self.path != '/api/change':
                return self.reply(404, {'error': '不存在'})
            self.reply(200, mutate(body))
        except (ValueError, OSError, sqlite3.Error, TypeError) as e:
            self.reply(400, {'error': str(e)})

    def log_message(self, fmt, *args):
        pass  # Do not log user IDs, character sheets, or payloads.


if __name__ == '__main__':
    print('Developer panel: http://localhost:8766', flush=True)
    HTTPServer(('0.0.0.0', 8766), Handler).serve_forever()
