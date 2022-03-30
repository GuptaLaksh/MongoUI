sudo -i
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' microbot_mongo
