from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from  alignment import prefix_mapping,greedy_mapping
def fill_rig(form_data,rdg):

    g = Graph()
    # rdg
    g.parse(data=rdg, format='n3')

    has_mapping_node = None
    for _, _, o in g.triples((None, Namespace("http://sswapmeet.sswap.info/sswap/").hasMapping, None)):
        if isinstance(o, BNode):
            has_mapping_node = o
            break

    prefix = prefix_mapping(['cottage'],rdg)
    print(prefix)
    cottage_namespace = Namespace(prefix['cottage'])

    # alignment
    form_data_keys = list(form_data.keys())
    rdg_key = []
    for s, p, o in g.triples((has_mapping_node, None, None)):
        if prefix['cottage'] in p:
            if'#' in p:
                p = p.split('#')[-1]
                if '/' in p:
                    p = p.split('/')[-1]
            else:
                p = p.split('/')[-1]
            rdg_key.append(p)

    key_mapping = greedy_mapping(form_data_keys,rdg_key,use_model=1)
    print('fill_rig key_mapping')
    print(key_mapping)
    # fill_rig here
    for key, value in form_data.items():
            for s, p, o in g.triples((has_mapping_node, getattr(cottage_namespace, key_mapping[key][0]), None)):
                g.remove((s, p, o))
                g.add((s, p, Literal(value)))

    rig = g.serialize(format='n3')
    # print(rig)
    return rig

def read_rig(rig):
    g = Graph()
    # rig
    # g.parse("rdg.rdf", format='n3')
    g.parse(data=rig, format='n3')


    prefix = prefix_mapping(['cottage'],rig)

    cottage_ns = Namespace(prefix['cottage'])
    sswap = Namespace("http://sswapmeet.sswap.info/sswap/")

    query = """
    SELECT ?propertyName ?propertyValue
    WHERE {
        ?mappingNode sswap:hasMapping ?objectNode.
        
        ?objectNode ?propertyName ?propertyValue.
    }
    """
    user_input = {}
    results = g.query(query, initNs={"sswap": sswap, "cottage":cottage_ns})

    for row in results:
        key = str(row['propertyName'])
        if prefix['cottage'] in key:
            # key = key.split("/")[-1]
            if '#' in key:
                key = key.split('#')[-1]
                if '/' in key:
                    key = key.split('/')[-1]
            else:
                key = key.split('/')[-1]


            value = str(row['propertyValue'])

            user_input[key] = value
        else:
            continue

    # print(user_input)
    return user_input

def fill_rrg(rig,offer):
    g = Graph()
    # rig
    g.parse(data=rig, format='n3')
    prefix = prefix_mapping(['cottage'], rig)
    cottage = Namespace(prefix['cottage'])
    sswap = Namespace("http://sswapmeet.sswap.info/sswap/")



    has_mapping_node = None
    for _, _, o in g.triples((None, Namespace("http://sswapmeet.sswap.info/sswap/").hasMapping, None)):
        if isinstance(o, BNode):
            has_mapping_node = o
            break

    mapsToNode = None
    for _, _, o in g.triples((None, Namespace("http://sswapmeet.sswap.info/sswap/").mapsTo, None)):
        if isinstance(o, BNode):
            mapsToNode = o
            break

    offer_keys = list(offer.keys())
    rig_key = []
    for s, p, o in g.triples((mapsToNode, None, None)):
        if prefix['cottage'] in p:
            if'#' in p:
                p = p.split('#')[-1]
                if '/' in p:
                    p = p.split('/')[-1]
            else:
                p = p.split('/')[-1]
            rig_key.append(p)
    key_mapping = greedy_mapping(offer_keys, rig_key, use_model=1)
    print('fill_rrg key_mapping')
    print(offer)
    print(key_mapping)
    offer = {v[0]:offer[k] for k,v in key_mapping.items()}
    print('fill_rrg offer')
    print(offer)

    keys = list(offer.keys())
    num_offer = len(offer[keys[0]])
    for i in range(num_offer):
        if i ==0:
            for key in keys:
                for s, p, o in g.triples((mapsToNode, getattr(cottage, key), None)):
                    g.remove((s, p, o))
                    g.add((s, p, Literal(offer[key][i])))

        else:
            new_maps_to_node = BNode()
            g.add((new_maps_to_node, RDF.type, sswap.Object))
            # g.add((new_maps_to_node, RDF.type, cottage.offers))  # add cottage:offers

            for key in keys:
                g.add((new_maps_to_node, getattr(cottage, key), Literal(offer[key][i])))
            g.add((has_mapping_node, sswap.mapsTo, new_maps_to_node))


    rrg = g.serialize(format='n3')

    return  rrg

def read_rrg(rrg):
    g = Graph()
    # rig
    g.parse(data=rrg, format='n3')

    prefix = prefix_mapping(['cottage'], rrg)
    cottage_ns = Namespace(prefix['cottage'])
    sswap = Namespace("http://sswapmeet.sswap.info/sswap/")

    query = """
        SELECT ?propertyName ?propertyValue
        WHERE {
            ?mappingNode sswap:hasMapping ?mapping.
            ?mapping sswap:mapsTo ?objectNode.
            ?objectNode ?propertyName ?propertyValue.
        }
        """
    rrg_offers = {}
    results = g.query(query, initNs={"sswap": sswap, "cottage": cottage_ns})

    for row in results:
        key = str(row['propertyName'])
        if prefix['cottage'] in key:

            if '#' in key:
                key = key.split('#')[-1]
                if '/' in key:
                    key = key.split('/')[-1]
            else:
                key = key.split('/')[-1]

            value = str(row['propertyValue'])

            if key not in rrg_offers:
                rrg_offers[key] = [value]
            else:
                rrg_offers[key].append(value)
        else:
            continue

    return rrg_offers

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



