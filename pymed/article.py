import json
import datetime
import re

from xml.etree.ElementTree import Element
from typing import TypeVar
from typing import Optional
from typing import Union

from .helpers import getContent
from .helpers import getContentList


class PubMedArticle(object):
    """ Data class that contains a PubMed article.
    """

    __slots__ = (
        "pubmed_id",
        "title",
        "abstract",
        "keywords",
        "mesh_headings",
        "journal",
        "page",
        "issns",
        "volume",
        "issue_number",
        "publication_type",
        "publication_date",
        "pubdate",
        "publication_status",
        "authors",
        "methods",
        "conclusions",
        "results",
        "owner",
        "copyrights",
        "doi",
        "nlm_unique_id",
        "article_ids",
        "pubmedtype",
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

    def _returnPubMedType(self: object) -> str:
        return "PubmedArticle"

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

    def _extractMeshHeadings(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//MeshHeadingList"
        meshList = getContentList(xml_element, path, None)
        if meshList is None or len(meshList) == 0:
            return None
        else:
            return [
                    {
                        descriptior.text: descriptior.attrib['MajorTopicYN']
                    }
                for heading in meshList for descriptior in heading.findall(".//DescriptorName")
            ]

    def _extractJournal(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//Journal/Title"
        return getContent(element=xml_element, path=path)

    def _extractPages(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//Pagination/MedlinePgn"
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

    def _extractNlmUniqueID(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//NlmUniqueID"
        return getContent(element=xml_element, path=path)

    def _extractArticleIDs(self: object, xml_element: TypeVar("Element")) -> dict:
        path = ".//ArticleIdList"
        return {
                id.attrib['IdType']: id.text

            for id in getContentList(xml_element, path, None)
            }

    def _extractPublicationType(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//PublicationTypeList/PublicationType"
        return getContent(element=xml_element, path=path)

    def _extractPublicationStatus(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//PublicationStatus"
        return getContent(element=xml_element, path=path)

    def _extractOwner(self: object, xml_element: TypeVar("Element")) -> str:
        path = ".//MedlineCitation"
        return xml_element.find(path).attrib['Owner']

    def _extractIssueNumber(self: object, xml_element: TypeVar("Element")) -> Optional[int]:
        path = ".//Issue"
        try:
            return int(getContent(element=xml_element, path=path))
        except Exception as e:
            print('line112')
            print(e)
            return None

    def _extractVolume(self: object, xml_element: TypeVar("Element")) -> Optional[int]:
        path = ".//Volume"
        try:
            return int(getContent(element=xml_element, path=path))
        except Exception as e:
            print('line161')
            print(e)
            return None

    def _extractPubDate(self: object, xml_element: TypeVar("Element")) -> Union[TypeVar("datetime.datetime"), TypeVar("str")]:
        # There are multiple ways the PubDate field can be stored in the xml_element
        # as such we ened to test multiple different PubDate formats to looks for the correct one
        try:
            pubDate = xml_element.find(".//PubDate")
        except Exception as e:
            print(e)
            print('No PubDate')
            return None
        try:
            publication_year = getContent(pubDate, ".//Year", None)
        # try to extract the year from the pubDate field
        except Exception as e:
            print(e)
            print("No Pubdate Year")
            # I'm thinking if the year doesn't exist that we should just drop the whole thing
            return None
        try:
            publication_month = getContent(pubDate, ".//Month", "1")
        except Exception as e:
            print(e)
            print("Issues with Pubdate Month")
            pass
        try:
            publication_day = getContent(pubDate, ".//Day", "1")
        except Exception as e:
            print(e)
            print("Date/Day error")
            pass
        try:
            publication_season = getContent(pubDate, ".//Season", None)
        except Exception as e:
            print(e)
            print("Season likely does not exist")
            pass

        # now let's try to create a datetime object from several different potential date formats
        # as currently laid out above, it should be possible to parse a pubDate WITHOUT a month or date fields
        # but it should fail spectactularly if year or the pubDate field do not exist.

        # at this point, all inputs should be str's, the goal is going to be to attempt to run through
        # different combination of str inputs through datetime.strptime() to find a date which works
        # try with abreviated month & numerical date
        try:
            date_string = publication_year + '-' + publication_month + '-' + publication_day
            return datetime.datetime.strptime(
                date_string, "%Y-%b-%d"
            )
        except Exception as e:
            print(e)
            print("Likely missing month or day")
            pass
        # try with only year and abbreviated month
        try:
            date_string = publication_year + '-' + publication_month
            return datetime.datetime.strptime(
                date_string, "%Y-%b"
            )
        except Exception as e:
            print(e)
            pass
        try:
            # assume the month is a number, but has no day component
            date_string = publication_year + '-' + publication_month
            return datetime.datetime.strptime(date_string, "%Y-%m")
        except Exception as e:
            print(e)
            pass
        try:
            # assume the month is a number, but has no day component
            date_string = publication_year + '-' + publication_month + '-' + publication_day
            return datetime.datetime.strptime(date_string, "%Y-%m-%d")
        except Exception as e:
            print(e)
            pass
        try:
            medlineDateStr = getContent(element=xml_element, path=".//PubDate/MedlineDate")
            return medlineDateStr
        except Exception as e:
            print(e)
            pass
        try:
            date_string = publication_year + '-' + publication_season
            return date_string
        except Exception as e:
            print(e)
            return None

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
        # adding regular expression support to extract ORCID more cleanly
        pattern = re.compile("(https?://orcid.org/)([0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9]{1}|[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}X)")
        authors = []
        for author in xml_element.findall(".//Author"):
            print(getContent(author, ".//Identifier", None))
            if getContent(author, ".//Identifier", None):
                try:
                    orcid = re.match(pattern, getContent(author, ".//Identifier", None))[2]
                except Exception as e:
                    print(e)
                    print(getContent(author, ".//Identifier"))
                    orcid = None
            else:
                orcid = None
            authors.append({
                "lastname": getContent(author, ".//LastName", None),
                "firstname": getContent(author, ".//ForeName", None),
                "initials": getContent(author, ".//Initials", None),
                "affiliation": getContent(author, ".//AffiliationInfo/Affiliation", None),
                "Identifier": orcid,
            })
        return authors

    def _extractISSNs(self: object, xml_element: TypeVar("Element")) -> dict:
        return {
                "eISSN": getContent(xml_element, ".//ISSN[@IssnType='Electronic']", None),
                "ISSN": getContent(xml_element, ".//ISSN[@IssnType='Print']", None),
                "ISSNLinking": getContent(xml_element, ".//ISSNLinking", None)
        }

    def _initializeFromXML(self: object, xml_element: TypeVar("Element")) -> None:
        """ Helper method that parses an XML element into an article object.
        """

        # Parse the different fields of the article
        self.pubmed_id = self._extractPubMedId(xml_element)
        self.title = self._extractTitle(xml_element)
        self.keywords = self._extractKeywords(xml_element)
        self.mesh_headings = self._extractMeshHeadings(xml_element)
        self.journal = self._extractJournal(xml_element)
        self.page = self._extractPages(xml_element)
        self.volume = self._extractVolume(xml_element)
        self.issue_number = self._extractIssueNumber(xml_element)
        self.issns = self._extractISSNs(xml_element)
        self.abstract = self._extractAbstract(xml_element)
        self.conclusions = self._extractConclusions(xml_element)
        self.methods = self._extractMethods(xml_element)
        self.results = self._extractResults(xml_element)
        self.copyrights = self._extractCopyrights(xml_element)
        self.doi = self._extractDoi(xml_element)
        self.nlm_unique_id = self._extractNlmUniqueID(xml_element)
        self.article_ids = self._extractArticleIDs(xml_element)
        self.owner = self._extractOwner(xml_element)
        self.publication_type = self._extractPublicationType(xml_element)
        self.publication_date = self._extractPublicationDate(xml_element)
        self.publication_status = self._extractPublicationStatus(xml_element)
        self.pubdate = self._extractPubDate(xml_element)
        self.authors = self._extractAuthors(xml_element)
        self.pubmedtype = self._returnPubMedType()
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
