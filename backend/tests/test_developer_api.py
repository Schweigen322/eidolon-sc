"""Developer controls require explicit ownership and preserve recoverable data."""
import sqlite3

from eidolon.config import Settings
from tests.conftest import ClientFactory
from tests.fakes import FakeLLM, system_of
from tests.test_text_turn import send_turn, start_conversation
from tests.test_delete_account import user_id


async def test_disabled_and_other_users_cannot_edit(make_client: ClientFactory, settings: Settings, monkeypatch):
    owner = make_client(FakeLLM())
    stranger = make_client(FakeLLM(), 'stranger')
    monkeypatch.delenv('EIDOLON_DEVELOPER_USER', raising=False)
    assert (await owner.get('/api/developer')).status_code == 404
    monkeypatch.setenv('EIDOLON_DEVELOPER_USER', user_id(settings.database_path, 'producer'))
    assert (await owner.get('/api/developer')).status_code == 200
    assert (await stranger.get('/api/developer/state')).status_code == 404
    assert (await stranger.post('/api/developer/change', json={'action': 'balances', 'draws': 7, 'cards': 1})).status_code == 404


async def test_changes_validate_backup_and_restore_only_owner(make_client: ClientFactory, settings: Settings, monkeypatch):
    owner = make_client(FakeLLM())
    make_client(FakeLLM(), 'stranger')
    uid = user_id(settings.database_path, 'producer')
    other = user_id(settings.database_path, 'stranger')
    monkeypatch.setenv('EIDOLON_DEVELOPER_USER', uid)
    change = '/api/developer/change'
    assert 'users' not in (await owner.get('/api/developer/state')).json()
    for payload in [dict(action='affinity', character='mano', value=101), dict(action='gift', gift='missing', count=9), dict(action='balances', draws=7.1, cards=0), dict(action='balances', draws=7, cards=True), dict(action='balances', draws=7, cards=1, user=other)]:
        assert (await owner.post(change, json=payload)).status_code in (400, 422)
    assert not list(settings.database_path.parent.glob('devtools-backups/*.db'))
    assert (await owner.post(change, json=dict(action='balances', draws=7, cards=3))).status_code == 200
    saved = await owner.post(change, json=dict(action='affinity', character='mano', value=100))
    assert saved.status_code == 200, saved.text
    with sqlite3.connect(settings.database_path) as db:
        assert db.execute('SELECT value,cooling FROM affinities WHERE user_id=?', (uid,)).fetchone() == (100, 0)
        db.execute("INSERT INTO gift_balances(user_id,draws,given_on,reset_cards) VALUES(?,2,'2026-10-18',2)", (other,))
    assert (await owner.post(change, json=dict(action='restore', backup=saved.json()['backup']))).status_code == 200
    with sqlite3.connect(settings.database_path) as db:
        assert db.execute('SELECT value FROM affinities WHERE user_id=?', (uid,)).fetchone() is None
        assert db.execute('SELECT draws,reset_cards FROM gift_balances WHERE user_id=?', (uid,)).fetchone() == (7, 3)
        assert db.execute('SELECT draws,reset_cards FROM gift_balances WHERE user_id=?', (other,)).fetchone() == (2, 2)
    assert (await owner.post(change, json=dict(action='restore', backup='../eidolon.db'))).status_code == 400
    assert (await owner.post(change, headers={'Origin': 'https://evil.invalid'}, json=dict(action='balances', draws=7, cards=3))).status_code == 403


async def test_sheet_backup_and_conflict(make_client: ClientFactory, settings: Settings, monkeypatch):
    llm = FakeLLM(['<ja>はい</ja><zh>好</zh>'])
    owner = make_client(llm)
    monkeypatch.setenv('EIDOLON_DEVELOPER_USER', user_id(settings.database_path, 'producer'))
    original = (await owner.get('/api/developer/sheet', params={'character': 'mano'})).json()['text']
    payload = dict(character='mano', text='# 新人设\n说话简洁，喜欢种花。', original=original)
    result = await owner.post('/api/developer/sheet', json=payload)
    assert result.status_code == 200, result.text
    assert (settings.characters_path.parent / 'sheets/mano.md').read_text('utf-8') == payload['text']
    backup = settings.database_path.parent / 'devtools-backups/sheets' / result.json()['backup']
    assert backup.read_text('utf-8') == original
    await send_turn(owner, await start_conversation(owner), '你好')
    assert payload['text'] in system_of(llm.prompts[-1])
    assert (await owner.post('/api/developer/sheet', json=payload)).status_code == 409
    assert (await owner.get('/api/developer/sheet', params={'character': '../private'})).status_code == 400
