import pandas as pd
import uuid
import numpy as np
from tqdm import tqdm
import os
#pd.set_option("display.max_rows", None, "display.max_columns", None)

def get_taux_frais_passif(mp, df_ref_frais):
    """
        Fonction qui permet de recupérer les taux de frais par produit à partir du référentiel de frais par produit.
        Ceci se fait par une jointure sur le num produit.

        :param df_mp: (Dataframe) model points passif
        :param df_ref_frais: (Dataframe) référentiel des taux de frais (plusieurs type de frais) par produit

        :returns: model points passif enrichie des taux frais
    """
    mp = pd.merge(mp, df_ref_frais, how='left', on=['num_prod'],
         indicator=False, validate='many_to_one')
    return mp

def initialisation_des_mp(df_mp, df_ref_frais, t):
    """Enrichissement du fichier de Mp en input de toutes les colonnes nécéssaires pour les futurs calculs
    
        :param df_mp: (Dataframe) Dataframe du représentant le fichier de Model point en input
        :param df_ref_frais: (Dataframe) référentiel des taux de frais (plusieurs type de frais) par produit

        :returns: Dataframe du fichier de Model point en input enrichi des colonnes qui seront calculées dans le run. 
    """
    mp_variable_list = ['num_mp', 'num_canton', 'num_prod', 'age', 'gen', 'num_tab_mort',
       'chgt_enc', 'ind_chgt_enc_pos', 'pm_fin_ap_pb', 'nb_contr_fin', 'anc', 'terme',
       'type_cot', 'periode_cot', 'tx_cible', 'chgt_prime', 'prime', 'tx_tech',
       'terme_tx_tech', 'tmg', 'terme_tmg', 'num_rach_tot', 'num_rach_part',
       'num_rach_dyn_tot', 'num_rach_dyn_part', 'chgt_rach', 'pm_gar',
       'tx_revalo_prec', 'tx_cible_prec','t', 'uuid']

    # creation d'un identifiant unique pour chaque ligne de mp.
    if t==0 :
        #initialisation de t à 0.
        df_mp = df_mp.rename(columns={"pm": "pm_fin_ap_pb"})
        df_mp = df_mp.rename(columns={"nb_contr": "nb_contr_fin"})
        df_mp['t'] = t
        df_mp['uuid'] = df_mp.apply(lambda _: uuid.uuid4(), axis=1)
    elif t==1 :
        df_mp = df_mp.loc[df_mp['t'] == (t-1), mp_variable_list]
        #initialisation de t.
        df_mp['t'] = t
        df_mp['age'] = df_mp['age'] + 1
        df_mp['anc'] = df_mp['anc'] + 1
        df_mp['pm_deb'] = df_mp['pm_fin_ap_pb']
        df_mp['nb_contr'] = df_mp['nb_contr_fin']
        df_mp = get_taux_frais_passif(df_mp, df_ref_frais)
    elif t>=2:
        df_mp = df_mp.loc[df_mp['t'] == (t-1), mp_variable_list]
        #initialisation de t.
        df_mp['t'] = t
        df_mp['age'] = df_mp['age'] + 1
        df_mp['anc'] = df_mp['anc'] + 1
        df_mp['pm_deb'] = df_mp['pm_fin_ap_pb']
        df_mp['nb_contr'] = df_mp['nb_contr_fin']
        df_mp = get_taux_frais_passif(df_mp, df_ref_frais)
    
    return df_mp

def get_proba_deces(mp, tm):
    """
        calcul des qx (décès) à partir de la table de mortalité

        :param mp: (Dataframe) model point passif
        :param tm: (Dataframe) table de survie

        :returns: model point passif enrichie des probabilité de survie
    """
    mp = pd.merge(mp, tm, how='left', on=['age'],
         indicator=False, validate='many_to_one')
    return mp

def get_proba_rachat_total(mp, rach):
    """
        Import de la probabilite de rachat structurel total à partir de la table des hypothèses de rachats structurels totaux.

        :param mp: (Dataframe) model point passif
        :param rach: (Dataframe) table de donnée contenant la probabilité de rachat total d'une contrat en fonction de l'ancienneté

        :returns: model point passif enrichie des probabilité de rachats structurels totaux
    """
    mp = pd.merge(mp, rach, how='left', on=['anc','age'],
         indicator=False, validate='many_to_one')
    return mp

