from alm_passif.model_passif import *
import alm_actif.model_actif as actif
import pandas as pd
import numpy as np
from tqdm import tqdm
import json
import os

"""
    run.py est l'unique point d'entré pour lancer un run de projection.
"""


# Execution main :
if __name__ == "__main__":

    ############################################################################################################
    # Parametres globaux
    ############################################################################################################
    Date_t0="31/12/2019"
    N = 40
    t = 0
    scenario = 1
    abs_path = os.path.abspath(os.curdir)

    ############################################################################################################
    # Chargement des donnees de l'actif
    ############################################################################################################

    # Chargement des input : Model point portefeuille financier
    oblig_path = abs_path + "/tests/input_test_data/ptf_oblig.csv"
    action_path = abs_path + "/tests/input_test_data/ptf_action.csv"
    treso_path = abs_path + "/tests/input_test_data/ptf_treso.csv"
    immo_path = abs_path + "/tests/input_test_data/ptf_immo.csv"

    # Chargement des données ESG 
    oblig_scena_path = abs_path + "/gse/gse_outputs/2009_ESWG_1000_scenarios.csv"
    action_scena_path = abs_path + "/gse/gse_outputs/esg_stock.csv"
    immo_scena_path = abs_path + "/gse/gse_outputs/esg_realestate.csv"
    treso_scena_path = abs_path + "/gse/gse_outputs/esg_shortrate.csv"

    # Chargement de l'allocaiton cible
    alloc_strat_cible_portfi_path = abs_path + "/tests/input_test_data/alloc_strat_cible_portfi.json"

    oblig = pd.read_csv(oblig_path)
    action = pd.read_csv(action_path)
    treso = pd.read_csv(treso_path)
    immo = pd.read_csv(immo_path)

    oblig_scena = pd.read_csv(oblig_scena_path, sep=";")
    action_scena = pd.read_csv(action_scena_path, sep=",")
    immo_scena = pd.read_csv(immo_scena_path, sep=",")
    treso_scena = pd.read_csv(treso_scena_path, sep=",")

    # Mise en forme du dataframe de l'oblig scena
    oblig_scena = pd.melt(oblig_scena, id_vars=['scenario', 'month'], value_vars=['0.25', '0.5', '1', '2','3', '5', '7', '10', '20','30'], var_name='maturities', value_name='rates')

    # read file json de l'allocaiton cible
    with open(alloc_strat_cible_portfi_path, 'r') as myfile:
        data=myfile.read()
    alloc_strat_cible_portfi = json.loads(data)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     

    # Creation de l'objet portefeuille financier pour la Modelisation de actif
    ptf_financier = actif.portefeuille_financier(action, oblig, immo, treso, action_scena, oblig_scena, immo_scena, treso_scena, alloc_strat_cible_portfi)

    ############################################################################################################
    # Chargement des donnees du passif
    ############################################################################################################

    mp_path = abs_path + "/tests/input_test_data/mp.csv"
    tm_path = abs_path + "/tests/input_test_data/th_dc_00_02.csv"
    rach_path = abs_path + "/tests/input_test_data/table_rachat.csv"
    ref_frais_path = abs_path + "/tests/input_test_data/ref_frais_produits.csv"

    # Chargement des input.
    mp = pd.read_csv(mp_path) # model point
    tm = pd.read_csv(tm_path) #table de mortalite
    rach = pd.read_csv(rach_path) # loi de rachat
    ref_frais = pd.read_csv(ref_frais_path) # referentiel de frais par produit
    ppe = np.array([]) #initialisation de la ppe

    ############################################################################################################
    # Projection : run BE
    ############################################################################################################

    # initialisation à t = 0
    mp_global_projection = initialisation_des_mp(mp, ref_frais, t = 0)
    #print(mp.columns)
    for time_index in tqdm(range(1,41,1)):
        # Modelisaiton du Passif
        mp_t = initialisation_des_mp(mp_global_projection, ref_frais, t = time_index)
        mp_t = calcul_des_primes(mp_t)
        mp_t = calcul_des_prestation(mp_t, t = time_index, rach = rach, tm = tm)
        mp_t = calcul_des_pm(mp_t)
        mp_t = calcul_des_frais(mp_t)
        mp_t = calcul_du_resultat_technique(mp_t)
        resultat_technique = np.sum(mp_t['resultat_technique'])

        # Modelisation de l'Actif
        ptf_financier.veillissement_treso(time_index, maturite = 0.5)
        ptf_financier.veillissement_treso(time_index, maturite = 0.5)
        ptf_financier.veillissement_action(time_index)
        ptf_financier.veillissement_immo(time_index)
        ptf_financier.veillissement_obligation(scenario, time_index)
        ptf_financier.calcul_assiette_tresorerie(0,np.sum(mp_t['rev_prest']))
        ptf_financier.allocation_strategique(time_index)
        resultat_financier = ptf_financier.calcul_resultat_financier(frais_produits = 0, frais_val_marche = 0, charges_reserve_capi = 0)

        # Calcul du resultat total
        resultat_total = resultat_financier + resultat_technique

        pvl_actifs = 0
        mp_t, ppe, ptf_financier = calcul_des_pm_ap_pb(resultat_total = resultat_total,
                                                        mp = mp_t,
                                                        ppe = ppe,
                                                        pvl_actifs = ptf_financier.calcul_des_pvl_action()+ptf_financier.calcul_des_pvl_immo(),
                                                        portefeuille_financier = ptf_financier)
    
        # Application de l'algorithme de profit share
        mp_global_projection = mp_global_projection.append(mp_t)

    mp_global_projection.to_csv(abs_path + "/tests/output_test_data/mp_global_projection.csv", index = False)