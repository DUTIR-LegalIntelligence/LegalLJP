import os
import tqdm
import json

def load_dataset(path):
    data = []
    with open(path,"r") as f:
        for line in tqdm.tqdm(f.readlines()):
            line = json.loads(line.strip())
            data.append(line)
    return data

def save_json(files,path):
    with open(path,"w") as f:
        for corpus in tqdm.tqdm(files):
            f.write(json.dumps(corpus,ensure_ascii=False))
            f.write("\n")

def prompt():
    
    dataset = load_dataset("./data/train_pure_n11000_quantile0.9_bert_easy.jsonl")

    data = []
    for d in dataset:
        assistant = []
        for a in d["Annotations"]:
            if a['criminals'] == None:
                continue
            judge = []
            for j in a["annotation"]:
                if j['penalty'] in ["无罪","免予刑事处罚","死刑","无期徒刑"]:
                    judge.append("犯%s罪，判处%s"%(j['charge'],j['penalty']))
                else:
                    judge.append("犯%s罪，判处%s%s"%(j['charge'],j['penalty'],j['imprisonment']))
            #judge = "；".join(judge)
            if a['penalty'] in ["无罪","免予刑事处罚","死刑","无期徒刑"]:
                judge.append("决定判处%s"%(a['penalty']))
            else:
                judge.append("决定判处%s%s"%(a['penalty'],a['imprisonment']))
            judge = "；".join(judge)
            judge = a['criminals'] + judge
            assistant.append(judge)
        
        if len(assistant) > 0:
            assistant = "\n".join(assistant)
        else:
            continue
         
        human = []
        for k in ["Procuratorate"]:
            if "<None>" in d[k]:
                continue
            #human = "".join([human,d[k]])
            string = "预测下文判罚结果:" + d[k].strip()
            if len(string) > 20 and len(string) < 896:
                human.append(string)
        
        if len(human) == 0:
            continue

        data.append({"conversation":[{"human":human[0],"assistant":assistant}]})
    print("save..")
    save_json(data,"./corpus/train_firefly_easy.jsonl")

if __name__ == "__main__":
    prompt()