from news.forms import CommentForm

NEWS_ON_HOME_PAGE = 10


def test_home_page_news_count_is_limited(
    news_list,
    client,
    home_url,
):
    response = client.get(home_url)

    object_list = response.context['object_list']

    assert len(object_list) == NEWS_ON_HOME_PAGE


def test_news_are_sorted_newest_first(
    news_list,
    client,
    home_url,
):
    response = client.get(home_url)

    object_list = response.context['object_list']
    all_dates = [item.date for item in object_list]

    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_are_sorted_oldest_first(
    comments,
    client,
    detail_url,
):
    response = client.get(detail_url)

    news = response.context['news']
    all_created = [item.created for item in news.comment_set.all()]

    assert all_created == sorted(all_created)


def test_anonymous_client_has_no_comment_form(
    client,
    detail_url,
):
    response = client.get(detail_url)

    assert 'form' not in response.context


def test_authorized_client_has_comment_form(
    author_client,
    detail_url,
):
    response = author_client.get(detail_url)

    assert isinstance(response.context['form'], CommentForm)
