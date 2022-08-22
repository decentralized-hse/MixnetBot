from typing import List, Union

from typeguard import typechecked


#
@typechecked
def some_function(a: int) -> bool:
    a: int = "2"
    return True
some_function(1)
