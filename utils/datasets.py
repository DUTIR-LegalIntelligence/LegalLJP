from torch.utils.data import Dataset
from typing import Any, Dict, List
import torch
import collections
import tqdm
import os
import json

def collate_fn(batch: List[Dict[str, Any]]):
    input_ids_batch, attention_mask_batch, input_mask_batch, charge_batch, id_batch, text_batch = [], [], [], [], [], []
    for x in batch:
        
        input_ids = x['input_ids']
        attention_mask = x['attention_mask']
        input_mask = x['input_mask']
        charge_ids = x['charge_ids']
        idx = x['id']
        text = x['text']
        
        input_ids_batch.append(input_ids)
        attention_mask_batch.append(attention_mask)
        input_mask_batch.append(input_mask)
        charge_batch.append(charge_ids)
        id_batch.append(idx)
        text_batch.append(text)
    
    input_ids_batch = torch.tensor(input_ids_batch, dtype=torch.long)
    attention_mask_batch = torch.tensor(attention_mask_batch, dtype=torch.long)
    input_mask_batch = torch.tensor(input_mask_batch, dtype=torch.long)
    charge_batch = torch.tensor(charge_batch,dtype=torch.long)
    id_batch = torch.tensor(id_batch, dtype=torch.long)
    inputs = {'input_ids': input_ids_batch,
              'attention_mask': attention_mask_batch,
              'input_mask': input_mask_batch,
              'charge_ids':charge_batch,
              'id':id_batch,
              'text':text_batch,
              }
    return inputs

class RepsDataset(Dataset):
    def __init__(self, reps, indices, charges, classes2id):
        self.reps = reps
        self.indices = indices
        self.charges = charges
        self.classes2id = classes2id

    def __len__(self):
        return len(self.reps)

    def __getitem__(self, idx):
        return self.reps[idx],self.indices[idx],self.charges[idx]

class CorpusDataset(Dataset):
    def __init__(self, args, data, tokenizer):
        self.data = data
        self.classes2id = {}
        self.model_type = args.model_type

        if args.use_representation:
            self.load_classes(args)
        else:
            self.create_classes()

        self.tokenizer = tokenizer
        if args.model_type == "qwen":
            self.tokenizer.add_special_tokens({
                "pad_token": "<|padoftoken|>",
                })
            self.bos_token_id = tokenizer.bos_token_id
            self.eos_token_id = tokenizer.eos_token_id
        elif args.model_type == "bert":
            self.eos_token_id = tokenizer.sep_token_id
            self.bos_token_id = tokenizer.cls_token_id
            pass
        self.pad_token_id = tokenizer.pad_token_id
        self.max_seq_length = args.max_seq_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        #corpus = [v for k,v in self.data[idx].items() if k in ["Defendant","Procuratorate","Defence","Fact","Conclusion",] and v not in "<None>"]
        corpus = [v for k,v in self.data[idx].items() if k in ["Fact",] and v not in "<None>"]
        corpus = "\n".join(corpus)

        #defendant = self.data[idx]["Defendant"]
        #procuratorate = self.data[idx]["Procuratorate"]
        #defence = self.data[idx]["Defence"]
        #fact = self.data[idx]["Fact"]
        #conclusion = self.data[idx]["Conclusion"]
        
        charge_ids = self.data[idx]["chargeid"]
        corpus_ids = self.tokenizer(corpus, add_special_tokens=True,padding=False,max_length=self.max_seq_length).input_ids       
        corpus_ids = corpus_ids[:int(self.max_seq_length) - 1] + [self.eos_token_id]

        input_mask = [0] * len(corpus_ids)
        attention_mask = [1] * len(corpus_ids)

        assert len(corpus_ids) == len(input_mask) == len(attention_mask)

        if len(corpus_ids) < self.max_seq_length:
            padding = self.max_seq_length - len(corpus_ids)
            corpus_ids = [self.pad_token_id] * padding + corpus_ids
            input_mask = [0] * padding + input_mask
            attention_mask = [0] * padding + attention_mask

        return {"input_ids":corpus_ids,
                "input_mask":input_mask,
                "attention_mask":attention_mask,
                "text":corpus,
                "charge_ids":charge_ids,
                "id":idx}
    
    def delete_sample(self,index:list):
        delete_index = sorted(index,reverse=False)
        delete_index += [-1]
        index_iter = iter(delete_index)

        index = []
        delete = next(index_iter)
        for i in range(len(self.data)):
            if i == delete:
                index.append(-1)
                delete = next(index_iter)
            else:
                index.append(i)
        
        data = []
        for i in tqdm.tqdm(index):
            if i == -1:
                continue
            data.append(self.data[i])

        self.data = data
    
    def sample(self,index:list):
        print("sample_data_from_corpus..")
        sample_index = sorted(index,reverse=False)
        sample_index += [-1]
        sample_iter = iter(sample_index)

        sample_data = []
        s = next(sample_iter)
        for i, _ in tqdm.tqdm(enumerate(self.data)):
            if i == s:
                s = next(sample_iter)
                sample_data.append(self.data[i])
        return sample_data
    
    def create_classes(self,):
        classes_counter = collections.Counter()
        for d in self.data:
            classes_counter[d["charge"]] += 1
        self.classes2id = {k:i for i,k in enumerate(classes_counter.keys())}
        for i in range(len(self.data)):
            self.data[i]["chargeid"] = self.classes2id[self.data[i]["charge"]]
    
    def load_classes(self,args):
        with open(os.path.join(args.save_path,"class2id.json"),"w") as f:
            self.classes2id = json.loads(f.readline().strip())
        for i in range(len(self.data)):
            self.data[i]["chargeid"] = self.classes2id[self.data[i]["charge"]]
