import unittest
import Simulator
import pandas as pd

df = pd.read_csv("countries.csv")
data = list(df.iloc[:,0])
i = 1
print("Please Select Countries Name from these data. {Eg. India Japan Iraq} (Note: Spelling Should be correct.................)\n\n")
for x in data:
    print("{}. ".format(i)+x, end='\t\t\t')
    i += 1
print()
count = list(map(str, input().split()))
sd = input("Please Enter starting date... Eg. YYYY-MM-DD\n")
ed = input("Please Enter ending date... Eg. YYYY-MM-DD\n")


SAMPLE_RATIO = int(input("Please Entern Population Ration:... {Eg. 1e6 }"))

class A3Test(unittest.TestCase):
    def runTest(self):
        Simulator.run(countries_csv_name='countries.csv', countries=count, sample_ratio= SAMPLE_RATIO, start_date= sd, end_date= ed)

unittest.main()
