import numpy as np
import pandas as pd
from pandas.core.indexes import base

def calcul_base_produit_financier(tra, ppb, mp):
    """
        Calcul de la base des produits financier attribuables aux PM
    """
    mp['base_prod_fi'] = (mp['pm_moy'] + np.sum(ppb.ppb_historique)*(mp['pm_moy']/np.sum(mp['pm_moy']))) * tra
    return mp

def calcul_marge_financiere(mp):
    # Calcul de la marge financiere avant revalorisation du stock
    # Retrait de la charge pour financement revalorisation des prestations
    # Ajout du financement venant de la PPB sur les TMG du stock et reprise pour taux cible
    mp['marge_fin'] = mp['base_prod_fi'] - \
                    mp['rev_prest_nette'] + mp['contrib_tmg_prest'] - \
                    mp['rev_stock_nette'] + mp['contrib_tmg_stock'] + \
                    mp['contrib_ppb_tx_cible']
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

def calcul_pb_contractuelle(mp, ref_taux_pb):
    """
        Fonction qui recupere les taux de pb contractuel par produit du referentiel de taux de pb par produit puis calcul les taux de pb
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
    mp['ch_enc_ap_pb_contr'] = mp['ch_enc_th'] + mp['add_pb_contr'] * mp['tx_enc_moy']
    # Calcul de la revalorisation nette sans application de limite sur les chargements sur encours
    mp['rev_stock_nette_contr'] = mp['rev_stock_brut'] + mp['add_pb_contr'] - mp['ch_enc_ap_pb_contr']
    #return mp.drop(['pb_contract', 'add_pb_contract','ch_enc_th','tx_enc_moy'], axis=1)
    return mp

    def finance_tx_cible_ppb():
        pass

def moteur_politique_revalo(mp, ref_taux_pb, ppb, portefeuille_financier, tx_frais_val_marche, tx_frais_produits, tx_charges_reserve_capi):
    tra = portefeuille_financier.calcul_tra(tx_frais_val_marche, tx_frais_produits, tx_charges_reserve_capi)
    # Etape 1 : Evaluation de la base de produits financier
    mp = calcul_base_produit_financier(tra, ppb, mp)
    # Etape 2 : Calcul de la PB contractuelle
    mp = calcul_pb_contractuelle(mp, ref_taux_pb)
    # Etape 3 : Financement de la revalorisation du stock et prestations au TMG par la PPB
    ppb = ppb.reprise_ppb(np.sum(mp['bes_tmg_prest']+mp['bes_tmg_prest']))
    # Etape 4 : Application de la regle des 8 ans
    ppb8ans = ppb.appliquer_ppb_8ans()
    mp['pp8_ind'] = ppb8ans * mp['pm_fin']/(np.sum(mp['pm_fin']))
    # Etape 5 : Financement du taux cible par la PPB
