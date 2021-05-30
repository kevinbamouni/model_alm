import numpy as np
from numpy.core.defchararray import array
import pandas as pd
from pandas.core.indexes import base

def attribution_ppb_8ans(mp, ppb):
    if len(ppb.ppb_historique) >= 8:
        ppb_8ans =  ppb.ppb_historique[-8]
        ppb.reprise_ppb_8ans()
    else:
        ppb_8ans =  0
    mp['ppb8_ind'] = ppb_8ans * mp['pm_fin']/(np.sum(mp['pm_fin']))
    return mp, ppb

def calcul_base_produit_financier(tra, ppb, mp):
    """
        Calcul de la base des produits financier attribuables aux PM
    """
    mp['base_prod_fi'] = (mp['pm_moy'] + np.sum(ppb.ppb_historique)*(mp['pm_moy']/np.sum(mp['pm_moy']))) * tra
    return mp

def calcul_marge_financiere(mp, ppb):
    # Calcul de la marge financiere avant revalorisation du stock
    # Retrait de la charge pour financement revalorisation des prestations
    # Ajout du financement venant de la PPB sur les TMG du stock et reprise pour taux cible
    mp['marge_fi'] = mp['base_prod_fi'] - \
                    mp['rev_prest_nette'] + mp['bes_tmg_prest'] - \
                    mp['rev_stock_nette'] + mp['bes_tmg_stock'] + np.sum(ppb.reprises)
    return mp

def get_taux_pb(mp, df_ref_taux_pb):
    """
        Fonction qui permet de recupérer les taux de pb par produit à partir du référentiel de pb par produit.
        Ceci se fait par une jointure sur le num produit.

        :param df_mp: (Dataframe) model points passif
        :param df_ref_taux_pb: (Dataframe) référentiel des taux de pb (plusieurs type de pb) par produit

        :returns: model points passif enrichie des taux pb
    """
    mp = pd.merge(mp, df_ref_taux_pb, how='left', on=['num_prod'],
         indicator=False, validate='many_to_one')
    return mp

def get_param_revalo(mp, df_ref_revalo):
    """
        Fonction qui permet de recupérer les taux de pb par produit à partir du référentiel de pb par produit.
        Ceci se fait par une jointure sur le num produit.

        :param df_mp: (Dataframe) model points passif
        :param df_ref_taux_pb: (Dataframe) référentiel des taux de pb (plusieurs type de pb) par produit

        :returns: model points passif enrichie des taux pb
    """
    mp = pd.merge(mp, df_ref_revalo, how='left', on=['num_prod'],
         indicator=False, validate='many_to_one')
    return mp

def calcul_pb_contractuelle(mp, ref_taux_pb):
    """
        Fonction qui recupere les taux de pb contractuel par produit du referentiel de taux de pb puis calcul les taux de pb
        par ligne de mp
    """
    mp = get_taux_pb(mp, ref_taux_pb)
    mp['pb_contract'] = np.maximum(0, mp['base_prod_fi']) * mp['tx_pb']
    # Calcul du supplement de revalorisation par produit : difference entre la pb contract et la revalo TMG
    mp['add_pb_contract'] = np.maximum(0, mp['pb_contract'] - mp['rev_stock_brut'])
    # Chargements sur encours
    # Calcul des chargements sur encours theoriques par produit
    mp['ch_enc_th'] = mp['enc_charg_base_th'] + mp['enc_charg_rmin_th']
    mp['tx_enc_moy'] = mp['ch_enc_th'] / mp['base_enc_th']
    mp['ch_enc_ap_pb_contr'] = mp['ch_enc_th'] + mp['add_pb_contract'] * mp['tx_enc_moy']
    # Calcul de la revalorisation nette sans application de limite sur les chargements sur encours
    mp['rev_stock_nette_contr'] = mp['rev_stock_brut'] + mp['add_pb_contract'] - mp['ch_enc_ap_pb_contr']
    #return mp.drop(['pb_contract', 'add_pb_contract','ch_enc_th','tx_enc_moy'], axis=1)
    return mp

