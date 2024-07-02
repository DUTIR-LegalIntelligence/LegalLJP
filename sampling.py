from datasketch import MinHashLSH, MinHash
from transformers.generation import GenerationConfig
import argparse
from utils.utils_sampling import load_tokenizer_and_model,load_data,remove_duplicates,representation,cluster,sampling
import os
from processing import save_files
import torch
import json

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

def get_evaluate_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('--batch_size', default=2, type=int)
    parser.add_argument('--max_seq_length', default=1024, type=int)

    parser.add_argument('--model_path', type=str)
    parser.add_argument('--model_type', default='bert', type=str)  # bert
    parser.add_argument('--device', default='cuda', type=str)

    parser.add_argument('--quantile', default=0.9, type=float)
    parser.add_argument('--use_representation', default=False, type=bool)

    parser.add_argument('--corpus_path', default='/home/sda/zhangyuanyu/workspace/Judgment/corpus/train.jsonl',
                        type=str)
    parser.add_argument('--pic_path', default='/home/sda/zhangyuanyu/workspace/Judgment/pic',
                        type=str)
    parser.add_argument('--log_path', default='/home/sda/zhangyuanyu/workspace/Judgment/log',
                        type=str)
    parser.add_argument('--save_path', default='/home/sda/zhangyuanyu/workspace/Judgment/data',
                        type=str)
    parser.add_argument('--difficulty', default='easy', type=str, choices=['easy', 'hard'])
    parser.add_argument('--ncentroids', default=11000, type=int)

    parser.add_argument('--save_representation', default=True, type=bool)

    arguments = parser.parse_args()
    return arguments


def main():
    args = get_evaluate_parser()
    tokenizer, model = load_tokenizer_and_model(args)
    model.to(args.device)


    if args.use_representation:
        path = os.path.join(args.save_path,"corpus_de_n%s_%s.jsonl"%(args.ncentroids,args.model_type))
        dataset = load_data(args, path, tokenizer, model)

    else:

        dataset = load_data(args, args.corpus_path, tokenizer, model)
        dataset = remove_duplicates(args,dataset,save_path=args.pic_path)

        print("save_data_de..")
        save_files(dataset.data, os.path.join(args.save_path,"corpus_de_n%s_%s.jsonl"%(args.ncentroids,args.model_type)))

    reps, indices, charges, classes2id = representation(args,model,dataset,)

    if args.save_representation:
        torch.save(reps,os.path.join(args.save_path,"representation_n%s_%s.pt"%(args.ncentroids,args.model_type)))
        torch.save(indices,os.path.join(args.save_path,"indices_n%s_%s.pt"%(args.ncentroids,args.model_type)))
        torch.save(charges,os.path.join(args.save_path,"charges_n%s_%s.pt"%(args.ncentroids,args.model_type)))      
        with open(os.path.join(args.save_path,"class2id_n%s_%s.json"%(args.ncentroids,args.model_type)),"w") as f:
            f.write(json.dumps(dataset.classes2id))

    n = args.ncentroids
    print("cluster_%s" % (str(n)))
    reps_dataset, cluster_centers = cluster(args, reps, indices, charges, classes2id, ncentroids=n)
    data_pure = sampling(args, reps_dataset, cluster_centers, dataset)
    print("save_data_pure..")
    data_pure_file = "train_pure_n%s_quantile%s_%s_%s.jsonl"%(n,args.quantile,args.model_type,args.difficulty)
    save_files(data_pure,os.path.join(args.save_path,data_pure_file))

if __name__ == "__main__":
    main()