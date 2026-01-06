TP1 - Traitement Batch avec Hadoop HDFS et MapReduce
Objectifs
Initiation au framework Hadoop et au patron MapReduce, utilisation de Docker pour lancer un cluster Hadoop de 3 noeuds.

Installation avec Docker
Prérequis Mac M1/M2/M3
bashbrew install docker colima
colima start --cpu 6 --memory 8
Télécharger l'image Hadoop
bashdocker pull liliasfaxi/hadoop-cluster:latest
Créer le réseau Docker
bashdocker network create --driver=bridge hadoop
Créer les 3 conteneurs
bashdocker run -itd --net=hadoop -p 9870:9870 -p 8088:8088 -p 7077:7077 -p 16010:16010 --name hadoop-master --hostname hadoop-master liliasfaxi/hadoop-cluster:latest

docker run -itd -p 8040:8042 --net=hadoop --name hadoop-worker1 --hostname hadoop-worker1 liliasfaxi/hadoop-cluster:latest

docker run -itd -p 8041:8042 --net=hadoop --name hadoop-worker2 --hostname hadoop-worker2 liliasfaxi/hadoop-cluster:latest
Démarrer les conteneurs existants
bashdocker start hadoop-master hadoop-worker1 hadoop-worker2
Accéder au master
bashdocker exec -it hadoop-master bash
Démarrer Hadoop
bashstart-dfs.sh
start-yarn.sh
Vérifier les services
bashjps
Vous devriez voir : NameNode, SecondaryNameNode, ResourceManager

Interfaces Web

HDFS : http://localhost:9870
YARN : http://localhost:8088
HBase : http://localhost:16010


Commandes HDFS
CommandeDescriptionhdfs dfs -lsAfficher le contenu du répertoire racinehdfs dfs -mkdir inputCréer un répertoirehdfs dfs -put file.txt inputUploader un fichierhdfs dfs -get file.txtTélécharger un fichierhdfs dfs -cat file.txtAfficher le contenuhdfs dfs -tail file.txtAfficher les dernières ligneshdfs dfs -rm file.txtSupprimer un fichierhdfs dfs -mv file.txt newfile.txtRenommer un fichier
Exemple pratique
bash# Créer un répertoire
hdfs dfs -mkdir -p input

# Uploader le fichier purchases.txt
hdfs dfs -put purchases.txt input

# Vérifier
hdfs dfs -ls input

# Voir les dernières lignes
hdfs dfs -tail input/purchases.txt

MapReduce
Concept
MapReduce est un modèle de programmation pour traiter de grandes quantités de données en parallèle.

Mapper : lit les données et extrait des paires clé/valeur
Shuffle : regroupe les paires par clé
Reducer : applique une fonction sur les valeurs (somme, moyenne, etc.)

Exemple : Compter les achats par moyen de paiement
Le fichier purchases.txt contient des transactions avec le format :
date    heure    ville    categorie    montant    moyen_paiement
Code Java (PaymentCount.java)
javaimport java.io.IOException;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

public class PaymentCount {
    // MAPPER : extrait le moyen de paiement de chaque ligne
    public static class PaymentMapper extends Mapper<LongWritable, Text, Text, IntWritable> {
        private final static IntWritable one = new IntWritable(1);
        private Text paymentMethod = new Text();
        
        public void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
            String[] fields = value.toString().split("\t");
            if (fields.length >= 6) {
                paymentMethod.set(fields[5].trim());
                context.write(paymentMethod, one);
            }
        }
    }
    
    // REDUCER : additionne les occurrences pour chaque moyen de paiement
    public static class PaymentReducer extends Reducer<Text, IntWritable, Text, IntWritable> {
        public void reduce(Text key, Iterable<IntWritable> values, Context context) throws IOException, InterruptedException {
            int sum = 0;
            for (IntWritable val : values) { 
                sum += val.get(); 
            }
            context.write(key, new IntWritable(sum));
        }
    }
    
    // MAIN : configure et lance le job
    public static void main(String[] args) throws Exception {
        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf, "payment count");
        job.setJarByClass(PaymentCount.class);
        job.setMapperClass(PaymentMapper.class);
        job.setCombinerClass(PaymentReducer.class);
        job.setReducerClass(PaymentReducer.class);
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(IntWritable.class);
        FileInputFormat.addInputPath(job, new Path(args[0]));
        FileOutputFormat.setOutputPath(job, new Path(args[1]));
        System.exit(job.waitForCompletion(true) ? 0 : 1);
    }
}
Compilation et exécution
bash# Créer le dossier pour les fichiers compilés
mkdir -p pc

# Compiler le code Java
javac -classpath $(hadoop classpath) -d pc PaymentCount.java

# Créer le fichier JAR
jar -cvf paymentcount.jar -C pc/ .

# Lancer le job MapReduce
hadoop jar paymentcount.jar PaymentCount input/purchases.txt output_payments
Voir les résultats
bashhdfs dfs -ls output_payments
hdfs dfs -cat output_payments/part-r-00000
Résultats obtenus
Amex       826535
Cash       828770
Discover   827426
MasterCard 828524
Visa       827221

HBase - Base de données NoSQL
Présentation
HBase est un système de gestion de bases de données distribué, non-relationnel et orienté colonnes, développé au-dessus de HDFS.
Modèle de données

Table : identifiée par un nom
Row : identifiée par une RowKey unique
Column Family : regroupement logique de colonnes
Column Qualifier : colonne à l'intérieur d'une famille
Cell : valeur identifiée par RowKey + Column Family + Column Qualifier
Version : chaque valeur est versionnée avec un timestamp

Démarrer HBase
bashstart-hbase.sh
hbase shell
Commandes HBase
Créer une table
bashcreate 'sales_ledger','customer','sales'
Lister les tables
bashlist
Insérer des données
bashput 'sales_ledger','101','customer:name','John White'
put 'sales_ledger','101','customer:city','Los Angeles, CA'
put 'sales_ledger','101','sales:product','Chairs'
put 'sales_ledger','101','sales:amount','$400.00'

put 'sales_ledger','102','customer:name','Jane Brown'
put 'sales_ledger','102','customer:city','Atlanta, GA'
put 'sales_ledger','102','sales:product','Lamps'
put 'sales_ledger','102','sales:amount','$200.00'

put 'sales_ledger','103','customer:name','Bill Green'
put 'sales_ledger','103','customer:city','Pittsburgh, PA'
put 'sales_ledger','103','sales:product','Desk'
put 'sales_ledger','103','sales:amount','$500.00'

put 'sales_ledger','104','customer:name','Jack Black'
put 'sales_ledger','104','customer:city','St. Louis, MO'
put 'sales_ledger','104','sales:product','Bed'
put 'sales_ledger','104','sales:amount','$1,600.00'
Afficher toutes les données
bashscan 'sales_ledger'
Afficher une ligne spécifique
bashget 'sales_ledger','101'

Résumé des apprentissages

Docker : Déploiement d'un cluster distribué avec des conteneurs
HDFS : Système de fichiers distribué pour stocker de grandes quantités de données
MapReduce : Modèle de programmation pour traiter les données en parallèle
HBase : Base de données NoSQL orientée colonnes pour le stockage massif