def finance_tx_cible_ppb(mp, ppb):
    # Calcul du besoin additionnelle à la ppb 8 ans individuelle pour atteindre la revalorisation au taux cible
    bes_add_ind = np.maximum(mp['bes_tx_cible'] - mp['ppb8_ind'], 0) - mp['rev_stock_nette_contr']
    bes_add = np.sum(bes_add_ind)
    if (bes_add<0):
        ppb.dotation_ppb(-bes_add)
        # Application de la revalorisation par produit
        mp['rev_stock_nette_cible'] = np.maximum(mp['bes_tx_cible'], mp['ppb8_ind'])
    else:
        ppb.reprise_ppb(bes_add)
        # Application de la revalorisation par produit
        mp['rev_stock_nette_cible'] = mp['rev_stock_nette_contr'] + mp['ppb8_ind']
    return mp, ppb

def finance_tx_cible_margefi(mp, df_ref_revalo):
    mp = get_param_revalo(mp, df_ref_revalo)
    # Calcul du besoin additionnelle à la ppb 8 ans individuelle pour atteindre la revalorisation au taux cible
    bes_add_ind = mp['bes_tx_cible'] - mp['rev_stock_nette_cible']
    bes_add = np.sum(bes_add_ind)
    mp['marge_min'] = mp['pm_moy'] * mp['tx_marge_min']
    # Evaluation du montant que peut financer la marge de l'assureur
    finance_marg = np.maximum(0, mp['marge_fi'] - mp['marge_min']) # Montant pouvant etre utilise pour financer le besoin supplementaire de revalorisation
    if (bes_add<0):
        bes_finance = 0
        # Application de la revalorisation par produit
        mp['rev_stock_nette_cible'] = mp['bes_tx_cible']
    else:
        # Besoin finance par la marge
        bes_finance = np.minimum(finance_marg, bes_add_ind)
        # Application de la revalorisation par produit
        mp['rev_stock_nette_cible'] = mp['rev_stock_nette_cible']
    mp['marge_fi'] = mp['marge_fi'] - bes_finance
    return mp

def finance_tx_cible_pmvl_action(mp, portefeuille_financier):
    """
        Methode permettant de determiner le financement d'une revalorisation au taux cible par une cession de plus-values latentes en actions
    """
    # Calcul du besoin additionnelle à la ppb 8 ans individuelle pour atteindre la revalorisation au taux cible
    bes_add_ind = mp['bes_tx_cible'] - mp['rev_stock_nette_cible']
    bes_add = np.sum(bes_add_ind)
    if (bes_add<0):
        # Mise a zero des PMVL liquidees
        pmvl_liq = 0
        # Application de la revalorisation par produit
        mp['rev_stock_nette_cible'] = mp['bes_tx_cible']
    else:
        # Application de la revalorisation par produit
        mp['rev_stock_nette_cible'] = mp['rev_stock_nette_cible']
        # Les PMVL sont calcules apres compensation
        if bes_add != 0:
            # Montant de PMVL qu'il faudrait liquider
            if np.sum(mp['base_prod_fi']) != 0:
                tx_pb_moy = np.sum(mp['base_prod_fi'] * mp['tx_pb'] / np.sum(mp['base_prod_fi']))
            else:
                tx_pb_moy = np.mean(mp['tx_pb'])
            pmvl_liq = np.sum(bes_add_ind) * 1 / tx_pb_moy # PMVL a liquider
        else:
            pmvl_liq = 0
        portefeuille_financier.realiser_les_pvl_action(pmvl_liq) # liquidation des PMVL action
    return mp, portefeuille_financier

