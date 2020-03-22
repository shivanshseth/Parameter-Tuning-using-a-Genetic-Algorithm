import os
import json
import numpy as np

directory = 'results'

all_results = []

for filename in os.listdir(directory):
    with open(directory+"/"+ filename,'r') as f:
        all_results.extend(json.load(f))

all_results = sorted(all_results, key=lambda x: np.mean(x[1]))

with open("combined_results",'w') as outfile:
    json.dump(all_results, outfile, indent=2)