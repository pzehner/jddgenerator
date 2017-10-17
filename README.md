# JDD Generator


Cette collection de scripts permet de générer des fichiers LaTeX pour les JDD depuis une série de fichiers `csv`. Le générateur peut créer des fichiers pour le planning et le recueil des résumés courts. Les deux types de documents peuvent être fusionnés dans le même fichier.

Ce projet a été réalisé pour et sous Linux. Je n'ai pas testé son fonctionnement sous Windows.


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
pip install --user -r requirements.txt
```

Si on est dans un virtualenv (ce qui est le mieux), il n'est plus nécessaire de spécifier `--user`. Pour plus d'informations concernant les virtualenvs, consulter cette page du [site de Sam et Max](http://sametmax.com/les-environnement-virtuels-python-virtualenv-et-virtualenvwrapper/).

```sh
pip install -r requirements.txt
```

Dans le cas où Pip n'est pas installé (et impossible à installer dans l'environnement actuel), il est toujours possible de [récupérer sa version bootstrap](https://bootstrap.pypa.io/get-pip.py) pour qu'il s'installe lui-même. Pour l'information, voici [quelques infos sur Pip](http://sametmax.com/votre-python-aime-les-pip/). Une fois le fichier `get-pip.py` récupéré, il suffit de le lancer :

```sh
python get-pip.py --user
```

Le script d'installation indiqué plus haut s'occupe de toutes ces étapes. Elles n'ont rien de sorcier, mais elles sont un peu déroutantes pour un débutant en Python (d'autant que l'environnement du labo n'aide pas).


## Utilisation


Maintenant que le script est installé, on peut l'utiliser !


### Comment utiliser le générateur


Il est possible d'utiliser le générateur par une interface en ligne de commande ou directement en utilisant ses modules.


#### Utiliser la ligne de commande


C'est sans doute la façon la plus simple de procéder. L'exécutable `jddgen` fournit une interface en ligne de commande pour créer les fichiers des JDD :

```sh
./jddgen # paramètres à placer ici
```

Pour afficher l'aide de la commande :

```sh
./jddgen -h
```

La commande ne génère qu'un seul type de document à la fois (planning ou recueil de résumés) :

```sh
./jddgen planning # pour le planning
./jddgen booklet # pour le recueil
```

Chaque sous-commande a sa propre aide :

```sh
./jddgen planning -h
./jddgen booklet -h
```

Pour générer tous les documents, il suffit de lancer les deux commandes successivement. À chaque fois, les fichiers nécessaires à la compilation sont générés.

On peut également spécifier plusieurs paramètres, comme le dossier de sortie (par défaut, le dossier `jdd`) :

```sh
./jddgen --output-directory /chemin/vers/le/dossier/de/sortie planning
```

Ou la localisation des différents fichiers nécessaires (voir la section sur les fichiers d'entrée) :

```sh
./jddgen planning --student-file /chemin/vers/le/fichier
```

Noter que ces deux paramètres ne se placent pas au même endroit.


##### Mode débug


S'il y a un problème quelque part dans le processus de génération, il est avisé d'activer le mode de débogage qui augmente la verbosité du programme (il indique ainsi chaque étape de progression du programme) et permet de mieux localiser l'erreur :

```sh
./jddgen -d planning
```

Comme les logs sont très verbeux, il peut être judicieux de rediriger l'erreur standard du programme vers un fichier pour l'analyser plus facilement :

```sh
./jddgen -d planning 2>log
```

##### Accéder facilement au script


Pour faciliter l'accès au script, on peut indiquer un alias pour avoir la commande à portée de main :

```sh
alias jddgen="/chemin/vers/jdd_generator/jddgen"
```

À mettre dans son fichier de configuration de shell favori en adaptant la syntaxe (`.bashrc`, `.cshrc`, `.zshrc`…). Il est déconseillé de déclarer le dossier du projet dans la variable d'environnement `PATH`, car le script `install` serait exécutable depuis n'importe où.

Si on n'aime pas les alias, on peut toujours faire un lien symbolique de `jddgen` dans `~/.local/bin/`, mais il faut alors déclarer le module du projet dans la variable d'environnement `PYTHONPATH` (voir la fin de la section sur l'utilisation en module).


#### Utiliser les modules


Il est aussi possible d'interagir directement avec les modules de `jdd_generator`. Pour ça, un fichier d'exemple `jdd_generator.sample.py` est fourni. Cette méthode permet d'inclure le générateur dans un autre script Python ou de sauvegarder quelque part les chemins vers les fichiers d'entrée (voir la section correspondante). Pour utiliser le générateur comme ça, un minimum de connaissances en Python et en programmation orientée objet sont nécessaires.

L'exemple donne la structure d'utilisation du projet. Il peut être judicieux d'aller lire la section sur le développement pour avoir quelques détails sur la philosophie du programme. Les modules à utiliser correspondent aux contrôleurs du projet, ils fournissent les commandes pour générer les documents LaTeX depuis les fichiers d'entrée. Trois modules, correspondant aux trois contrôleurs, sont disponibles.

Le contrôleur du planning s'utilise comme ceci :

```python
from jdd_generator.controllers.planning import PlanningController
planning = PlanningController()

