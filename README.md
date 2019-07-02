# similarity_calculation
The API_ENDPOINT-variable should be edited according to the SPARQL-service running. 
If the SPARQL-service is running through docker-compose you can write:
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <container_id>
In order to find the "public"-ip of the SPARQL-service.

The two docker-compose.yml should be placed in a folder with the three services, similarity-calculation, sparql-service and wikirevision-labeling. 

In order to start Kafka you can write:
docker-compose -f docker-compose.kafka.yml up -d

To start the docker-compose file:
docker-compose up --build 
