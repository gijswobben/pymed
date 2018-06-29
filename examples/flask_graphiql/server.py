from pymed import schema
from pymed import PubMedLoader

from flask import Flask
from flask_graphql import GraphQLView


# Create the Flask app
app = Flask(__name__)

# Create a PubMed object that GraphQL can use to query
# Note that the parameters are not required but kindly requested by PubMed Central
# https://www.ncbi.nlm.nih.gov/pmc/tools/developers/
pubmed = PubMedLoader(tool="MyGraphQL_API", email="my@email.address")

# Add an endpoint to the Flask app that serves GraphiQL
app.add_url_rule(
    "/graphql", view_func=GraphQLView.as_view("graphql", schema=schema, graphiql=True, context={"pubmed": pubmed})
)


# Add a default route that points users to the right URL
@app.route("/")
def index():
    return "Please visit /graphql to view the GraphiQL interface."


if __name__ == "__main__":

    # Start the app (debug mode is optional of course)
    app.run(debug=True)
