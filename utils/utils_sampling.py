from datasketch import MinHash, MinHashLSH
import torch
from transformers import AutoTokenizer, AutoModel,AutoModelForCausalLM
from torch.utils.data import Dataset,DataLoader
from torch.cuda.amp import autocast
from utils.datasets import CorpusDataset,RepsDataset, collate_fn
import os
import tqdm
import json
import collections
import matplotlib.pyplot as plt
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cdist

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

def load_tokenizer_and_model(args):
    #path = args.model_path

    tokenizer = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
    if args.model_type == "bert":
        model = SentenceTransformer(args.model_path,device = "cuda",trust_remote_code=True)
    else:
        model = AutoModelForCausalLM.from_pretrained(
            args.model_path,
            device_map="auto",
            trust_remote_code=True
        )

    return tokenizer, model


def load_data(args, path, tokenizer, model):
    print("load files..")

    '''
    corpus = [{"Defendant":"被告人吴某，协警。因涉嫌犯刑讯逼供罪于2015年1月24日被刑事拘留，同年2月9日被逮捕。现羁押于温州市看守所。",
               "Procuratorate":"洞头县人民检察院指控，2014年4月10日，被害人刘某因涉嫌犯盗窃罪被温州市公安局龙湾区分局监视居住在龙湾区状元街道拉芳舍商务宾馆内。同月中旬某日凌晨，该分局下辖状元派出所协警吴某等人在巡逻期间来到该宾馆，为获取被害人刘某的口供，被告人吴某用脚踢踹被害人刘某胸部、腿部，致其胸部左侧第7、8、9肋及右第9肋骨折。经鉴定，被害人刘某的损伤程度已达轻伤二级。",
               "Defence":"<None>",
               "Fact":"上述事实，被告人吴某在法庭审理过程中亦无异议，并有被害人刘某的陈述、证人张某甲、张某乙、徐某、林某、陈某达、邵某、娄某、张某丙、叶某某的证言、人物辨认笔录及照片、温州市人民检察院检验鉴定文书、温州医科大学司法鉴定中心司法鉴定意见书、劳动合同书、人员信息表、工作职责、日常管理制度、考核制度、就诊记录、门诊收费明细、CT检查报告单、CT片、刘某盗窃案材料、情况说明、归案说明、身份证明等证据予以证实，足以认定。",
               "Conclusion":"本院认为，被告人吴某身为司法工作人员，对犯罪嫌疑人实行刑讯逼供，其行为已构成刑讯逼供罪。公诉机关指控的罪名成立。鉴于被告人吴某归案后能如实供述其罪行，自愿认罪，予以从轻处罚。为严肃社会主义法制，保护公民人身权利不受侵犯，根据本案被告人犯罪的事实、犯罪的性质、情节和对于社会的危害程度，",
               "Judgement":"被告人吴某犯刑讯逼供罪，判处有期徒刑十个月。",
               "Article":[247,67],
               "Annotations":[]}]
    '''
    corpus = []
    with open(path,"r") as f:
        for line in tqdm.tqdm(f.readlines()):
            line = json.loads(line.strip())

            if line["Defendant"] in "<None>" or line["Procuratorate"] in "<None>" or line["Fact"] in "<None>":
                continue
            if len(line["Article"]) == 0 or len(line["Annotations"]) == 0:
                continue

            corpus.append(line)
        
    dataset = CorpusDataset(args, corpus, tokenizer)

    return dataset

def get_minhash(text):
    minhash = MinHash(num_perm=128)  
    for token in text:
        minhash.update(token.encode('utf8'))
    return minhash

def remove_duplicates(args,dataset,theta=0.9,save_path="./"):
    
    lsh = MinHashLSH(threshold=theta,num_perm=128)
    minhashes = {}

    print("minhash_get..")
    for i in tqdm.tqdm(range(len(dataset))):
        corpus = dataset[i]
        minhash = get_minhash(corpus["text"])
        lsh.insert(i, minhash)
        minhashes[i] = minhash
    
    print("minhash_search..")
    duplicates = {}
    for i in tqdm.tqdm(range(len(dataset))):
        duplicates[i] = sorted([(k,minhashes[i].jaccard(minhashes[k])) for k in lsh.query(minhashes[i])],
                           key=lambda x:x[1],
                           reverse=True)
    
    print("minhash_delete..")
    nodes = collections.Counter()
    for k,v in tqdm.tqdm(duplicates.items()):
        for s in v[1:]:
            if float(s[1]) > theta:
                nodes[s[0]] += 1
            else:
                break
    
    # draw pic
    distribution = collections.Counter()
    for k,v in nodes.items():
        distribution[v] += 1
    distribution = [(i,c) for i,c in distribution.items()]
    distribution = sorted(distribution,key=lambda x:x[0],reverse=False)
    x = np.array([d[0] for d in distribution])
    y = np.array([d[1] for d in distribution])
    plt.bar(x,y,color="r")
    plt.xlabel("Number of Similar Texts in Current Sample")
    plt.ylabel("Number of Samples")
    plt.savefig(os.path.join(args.pic_path,"savefig_distribution_nodecounter_%s.png"%(theta)))

    print("save_nodecounter..")
    distribution = np.array(distribution)
    np.save(os.path.join(args.log_path,"nodecounter.npy"),distribution)

    print("delete_sample..")
    dataset.delete_sample(list(nodes.keys()))

    return dataset

