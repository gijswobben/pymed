from typing import TypeVar


def batches(iterable: list, n: int = 1) -> list:
    """ Helper method that creates batches from an iterable.

        Parameters:
            - iterable      Iterable, the iterable to batch.
            - n             Int, the batch size.

        Returns:
            - batches       List, yields batches of n objects taken from the iterable.
    """

    # Get the length of the iterable
    length = len(iterable)

    # Start a loop over the iterable
    for index in range(0, length, n):

        # Create a new iterable by slicing the original
        yield iterable[index: min(index + n, length)]


def getContent(
    element: TypeVar("Element"), path: str, default: str = None, separator: str = "\n"
) -> str:
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
    result = element.findall(path)

    # Return the default if there is no such element
    if result is None or len(result) == 0:
        return default

    # Extract the text and return it
    else:
        return separator.join([sub.text for sub in result if sub.text is not None])


def getContentList(element: TypeVar("Element"), path: str, default: str = None) -> list:
    """ Internal helper method that retrieves the text content of an
            XML element.

            Parameters:
                - element   Element, the XML element to parse.
                - path      Str, Nested path in the XML element.
                - default   Str, default value to return when no text is found.

            Returns:
                - list of values of the XML list
    """
    # Find the path in the element
    result = element.findall(path)

    # Return the Default value if there is no such element
    if result is None or len(result) == 0:
        return default

    # Extracts and returns the results
    else:
        return [listelement for elem in result for listelement in elem]
