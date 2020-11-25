# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
import pandas as pd
import uuid
import numpy as np

Date_t0="31/12/2019" # Jour j de projection
N = 40 # Nombre d'années de projections
mp_path = "/Users/kevinbamouni/Documents/mp.csv"

mp = pd.read_csv(mp_path)

mp.iloc[1:10,:]

variables_de_calculs = ['qx_rach_part_dyn', 
        'qx_rach_tot_dyn',
        'qx_rach_tot',
        'qx_rach_tot_glob',
        'qx_dc',
        'qx_dc_rach',                
        'ind_ech',                
        'ech',
        'rach_tot',
        'dc',
        'rach_part',
        'prest',
        'rev_ech',
        'rev_rach_tot',
        'rev_dc',
        'rev_rach_part',
        'rev_prest',
        'rev_prest_nette',
        'enc_charg',
        'rach_charg',
        'soc_prest',
        'it_tech_prest',
        'arr_charg',
        'nb_ech',
        'nb_rach_tot',
        'nb_dc',
        'nb_sortie',
        'nb_contr_fin',
        'nb_contr_moy',
        'tx_cible_an',
        'tx_cible_se',
        'tx_tech_an',
        'tx_tech_se',
        'tx_an', 
        'tx_se',
        'rev_stock_brut',
        'rev_stock_nette',
        'enc_charg_stock',
        'enc_charg_base_th',
        'enc_charg_rmin_th',
        'base_enc_th',
        'soc_stock',
        'it_tech_stock',
        'it_tech',
        'bes_tx_cible',
        'rev_stock_brut_ap_pb',
        'rev_stock_nette_ap_pb',
        'enc_charg_stock_ap_pb',
        'soc_stock_ap_pb',
        'pm_fin_ap_pb',
        'nb_vers',
        'pri_brut',
        'pri_net',
        'pri_chgt']


# mp.loc[mp.age<18,"age"]=18
# mp.to_csv(mp_path, sep=',', encoding='utf-8', index=False)

def initialisation_des_mp(df_mp, list_colonnes_a_enrichir):
    """Enrichissement du fichier de Mp en input de toutes les colonnes nécéssaires pour les futurs calculs
    
    Input : Dataframe du représentant le fichier de Model point en input
    Output : Dataframe du fichier de Model point en input enrichi des colonnes qui seront calculées dans le run.
            
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
            qx_rach_tot_dyn
            qx_rach_part_dyn
            nb_vers
            pri_brut
            pri_net
            pri_chgt
    """
    #initialisation de t à 0.
    df_mp['t'] = 0
    
    # creation d'un identifiant unique pour chaque ligne de mp.
    df_mp['uuid'] = df_mp.apply(lambda _: uuid.uuid4(), axis=1)
    
    # 0 : Calcul des proba des flux
    # 1 : Calcul des flux de prestation
    # 2 : Calcul des taux cibles pour chaque mp : objectif de rendement en fonction des autres assureurs et du rendement des actifs
    # 3 : Taux minimum à servir par Model Point :
    # 4 : Calcul des primes projetées
    # 5 : Calcul de la PM
    # 6 : Calcul de la revalo de la PM avec pb
    
    for x in list_colonnes_a_enrichir:
        df_mp[x]= None
    
    return df_mp


def get_proba_deces(mp):
    mp['qx_dc'] = 0.0025
    return mp

def get_proba_rachat_total(mp):
    #TODO : Implementer la probabilite de charchat total via la table des hypothèse de rachat totaux
    mp['qx_rach_tot'] = 0.00025
    return mp

def get_rachat_dyn_partiel_et_total(mp):
    """Rachats dynamiques totaux et partiels. Rachat partiel exprimé en % de la PM: soit 2.5% .
    """
    #TODO : loi de rachat dynamique : total et partiel.
    mp['qx_rach_tot_dyn'] = 0.0025
    mp['qx_rach_part_dyn'] = 0.0025
    return mp


# Etape 1 de la projection : Calculer les primes et les chargements sur prime
def calcul_des_primes(mp):
    # Nombre de versements
    mp.loc[mp.prime > 0,"nb_vers"] = mp.nb_contr
    
    # Calcul les primes de l'annee
    mp.pri_brut = mp.prime * mp.nb_contr # primes brutes
    mp.pri_net = mp.pri_brut * (1 - mp.chgt_prime) # primes nettes
    mp.pri_chgt = mp.pri_brut * mp.chgt_prime # Chargements sur primes
    
    return mp


