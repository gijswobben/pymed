import graphene
from . import loaders as loaders


class Author(graphene.ObjectType):
    lastname = graphene.String(description="Last name of the author")
    firstname = graphene.String(description="Given names of the author")
    initials = graphene.String(description="Initials of the author")


class Journal(graphene.ObjectType):
    title = graphene.String(description="Title of the journal")


class Article(graphene.ObjectType):
    article_id = graphene.String(description="PubMed article ID")
    title = graphene.String(description="Title of the article")
    abstract = graphene.String(description="Abstract of the article")
    publication_date = graphene.types.datetime.Date(description="Date of publication in the PMC database.")
    authors = graphene.List(Author, description="List of authors that wrote the article.")
    journal = graphene.Field(Journal, description="The journal that publised the article.")
    keywords = graphene.List(graphene.String, description="Keywords that describe the article.")


class PMC(graphene.ObjectType):
    articles = graphene.List(
        Article,
        query=graphene.String(
            required=True,
            description="Query string to send to PMC. Should be in E-Search format (https://www.ncbi.nlm.nih.gov/books/NBK3825/#pmchelp.Search_Queries).",
        ),
        max_results=graphene.Int(description="Maximum number of results to retrieve."),
        description="Query articles. Returns a list of articles that match the query parameters.",
    )

    def resolve_articles(self, info, query=None, max_results=1):
        """ Method that returns articles based on the query parameters. The method "resolves" articles in the PMC database.
        """

        # Find article IDs that match the query parameters
        article_ids = info.context["pubmed"].queryArticleIds(query=query, max_results=max_results)

        # Use the data loader to fetch all the articles
        loader = loaders.ArticleDataLoader(pubmed=info.context["pubmed"])
        return loader.load(article_ids)


schema = graphene.Schema(query=PMC)
__all__ = ["schema"]
