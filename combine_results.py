import os
import json
import numpy as np

directory = 'results'

all_results = []

for filename in os.listdir(directory):
    with open(directory+"/"+ filename,'r') as f:
        all_results.extend(json.load(f))
all_results = sorted(all_results, key=lambda x: (1 * x[1][0] + 1 * x[1][1] + 0.5 * abs(x[1][1]-x[1][0])))
all_results = [result+[i] for i,result in enumerate(all_results)]

with open("combined_results3",'w') as outfile:
    json.dump(all_results, outfile, indent=2)