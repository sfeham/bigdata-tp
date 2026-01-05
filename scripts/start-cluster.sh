#!/bin/bash
# Démarrer le cluster Hadoop
./start-hadoop.sh

# Démarrer HBase
start-hbase.sh

# Vérifier les services
jps
