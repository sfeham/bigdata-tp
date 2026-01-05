# BigData TP - Hadoop, MapReduce & HBase

## Structure du projet
- `mapreduce/` : Jobs MapReduce (Java)
- `hbase/` : Commandes HBase
- `src/` : Scripts Python (API Velib)
- `scripts/` : Scripts utilitaires

## Installation
1. Démarrer Colima : `colima start --cpu 6 --memory 8`
2. Lancer les conteneurs Docker Hadoop
3. Exécuter `./start-hadoop.sh` puis `start-hbase.sh`

## MapReduce - Comptage par moyen de paiement
```bash
cd mapreduce
javac -classpath $(hadoop classpath) -d pc PaymentCount.java
jar -cvf paymentcount.jar -C pc/ .
hadoop jar paymentcount.jar PaymentCount input/purchases.txt output_payments
hdfs dfs -cat output_payments/part-r-00000
```

## HBase
```bash
hbase shell
# Puis exécuter les commandes dans hbase/commands.txt
```

## API Velib
```bash
cd src
python3 getapi.py
```
