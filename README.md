# JDD Generator


Cette collection de scripts permet de générer des fichiers LaTeX pour les JDD depuis une série de fichiers CSV. Le générateur peut créer des fichiers pour le planning et le recueil des résumés courts.


## Installation


Il y a deux façons de déployer le projet pour l'utiliser : la méthode automatique et la méthode manuelle.


### Installation automatisée


Il suffit d'appeler le script d'installation qui s'occupe de récupérer les dépendances. Le script est en Bash et il fait tout le sale boulot :

```sh
./install
```

Le script a plusieurs options pour le paramétrer, consulter son aide avec la commande :

```sh
./install -h
```


### Installation manuelle


Déployer le projet manuellement signifie en fait installer les dépendances. Elles sont spécifiées dans le projet et il suffit de faire :

```sh
pip install -r requirements.txt
```

Dans le cas où Pip n'est pas installé (et impossible à installer dans l'environnement actuel), il est toujours possible de le [récupérer un bootstrap](https://bootstrap.pypa.io/get-pip.py) pour qu'il s'installe lui-même :

```sh
python get-pip.py --user
```

Le script d'installation s'occupe de toutes ces étapes. Elles n'ont rien de sorcier, mais elles sont un peu déroutantes pour un débutant en Python (d'autant que l'environnement du labo n'aide pas).


## Utilisation


Maintenant que le script est installé, on peut l'utiliser.


### Comment utiliser le générateur


Il est possible d'utiliser le projet par ligne de commande ou directement en utilisant les modules.


#### Utiliser la ligne de commande


C'est sans doute la façon la plus simple de procéder. L'exécutable `jdd-generator` fournit une interface en ligne de commande pour créer les fichiers des JDD :

```sh
./jdd-generator
```

Pour afficher l'aide de la commande :

```sh
./jdd-generator -h
```

Les options supplémentaires permettent de spécifier les fichiers d'entrée (voir la section correspondante) et le dossier de sortie.

S'il y a un problème quelque part dans le processus de génération, il est avisé d'activer le mode de débogage qui augmente la verbosité du programme (il indique ainsi chaque étape) et permet de mieux localiser l'erreur :

```sh
./jdd-generator -d
```

Pour faciliter l'accès au script, on peut indiquer un alias pour avoir la commande à portée de main :

```sh
alias jdd-generator="/chemin/vers/jdd-generator"
```

À mettre dans son fichier de configuration de shell (`.bashrc`, `.cshrc`, `.zshrc`…).


#### Utiliser les modules


Il est aussi possible d'interagir directement avec les modules de `jdd_generator`. Pour ça, un fichier d'exemple `jdd_generator.py.sample` est fourni. Cela permet d'inclure le générateur dans un autre script Python ou de sauvegarder quelque part les chemins vers les fichiers d'entrée (voir la section correspondante).

Pour importer le module depuis n'importe où, il suffit de modifier la variable d'environnement `PYTHONPATH` pour qu'elle inclue le dossier du module :

```sh
export PYTHONPATH="/chemin/vers/jdd_generator/jdd_generator":$PYTHONPATH
```

Oui, il y a deux fois `jdd_generator` : une fois pour le dossier du projet, une fois pour le dossier du module (qui ont le même nom). À mettre dans son fichier de configuration de shell (`.bashrc`, `.cshrc`, `.zshrc`…).


### Fichiers d'entrée


Le flux de travail prévu dans le projet est simple : les organisateurs récupèrent les données, les organisent dans un tableur et les exportent en CSV pour être utilisées dans le générateur.

Pour exporter les données, dans LibreOffice, aller dans le menu « Fichier » puis « Enregistrer une copie sous. » Choisir le format « Texte CSV (.csv) » puis dans la boîte de dialogue suivante, choisir « Unicode (UTF-8) » pour le jeu de caractères et « {Tabulation} » pour le séparateur de champ.

Plusieurs fichiers CSV sont nécessaires :

| Désignation        | Explication                                                           | Utilisation       |
|--------------------|-----------------------------------------------------------------------|-------------------|
| `students_file`    | listing des doctorants                                                | planning, recueil |
| `repartition_file` | listing des répartitions des présentations des doctorants en sessions | planning, recueil |
| `planning_file`    | listing des événements du planning                                    | planning          |
| `abstracts_file`   | listing des résumés courts                                            | recueil           |
| `booklet_file`     | listing des sections du recueil de résumés courts                     | recueil           |

Le projet manipule chaque fichier CSV avec un ficher de configuration (encore appelé fichier compagnon) qui est un fichier INI. Cela permet notamment d'indiquer l'index de chaque colonne et le chemin vers le fichier CSV. Donc, quand on indique un fichier au générateur, on indique en fait ce fichier INI. Ces fichiers sont disponibles dans le dossier principal du projet, ils peuvent être copiés et modifiés pour correspondre aux besoins. La structure d'un tel fichier est la suivante :