def finance_contrainte_legale(mp,df_ref_revalo,ppb):
    """
        Methode permettant de calculer la contrainte legale de participation aux benefices et de l'appliquer si necessaire pour accroitre la revalorisation.
    """
    mp['ind_result_tech'] = (mp['resultat_technique'] > 0)
    mp['solde_pb'] = mp['taux_pb_fi'] * mp['base_prod_fi'] + mp['taux_pb_tech'] * mp['resultat_technique'] * mp['ind_result_tech'] + \
            mp['resultat_technique'] * (1 - mp['ind_result_tech']) - mp['it_tech_stock']
    # Report du solde negatif
    mp['solde_pb'] = mp['solde_pb'] + mp['solde_pb_regl']*(mp['solde_pb']/np.sum(mp['solde_pb']))
    # Mise a jour du solde de PB minimale
    if(np.sum(mp['solde_pb']) < 0):
        df_ref_revalo['solde_pb_regl'] = np.sum(mp['solde_pb'])
    else:
        df_ref_revalo['solde_pb_regl'] = 0
    # Calcul de la revalorisation legale
    rev_reg = np.maximum(0, mp['solde_pb'])
    # Montant de PB deja distribue
    tot_rev_assure = np.sum(mp['rev_stock_nette_cible'] + mp['rev_prest_nette']) + np.sum(ppb.dotations)
    # Reprise additionnelle
    suppl = np.maximum(0, (np.sum(rev_reg) - tot_rev_assure))
    # Marge financier finale
    mp['marge_fi'] = mp['marge_fi'] - suppl * mp['marge_fi']/np.sum(mp['marge_fi'])
    # Dotation
    ppb.dotation_ppb(suppl)
    # Revalorisation residuelle du stock
    add_rev_regl = max(0, suppl - np.sum(ppb.dotations))
    # Calcul de la revalorisation du stock nette apres prise en compte de la contrainte legale
    # L'attribution s'effectue uniquement sur les produits modelises.
    sum_base_fin = np.sum(mp['base_prod_fi'])
    if sum_base_fin != 0:
        mp['rev_stock_nette_regl'] = mp['rev_stock_nette_cible'] + add_rev_regl * mp['base_prod_fi'] / sum_base_fin
    else: # Repartition au prorara si la base financiere est nulle
        mp['rev_stock_nette_regl'] = mp['rev_stock_nette_cible'] + add_rev_regl * 1 / len(mp['base_prod_fi'])
    # On calcule le montant de revalorisation nette au dela de la revalorisation nette au taux minimum.
    mp['add_rev_nette_stock'] = mp['rev_stock_nette_cible'] - (mp['rev_stock_brut'] - mp['ch_enc_th'])
    # Permet de gerer le cas ou la revalo nette apres PB est positive et la revalo nette avant est negative
    ind = ((mp['rev_stock_brut'] - mp['ch_enc_th']) <= 0) & (mp['rev_stock_nette_cible'] > 0)
    mp['add_rev_nette_stock'] = np.maximum(0, mp['add_rev_nette_stock']) * (1 - ind) + mp['rev_stock_nette_cible'] * ind
    return mp, df_ref_revalo, ppb

def moteur_politique_revalo(mp, df_ref_revalo, ref_taux_pb, ppb, portefeuille_financier):
    """
        Methode permettant de d'appliquer l'ensemble de la politique de revalorisation d'un assureur.
    """
    # Calcul et recuperation du taux de rendement de l'actif
    tra = portefeuille_financier.calcul_tra()
    # Etape 1 : Evaluation de la base de produits financier
    mp = calcul_base_produit_financier(tra, ppb, mp)
    # Etape 2 : Calcul de la PB contractuelle
    mp = calcul_pb_contractuelle(mp, ref_taux_pb)
    # Etape 3 : Financement de la revalorisation du stock et prestations au TMG par la PPB
    ppb.reprise_ppb(np.sum(mp['bes_tmg_prest']+mp['bes_tmg_stock']))
    # Etape 4 : Application de la regle des 8 ans
    #ppb8ans = ppb.appliquer_ppb_8ans()
    #mp['ppb8_ind'] = ppb8ans * mp['pm_fin']/(np.sum(mp['pm_fin']))
    mp, ppb = attribution_ppb_8ans(mp, ppb)
    # Etape 5 : Financement du taux cible par la PPB
    mp, ppb = finance_tx_cible_ppb(mp, ppb)
    # Etape 6 : Financement du taux cible par des cessions de PVL actions
    mp, portefeuille_financier = finance_tx_cible_pmvl_action(mp, portefeuille_financier)
    # Etape 7 : Financement du taux cible par la marge de l'assureur
    # Calcul de la marge financiere de l'assureur
    mp = calcul_marge_financiere(mp, ppb)
    # Financement du taux cible par la marge de l'assureur
    mp = finance_tx_cible_margefi(mp, df_ref_revalo)
    # Etape 8 : Application de la contrainte de PB reglementaire
    mp, df_ref_revalo, ppb = finance_contrainte_legale(mp,df_ref_revalo,ppb)
    return mp, df_ref_revalo, ppb, portefeuille_financier