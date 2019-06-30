#import requests
from sseclient import SSEClient as EventSource
import json
from json import loads
from kafka import KafkaConsumer
import os


wikidata_id = ""
# defining the api-endpoint
API_ENDPOINT = "http://localhost:3000/runQuery"

KAFKA_BROKER_URL = os.environ.get('KAFKA_BROKER_URL')


def sparql_query(wikibase_item):
    query = """#CONSTRUCT query to get the RDF graph for a Wikidata item
        CONSTRUCT {
        wd:"""+f"""{wikibase_item}""" + """?p ?o .
        ?o ?a ?b .
        }
        WHERE {
        wd:"""+f"""{wikibase_item}""" + """ ?p ?o .
        ?o ?a ?b
        }
        """
    return query


if __name__ == '__main__':
  # Reading topic from kafka
  print('Making connection.')
  consumer = KafkaConsumer(bootstrap_servers=KAFKA_BROKER_URL)

  print('Assigning Topic.')
  consumer.subscribe(['queueing.wikidata'])

  print('Getting message.')
  for message in consumer:
      wikidata_id = str(message[6].decode("utf-8")).strip('"')
    # print("topic_name: " + str(message[0]) +  "message: " + str(message[6].decode("utf-8")))
      print("wikidata_id",wikidata_id)
  #  query = sparql_query(wikidata_id)
    # data to be sent to api
  #  data = {'query': query}

    # sending post request and saving response as response object
 #   r = requests.post(url=API_ENDPOINT, data=data)
#    sparql_graph = r.json()
    # print("data", data)
 #   print("query", sparql_graph)

''' wikidata_item = wikidata_id
print("wikidata_item",wikidata_item)
query = sparql_query(wikidata_item)

print("getting query")
print("query",query) '''


# def get_list_of_triples_in_subgraph_depth2(wikidata_endpoint_url, query, wikibase_item):
#     sparql = SPARQLWrapper(wikidata_endpoint_url)
#     sparql.setQuery(query)
#     sparql.setReturnFormat(JSON)
#     return sparql.query().convert()["results"]["bindings"]


# def calculate_oversimplified_similarity(root_node_properties, neighbour_node_properties):
#     score = 0
#     for rdf_property in root_node_properties:
#         if rdf_property in neighbour_node_properties:
#             score += 1

#     return score


# def remove_subjects_from_triple(triple):
#     del triple["subject"]


# def get_the_most_similar_entities(wikidata_id):
#     subgraph = get_list_of_triples_in_subgraph_depth2(
#         "https://query.wikidata.org/sparql",
#         sparql_query(wikidata_id),
#         wikidata_id)

#     root_node_properties = []
#     root_node_neighbours = []

#     for triple in subgraph:
#         if wikidata_id == triple["subject"]["value"].split("/")[-1]:
#             root_node_properties.append(triple)
#             root_node_neighbours.append(triple["object"]["value"])

#     # Speed up similarity calculations by removing all nodes without a direct
#     # edge to the rootnode as these nodes will have no effect on similarity
#     for triple in subgraph:
#         if triple["subject"]["value"] not in root_node_neighbours or triple in root_node_properties:
#             subgraph.remove(triple)

#     non_root_nodes_with_properties = {}
#     while len(subgraph) > 0:
#         for triple in subgraph:
#             node = triple["subject"]["value"]
#             if node not in non_root_nodes_with_properties:
#                 non_root_nodes_with_properties[node] = []
#             else:
#                 non_root_nodes_with_properties[node].append(triple)
#             subgraph.remove(triple)

#     for triple in root_node_properties:
#         remove_subjects_from_triple(triple)

#     similar_entities = []
#     for node, node_properties in non_root_nodes_with_properties.items():
#         for triple in node_properties:
#             remove_subjects_from_triple(triple)
#         similarity_to_root_node = calculate_oversimplified_similarity(
#             root_node_properties, node_properties)
#         similar_entities.append((node, similarity_to_root_node))

#     sorted(similar_entities, key=lambda x: x[1])

#     return similar_entities[-1], similar_entities[0]

# wikidata_id = "Q888"


# most_similar_entities, m2 = get_the_most_similar_entities(wikidata_id)

# print(most_similar_entities)
# print(m2)


# query = '''SELECT ?item ?itemLabel ?pic
# WHERE
# {?item wdt: P31 wd: Q146 .
#  ?item wdt: P18 ?pic
#  SERVICE wikibase: label {bd: serviceParam wikibase: language "[AUTO_LANGUAGE],en"}
#  }'''
