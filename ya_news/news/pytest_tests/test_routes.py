from http import HTTPStatus

import pytest
from django.urls import reverse


@pytest.mark.parametrize(
    'url_fixture',
    ('home_url', 'detail_url', 'login_url'),
)
def test_public_pages_are_available(client, request, url_fixture):
    url = request.getfixturevalue(url_fixture)

    response = client.get(url)

    assert response.status_code == HTTPStatus.OK


def test_signup_page_is_available(client):
    url = reverse('users:signup')

    response = client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url_fixture',
    ('edit_url', 'delete_url'),
)
def test_comment_pages_are_available_to_author(
    author_client,
    request,
    url_fixture,
):
    url = request.getfixturevalue(url_fixture)

    response = author_client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url_fixture',
    ('edit_url', 'delete_url'),
)
def test_comment_pages_are_unavailable_to_not_author(
    not_author_client,
    request,
    url_fixture,
):
    url = request.getfixturevalue(url_fixture)

    response = not_author_client.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'url_fixture',
    ('edit_url', 'delete_url'),
)
def test_anonymous_user_is_redirected_to_login(
    client,
    login_url,
    request,
    url_fixture,
):
    url = request.getfixturevalue(url_fixture)
    expected_url = f'{login_url}?next={url}'

    response = client.get(url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_url


def test_logout_accepts_post_request(author_client):
    url = reverse('users:logout')

    response = author_client.post(url)

    assert response.status_code == HTTPStatus.OK
    assert '_auth_user_id' not in author_client.session


@pytest.mark.parametrize(
    'url_fixture',
    ('home_url', 'detail_url', 'login_url'),
)
def test_public_pages_are_available(client, db, request, url_fixture):
    url = request.getfixturevalue(url_fixture)

    response = client.get(url)

    assert response.status_code == HTTPStatus.OK
