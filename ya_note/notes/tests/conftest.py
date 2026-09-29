import pytest
from django.test import Client

from notes.models import Note

from .constants import NOTES_ON_PAGE, NOTE_SLUG


@pytest.fixture
def author(django_user_model, db):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model, db):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author, db):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader, db):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def note(author, db):
    return Note.objects.create(
        title='Тестовая заметка',
        text='Текст тестовой заметки',
        slug=NOTE_SLUG,
        author=author,
    )


@pytest.fixture
def notes(author, db):
    return Note.objects.bulk_create(
        [
            Note(
                title=f'Заметка {index}',
                text='Текст тестовой заметки',
                slug=f'note-{index}',
                author=author,
            )
            for index in range(NOTES_ON_PAGE + 1)
        ]
    )
