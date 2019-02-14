import json
import datetime

from typing import TypeVar
from typing import Optional

import xml.etree.ElementTree as xml


class PubMedArticle(object):
    """ Data class that contains a PubMed article.
    """

    def __init__(
        self: object,
        xml_element: Optional[TypeVar("Element")] = None,
        *args: list,
        **kwargs: dict,
    ) -> None:
        """ Initialization of the object from XML or from parameters.
        """

        # If an XML element is provided, use it for initialization
        if xml_element is not None:
            self._initializeFromXML(xml_element=xml_element)

        # If no XML element was provided, try to parse the input parameters
        else:

            # All of these are required
            try:
                self.article_id = kwargs.get("article_id")
                self.title = kwargs.get("title")
                self.abstract = kwargs.get("abstract")
                self.keywords = kwargs.get("keywords")
                self.journal = kwargs.get("journal")
                self.publication_date = kwargs.get("publication_date")
                self.authors = kwargs.get("authors")

            except Exception as e:
                raise Exception(f"Required parameter not found: {e}")

    def _initializeFromXML(self: object, xml_element: TypeVar("Element")) -> None:
        """ Helper method that parses an XML element into an article object.
        """

        def _attemptGrab(xml_finder_text):
            # Try to parse and clean the element
            try:
                element = xml_element.find(xml_finder_text)
                if element is not None:
                    element = (
                        xml.tostring(element, method="text")
                        .decode("utf8")
                        .strip()
                        .replace("\n", " ")
                    )

            # Set to None if we're unable to parse it
            except:
                element = None

            return element



        def _getText(element: TypeVar("Element"), path: str, default: str = "") -> str:
            """ Internal helper method that retrieves the text content of an
                XML element.

                Parameters:
                    - element   Element, the XML element to parse.
                    - path      Str, Nested path in the XML element.
                    - default   Str, default value to return when no text is found.

                Returns:
                    - text      Str, text in the XML node.
            """

            # Find the path in the element
            result = element.find(path)

            # Return the default if there is no such element
            if result is None:
                return default

            # Extract the text and return it
            else:
                return result.text

        # Parse the basic info
        self.article_id = _getText(xml_element, ".//ArticleId[@IdType='pubmed']", None)
        self.title = _getText(xml_element, ".//ArticleTitle", None)
        self.keywords = [
            keyword.text
            for keyword in xml_element.findall(".//Keyword")
            if keyword is not None
        ]
        self.journal = _getText(xml_element, ".//Journal/Title", None)


        # Try to parse and clean abstract elements
        self.abstract = _attemptGrab(xml_finder_text=".//AbstractText")
        self.conclusion = _attemptGrab(xml_finder_text=".//AbstractText[@Label='CONCLUSION']")
        self.method = _attemptGrab(xml_finder_text=".//AbstractText[@Label='METHOD']")
        self.results = _attemptGrab(xml_finder_text=".//AbstractText[@Label='RESULTS']")


        # Get the publication date
        try:

            # Get the publication elements
            publication_date = xml_element.find(".//PubMedPubDate[@PubStatus='pubmed']")
            publication_year = int(_getText(publication_date, ".//Year", None))
            publication_month = int(_getText(publication_date, ".//Month", "1"))
            publication_day = int(_getText(publication_date, ".//Day", "1"))

            # Construct a datetime object from the info
            self.publication_date = datetime.date(
                year=publication_year, month=publication_month, day=publication_day
            )

        # Unable to parse the datetime
        except Exception as e:
            print(e)
            self.publication_date = None

        # Get the list of authors
        self.authors = [
            {
                "lastname": _getText(author, ".//LastName", None),
                "firstname": _getText(author, ".//ForeName", None),
                "initials": _getText(author, ".//Initials", None),
            }
            for author in xml_element.findall(".//Author")
        ]

    def toJSON(self: object) -> str:
        """ Helper method for debugging, dumps the object as JSON string.
        """

        return json.dumps(
            self,
            default=lambda o: o.__dict__
            if not isinstance(o, datetime.datetime)
            else str(o),
            sort_keys=True,
            indent=4,
        )
