import ctypes

from typing import Any


def _calculate_offset_with_index(index: int) -> int:
    return (
            ctypes.sizeof(ctypes.c_ssize_t)  # ob_refcnt
            + ctypes.sizeof(ctypes.c_void_p)  # ob_base
            + ctypes.sizeof(ctypes.c_ssize_t)  # ob_item
            + index * ctypes.sizeof(ctypes.c_void_p)
    )

def _resize_tuple(tup: tuple, new_size: int) -> None:
    """
    Resizes the given tuple to the specified size by modifying its internal structure.

    :param tup: The tuple to be resized.
    :param new_size: The new size for the tuple.
    """
    # Get the internal size pointer of the tuple
    tuple_size_ptr = id(tup) + ctypes.sizeof(ctypes.c_ssize_t)  # Offset for ob_size

    # Write the new size directly into the tuple's internal structure
    ctypes.memmove(
        tuple_size_ptr,
        ctypes.pointer(ctypes.c_ssize_t(new_size)),
        ctypes.sizeof(ctypes.c_ssize_t),
    )

def replace_at(tup: tuple, new_element: Any, index: int):
    """
    :param tup: Tuple object
    :param new_element: element to replace previous element on index
    :param index: index of element to replace
    :return:
    """
    if not isinstance(tup, tuple):
        raise TypeError("tup param must be a tuple")

    if len(tup) == 0:
        return ValueError("Tuple can't be empty")

    if not (0 <= index < len(tup)):
        raise IndexError("Index out of range")

    offset = _calculate_offset_with_index(index)

    ctypes.memmove(
        id(tup) + offset,
        ctypes.pointer(ctypes.py_object(new_element)),
        ctypes.sizeof(ctypes.c_void_p),
    )

def splice_from(tup1: tuple, tup2: tuple, start_index: int = 0):
    """
    Replaces elements of the first tuple with elements of the second tuple, starting at the given index.

    :param tup1: The tuple to be modified.
    :param tup2: The tuple whose elements will be injected into the first tuple.
    :param start_index: The index in the first tuple where the replacement starts.
    """
    if not isinstance(tup1, tuple) or not isinstance(tup2, tuple):
        raise TypeError("Both arguments must be tuples.")
    if not (0 <= start_index < len(tup1)):
        raise IndexError("Start index is out of bounds for the first tuple.")
    if start_index + len(tup2) > len(tup1):
        raise ValueError("Too many elements to replace: exceeds the size of the first tuple.")

    base_offset = _calculate_offset_with_index(start_index)

    # Iterate over elements of the second tuple and replace them in the first tuple
    for i, element in enumerate(tup2):
        current_offset = base_offset + i * ctypes.sizeof(ctypes.c_void_p)
        ctypes.memmove(
            id(tup1) + current_offset,
            ctypes.pointer(ctypes.py_object(element)),
            ctypes.sizeof(ctypes.c_void_p),
        )
if __name__ == "__main__":

    # Example usage
    tup11 = (1, 2, 3, 4, 5)
    tup22 = (42, 43)
    print("Before modification:", tup11)
    replace_at(tup11, 315, 1)
    print("After modification:", tup11)

    print("Before modification:", tup11)
    splice_from(tup11, tup22, start_index=3)
    print("After modification:", tup11)
