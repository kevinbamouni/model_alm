from alm_passif.model_passif import *
import alm_passif.ppb as ppb
from alm_passif.revalorisation_contrats import *
import alm_actif.model_actif as actif
import pandas as pd
import numpy as np
from tqdm import tqdm
import json
import os
from pathlib import Path
import logging

"""
    run.py est l'unique point d'entré pour lancer un run.
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
    abs_path = Path(os.path.dirname(os.path.abspath(__file__)))

    logging.basicConfig(filename=abs_path/'tests/output_test_data/modelealmrun.log',
                        level=logging.INFO, filemode='w',
                        format='%(asctime)s  %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')
    logging.info('===== Modele ALM version XX.XX =====')
    logging.info('===== Initialisation =====')
    ############################################################################################################
    # Chargement des donnees de l'actif
    ############################################################################################################

    # Chargement des input : Model point portefeuille financier
    oblig_path = abs_path / "tests/input_test_data/ptf_oblig.csv"
    action_path = abs_path / "tests/input_test_data/ptf_action.csv"
    treso_path = abs_path / "tests/input_test_data/ptf_treso.csv"
    immo_path = abs_path / "tests/input_test_data/ptf_immo.csv"

    # Chargement des données ESG 
    oblig_scena_path = abs_path / "gse/gse_outputs/2009_ESWG_1000_scenarios.csv"
    action_scena_path = abs_path / "gse/gse_outputs/esg_stock.csv"
    immo_scena_path = abs_path / "gse/gse_outputs/esg_realestate.csv"
    treso_scena_path = abs_path / "gse/gse_outputs/esg_shortrate.csv"

    # Chargement de l'allocaiton cible
    alloc_strat_cible_portfi_path = abs_path / "tests/input_test_data/alloc_strat_cible_portfi.json"

    oblig = pd.read_csv(oblig_path)
    action = pd.read_csv(action_path)
    treso = pd.read_csv(treso_path)
    immo = pd.read_csv(immo_path)

    oblig_scena = pd.read_csv(oblig_scena_path, sep=";")
    action_scena = pd.read_csv(action_scena_path, sep=",")
    immo_scena = pd.read_csv(immo_scena_path, sep=",")
    treso_scena = pd.read_csv(treso_scena_path, sep=",")

    # Mise en forme du dataframe de l'oblig scena
    oblig_scena = pd.melt(oblig_scena, id_vars=['scenario', 'month'],
                                    value_vars=['0.25', '0.5', '1', '2','3', '5', '7', '10', '20','30'], 
                                    var_name='maturities',
                                    value_name='rates')

    # read file json de l'allocaiton cible
    with open(alloc_strat_cible_portfi_path, 'r') as myfile:
        data=myfile.read()
    alloc_strat_cible_portfi = json.loads(data)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     

    # Creation de l'objet portefeuille financier pour la Modelisation de actif
    ptf_financier = actif.portefeuille_financier(action, oblig, immo, treso, action_scena, oblig_scena, immo_scena, treso_scena, alloc_strat_cible_portfi)
    ptf_financier.calcul_alloc_strateg_crt()
    logging.info('allocation_courante : %s ', ptf_financier.allocation_courante)
    logging.info('allocation_cible : %s ', ptf_financier.alloc_strat_cible_portfi)


    ############################################################################################################
    # Chargement des donnees du passif
    ############################################################################################################

    mp_path = abs_path / "tests/input_test_data/mp.csv"
    tm_path = abs_path / "tests/input_test_data/th_dc_00_02.csv"
    rach_path = abs_path / "tests/input_test_data/table_rachat.csv"
    ref_frais_path = abs_path / "tests/input_test_data/ref_frais_produits.csv"
    taux_pb = abs_path / "tests/input_test_data/taux_pb.csv"
    param_revalo = abs_path / "tests/input_test_data/param_revalo.csv"

    # Chargement des input.
    mp = pd.read_csv(mp_path) # model point
    tm = pd.read_csv(tm_path) #table de mortalite
    rach = pd.read_csv(rach_path) # loi de rachat
    ref_frais = pd.read_csv(ref_frais_path) # referentiel de frais par produit
    param_revalo = pd.read_csv(param_revalo)
    taux_pb = pd.read_csv(taux_pb)
    ppe = np.array([]) #initialisation de la ppe
    ppbe = ppb.ppb(np.array([0]))

    ############################################################################################################
    # Projection : run BE
    ############################################################################################################
    # initialisation à t = 0
    mp_global_projection = initialisation_des_mp(mp, ref_frais, t = 0)
    logging.info('Describe passif : %s ', description_mp(mp))
    for time_index in tqdm(range(1,41,1)):
        logging.info('========== DEBUT DU RUN / Horizon = %s ==========', time_index)
        # Modelisaiton du Passif
        mp_t = initialisation_des_mp(mp_global_projection, ref_frais, t = time_index)
        # Modelisation du passif avant Participation au bénéfice
        mp_t = calcul_des_primes(mp_t, projection_des_primes=False)
        mp_t = calcul_des_prestation(mp_t, t = time_index, rach = rach, tm = tm)
        mp_t = calcul_des_pm(mp_t)
        mp_t = calcul_des_frais(mp_t)
        mp_t = calcul_du_resultat_technique(mp_t)
        # Modélisation du passif après Participation au bénéfice
        #mp_t = calcul_revalo_pm(mp_t, rev_net_alloue = np.sum(mp_t['rev_stock_nette']), rev_brute_alloue_gar = np.sum(mp_t['rev_stock_brut']))
        resultat_technique = np.sum(mp_t['resultat_technique'])

        # Modelisation de l'Actif
        ptf_financier.calcul_assiette_tresorerie(np.sum(mp_t['flux_milieu'] + mp_t['flux_fin']))
        ptf_financier.veillissement_treso(time_index, maturite = 0.5)
        ptf_financier.veillissement_action(time_index)
        ptf_financier.veillissement_immo(time_index)
        ptf_financier.veillissement_obligation(scenario, time_index)
        ptf_financier.allocation_strategique(time_index)
        logging.info('allocation_courante avant pb : %s ', ptf_financier.allocation_courante)
        logging.info('allocation_cible avant pb : %s ', ptf_financier.alloc_strat_cible_portfi)
        ptf_financier.calcul_resultat_financier(tx_frais_val_marche=0, tx_frais_produits=0, tx_charges_reserve_capi=0)
        mp_t, param_revalo, ppbe, ptf_financier = moteur_politique_revalo(mp_t, param_revalo, taux_pb, ppbe, ptf_financier)
        mp_t = calcul_revalo_pm(mp_t, rev_brute_alloue_gar = ppbe.consommation)
        ptf_financier.allocation_strategique(time_index)
        ptf_financier.calcul_resultat_financier(tx_frais_val_marche=0, tx_frais_produits=0, tx_charges_reserve_capi=0)
        ppbe.re_init_ppb()
        #ptf_financier.initialisation_ptf_financier()
        logging.info('allocation_courante après pb : %s ', ptf_financier.allocation_courante)
        logging.info('allocation_cible après pb : %s ', ptf_financier.alloc_strat_cible_portfi)
        logging.info('Describe passif : %s ', description_mp(mp_t))
        logging.info('========== FIN DU RUN / Horizon = %s ==========', time_index)
        # Application de l'algorithme de profit share
        mp_global_projection = mp_global_projection.append(mp_t)

    mp_global_projection.to_csv(abs_path / "tests/output_test_data/mp_global_projection.csv", index = False)