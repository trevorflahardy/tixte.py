import aiohttp
import pytest
import os

import tixte

try:
    TIXTE_MASTER_KEY: str = os.environ['TIXTE_MASTER_TOKEN']
except KeyError as exc:
    raise Exception('TIXTE_MASTER_TOKEN environment variable not set') from exc

try:
    TIXTE_MASTER_DOMAIN: str = os.environ['TIXTE_MASTER_DOMAIN']
except KeyError as exc:
    raise Exception('TIXTE_MASTER_DOMAIN environment variable not set') from exc

try:
    TIXTE_ACCOUNT_EMAIL: str = os.environ['TIXTE_ACCOUNT_EMAIL']
except KeyError as exc:
    raise Exception('TIXTE_ACCOUNT_EMAIL environment variable not set') from exc

TIXTE_ACCOUNT_ID: str = '89b1c121b4f24b22aa8607748981c34a'
TIXTE_TESTING_URL: str = 'https://imgur.com/a/TKpgn1w'
TIXTE_TESTING_DOMAIN: str = 'tixte-testing.tixte.co'
TIXTE_OTHER_USER: str = '71dc9871ca28446c8baffbd74430f2ad'
TIXTE_TESTING_UPLOAD_NAME: str = 'xqc.png'
TIXTE_TESTING_UPLOAD_ID: str = 'l5r277bx20a'

@pytest.mark.asyncio
async def test_fetch_user() -> None:
    session = aiohttp.ClientSession()
    client = tixte.Client(TIXTE_MASTER_KEY, TIXTE_MASTER_DOMAIN, session=session)
    
    user = await client.fetch_user(TIXTE_ACCOUNT_ID)
    
    await client.cleanup()

    assert user.id == TIXTE_ACCOUNT_ID
    assert user.username == 'TTesting'