def get_rachat_dyn_partiel_et_total(mp):
    """
        # TODO : Implémenter les Rachats dynamiques (aussi appelé rachat conjoncturel) totaux et partiels (selon la methodologie transmise dans le ONC de l'ACPR de 2013.).
        Methode permettant de calculer la composante rachat dynamique selon la methodologie transmise dans le ONC de l'ACPR de 2013.

        :param mp: (Dataframe) model point passif

        :returns: (Dataframe) model point passif enrichie des rachats dynamiques totaux et partiels.
    """
    #TODO : loi de rachat dynamique : total et partiel.
    mp['qx_rach_tot_dyn'] = 0.0025
    mp['qx_rach_part_dyn'] = 0.0025
    return mp

def calcul_rachat_conjoncturel_acpr(ecart, loi='Min'):
    """
        Fonction qui permet de calculer la probabilité de rachat conjoncturel (aussi appelé rachat dynamique)

        :param ecart: (Numeric) calculé comme <- taux servi - taux cible
        :param loi: (String) prend la valeur 'Min' ou 'Max'

        :returns: (Numeric) Probabilité de rachat conjonturel.
    """
    if loi=="Min":
        alpha = -0.06
        beta = -0.02
        gamma = 0.01
        delta = 0.02
        RCmin = -0.06
        RCmax = 0.2
    else :
        if loi =="Max":
            alpha = -0.04
            beta = 0
            gamma = 0.01
            delta = 0.04
            RCmin = -0.04
            RCmax = 0.4
        else:
            alpha = -0.05
            beta = -0.01
            gamma = 0.01
            delta = 0.03
            RCmin = -0.05
            RCmax = 0.3
    if ecart<alpha:
        rachat = RCmax
    if alpha<ecart and ecart<beta:
        rachat = RCmax*(ecart-beta)/(alpha-beta)
    if beta<ecart and ecart<gamma:
        rachat = 0
    if gamma<ecart and ecart<delta:
        rachat = RCmin*(ecart-gamma)/(delta-beta)
    if ecart>delta:
        rachat = RCmin
    
    return rachat

# Etape 1 de la projection : Calculer les primes et les chargements sur prime
def calcul_des_primes(mp, projection_des_primes=False):
    """
        Calcul des primes. Par defaut les primes ne sont pas modélisées (primes = 0).

        :param mp: (Dataframe) model point passif
        :param projection_des_primes: (Bool) valeur par défaut "False".  "True" si avec projection des primes.

        :returns: model point enrichi des calculs des primes 
    """
    # Nombre de versements
    # mp.loc[mp['prime'] > 0,"nb_vers"] = np.maximum(mp['nb_contr'], 0)
    mp['nb_vers'] = mp['nb_contr']
    
    if projection_des_primes==True:
        # Calcul les primes de l'annee
        mp['pri_brut'] = mp['prime'] * mp['nb_vers'] # primes brutes
        mp['pri_net'] = mp['pri_brut'] * (1 - mp['chgt_prime']) # primes nettes
        mp['pri_chgt'] = mp['pri_brut'] * mp['chgt_prime'] # Chargements sur primes
    else:
        mp['pri_brut'] = 0
        mp['pri_net'] = 0
        mp['pri_chgt'] = 0
    
    return mp

# Etape 2 : Calcul des taux min
def calcul_des_taux_min(mp):
    """
     Fonction de calcul des taux techniques et tmg min pour chaque ligne de MP.
     # TODO : calcul des taux techniques et TMG min à revoir potentiellement.

     :param mp: (Dataframe) model point passif
     :returns: model point passif enrichie des taux techniques ainsi que des taux minimum garantis annuels et semestriels
    """ 
    # calcul du taux technique
    mp['tx_tech_an'] = np.maximum(mp['tx_tech'], 0)
    mp['tx_tech_se'] = mp['tx_tech_an'] / 2 # taux semestriel
    # Calcul du taux minimum
    mp['tx_an'] = np.maximum(np.maximum(mp['tx_tech_an'], mp['tmg']), 0) # taux annuel minimum
    mp['tx_se'] = mp['tx_an'] / 2 # taux semestriel
    
    return mp

