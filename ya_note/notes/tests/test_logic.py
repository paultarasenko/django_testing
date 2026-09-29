from http import HTTPStatus

from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note
from .constants import DUPLICATE_SLUG_WARNING, NOTE_SLUG

FORM_DATA = {
    'title': 'Новая заметка',
    'text': 'Новый текст',
    'slug': 'new-note',
}


def test_author_can_create_note(
    author,
    author_client,
):
    existing_ids = set(Note.objects.values_list('pk', flat=True))

    response = author_client.post(reverse('notes:add'), data=FORM_DATA)

    created_notes = Note.objects.exclude(pk__in=existing_ids)
    assert response.url == reverse('notes:success')
    assert created_notes.count() == 1
    note = created_notes.get()
    assert note.title == FORM_DATA['title']
    assert note.text == FORM_DATA['text']
    assert note.slug == FORM_DATA['slug']
    assert note.author == author


def test_slug_is_generated_from_title(
    author,
    author_client,
):
    form_data = FORM_DATA.copy()
    form_data.pop('slug')
    existing_ids = set(Note.objects.values_list('pk', flat=True))

    author_client.post(reverse('notes:add'), data=form_data)

    note = Note.objects.exclude(pk__in=existing_ids).get()
    assert note.slug == slugify(form_data['title'])
    assert note.author == author


def test_anonymous_cannot_create_note(
    client,
    db,
):
    notes_before = set(Note.objects.values_list('pk', flat=True))

    response = client.post(reverse('notes:add'), data=FORM_DATA)

    notes_after = set(Note.objects.values_list('pk', flat=True))
    assert response.status_code == HTTPStatus.FOUND
    assert notes_after == notes_before


def test_duplicate_slug_is_rejected(
    note,
    author_client,
):
    form_data = FORM_DATA | {'slug': NOTE_SLUG}
    notes_count = Note.objects.count()

    response = author_client.post(reverse('notes:add'), data=form_data)

    form = response.context['form']
    assert form.errors['slug'] == [
        NOTE_SLUG + DUPLICATE_SLUG_WARNING
    ]
    assert Note.objects.count() == notes_count


def test_author_can_edit_note(note, author_client):
    url = reverse('notes:edit', args=(NOTE_SLUG,))
    notes_count = Note.objects.count()

    response = author_client.post(url, data=FORM_DATA)

    updated_note = Note.objects.get(pk=note.pk)
    assert response.url == reverse('notes:success')
    assert Note.objects.count() == notes_count
    assert updated_note.title == FORM_DATA['title']
    assert updated_note.text == FORM_DATA['text']
    assert updated_note.slug == FORM_DATA['slug']
    assert updated_note.author == note.author


def test_reader_cannot_edit_note(
    note,
    reader_client,
):
    url = reverse('notes:edit', args=(NOTE_SLUG,))

    response = reader_client.post(url, data=FORM_DATA)

    saved_note = Note.objects.get(pk=note.pk)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert saved_note.title == note.title
    assert saved_note.text == note.text
    assert saved_note.slug == note.slug
    assert saved_note.author == note.author


def test_author_can_delete_note(
    note,
    author_client,
):
    url = reverse('notes:delete', args=(NOTE_SLUG,))

    response = author_client.post(url)

    assert response.url == reverse('notes:success')
    assert not Note.objects.filter(pk=note.pk).exists()


def test_reader_cannot_delete_note(
    note,
    reader_client,
):
    url = reverse('notes:delete', args=(NOTE_SLUG,))

    response = reader_client.post(url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Note.objects.filter(pk=note.pk).exists()
