# Projet Big Data - Hadoop, Spark & HBase

## Informations du Projet

| | |
|---|---|
| **Module** | Big Data |
| **Technologies** | Hadoop, HDFS, MapReduce, Spark, HBase |
| **Environnement** | Docker (cluster 3 noeuds) |
| **Langage** | Java, Scala, Python |

---

## Table des Matières

1. [Présentation](#présentation)
2. [Architecture du Projet](#architecture-du-projet)
3. [Installation](#installation)
4. [TP1 - Hadoop MapReduce & HBase](#tp1---hadoop-mapreduce--hbase)
5. [TP2 - Spark Batch & Streaming](#tp2---spark-batch--streaming)
6. [Rapport d'Analyse](#rapport-danalyse)
7. [Conclusion](#conclusion)

---

## Présentation

Ce projet explore les technologies Big Data à travers deux travaux pratiques complémentaires :

- **TP1** : Introduction à l'écosystème Hadoop avec HDFS, MapReduce et HBase
- **TP2** : Traitement de données avec Apache Spark (Batch et Streaming)

L'objectif est de comprendre les paradigmes de traitement distribué et de comparer les approches MapReduce traditionnelles avec les solutions modernes comme Spark.

---

## Architecture du Projet

```
bigdata-tp/
├── README.md                 # Documentation principale
├── docs/
│   ├── TP_1.md              # Instructions TP1
│   └── TP2_Spark.md         # Instructions TP2
├── mapreduce/
│   └── PaymentCount.java    # Job MapReduce (comptage paiements)
├── hbase/
│   └── commands.txt         # Commandes HBase
├── src/
│   └── getapi.py            # Script API Velib
├── scripts/
│   └── start-cluster.sh     # Script démarrage cluster
└── data/
    └── purchases_sample.txt # Échantillon de données
```

### Infrastructure Docker

Le cluster Hadoop est composé de 3 conteneurs Docker :

| Conteneur | Rôle | Services |
|-----------|------|----------|
| `hadoop-master` | Noeud maître | NameNode, ResourceManager, HBase Master |
| `hadoop-worker1` | Noeud esclave | DataNode, NodeManager |
| `hadoop-worker2` | Noeud esclave | DataNode, NodeManager |

### Interfaces Web

| Service | URL | Description |
|---------|-----|-------------|
| HDFS | http://localhost:9870 | Gestion du système de fichiers |
| YARN | http://localhost:8088 | Monitoring des applications |
| HBase | http://localhost:16010 | Interface HBase Master |
| Spark UI | http://localhost:4040 | Monitoring Spark (actif pendant les jobs) |

---

## Installation

### Prérequis (Mac M1/M2/M3)

```bash
brew install docker colima
colima start --cpu 6 --memory 8
```

### Déploiement du Cluster

```bash
# Télécharger l'image
docker pull liliasfaxi/hadoop-cluster:latest

# Créer le réseau
docker network create --driver=bridge hadoop

# Lancer les conteneurs
docker run -itd --net=hadoop -p 9870:9870 -p 8088:8088 -p 7077:7077 -p 16010:16010 \
    --name hadoop-master --hostname hadoop-master liliasfaxi/hadoop-cluster:latest

docker run -itd -p 8040:8042 --net=hadoop \
    --name hadoop-worker1 --hostname hadoop-worker1 liliasfaxi/hadoop-cluster:latest

docker run -itd -p 8041:8042 --net=hadoop \
    --name hadoop-worker2 --hostname hadoop-worker2 liliasfaxi/hadoop-cluster:latest
```

### Démarrage des Services

```bash
docker exec -it hadoop-master bash
start-dfs.sh
start-yarn.sh
start-hbase.sh  # Si besoin de HBase
```

---

## TP1 - Hadoop MapReduce & HBase

### Objectifs
- Comprendre le système de fichiers distribué HDFS
- Implémenter un job MapReduce en Java
- Manipuler une base NoSQL avec HBase

### Dataset
Fichier `purchases.txt` contenant **4 138 476 transactions** avec le format :
```
date    heure    ville    categorie    montant    moyen_paiement
```

### MapReduce : Comptage par Moyen de Paiement

#### Code Java (PaymentCount.java)
```java
// MAPPER : extrait le moyen de paiement (champ 6)
public void map(LongWritable key, Text value, Context context) {
    String[] fields = value.toString().split("\t");
    if (fields.length >= 6) {
        context.write(new Text(fields[5].trim()), new IntWritable(1));
    }
}

// REDUCER : additionne les occurrences
public void reduce(Text key, Iterable<IntWritable> values, Context context) {
    int sum = 0;
    for (IntWritable val : values) {
        sum += val.get();
    }
    context.write(key, new IntWritable(sum));
}
```

#### Exécution
```bash
# Compilation
mkdir -p pc
javac -classpath $(hadoop classpath) -d pc PaymentCount.java
jar -cvf paymentcount.jar -C pc/ .

# Upload des données
hdfs dfs -mkdir -p input
hdfs dfs -put purchases.txt input/

# Lancement du job
hadoop jar paymentcount.jar PaymentCount input/purchases.txt output_payments

# Résultats
hdfs dfs -cat output_payments/part-r-00000
```

#### Résultats Obtenus
| Moyen de Paiement | Nombre de Transactions |
|-------------------|------------------------|
| Amex | 826 535 |
| Cash | 828 770 |
| Discover | 827 426 |
| MasterCard | 828 524 |
| Visa | 827 221 |

### HBase : Base NoSQL

#### Création de table et insertion
```bash
hbase shell

# Créer une table avec 2 familles de colonnes
create 'sales_ledger', 'customer', 'sales'

# Insérer des données
put 'sales_ledger', '101', 'customer:name', 'John White'
put 'sales_ledger', '101', 'customer:city', 'Los Angeles, CA'
put 'sales_ledger', '101', 'sales:product', 'Chairs'
put 'sales_ledger', '101', 'sales:amount', '$400.00'

# Consulter
scan 'sales_ledger'
get 'sales_ledger', '101'
```

---

## TP2 - Spark Batch & Streaming

### Objectifs
- Manipuler les RDD (Resilient Distributed Datasets)
- Utiliser Spark SQL pour l'analyse de données
- Implémenter un traitement en streaming

### Lancement de Spark

```bash
spark-shell --driver-memory 512m --executor-memory 512m
```

### RDD : Opérations de Base

```scala
// Charger les données depuis HDFS
val rdd = sc.textFile("/input/purchases.txt")

// Compter les lignes
rdd.count()  // 4 138 476

// Filtrer les transactions Visa
val visaRdd = rdd.filter(_.contains("Visa"))
visaRdd.count()

// Échantillonnage (10% des données)
val sampleRdd = rdd.sample(false, 0.1)
```

### Comptage par Moyen de Paiement (équivalent MapReduce)

```scala
// En 2 lignes vs 50+ lignes en Java !
val paymentCounts = sampleRdd
  .map(line => (line.split("\t")(5), 1))
  .reduceByKey(_ + _)

paymentCounts.collect()
// Array((MasterCard,83248), (Amex,82755), (Visa,82147), (Discover,83040), (Cash,83275))
```

### Spark SQL : Analyse Avancée

```scala
import spark.implicits._

// Créer un DataFrame
val df = sampleRdd.map(line => {
  val f = line.split("\t")
  (f(0), f(1), f(2), f(3), f(4).toDouble, f(5))
}).toDF("date", "heure", "ville", "categorie", "montant", "paiement")

// Enregistrer comme table SQL
df.createOrReplaceTempView("ventes")

// Requêtes SQL
spark.sql("""
  SELECT paiement, COUNT(*) as nb, SUM(montant) as total
  FROM ventes
  GROUP BY paiement
""").show()

// Résultat :
// +----------+-----+--------------------+
// |  paiement|   nb|               total|
// +----------+-----+--------------------+
// |  Discover|83040|2.0758046359999962E7|
// |      Visa|82147|2.0515930209999904E7|
// |      Cash|83275| 2.087191399000003E7|
// |MasterCard|83248|2.0786604709999975E7|
// |      Amex|82755| 2.067904524000007E7|
// +----------+-----+--------------------+
```

### Spark Streaming

Le streaming permet de traiter des flux de données en temps réel par micro-batches.

#### Architecture du Test
```
┌─────────────┐    TCP 9999    ┌─────────────────┐
│   Netcat    │ ────────────▶  │  Spark Streaming │
│  (source)   │                │   (traitement)   │
└─────────────┘                └─────────────────┘
```

#### Terminal 1 : Source de données (Netcat)
```bash
# Installer netcat si nécessaire
apt-get update && apt-get install -y netcat

# Lancer le serveur TCP
nc -lk 9999
```

#### Terminal 2 : Spark Streaming
```scala
import org.apache.spark.streaming._

// Créer un contexte streaming (micro-batch de 5 secondes)
val ssc = new StreamingContext(sc, Seconds(5))

// Écouter sur le port TCP 9999
val lines = ssc.socketTextStream("localhost", 9999)

// Compter les mots en temps réel
val words = lines.flatMap(_.split(" "))
val wordCounts = words.map(x => (x, 1)).reduceByKey(_ + _)
wordCounts.print()

// Démarrer le streaming
ssc.start()
```

#### Résultats Obtenus

Entrée (Terminal 1 - Netcat) :
```
hello world
hello spark
test streaming bigdata
```

Sortie (Terminal 2 - Spark) :
```
-------------------------------------------
Time: 1767714475000 ms
-------------------------------------------
(world,1)
(hello,1)

-------------------------------------------
Time: 1767714480000 ms
-------------------------------------------
(hello,1)
(spark,1)

-------------------------------------------
Time: 1767714485000 ms
-------------------------------------------
(bigdata,1)
(streaming,1)
(test,1)
```

Le streaming traite chaque ligne en temps réel et affiche le comptage des mots toutes les 5 secondes.

---

## Rapport d'Analyse

### Comparaison MapReduce vs Spark

| Critère | MapReduce | Spark |
|---------|-----------|-------|
| **Lignes de code** | ~50 lignes (Java) | ~2 lignes (Scala) |
| **Temps d'exécution** | Minutes | Secondes |
| **Facilité** | Complexe (compilation, JAR) | Interactif (shell) |
| **Mémoire** | Disk-based | In-memory |
| **API** | Bas niveau | Haut niveau (RDD, DataFrame, SQL) |
| **Streaming** | Non natif | Natif (Spark Streaming) |

### Performance Observée

Sur le dataset de 4.1M de transactions :

| Opération | MapReduce | Spark |
|-----------|-----------|-------|
| Comptage par paiement | ~3-5 min | ~30 sec |
| Agrégation par catégorie | ~3-5 min | ~20 sec |

### Avantages de Chaque Approche

**MapReduce :**
- Robuste et mature
- Tolérance aux pannes éprouvée
- Adapté aux très gros volumes (PB)

**Spark :**
- Rapidité (100x plus rapide en mémoire)
- API unifiée (batch, SQL, streaming, ML)
- Développement interactif
- Écosystème riche (MLlib, GraphX)

### Modèle de Données HBase

HBase offre un modèle NoSQL orienté colonnes adapté aux :
- Lectures/écritures aléatoires rapides
- Données semi-structurées
- Versioning automatique des données
- Scalabilité horizontale

---

## Conclusion

### TP1 - Hadoop Écosystème

Le TP1 nous a permis de découvrir les fondamentaux du Big Data :

1. **HDFS** : Système de fichiers distribué permettant de stocker des données sur plusieurs noeuds avec réplication automatique
2. **MapReduce** : Paradigme de programmation pour le traitement parallèle, bien que verbeux, il reste la référence pour les traitements batch massifs
3. **HBase** : Base NoSQL offrant des accès rapides aux données stockées sur HDFS

**Compétences acquises :**
- Déploiement d'un cluster Hadoop avec Docker
- Manipulation de HDFS (upload, download, navigation)
- Développement et exécution de jobs MapReduce
- Modélisation et requêtage NoSQL avec HBase

### TP2 - Apache Spark

Le TP2 a démontré la puissance et la simplicité de Spark :

1. **RDD** : Abstraction permettant de manipuler des données distribuées de manière transparente
2. **Spark SQL** : Interface SQL familière pour l'analyse de données structurées
3. **Streaming** : Traitement de flux de données en temps réel

**Points clés :**
- Réduction drastique du code nécessaire (2 lignes vs 50+)
- Performances accrues grâce au traitement in-memory
- API unifiée pour batch et streaming
- Interactivité via le spark-shell

### Synthèse Globale

Ces TPs illustrent l'évolution des technologies Big Data :

| Génération | Technologie | Caractéristique |
|------------|-------------|-----------------|
| 1ère | Hadoop MapReduce | Fiable mais lent |
| 2ème | Apache Spark | Rapide et polyvalent |
| Stockage | HBase | NoSQL scalable |

**Recommandations d'usage :**
- **MapReduce** : Traitements batch très volumineux nécessitant une fiabilité maximale
- **Spark** : Analyses interactives, ML, streaming, cas d'usage variés
- **HBase** : Stockage NoSQL avec accès temps réel sur HDFS

L'écosystème Hadoop reste pertinent en 2026, avec Spark comme moteur de traitement privilégié pour sa polyvalence et ses performances.

---

## Références

- [Apache Hadoop Documentation](https://hadoop.apache.org/docs/)
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [Apache HBase Reference Guide](https://hbase.apache.org/book.html)
