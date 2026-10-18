"""Owner-only play-state editing; snapshots precede writes."""
import math
import sqlite3
from contextlib import closing
from pathlib import Path
from datetime import datetime, timezone, timedelta
import tomllib
from typing import Any

TABLES = ("affinities", "gift_balances", "gift_backpacks")

class DeveloperData:
    def __init__(self, db: Path, characters: Path):
        self.DB = db.resolve()
        self.CHARACTERS = characters.resolve()
        self.BACKUPS = self.DB.parent / "devtools-backups"

    def catalog(self):
        characters = tomllib.loads((self.CHARACTERS / 'characters.toml').read_text('utf-8'))['characters']
        gifts = tomllib.loads((self.CHARACTERS / 'gifts.toml').read_text('utf-8'))['gifts']
        return characters, gifts

    def connect(self):
        db = sqlite3.connect(f'{self.DB.as_uri()}?mode=rw', uri=True, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        return db

    def backup(self, db):
        self.BACKUPS.mkdir(exist_ok=True)
        name = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.db'
        with sqlite3.connect(self.BACKUPS / name) as dest:
            db.backup(dest)
        return name

    def user_exists(self, db, user):
        if not db.execute('SELECT 1 FROM users WHERE id=?', (user,)).fetchone():
            raise ValueError('请选择有效用户')

    def integer(self, value, high):
        if type(value) is not int or not 0 <= value <= high:
            raise ValueError(f'数量必须是 0 到 {high} 的整数')
        return value

    def state(self, user=None) -> dict[str, Any]:
        characters, gifts = self.catalog()
        with closing(self.connect()) as db:
            users = [dict(r) for r in db.execute('SELECT id,name FROM users ORDER BY name,id')]
            result: dict[str, Any] = dict(users=users, characters=[{'id': c['id'], 'name': c['name']} for c in characters],
                          gifts=[{'id': g['id'], 'name': g['name']} for g in gifts],
                          backups=sorted([p.name for p in self.BACKUPS.glob('*.db')], reverse=True)[:30])
            if user:
                self.user_exists(db, user)
                for table in TABLES:
                    result[table] = [dict(r) for r in db.execute(f'SELECT * FROM {table} WHERE user_id=?', (user,))]
            return result

    def mutate(self, body):
        action, user = body.get('action'), body.get('user')
        chars, gifts = self.catalog()
        with closing(self.connect()) as db:
            self.user_exists(db, user)
            now = datetime.now(timezone.utc)
            day = now.astimezone(timezone(timedelta(hours=8))).date().isoformat()
            char = gift = ''
            value = 0.0
            count = draws = cards = 0
            restored: dict[str, list[dict[str, Any]]] = {}
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
                count = self.integer(body.get('count'), 9999)
            elif action == 'balances':
                draws = self.integer(body.get('draws'), 7)
                cards = self.integer(body.get('cards'), 9999)
            elif action == 'restore':
                name = body.get('backup', '')
                if not isinstance(name, str) or Path(name).name != name or not (self.BACKUPS / name).is_file():
                    raise ValueError('请选择现有备份')
                with sqlite3.connect(f'{(self.BACKUPS / name).as_uri()}?mode=ro', uri=True) as source:
                    source.row_factory = sqlite3.Row
                    restored = {t: [dict(r) for r in source.execute(f'SELECT * FROM {t} WHERE user_id=?', (user,))] for t in TABLES}
            else:
                raise ValueError('未知操作')
            saved = self.backup(db)
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
            db.commit()
            return {'message': '已保存；刷新聊天页面查看。恢复只影响所选用户的好感度和背包。', 'backup': saved}

    def sheet_path(self, character):
        chars, _ = self.catalog()
        entry = next((c for c in chars if c['id'] == character), None)
        if entry is None:
            raise ValueError('无效角色')
        path = (self.CHARACTERS / entry['sheet']).resolve()
        if not path.is_relative_to((self.CHARACTERS / 'sheets').resolve()):
            raise ValueError('无效人设路径')
        return path
