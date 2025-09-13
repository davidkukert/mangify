from http import HTTPStatus
from pathlib import Path

import casbin
from fastapi import HTTPException

from src.security import CurrentUser


async def get_enforcer(model_path: str, policy_path: str):
    enforcer = casbin.AsyncEnforcer(model_path, policy_path)
    await enforcer.load_policy()
    return enforcer


async def get_authorization(
    user: CurrentUser, resource, action, resource_type: str
):
    enforcer = await get_enforcer(
        f'{Path.cwd()}/src/auth/models/{resource_type}_model.conf',
        f'{Path.cwd()}/src/auth/policies/{resource_type}_policy.csv',
    )
    if not enforcer.enforce(user, resource, action):
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Ação não autorizada'
        )
