import json
import datetime

from xml.etree.ElementTree import Element
from typing import TypeVar
from typing import Optional

from .helpers import getContent


class PubMedArticle(object):
    """ Data class that contains a PubMed article.
    """

    __slots__ = (
        "pubmed_id",
        "title",
        "abstract",
        "keywords",
        "journal",
        "publication_date",
        "authors",
        "methods",
        "conclusions",
        "results",
        "copyrights",
        "doi",
        "xml",
    )

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
            for field in self.__slots__:
                self.__setattr__(field, kwargs.get(field, None))

    def _extractPubMedId(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//ArticleId[@IdType='pubmed']"
        return getContent(element=xml_element, path=path)

    def _extractTitle(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//ArticleTitle"
        return getContent(element=xml_element, path=path)

    def _extractKeywords(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//Keyword"
        return [
            keyword.text for keyword in xml_element.findall(path) if keyword is not None
        ]

    def _extractJournal(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//Journal/Title"
        return getContent(element=xml_element, path=path)

    def _extractAbstract(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//AbstractText"
        return getContent(element=xml_element, path=path)

    def _extractConclusions(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//AbstractText[@Label='CONCLUSION']"
        return getContent(element=xml_element, path=path)

    def _extractMethods(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//AbstractText[@Label='METHOD']"
        return getContent(element=xml_element, path=path)

    def _extractResults(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//AbstractText[@Label='RESULTS']"
        return getContent(element=xml_element, path=path)

    def _extractCopyrights(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//CopyrightInformation"
        return getContent(element=xml_element, path=path)

    def _extractDoi(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//ArticleId[@IdType='doi']"
        return getContent(element=xml_element, path=path)

    def _extractPublicationDate(
        self: object, xml_element: TypeVar("Element")
    ) -> TypeVar("datetime.datetime"):
        # Get the publication date
        try:

            # Get the publication elements
            publication_date = xml_element.find(".//PubMedPubDate[@PubStatus='pubmed']")
            publication_year = int(getContent(publication_date, ".//Year", None))
            publication_month = int(getContent(publication_date, ".//Month", "1"))
            publication_day = int(getContent(publication_date, ".//Day", "1"))

            # Construct a datetime object from the info
            return datetime.date(
                year=publication_year, month=publication_month, day=publication_day
            )

        # Unable to parse the datetime
        except Exception as e:
            print(e)
            return None

    def _extractAuthors(self: object, xml_element: TypeVar("Element")) -> list:
        return [
            {
                "lastname": getContent(author, ".//LastName", None),
                "firstname": getContent(author, ".//ForeName", None),
                "initials": getContent(author, ".//Initials", None),
                "affiliation": getContent(author, ".//AffiliationInfo/Affiliation", None),
            }
            for author in xml_element.findall(".//Author")
        ]

    def _initializeFromXML(self: object, xml_element: TypeVar("Element")) -> None:
        """ Helper method that parses an XML element into an article object.
        """

        # Parse the different fields of the article
        self.pubmed_id = self._extractPubMedId(xml_element)
        self.title = self._extractTitle(xml_element)
        self.keywords = self._extractKeywords(xml_element)
        self.journal = self._extractJournal(xml_element)
        self.abstract = self._extractAbstract(xml_element)
        self.conclusions = self._extractConclusions(xml_element)
        self.methods = self._extractMethods(xml_element)
        self.results = self._extractResults(xml_element)
        self.copyrights = self._extractCopyrights(xml_element)
        self.doi = self._extractDoi(xml_element)
        self.publication_date = self._extractPublicationDate(xml_element)
        self.authors = self._extractAuthors(xml_element)
        self.xml = xml_element

    def toDict(self: object) -> dict:
        """ Helper method to convert the parsed information to a Python dict.
        """

        return {key: self.__getattribute__(key) for key in self.__slots__}

    def toJSON(self: object) -> str:
        """ Helper method for debugging, dumps the object as JSON string.
        """

        return json.dumps(
            {
                key: (value if not isinstance(value, (datetime.date, Element)) else str(value))
                for key, value in self.toDict().items()
            },
            sort_keys=True,
            indent=4,
        )
