import json
import pickle
from client_moodle import get_errors,submit
submitted = set()
to_be_submitted = 30

with open('submitted_results','rb') as sf:
    submitted = pickle.load(sf)
    
with open("combined_results",'r') as f:
    combined = json.load(f)
    point=0 
    while(to_be_submitted>0):
        if (tuple(combined[point][0]) not in submitted):
            submit_status = submit('oWWGKhmdis1hyUyJWgHPHDRcOrTLIF98xSuWuUMzLSHWkAeieT', combined[point][0])
            assert "submitted" in submit_status
            submitted.add(tuple(combined[point][0]))
            print(to_be_submitted)
            to_be_submitted-=1
        point+=1

# print(submitted)
with open("submitted_results",'ab') as outfile:
    pickle.dump(submitted,outfile)