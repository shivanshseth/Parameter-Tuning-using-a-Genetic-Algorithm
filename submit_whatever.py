import json
from client_moodle import get_errors,submit

total =700
with open("combined_results",'r') as f:
    combined = json.load(f)
    
    for i in range(total):
        submit_status = submit('oWWGKhmdis1hyUyJWgHPHDRcOrTLIF98xSuWuUMzLSHWkAeieT', combined[i][0])
        assert "submitted" in submit_status
        