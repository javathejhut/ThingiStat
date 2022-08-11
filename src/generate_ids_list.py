import random
import numpy as np
import os
from db_structure import DB_DIR

scrambled_ids_list = random.sample(range(1, 5437527), 5437526)
np.save(os.path.join(DB_DIR, "default_ids_list_v2"), scrambled_ids_list)