def representation(args,model,dataset,):

    dataloader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        num_workers=0,
        pin_memory=True,
        drop_last=False,
        shuffle=True,
        collate_fn=collate_fn)
    
    ndim = 1024 if args.model_type == "qwen" else 768
    reps = torch.zeros((len(dataloader) * args.batch_size, ndim))  # qwen1.5 hidden_size ~ (batch,seq,1024)
    indices = torch.zeros((len(dataloader) * args.batch_size, 1))
    charges = torch.zeros((len(dataloader) * args.batch_size, 1))
    i = 0

    if args.model_type == "qwen":
        model = model.half().cuda()
    model.eval()

    print("encoding..")
    for inputs in tqdm.tqdm(dataloader):
        input_ids = inputs["input_ids"]
        attention_mask = inputs["attention_mask"]
        input_mask = inputs["input_mask"]
        index = inputs["id"]
        charge_ids = inputs["charge_ids"]
        text = inputs["text"]

        input_ids = input_ids.to(model.device)
        attention_mask = attention_mask.to(model.device)
        input_mask = input_mask.to(model.device)


        outputs = model.encode(text)
        representations = torch.tensor(outputs)

        reps[i * args.batch_size: min((i + 1) * args.batch_size, len(dataset))] = representations.detach().cpu()
        indices[i * args.batch_size: min((i + 1) * args.batch_size, len(dataset))] = index[:, None]
        charges[i * args.batch_size: min((i + 1) * args.batch_size, len(dataset))] = charge_ids[:, None]

        i += 1

    return reps, indices, charges, dataset.classes2id

def load_representation(args):
    reps = torch.save(os.path.join(args.save_path,"representation_n%s_%s.pt"%(args.ncentroids,args.model_type)))
    indices = torch.save(os.path.join(args.save_path,"indices_n%s_%s.pt"%(args.ncentroids,args.model_type)))
    charges = torch.save(os.path.join(args.save_path,"charges_n%s_%s.pt"%(args.ncentroids,args.model_type)))
    with open(os.path.join(args.save_path,"class2id_n%s_%s.json"%(args.ncentroids,args.model_type)),"r") as f:
        classes2id = json.loads(f.readline().strip())
    return reps, indices, charges, classes2id


def cluster(args, reps, indices, charges, classes2id, ncentroids=11000):
    print("kmeans..")
    ndim = 1024 if args.model_type == "qwen" else 768
    
    kmeans = faiss.Kmeans(ndim,ncentroids,niter=20,gpu=False)
    kmeans.train(reps)
    
    cluster_centers = kmeans.centroids 
    
    #obj = kmeans.obj #目标函数，kmeans 中为总的平方差
    #iteration_stats = kmeans.iteration_stats #聚类中的统计信息

    reps_dataset = RepsDataset(reps,indices,charges,classes2id)


    return reps_dataset, torch.tensor(cluster_centers)

def sampling(args, reps_dataset, cluster_centers, dataset):
    print("sample..")
    res_values = []
    res_indices = []
    res_charge = []
    res_cluster_labels = []

    reps_dataloader = DataLoader(reps_dataset, batch_size=args.batch_size, shuffle=False)
    cluster_centers = cluster_centers.to(args.device)

    i = 0
    for tensor,idx,charge in tqdm.tqdm(reps_dataloader):
        tensor = tensor.to(args.device)
        #norm_tensor = torch.linalg.norm(tensor.unsqueeze(dim=1) - cluster_centers.unsqueeze(dim=0), dim=2).detach()
        norm_tensor = torch.nn.functional.cosine_similarity(tensor.unsqueeze(dim=1),cluster_centers.unsqueeze(dim=0),dim=2)
        norm_tensor, norm_tensor_indecies = torch.sort(norm_tensor, dim=1)
        if args.difficulty == 'hard':
            res_values += (norm_tensor[:, 0] - norm_tensor[:, 1] - norm_tensor[:, 2]).tolist()
        elif args.difficulty == 'easy':
            res_values += (-norm_tensor[:, 0]).tolist()

        res_indices += idx.squeeze().tolist()
        res_charge += charge.squeeze().tolist()

        res_cluster_labels += norm_tensor_indecies[:, 0].tolist()
        i += 1
    
    # reordering samples and finding quantiles baesd on each class
    cluster_scores = {k: [res_values[i] for i in range(len(res_values)) if int(res_cluster_labels[i]) == k] for k in
                          range(len(cluster_centers))}


    quantiles = {k: torch.quantile(torch.tensor(cluster_scores[k]), q=args.quantile) for k in range(args.ncentroids) if len(cluster_scores[k]) != 0}
    score_dicts = {int(res_indices[i]): (res_values[i], int(res_charge[i]), int(res_cluster_labels[i])) for i
                       in
                       range(len(res_values))}
    
    origin_based_on_class = {i: [] for i in range(len(reps_dataset.classes2id))}
    results_based_on_class = {i: [] for i in range(len(reps_dataset.classes2id))}

    # finding images which are in the quantile period
    for k, v in tqdm.tqdm(score_dicts.items(),):
        if v[0] > quantiles[v[2]].item():
            results_based_on_class[v[1]].append(k)
        elif len(results_based_on_class[v[1]]) < 20:
            results_based_on_class[v[1]].append(k)
        origin_based_on_class[v[1]].append(k)

    data_pure = []
    for v in results_based_on_class.values():
        data_pure += v
    data_pure = dataset.sample(data_pure)

    return data_pure
    

if __name__ == "__main__":
    pass    
