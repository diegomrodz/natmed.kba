from src.natmed import kgraph

def info(medicine):
    query = kgraph.run("MATCH (n:Medicine {name: {med}}) RETURN n", med=medicine)
    
    return query.single().values()[0]

def synonymous(medicine):
    query = kgraph.run("""MATCH (n:Medicine {name: {med}})-->(syn:Synonymous) 
                            RETURN syn.id""", med=medicine)

    return [id.values()[0] for id in query]

def scientific_names(medicine):
    query = kgraph.run("""MATCH (n:Medicine {name: {med}})-->(scy:ScientificName) 
                          RETURN scy.id""", med=medicine)

    return [id.values()[0] for id in query]

def from_other_name(name):
    query = kgraph.run("""MATCH (n {id: {name}})
                          MATCH (m:Medicine)-[:ALSO_KNOW_AS]->(n)
                          RETURN m""", name=name)

    return query.single().values()[0]

def relation_disease(medicine, disease):
    query = kgraph.run("""MATCH (a:Medicine {name:"%s"})
                            MATCH (b:Disease {id:"%s"})
                            MATCH (a)-[r1]->(i)-[r2]->(b)
                            MATCH (i)<-[]-(ref:Reference)
                            OPTIONAL MATCH (i)-[]->(ctx:Context)
                            RETURN a, i, b, collect(ref), ctx.id, labels(i), type(r1), type(r2)""" % (medicine, disease))
    relations = []

    for row in query:
        values = row.values()
        relation = {
            'info': dict(values[1].items()),
            'info_label': values[5][0],
            'references': [dict(e.items()) for e in values[3]],
            'context': values[4],
            'relation_labels': [
                values[6],
                values[7]
            ]}

        relations.append(relation)

    return relations

def similar_medicines(medicine, n=5):
    query = kgraph.run("""MATCH (a:Medicine {name:"%s"})
                          MATCH (a)-[]->()<-[]-(i:Reference)-[]->()<-[]-(b:Medicine)
                          WHERE NOT b.name = a.name
                          RETURN a.name, b.name, count(i) as c
                          ORDER BY c DESC
                          LIMIT %d""" % (medicine, n))
    result = []

    for row in query:
        values = row.values()
        result.append({
            'medicine': values[1],
            'score': int(values[2])
        })
    
    return result

def medicine_diseases(medicine):
    query = kgraph.run("""MATCH (a:Medicine {name:"%s"})
                          MATCH (a)-[]->()-[]->(b:Disease)
                          RETURN b.id""" % medicine)
    
    return [id.values()[0] for id in query]

def disease_medicines(disease):
    query = kgraph.run("""MATCH (a:Disease {id:"%s"})
                          MATCH (a)<-[]-()<-[]-(b:Medicine)
                          RETURN b.name, count(b.name) as c
                          ORDER BY c DESC""" % disease)

    return [e.values()[0] for e in query]