# on crée le planning en mémoire depuis les fichiers par défaut
planning.create()

# on écris la représentation du planning en LaTeX sur le disque dans le dossier par défaut
planning.retrieve()
```

Le contrôleur du recueil de résumés courts est très similaire. La méthode `create` permet de lire les sources d'entrées (fichiers `csv`, voir la section sur les fichiers d'entrée), tandis que la méthode `retrieve` permet de représenter ces données en LaTeX et d'écrire le résultat sur le disque.

Un dernier contrôleur permet de générer le fichier principal à compiler, le contrôleur des JDD :

```python
from jdd_generator.controllers.jdd import JddController
jdd = JddController()

# comme ce contrôleur ne prend aucune donnée en entrée, il n'y a pas de méthode `create`

# on écris la représentation du fichier principar sur le disque dans le dossier par défaut
jdd.retrieve()
```


##### Afficher la documentation des méthodes


Pour plus d'informations sur la façon d'appeler les méthodes (leurs arguments, etc.), voir l'aide des classes dans l'interpréteur :

```python
>>> from jdd_generator.controllers.planning import PlanningController
>>> help(PlanningController)
```


##### Importer le module depuis un autre dossier


Pour importer le module depuis n'importe où, il suffit de modifier la variable d'environnement `PYTHONPATH` pour qu'elle inclue le dossier du module :

```sh
export PYTHONPATH="/chemin/vers/jdd_generator/jdd_generator":$PYTHONPATH
```

Oui, il y a deux fois `jdd_generator` : une fois pour le dossier du projet, une fois pour le dossier du module (qui ont le même nom). À mettre dans son fichier de configuration de shell en adaptant la syntaxe (`.bashrc`, `.cshrc`, `.zshrc`…).


### Fichiers d'entrée


Le flux de travail prévu dans le projet est simple : les organisateurs récupèrent les données (auprès des doctorants, des chairmans, etc.), les organisent dans un tableur et les exportent en `csv` pour être utilisées dans le générateur.

Pour exporter les données, dans LibreOffice, aller dans le menu « Fichier » puis « Enregistrer une copie sous. » Choisir le format « Texte CSV (.csv) » puis dans la boîte de dialogue suivante, choisir « Unicode (UTF-8) » pour le jeu de caractères et « {Tabulation} » pour le séparateur de champ. Le [format `csv`](https://fr.wikipedia.org/wiki/Comma-separated_values) est un format simple de représentation d'un classeur, où les données sont représentées ligne par ligne, chaque colonne étant séparée par un caractère spécifique, historiquement la virgule. Comme ici la virgule peut être utilisée dans les textes, le caractère de tabulation est utilisé à la place. Enfin, [Unicode](https://fr.wikipedia.org/wiki/Unicode) est le standard universel pour représenter les caractères dans un fichier et [l'UTF-8](https://fr.wikipedia.org/wiki/UTF-8) en est une implémentation.

En parlant de `csv`, plusieurs fichiers sont nécessaires :

| Désignation        | Explication                                                           | Utilisation       |
|--------------------|-----------------------------------------------------------------------|-------------------|
| `students_file`    | listing des doctorants et de leur thèse                               | planning, recueil |
| `repartition_file` | listing des répartitions des présentations des doctorants en sessions | planning, recueil |
| `planning_file`    | listing des événements du planning                                    | planning          |
| `abstracts_file`   | listing des résumés courts                                            | recueil           |
| `booklet_file`     | listing des sections du recueil de résumés courts                     | recueil           |

Certains de ces fichiers pourraient être fusionnés en un seul, particulièrement ceux qui ont attrait au doctorant : `students_file`, `repartition_file` et `abstracts_file`. D'une part, cela amènerait à créer un très gros tableur, d'autre part l'organisation de JDD fait que ces trois fichiers sont remplis successivement (d'abord la liste des doctorants, puis leurs résumés, puis leur répartition). Du fait de cette séparation, on a besoin de désigner le même doctorant dans chacun des fichiers. Pour cela, on fait appel à un ID unique. Cet ID peut être construit de n'importe quelle manière que ce soit, pourvu qu'il soit unique. Une façon de faire peut être `année_nom_prénom` (exemple `1a_kaname_madoka`). Comme spécifié plus tard, il est important que cet ID existe dans les 3 fichiers `csv` mentionnés. Par ailleurs, les photos doivent avoir cet ID pour nom de fichier.

Le projet manipule chaque fichier `csv` avec un ficher de configuration (encore appelé fichier compagnon) qui est un fichier `ini`. Cela permet notamment d'indiquer l'index de chaque colonne et le chemin vers le fichier `csv`. Donc, quand on indique un fichier au générateur, on indique en fait ce fichier `ini`. Un set d'exemple de ces fichiers est disponible dans le dossier principal du projet ; ces fichiers peuvent être copiés et modifiés pour correspondre aux besoins. La structure d'un tel fichier compagnon est la suivante :

```dosini
[info]
# ici, on a des infos sur le fichier à ouvrir
file = /chemin/vers/le/fichier.csv # le chemin est relatif au dossier du fichier INI
skip = 1 # nombre de lignes à sauter en début de fichier, par défaut 1
separator = \t # séparateur de champ, par défaut la tabulation

