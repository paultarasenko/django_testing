from http import HTTPStatus

from news.models import Comment

FORM_DATA = {'text': 'Новый текст комментария'}
BAD_WORDS_DATA = {'text': 'Какой же ты редиска!'}
WARNING = 'Не ругайтесь!'


def test_anonymous_cannot_create_comment(
    client,
    detail_url,
):
    comments_before = set(Comment.objects.values_list('pk', flat=True))

    response = client.post(detail_url, data=FORM_DATA)

    comments_after = set(Comment.objects.values_list('pk', flat=True))
    assert response.status_code == HTTPStatus.FOUND
    assert comments_after == comments_before


def test_author_can_create_comment(
    author,
    author_client,
    news,
    detail_url,
):
    existing_ids = set(Comment.objects.values_list('pk', flat=True))

    response = author_client.post(detail_url, data=FORM_DATA)

    created = Comment.objects.exclude(pk__in=existing_ids)
    assert response.url == f'{detail_url}#comments'
    assert created.count() == 1
    new_comment = created.get()
    assert new_comment.text == FORM_DATA['text']
    assert new_comment.author == author
    assert new_comment.news == news


def test_comment_with_bad_words_is_not_created(
    author_client,
    detail_url,
):
    comments_count = Comment.objects.count()

    response = author_client.post(detail_url, data=BAD_WORDS_DATA)

    form = response.context['form']
    assert form.errors['text'] == [WARNING]
    assert Comment.objects.count() == comments_count


def test_author_can_edit_comment(
    author_client,
    comment,
    edit_url,
    detail_url,
):
    comments_count = Comment.objects.count()

    response = author_client.post(edit_url, data=FORM_DATA)

    updated = Comment.objects.get(pk=comment.pk)
    assert response.url == f'{detail_url}#comments'
    assert Comment.objects.count() == comments_count
    assert updated.text == FORM_DATA['text']
    assert updated.author == comment.author
    assert updated.news == comment.news


def test_not_author_cannot_edit_comment(
    not_author_client,
    comment,
    edit_url,
):
    response = not_author_client.post(edit_url, data=FORM_DATA)

    saved = Comment.objects.get(pk=comment.pk)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert saved.text == comment.text
    assert saved.author == comment.author
    assert saved.news == comment.news


def test_author_can_delete_comment(
    author_client,
    comment,
    delete_url,
    detail_url,
):
    response = author_client.post(delete_url)

    assert response.url == f'{detail_url}#comments'
    assert not Comment.objects.filter(pk=comment.pk).exists()


def test_not_author_cannot_delete_comment(
    not_author_client,
    comment,
    delete_url,
):
    response = not_author_client.post(delete_url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(pk=comment.pk).exists()
