# TP2 - Traitement par Lot et Streaming avec Spark

## Présentation

Spark est un système de traitement rapide et parallèle. Il fournit des APIs de haut niveau en Java, Scala, Python et R, et un moteur optimisé qui supporte l'exécution des graphes.

Il supporte également un ensemble d'outils de haut niveau :
- **Spark SQL** : traitement de données structurées
- **MLlib** : apprentissage des données (Machine Learning)
- **GraphX** : traitement des graphes
- **Spark Streaming** : traitement des données en streaming

L'image Docker `liliasfaxi/hadoop-cluster` contient déjà Spark.

---

## Démarrage

### Démarrer les conteneurs (si arrêtés)
```bash
docker start hadoop-master
docker start hadoop-worker1
docker start hadoop-worker2
```

### Accéder au conteneur master
```bash
docker exec -it hadoop-master bash
```

### Vérifier que Spark est installé
```bash
spark-shell --version
```

### Lancer Spark
```bash
spark-shell
```

### Tester Spark avec un code Scala simple
```scala
sc.parallelize(1 to 10).sum()
```

---

## Interfaces Web

- YARN : http://localhost:8088/

---

## RDD et Batch Processing avec Spark

Spark gravite autour du concept de **Resilient Distributed Dataset (RDD)**, qui est une collection d'éléments tolérante aux fautes qui peut être gérée en parallèle.

Les RDDs utilisent la mémoire et l'espace disque selon les besoins.

### Parallélisation de Collections

Les collections parallélisées sont créées en appelant la méthode `parallelize` du SparkContext sur une collection existante.
```scala
// Créer une liste Scala
val data = List(1, 2, 3, 4, 5)

// Créer un RDD Spark
val distData = sc.parallelize(data)

// Tester le RDD
distData.collect()
```

### Génération à partir d'un fichier externe
```scala
// Créer un RDD à partir du fichier HDFS
val rdd = sc.textFile("/input/velib_20260105_133010.json")

// Afficher les 5 premières lignes
rdd.take(5)

// Compter le nombre de lignes
rdd.count()
```