# Etape 2 : Calcul des taux min
def calcul_des_taux_min(mp):
    """
     Fonction de calcul des taux techniques et tmg min pour chaque ligne de MP.
     //TODO : calcul des taux min à revoir potentiellement
    """ 
    # calcul du taux technique    
    mp.tx_tech_an = np.maximum(mp.tech, 0)
    mp.tx_tech_se = mp.tx_tech_an / 2 # taux semestriel

    # Calcul du taux minimum
    mp.tx_an = np.maximum(mp.tx_tech_an, mp.tmg) # taux annuel minimum
    mp.tx_se = mp.tx_min / 2 # taux semestriel
    
    return mp


def calcul_des_proba_de_flux(mp, table_de_mortalite, table_de_rachat_total):
    return pass


def calcul_des_prestation(mp,t):
    """ Calcul des prestations !!! """
    # Indicatrice de sortie en echeance    
    mp.loc[mp['terme'] <= t, 'ind_ech'] = 0 # si le contrat n'est pas à terme
    mp.loc[mp['terme'] > t, 'ind_ech'] = 1 # si le contrat à terme
    
    # Calcul du nombre de contrat en echeance
    mp['nb_ech'] = mp['nb_contr'] * mp['ind_ech']
    
    # Extraction des taux de revalorisation minimum et des taux technique
    mp = calcul_des_taux_min(mp)
    
    # Calcul des montant des prestations pour sortie en echeances avec la revalorisation
    mp['ech'] = mp['pm_deb'] * mp['ind_ech']
    mp['rev_ech'] = mp['ech'] * mp['tx_se']
    
    # Calcul des flux  rachats totaux
    # Taux de rachat incluant les rachats structurels et conjoncturels
    mp = get_rachat_dyn_partiel_et_total(mp) # calcul de qx_rach_tot_dyn et de qx_rach_part_dyn
    mp = get_proba_rachat_total(mp) # calcul de qx_rach_tot
    mp['qx_rach_tot_glob'] = np.maximum(0, np.minimum(1, mp['qx_rach_tot'] + mp['qx_rach_tot_dyn'])) * (1 - mp['ind_ech']) # 1 si le contrat n'est pas a terme
    mp['nb_rach_tot'] = mp['nb_contr'] * mp['qx_rach_tot_glob']
    mp['rach_tot'] = mp['pm_deb'] * mp['qx_rach_tot_glob'] # Flux de rachats totaux
    mp['rev_rach_tot'] = mp['rach_tot'] * mp['tx_se'] # revalorisation au taux minimum
    
    # Calcul des flux de deces
    # Taux de deces sur la population des non rachetes
    mp = get_proba_deces(mp) # calcul de qx_dc
    mp['qx_dc_rach'] = mp['qx_dc'] * (1 - mp['qx_rach_tot_glob'])
    mp['dc'] = mp['pm_deb'] * mp['qx_dc_rach'] * mp['ind_ech'] # Flux de rachats totaux
    mp['rev_dc'] = mp['dc'] * mp['tx_se'] # revalorisation au taux minimum
    mp['nb_dc'] = mp['nb_contr'] * mp['qx_dc_rach'] 
    
    # Calcul des flux rachats partiels
    # Taux de rachat incluant les rachats structurels et conjoncturels sur la population des non rachetes et vivants
    mp['qx_rach_part_glob'] = (1 - mp['qx_rach_tot_glob']) * (1 - mp['qx_dc']) * np.maximum(0, np.minimum(1, mp['qx_rach_part'] + mp['qx_rach_tot_dyn']))
    mp['rach_part'] = mp['pm_deb'] * mp['qx_rach_part_glob'] # Flux de rachats partiels
    mp['rev_rach_part'] = mp['rach_part'] * mp['tx_se']  # revalorisation au taux minimum
    
    # Total des prestations
    mp['prest'] <- mp['rach_mass'] + mp['ech'] + mp['rach_tot'] + mp['dc'] + mp['rach_part'] # total prestations
    mp['rev_prest'] <- mp['rev_ech'] + mp['rev_rach_tot'] + mp['rev_dc'] + mp['rev_rach_part'] # total revalorisation des prestations
    
    # Total des mouvement des nombres de contrats
    mp['nb_sortie'] = mp['nb_ech'] + mp['nb_dc'] + mp['nb_rach_tot'] # nombre de sorties
    mp['nb_contr_fin'] = mp['nb_contr'] - mp['nb_sortie'] # nombre de contrats en cours en fin d'annee
    mp['nb_contr_moy'] = (mp['nb_contr'] + mp['nb_contr_fin']) / 2  # nombre de contrats moyen
    

#Vieillissement d'une ligne de MP d'un an
def vieillir_mp(row_mp):
    row_mp['t'] = row_mp['t'] + 1
    row_mp['age'] = row_mp['age'] + 1
    row_mp['anc'] = row_mp['anc'] + 1