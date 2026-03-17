from newsapi import NewsApiClient
from langchain.tools import tool
from schemas.schema import NewsArticle
import dotenv
import os
from agents.shared import USE_MOCK_NEWS
from tests.fixtures import mock_news

dotenv.load_dotenv()

@tool
def get_articles(query: str, language: str, sources = None, max_results: int = 10) -> list[dict]:
    """ Fetches news articles from the NewsAPI based on the provided query, language, date range, and sources.
    Args:        query (str): The search query to find relevant news articles, e.g., "climate change", "technology advancements", "sports news".
        language (str): The language in which the user wants to find news articles, e.g., "en" for English, "es" for Spanish, "fr" for French.
        from_date (str): The start date for the news articles in the format "YYYY-MM-DD", e.g., "2023-01-01".
        to_date (str): The end date for the news articles in the format "YYYY-MM-DD", e.g., "2023-12-31".
        sources (str | None): A comma-separated string of news sources to filter the articles, e.g., "bbc-news,the-verge". 
            If None, articles from all sources
    """
    if USE_MOCK_NEWS:
        return mock_news

    newsapi = NewsApiClient(os.getenv("NEWSAPI_KEY"))

    # /v2/everything
    all_articles = newsapi.get_everything(q=query, 
                                        language=language,
                                        sort_by='relevancy',
                                        sources=sources
                                        )

    # /v2/top-headlines/sources
    articles = []
    for article in all_articles['articles'][:max_results]:
        articles.append(NewsArticle(
            title=article['title'],
            author=article['author'],
            source=article['source']['name'],
            description=article['description'],
            published_at=article['publishedAt'],
            url=article['url']
        ))
        
    return [art.model_dump() for art in articles]