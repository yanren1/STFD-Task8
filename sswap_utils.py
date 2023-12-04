from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef

def fill_rig(form_data,rdg):

    g = Graph()
    # rdg
    g.parse(data=rdg, format='n3')

    has_mapping_node = None
    for _, _, o in g.triples((None, Namespace("http://sswapmeet.sswap.info/sswap/").hasMapping, None)):
        if isinstance(o, BNode):
            has_mapping_node = o
            break

    cottage_namespace = Namespace("http://example.org/cottage/")
    for key, value in form_data.items():
            # check keys in Cottage ontology
            if hasattr(cottage_namespace, key):
                for s, p, o in g.triples((has_mapping_node, getattr(cottage_namespace, key), None)):
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

    cottage_ns = Namespace("http://example.org/cottage/")
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
        if "http://example.org/cottage/" in key:
            key = key.split("/")[-1]
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

    cottage = Namespace("http://example.org/cottage/")
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
            g.add((new_maps_to_node, RDF.type, cottage.offers))  # add cottage:offers

            for key in keys:
                g.add((new_maps_to_node, getattr(cottage, key), Literal(offer[key][i])))
            g.add((has_mapping_node, sswap.mapsTo, new_maps_to_node))


    rrg = g.serialize(format='n3')
    print(rrg)
    return  rrg

def read_rrg(rrg):
    g = Graph()
    # rig
    g.parse(data=rrg, format='n3')

    cottage_ns = Namespace("http://example.org/cottage/")
    sswap = Namespace("http://sswapmeet.sswap.info/sswap/")

    query = """
        SELECT ?propertyName ?propertyValue
        WHERE {
            ?mappingNode sswap:hasMapping ?mapping.
            ?mapping sswap:mapsTo ?objectNode.
            ?objectNode ?propertyName ?propertyValue.
        }
        """
    offers = {}
    results = g.query(query, initNs={"sswap": sswap, "cottage": cottage_ns})

    for row in results:
        key = str(row['propertyName'])
        if "http://example.org/cottage/" in key:

            key = key.split("/")[-1]
            value = str(row['propertyValue'])

            if key not in offers:
                offers[key] = [value]
            else:
                offers[key].append(value)
        else:
            continue

    return offers
