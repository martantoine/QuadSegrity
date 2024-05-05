from gymnasium.spaces import Box, Tuple
from gymnasium.spaces.utils import flatten_space
import numpy as np

force_max = 40.0
switching_max = 10
test = Tuple((Box(low=0, high=force_max, shape=(2,), dtype=np.float64), Box(low=0, high=switching_max, shape=(8,), dtype=np.int8)))
# error with this tupleof boxes,fix it
test1 = Box(low=0, high=force_max, shape=(2,), dtype=np.float64)
test2 = Box(low=0, high=switching_max, shape=(8,), dtype=np.int8)
print(flatten_space(test))
print(flatten_space(test).sample())

flatten_space(Tuple((
            Box(low=0, high=force_max, shape=(2,), dtype=np.float64),
            Box(low=0, high=switching_max, shape=(8,), dtype=np.int8)
        )))

    
