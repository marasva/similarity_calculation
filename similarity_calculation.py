import requests
from sseclient import SSEClient as EventSource
import json
from json import loads
from kafka import KafkaConsumer
import os
from firebase import Firebase
from SPARQLWrapper import SPARQLWrapper, JSON

wikidata_id = ""
# defining the api-endpoint
API_ENDPOINT = "http://172.21.0.4:3020/runQuery"
KAFKA_BROKER_URL = os.environ.get('KAFKA_BROKER_URL')



def get_list_of_triples_in_subgraph_depth2(wikidata_endpoint_url, wikibase_item):
    query = sparql_query(wikibase_item)
    response = requests.post(wikidata_endpoint_url, data={"query": query})
    return json.loads(response.text)

    # sparql = SPARQLWrapper(wikidata_endpoint_url)
    # sparql.setQuery(query)
    # sparql.setReturnFormat(JSON)
    # return sparql.query().convert()["results"]["bindings"]

def sparql_query(wikibase_item):
    query = """#CONSTRUCT query to get the RDF graph for a Wikidata item
        CONSTRUCT {
        wd:"""+f"""{wikibase_item}""" + """ ?p ?o .
        ?o ?a ?b .
        }
        WHERE {
        wd:"""+f"""{wikibase_item}""" + """ ?p ?o .
        ?o ?a ?b
        }
        """
    return query

def calculate_oversimplified_similarity(root_node_properties, neighbour_node_properties):
    score = 0
    for rdf_property in root_node_properties:
        if rdf_property in neighbour_node_properties:
            score += 1
    return score


def remove_subjects_from_triple(triple):
    del triple["subject"]


def get_the_most_similar_entities(api_endpoint,wikidata_id):
    print("getting most similar entities")
    subgraph = get_list_of_triples_in_subgraph_depth2(api_endpoint,wikidata_id)
    root_node_properties = []
    root_node_neighbours = []

    for triple in subgraph:
        if wikidata_id == triple["subject"]["value"].split("/")[-1]:
            root_node_properties.append(triple)
            # root_node_neighbours.append(triple["object"]["value"])

    # Speed up similarity calculations by removing all nodes without a direct
    # edge to the rootnode as these nodes will have no effect on similarity
    for triple in subgraph:
        if triple in root_node_properties:
            subgraph.remove(triple)
    non_root_nodes_with_properties = {}
    while len(subgraph) > 0:
        for triple in subgraph:
            node = triple["subject"]["value"]
            if node not in non_root_nodes_with_properties:
                non_root_nodes_with_properties[node] = []
            else:
                non_root_nodes_with_properties[node].append(triple)
            subgraph.remove(triple)

    for triple in root_node_properties:
        remove_subjects_from_triple(triple)

    similar_entities = []
    for node, node_properties in non_root_nodes_with_properties.items():
        for triple in node_properties:
            remove_subjects_from_triple(triple)
        similarity_to_root_node = calculate_oversimplified_similarity(
            root_node_properties, node_properties)
        similar_entities.append((node, similarity_to_root_node))

    similar_entities = sorted(similar_entities, key=lambda x: x[1])
    return similar_entities[-1]


if __name__ == '__main__':
  firebase_config = {
      "apiKey": "AIzaSyDZKI2COnqy7jbCooNG2sIJn4_0qRrhtDw",
      "authDomain": "wikidata-analysis.firebaseapp.com",
      "databaseURL": "https://wikidata-analysis.firebaseio.com",
      "projectId": "wikidata-analysis",
      "storageBucket": "",
      "messagingSenderId": "35972699557",
      "appId": "1:35972699557:web:8e0a19c7f368ee04"
  }
  firebase = Firebase(firebase_config)
  db = firebase.database()
  # Reading topic from kafka
  print('Creating connection.')
  consumer = KafkaConsumer(bootstrap_servers=KAFKA_BROKER_URL)

  print('Assigning Topic.')
  consumer.subscribe(['queueing.wikidata'])

  print('Getting message.')
  for message in consumer:
        data = message.value.decode('utf-8')
        data = json.loads(data)
        wikidata_id = ""
        try:
            result_object = {
                    "name": data["name"],
                    "rev-id": data["rev_id"],
                    "wikidata-id": data["wikidata_id"],
                    "uri": data["uri"],
                    "wikidata_entity": data["wikidata_entity"],
                    "most_similar": data["most_similar"],
                    "edit_intention": data["edit_intention"]
                }
            wikidata_id = data["wikidata_id"]
        except TypeError as e:
            print(e)
            continue

        print(wikidata_id)
        # Add to database
        most_similar_entities = get_the_most_similar_entities(API_ENDPOINT,wikidata_id)
        result_object['most_similar'] = most_similar_entities
        print(most_similar_entities)
        # Push results to database
        db.child('/results').push(result_object)

        


