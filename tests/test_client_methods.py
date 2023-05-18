import asyncio
import os

import pytest

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
TIXTE_TESTING_URL: str = (
    'https://cdn.discordapp.com/attachments/813293906467880961/1108797596996222986/830954810793525258.png'
)
TIXTE_TESTING_DOMAIN: str = 'tixte-testing.tixte.co'
TIXTE_OTHER_USER: str = '71dc9871ca28446c8baffbd74430f2ad'
TIXTE_TESTING_UPLOAD_NAME: str = 'xqc.png'
TIXTE_TESTING_UPLOAD_ID: str = 'l5r277bx20a'


@pytest.mark.asyncio
async def fetch_client_user() -> None:
    client = tixte.Client(TIXTE_MASTER_KEY, TIXTE_MASTER_DOMAIN)
    async with client:
        client_user = await client.fetch_client_user()

        assert client_user.id == TIXTE_ACCOUNT_ID
        assert client_user.email == TIXTE_ACCOUNT_EMAIL


@pytest.mark.asyncio
async def test_fetch_user() -> None:
    client = tixte.Client(TIXTE_MASTER_KEY, TIXTE_MASTER_DOMAIN)
    async with client:
        user = await client.fetch_user(TIXTE_ACCOUNT_ID)

        assert user.id == TIXTE_ACCOUNT_ID
        assert user.username == 'TTesting'


@pytest.mark.asyncio
async def test_url_to_file() -> None:
    client = tixte.Client(TIXTE_MASTER_KEY, TIXTE_MASTER_DOMAIN)
    async with client:
        file = await client.url_to_file(TIXTE_TESTING_URL, filename=TIXTE_TESTING_UPLOAD_NAME)

        assert file.filename == TIXTE_TESTING_UPLOAD_NAME


@pytest.mark.asyncio
async def test_public_upload() -> None:
    client = tixte.Client(TIXTE_MASTER_KEY, TIXTE_MASTER_DOMAIN)
    async with client:
        file = await client.url_to_file(TIXTE_TESTING_URL, filename=TIXTE_TESTING_UPLOAD_NAME)
        upload = await client.upload(file, upload_type=tixte.UploadType.public)

        clent_user = await client.fetch_user(TIXTE_ACCOUNT_ID)

        permissions = upload.permissions.get()
        assert permissions, "Permissions None on new upload"

        assert permissions[clent_user] == tixte.UploadPermissionLevel.owner


@pytest.mark.asyncio
async def test_event_dispatching() -> None:
    client = tixte.Client(TIXTE_MASTER_KEY, TIXTE_MASTER_DOMAIN)

    request_response: asyncio.Future[int] = asyncio.get_event_loop().create_future()

    @client.listen('on_test')
    async def _on_client_request(parameter: int) -> None:  # pyright: ignore[reportUnusedFunction]
        request_response.set_result(parameter)

    async with client:
        client.dispatch('test', 1)

        import async_timeout

        async with async_timeout.timeout(10):
            await request_response


@pytest.mark.asyncio
async def test_wait_for() -> None:
    client = tixte.Client(TIXTE_MASTER_KEY, TIXTE_MASTER_DOMAIN)

    async def _wrapped_wait_for():
        def check(parameter: int) -> bool:
            assert parameter == 1
            return True

        return await client.wait_for('test', check=check, timeout=10)

    task: asyncio.Task[int] = asyncio.create_task(_wrapped_wait_for())

    await asyncio.sleep(0.5)  # Wait for the task to spin up

    client.dispatch('test', 1)

    await task
    assert task.result() == 1

    assert client._waiters == {'on_test': []}


# TODO: Add testing for private uploads, upload permission management (viewing access), deleting uploads, and more.
