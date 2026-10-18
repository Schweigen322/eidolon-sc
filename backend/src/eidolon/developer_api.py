"""Optional developer settings, restricted to one explicitly configured user ID."""
import os
import sqlite3
from dataclasses import replace
from datetime import datetime, timezone
from typing import Annotated
from threading import Lock

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from eidolon.assembly import Backend
from eidolon.developer_data import DeveloperData
from eidolon.sessions import current_user


def developer_user(user: Annotated[str, Depends(current_user)]) -> str:
    owner = os.environ.get('EIDOLON_DEVELOPER_USER', '').strip()
    if not owner or user != owner:
        raise HTTPException(404)
    return user


Developer = Annotated[str, Depends(developer_user)]


class Change(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    action: str
    character: str | None = None
    value: float | None = None
    gift: str | None = None
    count: int | None = None
    draws: int | None = None
    cards: int | None = None
    backup: str | None = None


class SheetInput(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    character: str
    text: str = Field(min_length=1, max_length=80000)
    original: str = Field(max_length=80000)


def add_developer_routes(app: FastAPI, backend: Backend) -> None:
    data = DeveloperData(backend.settings.database_path, backend.settings.characters_path.parent)

    sheet_lock = Lock()

    @app.get('/api/developer')
    def capabilities(user: Developer) -> dict:
        return {'enabled': True, 'user_id': user, 'affinity_on': backend.config.affinity_on}

    @app.get('/api/developer/state')
    def state(user: Developer) -> dict:
        try:
            result = data.state(user)
            result.pop('users', None)
            result['affinity_on'] = backend.config.affinity_on
            return result
        except (ValueError, OSError, sqlite3.Error) as exc:
            raise HTTPException(400, str(exc)) from exc

    @app.post('/api/developer/change')
    def change(body: Change, user: Developer) -> dict:
        try:
            return data.mutate(body.model_dump(exclude_none=True) | {'user': user})
        except (ValueError, OSError, sqlite3.Error) as exc:
            raise HTTPException(400, str(exc)) from exc

    @app.get('/api/developer/sheet')
    def read_sheet(character: str, user: Developer) -> dict:
        try:
            return {'text': data.sheet_path(character).read_text('utf-8')}
        except (ValueError, OSError) as exc:
            raise HTTPException(400, str(exc)) from exc

    @app.post('/api/developer/sheet')
    def save_sheet(body: SheetInput, user: Developer) -> dict:
        try:
            with sheet_lock:
                path = data.sheet_path(body.character)
                if body.character not in backend.characters:
                    raise ValueError('角色未加载，请先重启后端')
                original = path.read_text('utf-8')
                if body.original != original:
                    raise HTTPException(409, '人设已被其他设备修改，请重新加载后再编辑')
                if not body.text.strip():
                    raise ValueError('人设不能为空')
                folder = data.BACKUPS / 'sheets'
                folder.mkdir(parents=True, exist_ok=True)
                name = path.stem + '-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.md'
                (folder / name).write_text(original, 'utf-8')
                path.write_text(body.text, 'utf-8')
                backend.characters[body.character] = replace(backend.characters[body.character], sheet=body.text.strip())
                return {'message': '人设已保存并生效。进行中的回复和通话请结束后再测试；建议新建对话。', 'backup': name}
        except (ValueError, OSError) as exc:
            raise HTTPException(400, str(exc)) from exc