def calcul_des_taux_cibles(mp):
    """
        Taux optimal de revalorisation (supérieur ou égal au TMG) auquel l'assreur souhaite revaloriser sa PM afin de minimiser 
        les effets de rachat dynamiques.
        # TODO : Implémenter le calcul des taux cibles par ligne de MP

        :param mp: (Dataframe) model point passif

        :returns: model point passif enrichie des taux de revalorisation cibles
    """

    # taux_marche = np.sum(rendement * allocation_marche)

    # tp_max = taux_marche - charg_enc_mar

    # if tp_max > 0:
    #     tx_cible_an = tp_max * w_n * (1.0 - marge_mar)

    # tx_cible_an + (1.0 - w_n) * tx_cible_prec

    mp['tx_cible_an'] = 0.05
    mp['tx_cible_se'] = 0.05

    return mp

def calcul_des_taux_de_prel_sociaux(mp, tx_soc = 0.05):
    """
        :param mp: (Dataframe) model point passif
        :param tx_soc: (Numeric Default = 0.05) Taux des prelevements sociaux

        :returns: model point passif enrichie des taux de prélèvement sociaux

        #TODO : calcul des taux de prelevement sociaux A revoir potentiellement
    """
    mp['tx_soc'] = tx_soc
    return mp

def calcul_des_prestation(mp,t, rach, tm):
    """ 
    Calcul les flux de prestations pour des contrats epargne en euros ou retraite euros en phases de restitution.
    Calcul des prestations en année t de projection : 
    - Prestation avec revalorisation pour rachat total
    - Prestions avec revalorisation pour rachat total dynamique
    - Prestation avec revalorisation pour rachat partiel dynamique
    - Prestations avec revalorisation pour sinistre DC
    - Prestations avec revalorisation pour contrat arrivé à échéance
    - Chargements sur les différentes prestations
    - Prestations avec revalorisation net global
    
    :param mp: (Dataframe) model point passif enrichie des colonnes de la fonction *calcul_des_primes*
    :param t: (Int) année de projection
    :param rach: (Dataframe) table de donnée contenant la probabilité de rachat total d'une contrat en fonction de l'ancienneté
    :param tm: (Dataframe) table de survie

    Le calcul des prestations fait appel aux fonctions suivantes :
    calcul_des_taux_min(mp) ; get_rachat_dyn_partiel_et_total(mp) ; get_proba_rachat_total(mp, rach) ; get_proba_deces(mp, tm) ; calcul_des_taux_de_prel_sociaux(mp)
    
    :returns: (Dataframe) Model point enrichie des colonnes des prestations calculées
    """
    # Indicatrice de sortie en echeance    
    mp.loc[mp['terme'] > t, 'ind_ech'] = 0 # si le contrat n'est pas à terme
    mp.loc[mp['terme'] <= t, 'ind_ech'] = 1 # si le contrat à terme
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
    # mp = get_proba_rachat_total(mp) # calcul de qx_rach_tot
    mp = get_proba_rachat_total(mp, rach)
    mp['qx_rach_tot_glob'] = np.maximum(0, np.minimum(1, mp['qx_rach_tot'] + mp['qx_rach_tot_dyn'])) * (1 - mp['ind_ech']) # 1 si le contrat n'est pas a terme
    mp['nb_rach_tot'] = mp['nb_contr'] * mp['qx_rach_tot_glob']
    mp['rach_tot'] = mp['pm_deb'] * mp['qx_rach_tot_glob'] # Flux de rachats totaux
    mp['rev_rach_tot'] = mp['rach_tot'] * mp['tx_se'] # revalorisation au taux minimum
    # Calcul des flux de deces
    # Taux de deces sur la population des non rachetes
    # mp = get_proba_deces(mp) # calcul de qx_dc
    mp = get_proba_deces(mp, tm)
    mp['qx_dc_rach'] = mp['qx_dc'] * (1 - mp['qx_rach_tot_glob'])
    mp['dc'] = mp['pm_deb'] * mp['qx_dc_rach'] * (1-mp['ind_ech']) # Flux de rachats totaux
    mp['rev_dc'] = mp['dc'] * mp['tx_se'] # revalorisation au taux minimum
    mp['nb_dc'] = mp['nb_contr'] * mp['qx_dc_rach']
    # Calcul des flux rachats partiels
    # Taux de rachat incluant les rachats structurels et conjoncturels sur la population des non rachetes et vivants
    mp['qx_rach_part_glob'] = (1 - mp['qx_rach_tot_glob']) * (1 - mp['qx_dc']) * np.maximum(0, np.minimum(1, mp['qx_rach_part'] + mp['qx_rach_tot_dyn']))
    mp['rach_part'] = mp['pm_deb'] * mp['qx_rach_part_glob'] # Flux de rachats partiels
    mp['rev_rach_part'] = mp['rach_part'] * mp['tx_se']  # revalorisation au taux minimum
    # Total des prestations
    mp['prest'] = mp['ech'] + mp['rach_tot'] + mp['dc'] + mp['rach_part'] # total prestations
    mp['rev_prest'] = mp['rev_ech'] + mp['rev_rach_tot'] + mp['rev_dc'] + mp['rev_rach_part'] # total revalorisation des prestations
    # Total des mouvement des nombres de contrats
    mp['nb_sortie'] = mp['nb_ech'] + mp['nb_dc'] + mp['nb_rach_tot'] # nombre de sorties
    mp['nb_contr_fin'] = mp['nb_contr'] - mp['nb_sortie'] # nombre de contrats en cours en fin d'annee
    mp['nb_contr_moy'] = (mp['nb_contr'] + mp['nb_contr_fin']) / 2  # nombre de contrats moyen
    # Calcul du taux de chargement sur encours
    # Applique une limite sur le chargement sur encours selon la valeur de l'indicatrice
    # permettant les taux negatifs.
    # TODO: refactorer le nom de la variable pour préciser que c'est bien un taux de chargement sur les encours
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
    # Evaluation du besoin pour le financement des TMG sur prestations
    mp['bes_tmg_prest'] = np.minimum(mp['rev_prest'] - mp['it_tech_prest'], 0)
    return mp

