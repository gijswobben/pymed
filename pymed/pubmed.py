from .schema import schema
from .loaders import PubMedLoader

from typing import TypeVar


class PubMed(object):
    """ Wrapper class that allows users to query PubMed through GraphQL queries.
    """

    def __init__(self: object, tool: str = "MyGraphQL_API", email: str = "my@email.address") -> None:
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

        self.pubmed_loader = PubMedLoader(tool=tool, email=email)
        self.schema = schema

    def query(self: object, query: str) -> TypeVar("ExecutionResult"):
        """ Method that executes a query agains the GraphQL schema, automatically
            inserting the PubMed data loader.

            Parameters:
                - query     String, the GraphQL query to execute against the schema.

            Returns:
                - result    ExecutionResult, GraphQL object that contains the result
                            in the "data" attribute.
        """

        return schema.execute(query, context_value={"pubmed": self.pubmed_loader})
