import Levenshtein

from transformers import DistilBertModel, DistilBertTokenizer
import torch
import numpy as np
import re

model_name = 'distilbert-base-uncased'
tokenizer = DistilBertTokenizer.from_pretrained(model_name)
model = DistilBertModel.from_pretrained(model_name)

def add_space_before_uppercase(text):
    # 使用正则表达式，在大写字母的前面加上空格
    modified_text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    return modified_text

def get_bert_embedding(sentence, model, tokenizer):
    tokens = tokenizer(sentence, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**tokens)
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)

    similarity = dot_product / (norm_vec1 * norm_vec2)
    return similarity



def get_prefix(rdf):
    prefix_dict = {}

    lines = [line for line in rdf.split('\n') if line.startswith('@prefix')]
    for line in lines:
        ele = line.split('<')
        key = ''
        for i in ele:
            if '@prefix' in i:
                key = i.split('@prefix')[-1].strip().strip(':').strip()
                prefix_dict[key] = ''
            if 'http' in i:
                value = i.split('>')[0].strip()
                prefix_dict[key] = value
    return prefix_dict

def calculate_similarity(str1, str2, use_model=0):
    if use_model==0:
        distance = Levenshtein.distance(str1, str2)
        max_len = max(len(str1), len(str2))
        similarity = 1 - distance / max_len
        return similarity
    else:
        str1 = add_space_before_uppercase(str1)
        str2 = add_space_before_uppercase(str2)

        vec1 = get_bert_embedding(str1, model, tokenizer)
        vec2 = get_bert_embedding(str2, model, tokenizer)

        similarity = cosine_similarity(vec1, vec2)
        # print(str1,str2,similarity)
        return similarity


def greedy_mapping(list1, list2, use_model=0):
    mapping = {}
    used_indices = set()

    for i, item1 in enumerate(list1):
        best_match = None
        best_similarity = 0

        for j, item2 in enumerate(list2):
            if '/' in item2:
                if item2.split('/')[-1] != '':
                    item2 = item2.split('/')[-1]
                else:
                    item2 = item2.split('/')[-2]

            if j not in used_indices:
                similarity = calculate_similarity(item1, item2,use_model=use_model)

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = j

        if best_match is not None:
            mapping[item1] = [list2[best_match], best_similarity]
            used_indices.add(best_match)

    return mapping


def prefix_mapping(a, rdf):
    prefix_dict = get_prefix(rdf)
    keys = list(prefix_dict.keys())
    values = list(prefix_dict.values())

    name_sim = greedy_mapping(a, keys)
    http_sim = greedy_mapping(a, values)

    # print(name_sim)
    # print(http_sim)

    final_mapping = {}
    for i in a:
        sim0 = name_sim[i][-1]
        sim1 = http_sim[i][-1]
        if sim0 >= sim1:
            final_mapping[i] = prefix_dict[name_sim[i][0]]
        else:
            final_mapping[i] = http_sim[i][0]

    if len(list(final_mapping.values())) != len(set(list(final_mapping.values()))):
        sim0 = 0
        sim1 = 0
        for _ in name_sim.keys():
            sim0 += name_sim.values()[-1]
            sim1 += http_sim.values()[-1]

        if sim0 >= sim1:
            final_mapping = {k: prefix_dict[v[0]] for k, v in name_sim.items()}
            return final_mapping
        else:
            final_mapping = {k: v[0] for k, v in http_sim.items()}
            return final_mapping

    return final_mapping

