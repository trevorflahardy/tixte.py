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


@pytest.mark.asyncio
async def test_client_fetch_client_user() -> None:
    client = tixte.Client(TIXTE_MASTER_KEY, TIXTE_MASTER_DOMAIN)
    async with client:
        user = await client.fetch_client_user()

    assert user.id == TIXTE_ACCOUNT_ID
    assert user.username == 'TTesting'
    assert user.email == TIXTE_ACCOUNT_EMAIL
    assert user.email_verified == True

    assert client.user == user


@pytest.mark.asyncio
async def test_client_fetch_user() -> None:
    client = tixte.Client(TIXTE_MASTER_KEY, TIXTE_MASTER_DOMAIN)
    async with client:
        user = await client.fetch_user(TIXTE_ACCOUNT_ID)

    assert user.id == TIXTE_ACCOUNT_ID
    assert user.username == 'TTesting'

    assert user in client.users

    cached_user = client.get_user(TIXTE_ACCOUNT_ID)
    assert cached_user is not None
    assert cached_user == user


@pytest.mark.asyncio
async def test_client_url_to_file() -> None:
    client = tixte.Client(TIXTE_MASTER_KEY, TIXTE_MASTER_DOMAIN)
    async with client:
        file = await client.url_to_file(TIXTE_TESTING_URL, filename='testing.png')

    assert file.filename == 'testing.png'


@pytest.mark.asyncio
async def test_client_file_methods() -> None:
    client = tixte.Client(TIXTE_MASTER_KEY, TIXTE_MASTER_DOMAIN)
    async with client:
        file = await client.url_to_file(TIXTE_TESTING_URL, filename='testing.png')
        upload = await client.upload(file)

        upload = await upload.to_file()
        assert upload.filename == 'testing.png'

        assert upload.filename == 'testing'
        assert upload.extension == '.png'

        # Now we can delete this upload
        response = await upload.delete()
        print(response.message)


@pytest.mark.asyncio
async def test_client_fetch_domains() -> None:
    client = tixte.Client(TIXTE_MASTER_KEY, TIXTE_MASTER_DOMAIN)
    async with client:
        domains = await client.fetch_domains()

        testing_domain: tixte.Domain = next(
            domain for domain in domains if domain.url == 'testing.tixte.io'
        )

        assert testing_domain.url == 'testing.tixte.io'
        assert testing_domain.owner_id == TIXTE_ACCOUNT_ID

        domain_owner = await testing_domain.fetch_owner()
        assert domain_owner == await client.fetch_client_user()

    assert client.domains == domains


@pytest.mark.asyncio
async def test_client_configuration() -> None:
    client = tixte.Client(TIXTE_MASTER_KEY, TIXTE_MASTER_DOMAIN)
    async with client:
        config = await client.fetch_config()

    assert config.to_dict() == {
        'title': None,
        'description': None,
        'author': {'name': None, 'url': None},
        'color': 5793266,
        'provider': {'name': None, 'url': None},
    }
