import datetime
import requests
import itertools

import xml.etree.ElementTree as xml

from typing import Union

from .helpers import batches
from .article import PubMedArticle
from .book import PubMedBookArticle


# Base url for all queries
BASE_URL = "https://eutils.ncbi.nlm.nih.gov"


class PubMed(object):
    """ Wrapper around the PubMed API.
    """

    def __init__(
        self: object, tool: str = "my_tool", email: str = "my_email@example.com"
    ) -> None:
        """ Initialization of the object.

            Parameters:
                - tool      String, name of the tool that is executing the query.
                            This parameter is not required but kindly requested by
                            PMC (PubMed Central).
                - email     String, email of the user of the tool. This parameter
                            is not required but kindly requested by PMC (PubMed Central).

            Returns:
                - None
        """

        # Store the input parameters
        self.tool = tool
        self.email = email

        # Keep track of the rate limit
        self._rateLimit = 3
        self._requestsMade = []

        # Define the standard / default query parameters
        self.parameters = {"tool": tool, "email": email, "db": "pubmed"}

    def query(self: object, query: str, max_results: int = 100):
        """ Method that executes a query agains the GraphQL schema, automatically
            inserting the PubMed data loader.

            Parameters:
                - query     String, the GraphQL query to execute against the schema.

            Returns:
                - result    ExecutionResult, GraphQL object that contains the result
                            in the "data" attribute.
        """

        # Retrieve the article IDs for the query
        article_ids = self._getArticleIds(query=query, max_results=max_results)

        # Get the articles themselves
        articles = list(
            [
                self._getArticles(article_ids=batch)
                for batch in batches(article_ids, 250)
            ]
        )

        # Chain the batches back together and return the list
        return itertools.chain.from_iterable(articles)

    def getTotalResultsCount(self: object, query: str) -> int:
        """ Helper method that returns the total number of results that match the query.

            Parameters:
                - query                 String, the query to send to PubMed

            Returns:
                - total_results_count   Int, total number of results for the query in PubMed
        """

        # Get the default parameters
        parameters = self.parameters.copy()

        # Add specific query parameters
        parameters["term"] = query
        parameters["retmax"] = 1

        # Make the request (request a single article ID for this search)
        response = self._get(url="/entrez/eutils/esearch.fcgi", parameters=parameters)

        # Get from the returned meta data the total number of available results for the query
        total_results_count = int(response.get("esearchresult", {}).get("count"))

        # Return the total number of results (without retrieving them)
        return total_results_count
    
    def _exceededRateLimit(self) -> bool:
        """ Helper method to check if we've exceeded the rate limit.

            Returns:
                - exceeded      Bool, Whether or not the rate limit is exceeded.
        """

        # Remove requests from the list that are longer than 1 second ago
        self._requestsMade = [requestTime for requestTime in self._requestsMade if requestTime > datetime.datetime.now() - datetime.timedelta(seconds=1)]

        # Return whether we've made more requests in the last second, than the rate limit
        return len(self._requestsMade) > self._rateLimit

    def _get(
        self: object, url: str, parameters: dict, output: str = "json"
    ) -> Union[dict, str]:
        """ Generic helper method that makes a request to PubMed.

            Parameters:
                - url           Str, last part of the URL that is requested (will
                                be combined with the base url)
                - parameters    Dict, parameters to use for the request
                - output        Str, type of output that is requested (defaults to
                                JSON but can be used to retrieve XML)

            Returns:
                - response      Dict / str, if the response is valid JSON it will
                                be parsed before returning, otherwise a string is
                                returend
        """

        # Make sure the rate limit is not exceeded
        while self._exceededRateLimit():
            pass

        # Set the response mode
        parameters["retmode"] = output

        # Make the request to PubMed
        response = requests.get(f"{BASE_URL}{url}", params=parameters)

        # Check for any errors
        response.raise_for_status()

        # Add this request to the list of requests made
        self._requestsMade.append(datetime.datetime.now())

        # Return the response
        if output == "json":
            return response.json()
        else:
            return response.text

    def _getArticles(self: object, article_ids: list) -> list:
        """ Helper method that batches a list of article IDs and retrieves the content.

            Parameters:
                - article_ids   List, article IDs.

            Returns:
                - articles      List, article objects.
        """

        # Get the default parameters
        parameters = self.parameters.copy()
        parameters["id"] = article_ids

        # Make the request
        response = self._get(
            url="/entrez/eutils/efetch.fcgi", parameters=parameters, output="xml"
        )

        # Parse as XML
        root = xml.fromstring(response)

        # Loop over the articles and construct article objects
        for article in root.iter("PubmedArticle"):
            yield PubMedArticle(xml_element=article)
        for book in root.iter("PubmedBookArticle"):
            yield PubMedBookArticle(xml_element=book)

    def _getArticleIds(self: object, query: str, max_results: int) -> list:
        """ Helper method to retrieve the article IDs for a query.

            Parameters:
                - query         Str, query to be executed against the PubMed database.
                - max_results   Int, the maximum number of results to retrieve.

            Returns:
                - article_ids   List, article IDs as a list.
        """

        # Create a placeholder for the retrieved IDs
        article_ids = []

        # Get the default parameters
        parameters = self.parameters.copy()

        # Add specific query parameters
        parameters["term"] = query
        parameters["retmax"] = 50000

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

        # If not all articles are retrieved, continue to make requests untill we have everything
        while retrieved_count < total_result_count and retrieved_count < max_results:

            # Calculate a cut off point based on the max_results parameter
            if (max_results - retrieved_count) < parameters["retmax"]:
                parameters["retmax"] = max_results - retrieved_count

            # Start the collection from the number of already retrieved articles
            parameters["retstart"] = retrieved_count

            # Make a new request
            response = self._get(
                url="/entrez/eutils/esearch.fcgi", parameters=parameters
            )

            # Add the retrieved IDs to the list
            article_ids += response.get("esearchresult", {}).get("idlist", [])

            # Get information from the response
            retrieved_count += int(response.get("esearchresult", {}).get("retmax"))

        # Return the response
        return article_ids
