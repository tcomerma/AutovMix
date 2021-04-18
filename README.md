# AutovMix
 Prova de concepte per remotar un vMix.

El que es pretén és veure les capacitats de la API per fer una realització automatitzada.

AutovMix.py carrega una coonfiguració i executa les accions de forma planificada
AutovMixWeb.py fa quelcom similar però via web, permetent ja una interacció amb el vMix

Atenció: El codi és basura. Sense control d'errors ni res. És una POC i prou

## Autor
Toni Comerma
abril 2021


# Us

## First time

- Download
- Load environment
```
source venv/bin/activate
```
- Install dependencies
```
python3 -m pip install -r requirements.txt
```

## Use
- amb virtualenv virtualenv
```
source venv/bin/activate
```
- Arrancar vmix, activar la API
- Retocar el fitxer de settings
Executar una de les 2 versions
```
python3 AutovMix.py -f settings1_short.json
python3 AutovMixWeb.py
```


## Notes
