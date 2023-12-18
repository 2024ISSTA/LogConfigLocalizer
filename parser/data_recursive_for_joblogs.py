#!/usr/bin/env python

import sys
import os
sys.path.append('../../')
from Drain import LogParser
import time

log_format = '<Date> <Time>,<Pid> <Level> <Component>: <Content>'  # HDFS log format
directory_path = r"/usr/local/evaluation-logs/kmeans/may-fault-8/job-logs" 

regex      = [
    r'blk_(|-)[0-9]+' , # block id
    r'(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)', # IP
    r'(?<=[^A-Za-z0-9])(\-?\+?\d+)(?=[^A-Za-z0-9])|[0-9]+$', # Numbers
]
st         = 0.5  # Similarity threshold
depth      = 4  # Depth of all leaf nodes

i=0
d02=set()
start_time=time.time()
for root, dirs, files in os.walk(directory_path):
    for dir_name in dirs:
        if dir_name.startswith("application_"):
            application_dir = os.path.join(root, dir_name)
            xml_files = [f for f in os.listdir(application_dir) if f.endswith(".xml")]
            if xml_files:
                print(f"Found XML files in {application_dir}")
                combined_dir = os.path.join(application_dir, "combined")
                if os.path.exists(combined_dir):
                    newsyslog_path = os.path.join(combined_dir,"newsyslog")
                    if os.path.exists(newsyslog_path):
                        input_dir  = combined_dir # The input directory of log file
                        log_file   = 'newsyslog'  # The input log file name
                        output_dir = os.path.join(combined_dir,"parsed_output")
                        print(input_dir)
                        print(output_dir)
                        parser = LogParser(log_format, indir=input_dir, outdir=output_dir,  depth=depth, st=st, rex=regex)
                        parser.parse(log_file)
                        i+=1
                    else:
                        d02.add(application_dir)
                else:
                    d02.add(application_dir)
            else:
                d02.add(application_dir)
        else:
            d02.add(application_dir)





end_time=time.time()
print("Total Time:",end_time-start_time)
print("Total ",i," files")
for d in d02:
    print(d)






