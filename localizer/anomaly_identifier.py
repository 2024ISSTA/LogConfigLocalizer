import os
import csv
import pandas as pd
import argparse
from util import gen_bug_report
import sys 

negative_set = ['error','exception','invalid', 'failure','disable', 'false','fault','warn','because','exit'] #'kill',

#加载normal/single log file的template 用于比较
#path:就是csv file path
def load_template_data(path):
    data = []
    with open(path, 'r') as file:
        csv_reader = csv.DictReader(file)
        for line in csv_reader:
            event_id = line['EventId']
            event_template = line['EventTemplate']
            data.append((event_id,event_template))
    return data


#norm:是包含templated_id 和 template的
#may:是单个log file包含上述两个东西
#name是对应的log file的path
def get_specific_templates(norm,may,name):
    norm = pd.DataFrame(norm)
    norm_id = set(norm.iloc[:,0])
    may = pd.DataFrame(may)
    may_id = set(may.iloc[:,0])
    intersect = norm_id.intersection(may_id)
    may_specific = may_id - intersect
    free_specific = norm_id - intersect
    #保存may_specific对应的csv文件
    filename = os.path.join(name ,"may_specific.csv")
    norm_name = os.path.join(name,"free_specific.csv")
    may[may[0].isin(may_specific)].to_csv(filename, index=False)
    norm[norm[0].isin(free_specific)].to_csv(norm_name,index=False)
    print("may_specific.csv stored.")
    print("free_specific.csv stored.")
    return may[may[0].isin(may_specific)]


def count_anomaly_degree(str):
    anm = 0
    for char in negative_set:
        if char in str.lower():
            anm = anm+0.1
            # print(char)
    return anm

#may_specific:是包含logid 和 logtemplate的
def get_anomaly_degree(may_specific):
    dats = []
    maxanum = -1
    maxhashid = -1
    for index,row in may_specific.iterrows():
        log_tem = row[1]
        anm = count_anomaly_degree(log_tem)
        if anm>maxanum:
            maxanum = anm
            maxhashid = row[0]
        if anm>0:
            dats.append((anm,row[0]))
    return dats
        
#读单个logfile的
def get_structure_data(path):
    data = dict()
    hashmap = dict()
    # templates = dict()
    with open(path) as file:
        csv_reader = csv.DictReader(file)
        for line in csv_reader:
            stat_level = line['Level'] #parse的时候出错了
            line_id = line['LineId']
            event_id = line['EventId']
            stat_content = stat_level+"\t"+line['Content'].strip() #line['Component']+
            # template = line['EventTemplate']
            # contnt = ""
            # for line in stat_content:
            #     # print(line)
            #     contnt = contnt+line.strip()
            # print(contnt+" "+stat_level)
            # stat_content = contnt
            # event_template = line['EventTemplate']
            # event_parm = line_id+":"+line['ParameterList']+"\t"+stat_level
            if event_id in data:
                #data[event_id].append(event_parm)
                data[event_id].append(line_id)
            else:
                #data[event_id] = [event_parm]
                data[event_id] = [line_id]
            # if line_id in hashmap:
            #     hashmap[line_id].append(stat_content)
            # else:
            #     hashmap[line_id] = [stat_content]
            hashmap[line_id]=stat_content
            # templates[line_id] = template
    return data,hashmap#,templates


#提供tuple(anmoaly_degree,hashid), 来算这个template是否有对应的高于当前anomaly degree的logging statements
def recover_and_add(t,path):
    stru,linemap = get_structure_data(path)#,tems
    hashid = t[1]
    oldanm = t[0]
    lineids = stru[hashid]
    newrecord = dict() #format: hashid - (the biggest anomaly degree, lineid)
    records = []
    # if there are the same, choose the first one
    for lineid in lineids:
        line = linemap[lineid]
        newanm = oldanm + count_anomaly_degree(line)
        if newanm > oldanm:
            # print(hashid,newanm,linemap[lineid])
            if hashid in newrecord:
                temp_anm = newrecord[hashid][0]
                if newanm > temp_anm:
                    newrecord[hashid] = (newanm,lineid)
                    # print(linemap[lineid])
            else:
                newrecord[hashid] = (newanm,lineid)
                # print(hashid,newanm,linemap[lineid])
            records.append(linemap[lineid])
    most_anomaly_logs = [newrecord[hashid][0],linemap[newrecord[hashid][1]]] #,tems[newrecord[hashid][1]]
    return most_anomaly_logs
    
    
def main(norm_path,err_path):
    template = 'newsyslog_templates.csv'
    strucutred = 'newsyslog_structured.csv'
    
    norm_template = os.path.join(norm_path,template)
    err_template = os.path.join(err_path,template)
    err_strucutre = os.path.join(err_path,strucutred)
    # err_stru = get_structure_data(err_strucutre)
    
    may_anomaly_degree = get_anomaly_degree(get_specific_templates(load_template_data(norm_template),load_template_data(err_template),err_path))
    
    if len(may_anomaly_degree)==0:
        gen_bug_report.main(err_path,"False")
        print("identified as configuration-error-free.")
        sys.exit(0)
        
    lines = []
    for d in may_anomaly_degree:
        # print(d)
        lines.append(recover_and_add(d,err_strucutre)) 
        
    df = pd.DataFrame(lines)
    df = df.rename(columns={0:'anomaly_degree',1:"content"}) #,2:'template'
    df.to_csv(os.path.join(err_path,'anomaly_logs.csv'),index=False)
    print("anomaly_log.csv stored.")
    # print(df)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-fp",help="fault-free-template file path")
    parser.add_argument("-mp",help="fuzzed-file template & strucutre path")
    # parser.add_argument("may_stru_path",help="fuzzed-file stru path")
    args = parser.parse_args()
    if args.fp == None or args.mp == None:
        print("free_path(-fp) and may_path(-mp) are not to be empty!")
        sys.exit(1)
    main(args.fp,args.mp)