def calcul_des_pm(mp):
    """
    calcul_des_pm() est une methode permettant de calculer les provisions mathematiques (PM)
    de fin de periode avant application de la revalorisation au titre de la participation aux benefices
    et après versement des prestations.

    :param mp: (Dataframe) model point passif enrichi des colonnes de la fonction *calcul_des_prestations*

    :returns: (Dataframe) model point passif enrichi  des calculs de provision mathématiques (pm)
    """
    # Calculs effectues plusieurs fois
    mp['diff_pm_prest'] = mp['pm_deb'] - mp['prest']
    # Calcul des taux cibles
    mp = calcul_des_taux_cibles(mp)
    # Calcul de la revalorisation brute
    mp['rev_stock_brut'] = mp['diff_pm_prest'] * mp['tx_an'] + mp['pri_net'] * mp['tx_se']
    # Chargement sur encours
    mp['enc_charg_stock'] = mp['diff_pm_prest'] * (1+mp['tx_an'])  * mp['chgt_enc'] + mp['pri_net'] * (1 + mp['tx_se']) * (mp['chgt_enc']/2)
    # Chargement sur encours théorique en decomposant la part relative au passif non revalorisés et à la revalorisation
    mp['enc_charg_base_th'] = mp['diff_pm_prest'] * mp['chgt_enc'] + mp['pri_net'] * (mp['chgt_enc']/2)
    mp['enc_charg_rmin_th'] = mp['diff_pm_prest'] * mp['chgt_enc'] * mp['tx_an'] + mp['pri_net'] * (mp['chgt_enc']/2) * mp['tx_se']
    # Base utilise pour appliques le calcul du taux de chargement sur encours
    mp['base_enc_th'] = mp['diff_pm_prest'] * (1+mp['tx_an']) + mp['pri_net'] * (1+mp['tx_se'])
    # Calcul de la revalorisation sur stock
    mp['rev_stock_nette'] = mp['rev_stock_brut'] - mp['enc_charg_stock']
    # Revalorisation nette totale
    mp['rev_total_nette'] = mp['rev_stock_nette'] + mp['rev_prest_nette']
    # Prelevement sociaux
    mp['soc_stock'] = np.maximum(0, mp['rev_stock_nette']) * mp['tx_soc']
    # Evaluation des provisions mathématiques avant PB
    mp['pm_fin'] = mp['diff_pm_prest'] + mp['pri_net'] + mp['rev_stock_nette'] - mp['soc_stock']
    # PM moy et taux de chargement
    mp['pm_moy'] = (mp['pm_deb'] + mp['pm_fin']) / 2
    # Evaluation des interets techniques
    mp['it_tech_stock']   = mp['diff_pm_prest'] * mp['tx_tech_an'] + mp['pri_net'] * mp['tx_tech_se']
    mp['it_tech'] = mp['it_tech_stock'] + mp['it_tech_prest']
    # Evaluation du besoin pour le financement du taux cible
    mp['bes_tx_cible'] = np.maximum(0, (mp['tx_cible_an'] * mp['diff_pm_prest'] + mp['tx_cible_se'] * mp['pri_net']))
    # Evaluation du besoin pour le financement des TMG sur les stock
    mp['bes_tmg_stock'] = np.minimum(mp['rev_stock_brut'] - mp['it_tech_stock'],0)
    return mp

