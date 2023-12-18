# LogConfigLocalizer
This repository is for "Face it Yourselves: An LLM-based Two-Stage Strategy to Localize Configuration Errors"
## Install
1. python >=3.8
## Datasets & Experimental Results
**wordcount**,**sort**,**terasort**,**pagerank**,**kmeans**: five workloads for Hadoop
- *default*, logs generated in the default mode
- *may-fault-8*, logs generated in the mutated mode for 8 hours fuzzing
  - raw-logs: generated logs
  - experimental:
     1. nl/nv-logs: for RQ2 & RQ4;
     2. o-baseline-logs: for RQ1 & RQ2;
     3. statistics: for RQ1 - "S1-A"
  
**Practical_Case_Study**: 33 selected cases from the preliminary study
  - *logs-practical*: logs offered by end-users
  - *results-practical*: the results of the practical case study
    - `application_001` and  `application_070` is the selected cases to elaborate.  
## Code
**Localizer**
  - Stage 1: *anomaly_idnetifier.py*
  - Stage 2: *failure_diagnoser_with_des_with_direct.py*

    tips: **Set the API Key inside it before using it.**
  - Diagnosis Report Generation:  *util.gen_bug_report.py*
    
**Parser**
  - Improved Drain: *Drain.py*
## Scripts to Activate LogConfigLocalizer
-   Stage 1: *evaluation_hadoop_first_stage_only.sh*
    1. Parsing: build `Drain` first, see [README](https://github.com/2024ISSTA/LogConfigLocalizer/blob/main/parser/README.md)

        Please change the `directory_path` inside the `data_recursive.py` first and then
       ```python3 /parser/data_recursive.py```
    3. Remaining Steps:
    ```./evaluation_hadoop_first_stage_only.sh <path/to/may-fault-8/rawlogs/> <path/to/fault-free/parsed_output>```

       Example: Test Cases of the terasort workload.
       1. `directory_path="terasort/may-fault-8/raw-logs"`
       2. `python3 /parser/data_recursive.py`
       3. `./evaluation_hadoop_first_stage_only.sh /terasort/may-fault-8/raw-logs /terasort/fault-free/parsed_output`
-   Stage 2: *evaluation_hadoop_second_stage_only.sh*   
    ```./evaluation_hadoop_second_stage_only.sh <path/to/may-fault-8/rawlogs/>```

      Example: Test Cases of the terasort workload.
    
      `./evaluation_hadoop_second_stage_only.sh /terasort/may-fault-8/raw-logs`
-   Diagnosis Report Generation: *evaluation_hadoop_added_report.sh*

    ```./evluation_hadoop_added_report.sh <path/to/may-fault-8/rawlogs>```

    Example: Test Cases of the terasort workload.

    `./evaluation_hadoop_added_report.sh ./terasort/may-fault-8/raw-logs/`
