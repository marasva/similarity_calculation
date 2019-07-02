# similarity_calculation
The API_ENDPOINT-variable should be edited according to the SPARQL-service running. 
If the SPARQL-service is running through docker-compose you can write:
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <container_id>
In order to find the "public"-ip of the SPARQL-service.
