import Levenshtein

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

def calculate_similarity(str1, str2):
    distance = Levenshtein.distance(str1, str2)
    max_len = max(len(str1), len(str2))
    similarity = 1 - distance / max_len
    return similarity


def greedy_mapping(list1, list2):
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
                similarity = calculate_similarity(item1, item2)

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

