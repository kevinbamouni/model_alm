# Sources (09/12/2020):
- Modele de projection ALM et donnees de tests :  package R "Simbel" de Q. Guibert, code source disponible sur github. Il est présenté comm eun package de calcul du best estimate epargne sous solvabilite 2 (voir : https://github.com/qguibert/SimBEL)
- Generateur de scénarios économiques : (package R ESG et ESGToolkit voir : http://www.ressources-actuarielles.net/C1256F13006585B2/0/A5E99E9ABF5D3674C125772F00600F6C) 


# Dictionnaire de données.
Colonnes enrichies :
            
            ech : un vecteur contenant les flux de sortie en echeance de l'annee : nul si l'objet est de type RetraiteEuroRest.
            ind_ech : indicatrice de sortie en echeance : 1 si vrai 0 si faux.
            rach_tot : un vecteur contenant les flux de rachat totaux de l'annee : nul si l'objet est de type RetraiteEuroRest.
            dc : un vecteur contenant les flux de deces de l'annee : nul si l'objet est de type RetraiteEuroRest.
            rach_part : un vecteur contenant les flux de rachat partiel de l'annee : nul si l'objet est de type RetraiteEuroRest.
            rente : le flux annuel de rente par model point : nul si l'objet est de type EpEuroInd.
            prest : un vecteur contenant les flux prestations de l'annee (renseigne que l'objet x soit de type RetraiteEuroRest ou EpEuroInd).
            rev_ech : un vecteur contenant la revalorisation des echeances de l'annee : nul si l'objet est de type RetraiteEuroRest.
            rev_rach_tot : un vecteur contenant la revalorisation des rachats totaux de l'annee : nul si l'objet est de type RetraiteEuroRest.
            rev_dc : un vecteur contenant la revalorisation des deces de l'annee : nul si l'objet est de type RetraiteEuroRest.
            rev_rach_part : un vecteur contenant la revalorisation des rachats partiels de l'annee : nul si l'objet est de type RetraiteEuroRest.
            rev_prest : un vecteur contenant la revalorisation brute des prestations de l'annee : nul si l'objet est de type RetraiteEuroRest.
            rev_prest_nette : un vecteur contenant la revalorisation des prestations nette de l'annee : nul si l'objet est de type RetraiteEuroRest.
            enc_charg : un vecteur contenant les chargements sur l'encours de l'annee : nul si l'objet est de type RetraiteEuroRest.
            rach_charg : un vecteur contenant les chargements sur les rachats de l'annee : nul si l'objet est de type RetraiteEuroRest.
            soc_prest : un vecteur contenant les prelevements sociaux sur prestations de l'annee : nul si l'objet est de type RetraiteEuroRest.
            it_tech_prest : un vecteur contenant les interets techniques sur prestations de l'annee. : nul si l'objet est de type RetraiteEuroRest.
            arr_charg : un vecteur contenant les chargements sur arrerages. : nul si l'objet est de type EpEuroInd.
            nb_ech : un vecteur contenant le nombre de sorties en echeance de l'annee : nul si l'objet est de type RetraiteEuroRest.
            nb_rach_tot : un vecteur contenant le nombre de rachats totaux de l'annee : nul si l'objet est de type RetraiteEuroRest.
            nb_dc : un vecteur contenant le nombre de deces de l'annee
            nb_sortie : un vecteur contenant le nombre de sorties de l'annee
            nb_contr_fin : un vecteur contenant le nombre de contrats en cours en fin d'annee
            nb_contr_moy : un vecteur contenant la moyenne du nombre de contrats sur l'annee.
            tx_cible_an : un vecteur contenant les taux cible de l'annee
            tx_cible_se : un vecteur contenant les taux cible de l'annee sur base semestrielle
            tx_tech_an : un vecteur contenant les taux de technique de l'annee
            tx_tech_se : un vecteur contenant les taux de technique de l'annee sur base semestrielle
            tx_an : un vecteur contenant les taux de revalorisation minimum de l'annee
            tx_se : un vecteur contenant les taux de revalorisation minimum de l'annee exprimes en semestriel.
            rev_stock_brut_ap_pb : un vecteur contenant la revalorisation brute de l'annee appliquee au PM
            rev_stock_nette_ap_pb : un vecteur contenant la revalorisation nette de l'annee appliquee au PM. Elle peut etre negative pour des contrats a taux negatif.
            enc_charg_stock_ap_pb : un vecteur contenant les montants de chargement sur encours de l'annee calcules pour le stock de PM
            soc_stock_ap_pb : un vecteur contenant les prelevements sociaux de l'annee
            rev_stock_brut : un vecteur contenant la revalorisation minimale ##' brute de l'annee appliquee au PM (nul en cas de typage RetraiteEuroRest).
            rev_stock_nette : un vecteur contenant la revalorisation minimale ##' nette de l'annee appliquee au PM (nul en cas de typage RetraiteEuroRest).
            enc_charg_stock : un vecteur contenant les chargement sur encours de l'annee, calcules en prenant en compte la revalorisation minimale (nul en cas de typage RetraiteEuroRest).
            enc_charg_base_th : un vecteur contenant les chargements sur encours theoriques de l'annee, evalues sur la base de la PM non revalorisees (nul en cas de typage RetraiteEuroRest).
            enc_charg_rmin_th : un vecteur contenant les chargements sur encours theoriques de l'annee, evalues sur la seule base de la revalorisation minimale des PM (nul en cas de typage RetraiteEuroRest).
            base_enc_th : un vecteur contenant l'assiette de calcul des chargements sur encours de l'annee (nul en cas de typage RetraiteEuroRest).
            soc_stock : un vecteur contenant le prelevements sociaux de l'annee (nul en cas de typage RetraiteEuroRest).
            it_tech_stock : un vecteur contenant les interets techniques sur stock de l'annee (nul en cas de typage RetraiteEuroRest).
            it_tech : un vecteur contenant les interets techniques sur stock et sur prestations de l'annee (nul en cas de typage RetraiteEuroRest).
            bes_tx_cible : un vecteur contenant le besoin de financement de l'annee pour atteindre le taux cible de chaque assure.
            qx_rach_tot_dyn : qx rachat total dynamique
            qx_rach_part_dyn : qx rachat partiel dynamique
            nb_vers : Nombre de versement de primes
            pri_brut : prime brut
            pri_net : prime net
            pri_chgt : chargement sur prime


Etape de calcul de projection annuelle:

    # 0 : Primes
    # 1 : Taux min
    # 2 : Calcul proba flux
    # 3 : Calcul proba dynamique
    # 4 : Prestations normal & garantie
    # 5 : Taux cible des rendements
    # 6 : PM