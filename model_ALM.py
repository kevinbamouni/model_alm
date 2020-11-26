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
        'tx_soc',
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
        'pri_chgt',
        'pm_deb',
        'pm_moy']


# mp.loc[mp.age<18,"age"]=18
# mp.to_csv(mp_path, sep=',', encoding='utf-8', index=False)

def initialisation_des_mp(df_mp, list_colonnes_a_enrichir, t):
    """Enrichissement du fichier de Mp en input de toutes les colonnes nécéssaires pour les futurs calculs
    
    Input : Dataframe du représentant le fichier de Model point en input
    Output : Dataframe du fichier de Model point en input enrichi des colonnes qui seront calculées dans le run. 
    """
    
    # creation d'un identifiant unique pour chaque ligne de mp.
    if t==0 :
        #initialisation de t à 0.
        df_mp['t'] = t
        df_mp['uuid'] = df_mp.apply(lambda _: uuid.uuid4(), axis=1)

        for x in list_colonnes_a_enrichir:
            df_mp[x]= None

        df_mp.rename(columns={"pm": "pm_fin"})

    elif t==1:
        df_mp = df_mp.loc[mp.t == (t-1),:]
        #initialisation de t.
        df_mp['t'] = t
        df_mp['age'] = df_mp['age'] + 1
        df_mp['anc'] = df_mp['anc'] + 1
        df_mp['pm_deb'] = df_mp['pm_fin']

    elif t>=2:
        df_mp = df_mp.loc[mp.t == (t-1),:]
        #initialisation de t.
        df_mp['t'] = t
        df_mp['age'] = df_mp['age'] + 1
        df_mp['anc'] = df_mp['anc'] + 1
        df_mp['pm_deb'] = df_mp['pm_fin']

        # 0 : Calcul des proba des flux
        # 1 : Calcul des flux de prestation
        # 2 : Calcul des taux cibles pour chaque mp : objectif de rendement en fonction des autres assureurs et du rendement des actifs
        # 3 : Taux minimum à servir par Model Point :
        # 4 : Calcul des primes projetées
        # 5 : Calcul de la PM
        # 6 : Calcul de la revalo de la PM avec pb
    
    return df_mp


def get_proba_deces(mp):
    """
        # TODO : Implémenter le calcul des qx (décès) à partir de la table de mortalité
    """
    mp['qx_dc'] = 0.0025
    return mp

def get_proba_rachat_total(mp):
    """
        # TODO : Implementer la probabilite de charchat total via la table des hypothèse de rachat totaux
    """
    mp['qx_rach_tot'] = 0.00025
    return mp

def get_rachat_dyn_partiel_et_total(mp):
    """
        # TODO : Implémenter les Rachats dynamiques totaux et partiels (selon la methodologie transmise dans le ONC de l'ACPR de 2013.).
        Methode permettant de calculer la composante rachat dynamique selon la methodologie transmise dans le ONC de l'ACPR de 2013.
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
     # TODO : calcul des taux techniques et TMG min à revoir potentiellement
    """ 
    # calcul du taux technique    
    mp.tx_tech_an = np.maximum(mp.tech, 0)
    mp.tx_tech_se = mp.tx_tech_an / 2 # taux semestriel

    # Calcul du taux minimum
    mp.tx_an = np.maximum(mp.tx_tech_an, mp.tmg) # taux annuel minimum
    mp.tx_se = mp.tx_min / 2 # taux semestriel
    
    return mp

def calcul_des_taux_cibles(mp):
    """
        # TODO : Implémenter le calcul des taux cibles par ligne de MP
    """
    mp['tx_cible_an'] = 0
    mp['tx_cible_se'] = 0

    return mp


def calcul_des_taux_de_prel_sociaux(mp):
    """
        #TODO : calcul des taux de prelevement sociaux A revoir potentiellement
    """
    mp['tx_soc'] = 0.05
    return mp


