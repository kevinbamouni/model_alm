================================================================
 Configuration de l'environnement de developpement et de python
================================================================

Installer Python 3.x
=======================

Pour installer python (Version 3.x) sur votre ordinateur vous avez le choix entre deux méthodes :
1. Télécharger et installer Python à partir du site officiel de la Python Software Foundation
2. Installer le bundle python Anaconda


Installation via la Python Software Foundation
---------------------------------------------------

1. Télécharger la dernière version de python qui est (3.9) à ce jour ici : https://www.python.org/downloads/. (Ne pas prendre de version 2.x, elle n'est plus supportée à ce jour)
2. Installer python 3.x (En suivant les instructions d'installation)
3. Installer l'ensemble des bibliothèques nécéssaires en utilisant le fichier "requirements.txt" qui se situe à la racine du projet MODELE_ALM.
    a. Ouvrir l'éditeur de commande de votre ordinateur (Pour windows c'est le cmd ou powershell)
    b. Se déplacer dans le dossier racine du projet MODELE_ALM (qui contient le fichier requirements.txt) à l'aide de la commande ``chdir`` sur windows ou ``cd`` sur linux et macos.
    c. Exécuter la commande suivante : ``pip install -r requirements.txt``.


Installation Anaconda
----------------------------------

Anaconda est une distribution python intégrant tout un ensemble de packages prêts à être utilisés pour la data science. (Anaconda = Python + packages de data science)

1. Télécharger Anaconda ici : https://www.anaconda.com/products/individual
2. Installer Anaconda

Installer un environnement de developpement intégré : Microsoft Visual Studio Code ou Pycharm Comunity Edition
=================================================================================================================

Pour le developper/Exécuter/debugger le code python l'EDI qui a été utilisé est Visual Studio Code avec des Extensions utiles au developpement python.

Installation de Visual Studio Code
-------------------------------------

1. Télécharger Visual Studio Code ici : https://code.visualstudio.com/Download
2. Se reférer au manuel de visual studio code pour configurer un environnement de developpement python pour la data science. (https://code.visualstudio.com/docs/languages/python)

Installation de Pycharm
--------------------------

1. Télécharger Pycharm Comunity Edition (qui est gratuite) ici :  https://www.jetbrains.com/fr-fr/pycharm/
2. Installer Pycharm Community Edition.