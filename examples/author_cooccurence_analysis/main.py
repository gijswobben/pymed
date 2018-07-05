import csv
import itertools

from pymed import PubMed


# Create a PubMed object that GraphQL can use to query
# Note that the parameters are not required but kindly requested by PubMed Central
# https://www.ncbi.nlm.nih.gov/pmc/tools/developers/
pubmed = PubMed(tool="Author co-occurence analysis", email="my@email.address")

# Create a GraphQL query in plain text
query = "occupational health[Title]"


# Execute the query against the API
results = list(pubmed.query(query, max_results=1344))


# Create a node for each unique author
nodes = {
    author: index
    for index, author in enumerate(
        set(
            itertools.chain.from_iterable(
                [
                    [
                        f'{author["lastname"]} {author["firstname"]}'
                        for author in article.authors
                    ]
                    for article in results
                ]
            )
        )
    )
}

# Create an edge for each combination of authors (co-authorship)
edges = list(
    itertools.chain.from_iterable(
        [
            [combination for combination in itertools.combinations(co_author_list, 2)]
            for co_author_list in [
                [
                    nodes[f'{author["lastname"]} {author["firstname"]}']
                    for author in article.authors
                ]
                for article in results
            ]
        ]
    )
)

# De-duplicate the list of edges by adding a weight
edges = set([(edge[0], edge[1], edges.count(edge)) for edge in edges])


# Open the nodes file
with open("./nodes.csv", "w", encoding="utf8", newline="") as nodes_file:

    # Create a CSV writer
    writer = csv.writer(nodes_file, delimiter=",")

    # Write the header
    writer.writerow(["id", "label"])

    # Loop over the authors and create rows
    for name, index in nodes.items():
        writer.writerow([index, name])


with open("./edges.csv", "w", encoding="utf8", newline="") as edge_file:

    # Create a CSV writer
    writer = csv.writer(edge_file, delimiter=",")

    # Write the header
    writer.writerow(["source", "target", "weight"])

    # Loop over the edges and put them in the file
    for edge in edges:
        writer.writerow(edge)