def calcul_des_prestation(mp,t):
    """ 
        Calcul des prestations en année t de projection : 
            - Prestation avec revalorisation pour rachat total :
            - Prestions avec revalorisation pour rachat total dynamique
            - Prestation avec revalorisation pour rachat partiel dynamique
            - Prestations avec revalorisation pour sinistre DC
            - Prestations avec revalorisation pour contrat arrivé à échéance
            - Chargements sur les différentes prestations
            _ Prestations avec revalorisation net global
    """
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
    mp['prest'] = mp['rach_mass'] + mp['ech'] + mp['rach_tot'] + mp['dc'] + mp['rach_part'] # total prestations
    mp['rev_prest'] = mp['rev_ech'] + mp['rev_rach_tot'] + mp['rev_dc'] + mp['rev_rach_part'] # total revalorisation des prestations
    
    # Total des mouvement des nombres de contrats
    mp['nb_sortie'] = mp['nb_ech'] + mp['nb_dc'] + mp['nb_rach_tot'] # nombre de sorties
    mp['nb_contr_fin'] = mp['nb_contr'] - mp['nb_sortie'] # nombre de contrats en cours en fin d'annee
    mp['nb_contr_moy'] = (mp['nb_contr'] + mp['nb_contr_fin']) / 2  # nombre de contrats moyen

    # Calcul du taux de chargement sur encours
    # Applique une limite sur le chargement sur encours selon la valeur de l'indicatrice
    # permettant les taux negatifs.
    mp['chgt_enc'] = np.minimum(mp['chgt_enc'], mp['tx_an'] / (1 + mp['tx_an'])) * mp['ind_chgt_enc_pos'] + mp['chgt_enc'] * (1 - mp['ind_chgt_enc_pos'])

    # Calcul des chargements sur encours
    mp['enc_charg'] = (mp['prest'] + mp['rev_prest']) * mp['chgt_enc'] / 2

    # Calcul de la revalorisation nette des prestations avec capitalisation sur un semestre
    mp['rev_prest_nette'] = mp['rev_prest'] - mp['enc_charg']

    # Calcul des autres chargements et des prelevements sociaux
    mp = calcul_des_taux_de_prel_sociaux(mp) # calcul de tx_soc
    mp['rach_charg'] = (mp['rach_tot'] + mp['rach_part'] + mp['rev_rach_tot'] + mp['rev_rach_part']) * mp['chgt_rach']
    mp['soc_prest'] = np.maximum(0, mp['rev_prest_nette']) * mp['tx_soc'] # prelevements sociaux

    # Calcul des interets techniques sur prestations
    mp['it_tech_prest'] = mp['prest'] * mp['tx_tech_se']

    return mp


def calcul_des_pm(mp, t):

    # Calculs effectues plusieurs fois
    mp['diff_pm_prest'] = mp['pm_deb'] - mp['prest'] # PM restant après versement en milieu d'année des prestations 

    # Calcul de la revalorisation brute
    mp['rev_stock_brut'] = mp['diff_pm_prest'] * mp['tx_an'] + mp['pri_net'] * mp['tx_se'] # on suppose que les primes sont versées en milieu d'années

    # Chargements : sur encours
    mp['enc_charg_stock'] = mp['diff_pm_prest'] * (1 + mp['tx_an']) * mp['chgt_enc'] + mp['pri_net'] * (1 + mp['tx_se']) * mp['chgt_enc'] / 2

    # Chargement sur encours theorique en decomposant la part revalative au passif non revalorises et a la revalorisation
    mp['enc_charg_base_th'] = mp['diff_pm_prest'] * mp['chgt_enc'] + mp['pri_net'] * mp['chgt_enc'] / 2
    mp['enc_charg_rmin_th'] = (mp['diff_pm_prest'] * mp['chgt_enc']) * mp['tx_an'] + (mp['pri_net'] * mp['chgt_enc'] / 2) * mp['tx_se']

    # Base utilise pour appliques le calcul du taux de chargement sur encours
    mp['base_enc_th'] = mp['diff_pm_prest'] * (1 + mp['tx_an']) + mp['pri_net'] * (1 + mp['tx_se'])

    # Calcul de la revalorisation sur stock
    mp['rev_stock_nette'] = mp['rev_stock_brut'] - mp['enc_charg_stock']

    # Revalorisation nette totale
    # mp['rev_total_nette'] = mp['rev_stock_nette'] + mp['rev_prest_nette']

    # Prelevement sociaux
    mp['soc_stock'] = np.maximum(0, mp['rev_stock_nette']) * mp['tx_soc']

    # Evaluation des provisions mathematiques avant PB
    mp['pm_fin'] = mp['diff_pm_prest'] + mp['pri_net'] + mp['rev_stock_nette'] - mp['soc_stock']

    # PM moyenne et taux de chargement
    mp['pm_moy'] = (mp['pm_deb'] + mp['pm_fin']) / 2

    # Evaluation des interets techniques
    mp['it_tech_stock']   = mp['diff_pm_prest'] * mp['tx_tech_an'] + mp['pri_net'] * mp['tx_tech_se']
    mp['it_tech'] = mp['it_tech_stock'] + mp['it_tech_prest']

    # EValuation du besoin de taux cible
    mp = calcul_des_taux_cibles(mp)
    mp['bes_tx_cible'] = np.maximum(0, (mp['tx_cible_an'] * mp['diff_pm_prest'] + mp['tx_cible_se'] * mp['pri_net']))