def calcul_revalo_pm(mp, rev_brute_alloue_gar):
    """
    calcul_revalo_pm() est une methode permettant de calculer les provisions mathematiques (PM)
    de fin de periode après application de la revalorisation au titre de la participation aux benefices
    et après versement des prestations.

    :param mp: (Dataframe) model point passif enrichi des colonnes de la fonction *calcul_des_pm*

    :returns: (Dataframe) model point passif enrichi des calculs de participation au bénéfice (pm)
    """
    # chargement theorique avant pb
    mp['chgt_enc_stock_th_av_pb'] = mp['enc_charg_rmin_th'] + mp['enc_charg_base_th']
    # Revalorisation nette avant pb
    mp['rev_stock_nette_av_pb'] = mp['rev_stock_brut'] - mp['chgt_enc_stock_th_av_pb']
    # Application de la contrainte de taux negatif
    mp['rev_stock_nette_av_pb'] = np.maximum(0, mp['rev_stock_nette_av_pb']) * mp['ind_chgt_enc_pos'] + mp['rev_stock_nette_av_pb'] * (1 - mp['ind_chgt_enc_pos'])
    # Calcul des chargements et de la revalorisation nette
    # mp['add_rev_nette_stock'] = rev_net_alloue
    if(np.sum(mp['add_rev_nette_stock']) == 0):
        # chargements reels
        mp['enc_charg_stock_ap_pb'] = mp['rev_stock_brut'] * mp['ind_chgt_enc_pos'] + mp['chgt_enc_stock_th_av_pb'] * (1 - mp['ind_chgt_enc_pos'])
        # revaloristation nette
        mp['rev_stock_nette_ap_pb'] = mp['rev_stock_nette_av_pb']
    else:
        #allocation de la revalorisation additionnelle selon le taux cible
        if(np.sum(mp['bes_tx_cible']) != 0):
            mp['rev_net_alloue_mp'] = mp['add_rev_nette_stock'] * (mp['bes_tx_cible'] / np.sum(mp['bes_tx_cible']))
        else:
            #  Attribution proportionnelle
            mp['rev_net_alloue_mp'] = mp['add_rev_nette_stock'] * (mp['nb_contr'] / np.sum(mp['nb_contr']))
        # Revalorisation nette
        mp['rev_stock_nette_ap_pb'] = mp['rev_stock_nette_av_pb'] * (mp['rev_stock_nette_av_pb']>0) + mp['rev_net_alloue_mp']
        # Chargements reels
        mp['enc_charg_stock_ap_pb'] = mp['chgt_enc_stock_th_av_pb'] + mp['rev_net_alloue_mp'] / (1 - mp['chgt_enc']) * mp['chgt_enc']
        # Revalorisation brute
        mp['rev_stock_brut_ap_pb'] = mp['rev_stock_brut'] * (mp['rev_stock_nette_av_pb']>0) \
                                + mp['chgt_enc_stock_th_av_pb'] * (mp['rev_stock_nette_av_pb']<=0) + mp['rev_net_alloue_mp'] / (1-mp['chgt_enc'])
    # Attribution de la revalorisation garantie
    if(rev_brute_alloue_gar != 0):
        # Allocation de la revalorisation additionnelle selon le taux cible
        if(np.sum(mp['bes_tx_cible']) != 0):
            mp['rev_brute_alloue_gar_mp'] =  rev_brute_alloue_gar * (mp['bes_tx_cible']/np.sum(mp['bes_tx_cible']))
        else:
            # Attribution proportionnelle
            mp['rev_brute_alloue_gar_mp'] = mp['rev_brute_alloue_gar_mp'] * (mp['nb_contr'] / np.sum(mp['nb_contr']))
    else:
        mp['rev_brute_alloue_gar_mp'] = 0
    #Calcul du taux de revalorisation net
    mp['tx_rev_net'] = mp['rev_stock_nette_ap_pb'] / (mp['pm_deb'] - mp['prest'] + (0.5 * mp['pri_net']))
    mp['tx_rev_net'].fillna(0)
    # Prelevement sociaux 
    mp['soc_stock_ap_pb'] = np.maximum(0, mp['rev_stock_nette_ap_pb']) * mp['tx_soc']
    # Evaluation des PM avant PB
    mp['pm_fin_ap_pb'] = mp['pm_deb'] - mp['prest'] + mp['pri_net'] + mp['rev_stock_nette_ap_pb'] - mp['soc_stock'] 
    # PM garantie
    #mp['pm_gar_ap_pb'] = mp['pm_gar'] + mp['rev_brute_alloue_gar_mp'] * (1 - mp['chgt_enc'] ) * (1-mp['tx_soc'])
    # Application d'un seuil pour eviter les problemes d'arrondi
    return mp

