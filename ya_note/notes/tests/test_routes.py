from http import HTTPStatus

import pytest
from django.urls import reverse

from .constants import NOTE_SLUG


@pytest.mark.parametrize(
    'name',
    ('notes:home', 'users:login', 'users:signup'),
)
def test_public_pages_are_available(client, name):
    url = reverse(name)

    response = client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('notes:add', 'notes:list', 'notes:success'),
)
def test_private_pages_are_available_to_author(author_client, name):
    url = reverse(name)

    response = author_client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('notes:detail', 'notes:edit', 'notes:delete'),
)
def test_note_pages_are_available_to_author(note, author_client, name):
    url = reverse(name, args=(NOTE_SLUG,))

    response = author_client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('notes:detail', 'notes:edit', 'notes:delete'),
)
def test_note_pages_are_unavailable_to_reader(
    note,
    reader_client,
    name,
):
    url = reverse(name, args=(NOTE_SLUG,))

    response = reader_client.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    ('name', 'args'),
    (
        ('notes:add', ()),
        ('notes:list', ()),
        ('notes:success', ()),
        ('notes:detail', (NOTE_SLUG,)),
        ('notes:edit', (NOTE_SLUG,)),
        ('notes:delete', (NOTE_SLUG,)),
    ),
)
def test_anonymous_user_is_redirected_to_login(
    note,
    client,
    name,
    args,
):
    url = reverse(name, args=args)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'

    response = client.get(url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_url


def test_logout_accepts_post_request(
    author_client,
):
    url = reverse('users:logout')

    response = author_client.post(url)

    assert response.status_code == HTTPStatus.OK
    assert '_auth_user_id' not in author_client.session
