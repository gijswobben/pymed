import json
import datetime

from typing import TypeVar
from typing import Optional

from .helpers import getContent


class PubMedBookArticle(object):
    """ Data class that contains a PubMed article.
    """

    __slots__ = (
        "pubmed_id",
        "title",
        "abstract",
        "publication_date",
        "authors",
        "copyrights",
        "doi",
        "isbn",
        "language",
        "publication_type",
        "sections",
        "publisher",
        "publisher_location",
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
        path = ".//BookTitle"
        return getContent(element=xml_element, path=path)

    def _extractAbstract(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//AbstractText"
        return getContent(element=xml_element, path=path)

    def _extractCopyrights(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//CopyrightInformation"
        return getContent(element=xml_element, path=path)

    def _extractDoi(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//ArticleId[@IdType='doi']"
        return getContent(element=xml_element, path=path)

    def _extractIsbn(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//Isbn"
        return getContent(element=xml_element, path=path)

    def _extractLanguage(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//Language"
        return getContent(element=xml_element, path=path)

    def _extractPublicationType(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//PublicationType"
        return getContent(element=xml_element, path=path)

    def _extractPublicationDate(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//PubDate/Year"
        return getContent(element=xml_element, path=path)

    def _extractPublisher(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//Publisher/PublisherName"
        return getContent(element=xml_element, path=path)

    def _extractPublisherLocation(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//Publisher/PublisherLocation"
        return getContent(element=xml_element, path=path)

    def _extractAuthors(self: object, xml_element: TypeVar("Element")) -> list:
        return [
            {
                "collective": getContent(author, path=".//CollectiveName"),
                "lastname": getContent(element=author, path=".//LastName"),
                "firstname": getContent(element=author, path=".//ForeName"),
                "initials": getContent(element=author, path=".//Initials"),
            }
            for author in xml_element.findall(".//Author")
        ]

    def _extractSections(self: object, xml_element: TypeVar("Element")) -> list:
        return [
            {
                "title": getContent(section, path=".//SectionTitle"),
                "chapter": getContent(element=section, path=".//LocationLabel"),
            }
            for section in xml_element.findall(".//Section")
        ]

    def _initializeFromXML(self: object, xml_element: TypeVar("Element")) -> None:
        """ Helper method that parses an XML element into an article object.
        """

        # Parse the different fields of the article
        self.pubmed_id = self._extractPubMedId(xml_element)
        self.title = self._extractTitle(xml_element)
        self.abstract = self._extractAbstract(xml_element)
        self.copyrights = self._extractCopyrights(xml_element)
        self.doi = self._extractDoi(xml_element)
        self.isbn = self._extractIsbn(xml_element)
        self.language = self._extractLanguage(xml_element)
        self.publication_date = self._extractPublicationDate(xml_element)
        self.authors = self._extractAuthors(xml_element)
        self.publication_type = self._extractPublicationType(xml_element)
        self.publisher = self._extractPublisher(xml_element)
        self.publisher_location = self._extractPublisherLocation(xml_element)
        self.sections = self._extractSections(xml_element)

    def toDict(self: object) -> dict:
        """ Helper method to convert the parsed information to a Python dict.
        """

        return {
            key: (self.__getattribute__(key) if hasattr(self, key) else None)
            for key in self.__slots__
        }

    def toJSON(self: object) -> str:
        """ Helper method for debugging, dumps the object as JSON string.
        """

        return json.dumps(
            {
                key: (value if not isinstance(value, datetime.date) else str(value))
                for key, value in self.toDict().items()
            },
            sort_keys=True,
            indent=4,
        )
