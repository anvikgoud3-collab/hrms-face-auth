import numpy as np
from database import init_db, save_samples, get_samples

init_db()
fake = [np.random.rand(128) for _ in range(5)]   # 5 pretend faces
save_samples("TEST001", fake)

saved = get_samples("TEST001")
print("Saved samples:", len(saved), "| numbers in each:", len(saved[0]))