from pymed import PubMed


# Create a PubMed object that GraphQL can use to query
# Note that the parameters are not required but kindly requested by PubMed Central
# https://www.ncbi.nlm.nih.gov/pmc/tools/developers/
pubmed = PubMed(tool="MyGraphQL_API", email="my@email.address")

# Create a GraphQL query in plain text
query = '''
{
  articles(query: "asthma", maxResults: 15) {
    articleId
    title
    keywords
    publicationDate
  }
}
'''


# Execute the query against the GraphQL schema
result = pubmed.query(query)

# Loop over the retrieved articles
for article in result.data.get("articles"):

    # Extract information from the retrieved article
    article_id = article.get("articleId", "")
    title = article.get("title", "")
    keywords = "\", \"".join(article.get("keywords", []))
    publication_date = article.get("publicationDate", "")

    # Show information about the article
    print(f"{article_id} - {publication_date} - {title}\nKeywords: \"{keywords}\"\n")