def calcul_des_frais(mp):
    """
        Fonction qui permet de calculer les frais (après avoir récupérer les taux de frais du référentiel de frais par produit)
        Calcul des frais sur passif : prestations, primes, encours.

        :param mp: (Dataframe) model point passif enrichi des colonnes de la fonction *calcul_des_pm*

        :returns: (Dataframe) model point passif enrichi des calculs des frais
    """
    # Calcul de frais du prime
    mp['frais_fixe_prime'] = mp['nb_vers'] * mp['tx_frais_fixe_prime'] * (1 + mp['ind_inf_frais_fixe_prime']) * (mp['coef_inf'] - 1)
    mp['frais_var_prime'] = mp['pri_brut'] * mp['tx_frais_var_prime'] * (1 + mp['ind_inf_frais_var_prime']) * (mp['coef_inf'] - 1)

    # Calcul de frais de prestation
    mp['frais_fixe_prest'] = mp['nb_sortie'] * mp['tx_frais_fixe_prest'] * (1 + mp['ind_inf_frais_fixe_prest']) * (mp['coef_inf'] - 1)
    mp['frais_var_prest'] = mp['prest'] * mp['tx_frais_var_prest'] * (1 + mp['ind_inf_frais_var_prest']) * (mp['coef_inf'] - 1)

    # Calcul de frais sur encours
    mp['frais_fixe_enc'] = mp['nb_contr_moy'] * mp['tx_frais_fixe_enc'] * (1 + mp['ind_inf_frais_fixe_enc']) * (mp['coef_inf'] - 1)
    mp['frais_var_enc'] = mp['pm_moy'] * mp['tx_frais_var_enc'] * (1 + mp['ind_inf_frais_var_enc']) * (mp['coef_inf'] - 1)

    return mp

def calcul_du_resultat_technique(mp):
    """ 
        Calcul du resultat technique.

        :param mp: (Dataframe) model point passif enrichi des colonnes de la fonction *calcul_des_frais*.

        :returns: (Dataframe) model point passif enrichi du resultat technique
        # TODO modéliser le choc de rachat : le rachat massif.
    """
    # calcul des flux debut d'annee: rach_mass est le choc de rachat massif non encore implémenter,
    mp['rach_mass'] = 0
    mp['rach_charg_mass'] = 0
    flux_debut = mp['rach_mass'] - mp['rach_charg_mass'] 
    #  calcul des flux_milieu d'annee : primes - prestation - (charges sur prestations + charges sur primes) 
    # TODO intégrer les flux hors modèle (non modéliser)
    mp['flux_milieu'] = mp['pri_brut'] - (mp['rev_prest_nette'] + 
                                        mp['prest']
                                 ) - \
                                 (
                                     mp["frais_var_prime"] + 
                                    mp["frais_fixe_prime"] + 
                                    mp["frais_var_prest"] + 
                                    mp["frais_fixe_prest"]
                                 )
    # calcul des flux_fin d'annee :
    mp['flux_fin'] = mp['frais_var_enc'] + mp['frais_fixe_enc']
    mp['resultat_technique'] = mp['pm_deb'] - mp['pm_fin'] +  mp['flux_milieu'] + mp['flux_fin']   #TODO intégrer les flux hors modèle (non modélisé)
    return mp

def projection_autres_passifs(an, autre_passif, coef_inf):
    """ 
    Méthode permettant de calculer les PM et les flux sur une annee pour des passif non modelises :

    :Param an: (int) année de projection
    :Param autre_passif: (Dataframe) dataframe représentant le passif non modélisé
    :Param coef_inf: (Float) coefiscient d'inflation pour les frais
    """
    autre_passif = autre_passif.loc[autre_passif['annee'] == an,:]
    autre_passif = autre_passif['pm_moy'] * coef_inf
    return  autre_passif