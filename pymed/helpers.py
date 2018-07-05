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
        yield iterable[index : min(index + n, length)]
