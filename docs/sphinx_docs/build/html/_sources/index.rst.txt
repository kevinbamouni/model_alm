.. ALM Epargne Euro Individuel documentation master file, created by
   sphinx-quickstart on Wed May 19 04:49:05 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ALM Epargne Euro Individuel's documentation!
=======================================================

.. toctree::
   :maxdepth: 2
   :numbered:
   :titlesonly:
   :glob:
   :hidden:
   
   environnement.rst
   modele_alm.rst
   alm_actif.rst
   alm_passif.rst
   sphynx.rst

Ce modèle est une reprise en python du code source du Package R ‘SimBEL’ qui est un package de calcul du best estimate epargne (euro individuelle) sous Solvabilite 2.

Il reprend l'algorithme du modèle source avec un developpement adaptée en python dans un but d'avoir un code simple/compréhensible, maintenable et extensible.

Le code source est hébergé ici (repos git public): https://github.com/kevinbamouni/modele_alm/tree/test_debut_fin


TO DO :
===========

1. Revue de l'algorithme de participation au bénéfice et de provision de participation au bénéfice.
2. Revue de l'impact des différents flux sur la trésorerie à l'actif
3. Revue de la modélisation de l'actif avec les scénarios économiques. (Viellissement de action, immo, obligations)
4. Revue/Implémentation des actualisations des variables post revalo au participations au bénéfices (tresorerie, resultat technique, resultat financier...)
5. Implémentation du run multiscénarios, pour l'instant un seul scénarions est exécuté. (à priori il suffira de boucler sur chaque scénarion du GSE)
6. Implémentation du calcul de Best estimate
7. Implémentation d'un module complet de reporting (le script à date étant basique)
8. Recette fonctionnelle complete
9. Historiser le portefeuille_financier et la PPB.


Références :
======================

1. Documentation : http://www.ressources-actuarielles.net/simbel
2. Documentation R : https://rdrr.io/github/qguibert/SimBEL/
3. Code source : 
      - https://github.com/qguibert/SimBEL
      - https://github.com/qguibert/Environnement

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`