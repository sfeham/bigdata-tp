# BigData TP - Hadoop MapReduce & API Velib

## Contenu
- `src/PaymentCount.java` : Job MapReduce pour compter les achats par moyen de paiement
- `src/getapi.py` : Script pour recuperer les donnees Velib en temps reel

## Utilisation MapReduce
```bash
javac -classpath $(hadoop classpath) -d pc PaymentCount.java
jar -cvf paymentcount.jar -C pc/ .
hadoop jar paymentcount.jar PaymentCount input/purchases.txt output_payments
```

## Utilisation API Velib
```bash
cd src
python3 getapi.py
```