[fields]
# ici, on a l'association du nom de la colonne avec son index
# l'index peut être numérique (en commençant à 0) ou alphabétique (comme dans un tableur, en commençant par A)
field_1 = 0
field_2 = b
field_3 = c
field_4 = d
field_5 = 4
field_6 = 5
...
```

Le programme utilise la section `[fields]` pour se repérer dans le fichier car il accède aux colonnes par leur nom. Il est très important que ces informations soient justes. Il est possible de modifier les index dans le tableur, tant que la section `[fields]` est mise à jour. S'il y a un décalage entre l'index de la colonne indiqué dans le fichier compagnon et la position réelle de la colonne, des erreurs très bizarres vont se produire ! L'ensemble des champs utilisés par le programme sont définis ci-après.

Les fichiers compagnons ont les noms par défaut suivant :

| Désignation        | Nom par défaut  |
|--------------------|-----------------|
| `students_file`    | `listing.ini`   |
| `repartition_file` | `timings.ini`   |
| `planning_file`    | `planning.ini`  |
| `abstracts_file`   | `abstracts.ini` |
| `booklet_file`     | `booklet.ini`   |

Bien entendu, il est possible de spécifier un autre nom. Se reporter à la documentation de l'interface en ligne de commande ou au script d'exemple pour voir comment.


#### Fichier `students_file`


| Champ           | Description                                 | Remarques                  |
|-----------------|---------------------------------------------|----------------------------|
| `come`          | particie aux JDD ? sinon, est ignoré        | Pré-formaté                |
| `code`          | ID                                          |                            |
| `grade`         | année                                       |                            |
| `name`          | nom                                         |                            |
| `first-name`    | prénom                                      |                            |
| `department`    | département                                 |                            |
| `unit`          | unité (peut être vide)                      |                            |
| `location`      | centre                                      | Pré-formaté                |
| `email`         | courriel                                    |                            |
| `title`         | titre de la thèse                           |                            |
| `s0-name`       | nom encadrant 1                             | Incrémentable              |
| `s0-origin`     | établissement encadrant 1                   | Incrémentable              |
| `s0-department` | département encadrant 1                     | Incrémentable              |
| `s0-unit`       | unité encadrant 1                           | Incrémentable              |
| `s0-title`      | titre encadrant 1 (docteur professeur etc.) | Incrémentable, pré-formaté |
| `d0-name`       | nom directeur 1                             | Incrémentable              |
| `d0-origin`     | établissement directeur 1                   | Incrémentable              |
| `d0-title`      | titre directeur 1 (docteur professeur)      | Incrémentable, pré-formaté |
| `funding`       | financement                                 |                            |

Les champs « incrémentables » (tout ce qui a attrait aux encadrants avec `s` et aux directeurs avec `d`), peuvent avoir leur numéro incrémenté pour désigner un autre encadrant/directeur (le numéro commence à 0). Par exemple : `s0-name`, puis `s1-name`, `s2-name`…

Les champs « pré-formatés » (tout ce qui touche aux centres et aux titres) doivent contenir des valeurs particulières. Voir la sections sur la configuration du projet.


#### Fichier `repartition_file`


| Champ     | Description               |
|-----------|---------------------------|
| `code`    | ID                        |
| `length`  | durée en minutes          |
| `day`     | numéro du jour de passage |
| `session` | numéro de session         |
| `order`   | ordre pour le classement  |

L'ordre (`order`) est propre à la session.


#### Fichier `planning_file`


| Champ        | Description                                                                               |
|--------------|-------------------------------------------------------------------------------------------|
| `type`       | type d'événement (le type sera indiqué dans le plannig), si c'est une session, l'indiquer |
| `number`     | numéro de l'événement pour le type donné                                                  |
| `day`        | jour de début dans le format ISO 8601 (`aaaa-mm-jj`)                                      |
| `start`      | heure de début (`hh:mm`)                                                                  |
| `stop`       | heure de fin (`hh:mm`)                                                                    |
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


### Dossier de photos


Les photos sont utilisées pour la génération du recueil des résumés courts. Le dossier par défaut est `photos`. À l'intérieur, comme indiqué plus haut, la photo d'un doctorant doit avoir pour nom de fichier son code (plus l'extension du fichier, bien entendu).

La photo est automatiquement recadrée pour obtenir un carré.

Lors de la génération du recueil, si un dossier de photos ne se trouve pas déjà dans la structure de fichiers générés, un lien symbolique est automatiquement créé depuis le dossier de photos source.


### Fichier de configuration


La configuration du projet est stockée dans le fichier `jdd_generator/config.ini`. Chacune de ses sections correspond à une partie des paramètres.

Ce fichier peut être modifié pour s'adapter aux besoins.


#### Configuration des titres dans `[titles]`


Les encadrants et les directeurs peuvent avoir un titre. Si ce titre est en toutes lettres dans le listing, il est converti en abréviation (par exemple « docteur » en « Dr. »). Cette section contient la liste des abréviations, avec leur équivalent en toutes lettres.

La clé `disabled` permet de désactiver le traitement des titres. Dans ce cas, les titres sont utilisés tels quels.


#### Configuration des centres dans `[locations]`


Les doctorants peuvent être affectés à un centre. Comme les centres sont souvent indiqués par leurs initiales (par exemple « CC » pour « Centre de Châtillon »), cette section fait le lien entre les initiales et le nom complet. Dans l'idée, le nom complet sera affiché.

La clé `disabled` permet de désactiver le traitement des centres. Dans ce cas, l'indication de centre est utilisée telle quelle.


#### Configurations des valeurs booléennes dans `[booleans]`


Cette section définit la valeur booléenne de certaines chaînes de caractères. C'est en particulier utilisé pour interpréter le champ `come` de `students_file`.


### Fichier générés


Le générateur crée les différents fichiers LaTeX dans un dossier de sortie. Il génère également un fichier `jdd.tex` qui est le fichier principal à compiler. Il génère le planning dans le sous dossier `planning` et le recueil dans le sous dossier `booklet`. Pour les deux, il crée un fichier par session/section, qui porte un numéro, et un fichier principal qui a l'extension `.tex.sample`. Ce fichier ne doit pas être modifié, car il sera écrasé à chaque appel du générateur. Pour le modifier, il suffit de remplacer son extension par `.tex`. Le fichier principal `jdd.tex` importe automatiquement le fichier en `.tex`, sauf s'il n'existe pas auquel cas il importe le fichier `.tex.sample`.

Par exemple, pour le planning, le générateur crée le fichier `session_0.tex`, `session_1.tex` et le fichier de planning `planning.tex.sample`. Si on veut le modifier, il faut le renommer en `planning.tex`, auquel cas il sera importé par `jdd.tex` à la place de `planning.tex.sample` et ne sera plus écrasé à un prochain appel du générateur. Pareil pour le recueil de résumés.

Le fichier `jdd.tex` peut être écrasé. Si des modifications ont été faites dessus, il vaut mieux le copier sous un autre nom. Il ne reste plus qu'à le compiler avec `pdflatex`.


## Développement


Le projet a les dépendances suivantes:

* Python 2.7 (les dépendances sont spécifiées dans `requirements.txt`) :
 * `colour`, pour la gestion des couleurs ;
 * `jinja2`, pour la gestion des templates ;
 * `argparse`, pour la gestion des arguments passés en ligne de commande.
* LaTeX, testé avec TeXLive 2014 (tous les paquets sont standards) :
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
 * `placeins`, pour forcer les images à rester où on veut ;
 * `import`, pour faciliter les imports relatifs ;
 * `setspace`, pour gérer les interlignes ;
 * `afterpage`, pour exécuter des commandes après un saut de page ;
 * `keyval`, pour passes des options à une macro par clé/valeur.
* Bash v4 (pour le script d'installation) :
 * `wget`, pour récupérer Pip.

Le projet utilise Python 2.7 parce que c'est la seule version disponible dans le milieu d'exécution au labo. Une transition vers Python 3 le jour où ce sera nécessaire ne devrait pas être trop difficile à faire avec `2to3`.

J'ai beaucoup hésité à utiliser des dépendances, vu à quel point l'environnement Python du labo est pauvre (`argparse` n'est pas disponible, alors qu'il devrait l'être) et vieux (Pip est impossible à installer sans son bootstrap). Notamment pour le templating, j'ai essayé d'aller aussi loin que je pouvais avec `string.Template`, mais ce n'était pas élégant et ça mélangeait du code de template avec du code de manipulation de données. Quand j'ai essayé Jinja2, tous ces problèmes ont disparu et le gain était tel (ne serait-ce que pour simplifier la maintenance et la lisibilité du code) que je me suis dit que ça valait la peine de faire un script d'installation.

Ce projet sépare ses différentes parties selon la philosophie MVC (Modèle, Vue, Contrôler). Dans l'idée, le modèle représente les données que l'on traite, la vue s'occupe d'afficher ces données (ici, en fichier LaTeX) et le contrôleur s'occupe de tout le reste (lire les fichiers d'entrée, mettre leurs données dans les modèles, mettre en forme tout ça avec les vues et écrire le résultat sur le disque). Pour plus d'informations sur cette philosophie de développement, je conseille cette bonne introduction du [site de Sam et Max](http://sametmax.com/quest-de-que-mvc-et-a-quoi-ca-sert/). Pour le projet, les modèles sont dans `jdd_generator/models`, les vues dans `jdd_generator/views` et les contrôleurs dans `jdd_generator/controllers`.

Le projet utilise Jinja2 pour les vues. Les fichiers de template sont dans le dossier `jdd_generator/views/templates`. La syntaxe de Jinja2 a été adaptée à la syntaxe de LaTeX, donc les habitués de ce moteur de template auront besoin d'un petit temps d'adaptation. Afin de simplifier les templates autant que possible, beaucoup de macros et d'environnements ont été créés. Ils sont définis dans le template du fichier principal.
