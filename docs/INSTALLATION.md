# Installation du cluster Hadoop avec Docker

## Prerequis Mac
brew install docker colima
colima start --cpu 6 --memory 8

## Demarrer les conteneurs existants
docker start hadoop-master hadoop-worker1 hadoop-worker2
docker exec -it hadoop-master bash
./start-hadoop.sh
