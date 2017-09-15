import sys
import pandas as pd

arg = sys.argv[1]
df = pd.DataFrame(range(10))
df.to_csv("M:/CNRACL/test/toto_{}.csv".format(arg))