```dosini
[info]
# ici, on a des infos sur le fichier à ouvrir
file = /chemin/vers/le/fichier/csv # le chemin est relatif au point d'appel du générateur
skip = 1 # nombre de lignes à sauter en début de fichier, par défaut 1
separator = \t # séparateur de champ, par défaut la tabulation

[fields]
# ici, on a l'association du nom de la colonne avec son index
# l'index peut être numérique (en commençant à 0) ou alphabétique (comme dans un tableur, en commençant par A)
field_1 = 0
field_2 = b
...
```

Le programme utilise la section `[fields]` pour se repérer dans le fichier car il accède les colonnes par leur nom. Il est très important que ces informations soient justes. Il est possible de modifier les index dans le tableur, tant que la section `[fields]` est mise à jour. L'ensemble des champs utilisés par le programme sont définis ci-après.

Les fichiers compagnons ont les noms par défaut suivant :

| Désignation        | Nom par défaut  |
|--------------------|-----------------|
| `students_file`    | `listing.ini`   |
| `repartition_file` | `timings.ini`   |
| `planning_file`    | `planning.ini`  |
| `abstracts_file`   | `abstracts.ini` |
| `booklet_file`     | `booklet.ini`   |


#### Fichier `students_file`


| Champ           | Description                                  |
|-----------------|----------------------------------------------|
| `come`          | particie aux JDD ? sinon, est ignoré         |
| `code`          | ID                                           |
| `grade`         | année                                        |
| `name`          | nom                                          |
| `first-name`    | prénom                                       |
| `unit`          | unité (peut être vide)                       |
| `location`      | centre                                       |
| `email`         | courriel                                     |
| `department`    | département                                  |
| `title`         | titre de la thèse                            |
| `s1-name`       | nom encadrant 1*                             |
| `s1-origin`     | établissement encadrant 1*                   |
| `s1-department` | département encadrant 1*                     |
| `s1-unit`       | département encadrant 1*                     |
| `s1-title`      | titre encadrant 1 (docteur professeur etc.)* |
| `d1-name`       | nom directeur 1*                             |
| `d1-origin`     | établissement directeur 1*                   |
| `d1-title`      | titre directeur 1 (docteur professeur)*      |
| `funding`       | financement                                  |

(\*) Pour les autres encadrants/directeurs, il suffit d'incrémenter le numéro (qui commence à 1).

Le centre et le titre des encadrants/directeurs subit un pré-formatage. De même, le champ `come` est codifié. Voir la sections sur la configuration du projet.


#### Fichier `repartition_file`


| Champ     | Description              |
|-----------|--------------------------|
| `code`    | ID                       |
| `length`  | durée en minutes         |
| `session` | numéro de session        |
| `order`   | ordre pour le classement |


#### Fichier `planning_file`


| Champ        | Description                                                                               |
|--------------|-------------------------------------------------------------------------------------------|
| `type`       | type d'événement (le type sera indiqué dans le plannig), si c'est une session, l'indiquer |
| `number`     | numéro de l'événement pour le type donné                                                  |
| `day`        | jour de début dans le format ISO 8601 (aaaa-mm-jj)                                        |
| `start`      | heure de début (hh:mm)                                                                    |
| `stop`       | heure de fin (hh:mm)                                                                      |
| `chairman`   | animateur/responsable de l'événement                                                      |
| `color`      | couleur du bandeau de l'événement (si la couleur commence par # elle est traitée en hexa) |
| `color-mode` | mode de représentation de la couleur (rgb, hsl... peut être vide)                         |


#### Fichier `abstracts_file`


| Champ      | Description                                                    |
|------------|----------------------------------------------------------------|
| `code`     | ID                                                             |
| `keywords` | mots clés, séparés par des virgules ou des points virgules     |
| `text`     | texte du résumé, il est possible d'ajouter des commandes LaTeX |


#### Fichier `booklet_file`


| Champ        | Description                                                                               |
|--------------|-------------------------------------------------------------------------------------------|
| `number`     | numéro de la section                                                                      |
| `color`      | couleur du bandeau de l'événement (si la couleur commence par # elle est traitée en hexa) |
| `color-mode` | mode de représentation de la couleur (rgb, hsl... peut être vide)                         |


### Fichier de configuration


La configuration du projet est stockée dans un fichier INI `config.ini`. Chacune de ses sections correspond à une partie des paramètres.

Ce fichier peut être modifié pour s'adapter aux besoins.


#### Configuration des titres


Les encadrants et les directeurs peuvent avoir un titre. Si ce titre est en toutes lettres dans le listing, il est converti en abréviation. Cette section contient la liste des abréviations, avec leur équivalent en toutes lettres.

La clé `disabled` permet de désactiver le traitement des titres. Dans ce cas, les titres sont utilisés tels quels.


#### Configuration des centres


