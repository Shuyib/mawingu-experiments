from datetime import datetime
import time
import numpy as np 

# print string with time now
print("Starting dot product operation at: ", datetime.now())

print("Doing the operation.....")

# do a dot product with matrix with 2D array
# row by column that's how its done.
dot_product = np.random.randn(2,4) @ np.ones((4,2))

print(dot_product)

# wait for 30 seconds
time.sleep(30)

print("Stopping job: ", datetime.now())