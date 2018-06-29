import requests
import datetime
import itertools

from . import schema as schema
import xml.etree.ElementTree as xml

from typing import TypeVar


# Create a type
PubMed_type = TypeVar("PubMed")

# Base url for all queries
BASE_URL = "https://eutils.ncbi.nlm.nih.gov"


def batches(iterable, n=1):
    length = len(iterable)
    for index in range(0, length, n):
        yield iterable[index:min(index + n, length)]


class ArticleDataLoader(object):

    def __init__(self: object, pubmed: PubMed_type) -> None:
        self.pubmed = pubmed

    def load(self: object, article_ids: list):

        # Get articles in batches of 250 articles at a time to prevent overloading the target
        articles = list([self.pubmed.getArticles(article_ids=batch) for batch in batches(article_ids, 250)])

        # Chain the articles together into a single list and return that list
        return itertools.chain.from_iterable(articles)


class PubMedLoader(object):
    def __init__(self: object, tool: str = "my_tool", email: str = "my_email@example.com", *args: list, **kwargs: dict) -> None:
        """
        """

        # Store the input parameters
        self.tool = tool
        self.email = email

        # Define the standard / default query parameters
        self.parameters = {"tool": tool, "email": email, "db": "pmc"}

    def _get(self: object, url: str, parameters: dict, output: str = "json"):
        """ Generic helper method that makes a request to PubMed.
        """

        # Set the response mode
        parameters["retmode"] = output

        # Make the request to PubMed
        response = requests.get(f"{BASE_URL}{url}", params=parameters)

        # Return the response
        if output == "json":
            return response.json()
        else:
            return response.text

    def queryArticleIds(self: object, query: str, max_results: int = -1) -> list:
        """ Return a list of article IDs matching the query.
        """

        # Create a placeholder for the retrieved IDs
        article_ids = []

        # Get the default parameters
        parameters = self.parameters.copy()

        # Add specific query parameters
        parameters["term"] = query
        parameters["retmax"] = 10000

        # Calculate a cut off point based on the max_results parameter
        if max_results < parameters["retmax"]:
            parameters["retmax"] = max_results

        # Make the first request to PubMed
        response = self._get(url="/entrez/eutils/esearch.fcgi", parameters=parameters)

        # Add the retrieved IDs to the list
        article_ids += response.get("esearchresult", {}).get("idlist", [])

        # Get information from the response
        total_result_count = int(response.get("esearchresult", {}).get("count"))
        retrieved_count = int(response.get("esearchresult", {}).get("retmax"))

        # If no max is provided (-1) we'll try to retrieve everything
        if max_results == -1:
            max_results = total_result_count

        # If not all articles are retrieved, continue to make requests untill we haver everything
        while retrieved_count < total_result_count and retrieved_count < max_results:

            # Calculate a cut off point based on the max_results parameter
            if (max_results - retrieved_count) < parameters["retmax"]:
                parameters["retmax"] = (max_results - retrieved_count)

            # Start the collection from the number of already retrieved articles
            parameters["retstart"] = retrieved_count

            # Make a new request
            response = self._get(url="/entrez/eutils/esearch.fcgi", parameters=parameters)

            # Add the retrieved IDs to the list
            article_ids += response.get("esearchresult", {}).get("idlist", [])

            # Get information from the response
            retrieved_count += int(response.get("esearchresult", {}).get("retmax"))

        # Return the response
        return article_ids

    def getArticles(self: object, article_ids: list):

        # Get the default parameters
        parameters = self.parameters.copy()
        parameters["id"] = article_ids

        # Make the request
        response = self._get(url="/entrez/eutils/efetch.fcgi", parameters=parameters, output="xml")

        # Parse as XML
        root = xml.fromstring(response)

        def _getText(element, path, default=""):
            result = element.find(path)
            if result is None:
                return default
            else:
                return result.text

        # Loop over the articles and parse them
        article_objects = []
        for article in root.iter("article"):

            # Create an empty holder
            article_object = {}

            # Add basic info
            article_object["article_id"] = _getText(article, ".//article-id[@pub-id-type='pmc']", None)
            article_object["title"] = _getText(article, ".//article-title", None)
            if article_object["title"] is None:
                article_object["title"] = _getText(article, ".//ArticleTitle", None)
            if article_object["title"] is None:
                continue
            article_object["keywords"] = [keyword.text for keyword in article.findall(".//kwd") if keyword is not None]
            article_object["journal"] = schema.Journal(
                title=_getText(article, ".//journal-title", None),
                publisher=_getText(article, ".//publisher-name", None),
            )

            try:
                article_object["abstract"] = xml.tostring(article.find(".//abstract"), method="text").decode("utf8").strip().replace("\n", " ")
            except Exception as e:
                article_object["abstract"] = None

            # Get the publication date
            try:

                # Get the publication element
                publication_date = article.find(".//pub-date[@pub-type='pmc-release']")
                print(publication_date)
                if publication_date is None:
                    publication_date = article.find(".//PubMedPubDate[@PubStatus='pubmed']")
                    print(publication_date)
                if publication_date is None:
                    publication_date = article.find(".//PubDate")
                    print(publication_date)

                publication_year = int(_getText(publication_date, ".//year", None))
                if publication_year is None:
                    publication_year = int(_getText(publication_date, ".//Year", None))
                publication_month = int(_getText(publication_date, ".//month", None))
                if publication_month is None:
                    publication_month = int(_getText(publication_date, ".//Month", None))
                publication_day = int(_getText(publication_date, ".//day", None))
                if publication_day is None:
                    publication_day = int(_getText(publication_date, ".//Day", None))

                article_object["publication_date"] = datetime.date(
                    year=publication_year, month=publication_month, day=publication_day
                )
            except Exception as e:
                article_object["publication_date"] = None

            # Get the list of authors
            article_object["authors"] = [
                schema.Author(
                    surname=_getText(author, ".//surname", None),
                    given_names=_getText(author, ".//given-names", None),
                    email=_getText(author, ".//email", None),
                )
                for author in article.findall(".//contrib[@contrib-type='author']")
            ]

            # Return the article object
            article_objects.append(schema.Article(**article_object))

        return article_objects