Les doctorants peuvent être affectés à un centre. Comme les centres sont souvent indiqués par leurs initiales (par exemple CC pour Centre de Châtillon), cette section fait le lien entre les initiales et le nom complet. Dans l'idée, le nom complet sera affiché.

La clé `disabled` permet de désactiver le traitement des centres. Dans ce cas, l'indication de centre est utilisée telle quelle.


#### Configurations des valeurs booléennes


Cette section définit la valeur booléenne de certaines chaînes de caractères. C'est en particulier utilisé pour interpréter le champ `come` de `students_file`.


### Fichier générés


Le générateur crée les différents fichiers LaTeX dans un dossier de sortie. Il génère également un fichier `jdd.tex` qui est le fichier principal à compiler. Il génère le planning dans le dossier `planning` et le recueil dans le dossier `booklet`. Pour les deux, il crée un fichier par session/section, qui porte un numéro, et un fichier principal qui a l'extension `.tex.sample`. Ce fichier ne doit pas être modifié, car il sera écrasé à chaque appel du générateur. Pour le modifier, il suffit de remplacer son extension par `.tex`. Le fichier principal `jdd.tex` importer automatiquement le fichier en `.tex`, sauf s'il n'existe pas auquel cas il importe le fichier `.tex.sample`.

Par exemple, pour le planning, le générateur crée le fichier `session_0.tex`, `session_1.tex` et le fichier de planning `planning.tex.sample`. Si on veut le modifier, il faut le renommer en `planning.tex`, auquel cas il sera importé par `jdd.tex` à la place de `planning.tex.sample` et ne sera plus écrasé à un prochain appel du générateur. Pareil pour le recueil de résumés.

Il ne reste plus qu'à compiler le fichier principal `jdd.tex` avec `pdflatex`.


## Développement


Le projet a les dépendances suivantes:

* Python 2.7 :
 * `colour`, pour la gestion des couleurs ;
 * `jinja2`, pour la gestion des templates ;
 * `argparse`, pour la gestion des arguments passés en ligne de commande.
* LaTeX v? (tous les paquets sont standards) :
 * `inputenc`, pour l'entrée ;
 * `babel`, pour la langue ;
 * `fontenc`, pour l'encodage ;
 * `graphicx`, pour les images ;
 * `sans`, pour la police sans empattements ;
 * `microtype`, pour la gestion du crénage ;
 * `geometry`, pour les marges ;
 * `tabularx`, pour des tableaux en pleine largeur ;
 * `booktabs`, pour les lignes des tableaux ;
 * `xcolor`, pour les couleurs ;
 * `colortbl`, pour les cellules de tableau colorées (c'est comme ça que sont générés les bandeaux de couleurs) ;
 * `eso-pic`, pour les images de fond ;
 * `hyperref`, pour les liens ;
 * `url`, pour les liens hypertextes et le formatage des adresses courriel ;
 * `amsmath`, pour les maths ;
 * `amsfonts`, pour les maths ;
 * `amssymb`, pour les maths ;
 * `adjustbox`, pour ? ;
 * `calc`, pour calculer des valeurs ;
 * `ifthen`, pour avoir des structures conditionnelles faciles ;
 * `placeins`, pour ? ;
 * `import`, pour faciliter les imports relatifs ;
 * `setspace`, pour ? ;
 * `afterpage`, pour ? ;
 * `keyval`, pour passes des options à une macro par clé/valeur.
* Bash v? (pour le script d'installation) :
 * `wget`, pour récupérer Pip.

Le projet utilise Python 2.7 parce que c'est la seule version disponible dans le milieu d'exécution au labo.

J'ai beaucoup hésité à utiliser des dépendances, vu à quel point l'environnement Python du labo est pauvre (`argparse` n'est pas disponible, alors qu'il devrait l'être) et vieux (Pip est impossible à installer sans le bootstrap). Notamment pour le templating, j'ai essayé d'aller aussi loin que je pouvais avec `string.Template`, mais ce n'était pas élégant et ça mélangeait du code de template avec du code de manipulation de données. Quand j'ai essayé Jinja2, tous ces problèmes ont disparu et le gain était tel (ne serait-ce que pour simplifier la maintenance et la lisibilité du code) que je me suis dit que ça valait la peine de faire un script d'installation.

Ce projet sépare ses différentes parties selon la philosophie MVC (Modèle, Vue, Contrôler). Dans l'idée, le modèle représente les données que l'on traite, la vue s'occupe d'afficher ces données (ici, en fichier LaTeX) et le contrôleur s'occupe de tout le reste (lire les fichiers d'entrée, utiliser les modèles, mettre en forme avec les vues et écrire les résultats sur le disque). Pour plus d'informations sur cette philosophie de développement, je conseille cette bonne introduction du [site de Sam et Max](http://sametmax.com/quest-de-que-mvc-et-a-quoi-ca-sert/).
