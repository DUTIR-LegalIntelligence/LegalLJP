import os
import json
import tqdm
import random
from processing import save_files

def load_index(path):
    index = {}
    with open(path,"r") as f:
        for i,l in enumerate(f.readlines()):
            try:
                l = l.split(",")
                index[l[1].strip()] = l[0].strip()
            except Exception:
                print(l)
                exit()
    return index

def load_data(path):
    print("load files..")
    corpus = []
    with open(path,"r") as f:
        for line in tqdm.tqdm(f.readlines()):
            line = json.loads(line.strip())

            if line["Defendant"] in "<None>" or line["Procuratorate"] in "<None>" or line["Fact"] in "<None>":
                continue
            if len(line["Article"]) == 0 or len(line["Annotations"]) == 0:
                continue

            corpus.append(line)
        
    return corpus


def corpus_split():
    #path = "/home/sda/zhangyuanyu/workspace/Judgment/codekey_proofread.txt"
    index = load_index("./codekey_proofread.txt")
    corpus = load_data("./data/corpus.jsonl")
    
    pool = {i:[] for i in index.keys()}
    for cps in tqdm.tqdm(corpus):
        if cps["charge"] in index.keys():
            pool[cps["charge"]].append(cps)
    
    print(len(index.keys()))
    print(len(pool.keys()))

    delete = [i for i in pool.keys() if len(i) <= 30]
    pool = {k:v for k,v in pool.items() if len(v) > 30}
    print(len(pool))
    print(delete)

    train,test = [],[]
    for k, v in pool.items():
        random.shuffle(v)
        # 一阶段，每个罪名至少保留30份文档
        test += v[:10]
        train += v[10:20]
        # 二阶段，将10per的数据集作为测试集，90per的数据集作为训练集
        for d in v[20:]:
            p = random.random()
            if p > 0.9:
                test.append(d)
            else:
                train.append(d)
    print(len(train))
    print(len(test))

    save_files(train,os.path.join("./corpus","train.jsonl"))
    save_files(test,os.path.join("./corpus","test.jsonl"))
  

if __name__ == "__main__":
    corpus_split()

