from datetime import datetime, timedelta

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

NEWS_COUNT = 11
COMMENTS_COUNT = 3


@pytest.fixture
def author(django_user_model, db):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model, db):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author, db):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author, db):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news(db):
    return News.objects.create(title='Заголовок', text='Текст новости')


@pytest.fixture
def comment(news, author, db):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )


@pytest.fixture
def news_list(db):
    today = datetime.today()
    return News.objects.bulk_create(
        [
            News(
                title=f'Новость {index}',
                text='Текст новости',
                date=today - timedelta(days=index),
            )
            for index in range(NEWS_COUNT)
        ]
    )


@pytest.fixture
def comments(news, author, db):
    now = timezone.now()
    for index in range(COMMENTS_COUNT):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {index}',
        )
        comment.created = now - timedelta(days=index)


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.pk,))


@pytest.fixture
def login_url():
    return reverse('users:login')
