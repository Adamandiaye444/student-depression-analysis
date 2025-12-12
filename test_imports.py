import time
start = time.time()

print('Import pandas...')
import pandas as pd
print(f'Pandas: {time.time()-start:.2f}s')

print('Import numpy...')
import numpy as np
print(f'Numpy: {time.time()-start:.2f}s')

print('Import student_vector_ml...')
try:
    from student_vector_ml import StudentVectorML
    print(f'StudentVectorML: {time.time()-start:.2f}s')
except Exception as e:
    print(f'ERREUR: {e}')
