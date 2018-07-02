from pymed import PubMed


# Create a PubMed object that GraphQL can use to query
# Note that the parameters are not required but kindly requested by PubMed Central
# https://www.ncbi.nlm.nih.gov/pmc/tools/developers/
pubmed = PubMed(tool="MyTool", email="my@email.address")

# Create a GraphQL query in plain text
query = "occupational health[Title]"


# Execute the query against the API
results = pubmed.query(query, max_results=500)

# Loop over the retrieved articles
for article in results:

    # Extract and format information from the article
    article_id = article.article_id
    title = article.title
    keywords = '", "'.join(article.keywords)
    publication_date = article.publication_date
    abstract = article.abstract

    # Show information about the article
    print(f'{article_id} - {publication_date} - {title}\nKeywords: "{keywords}"\n{abstract}\n')
