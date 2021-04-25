import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline

"""
    Bibiliotheques de fonctions
"""

def valeur_marche_oblig(tx_coupon, nominal, courbe, maturite, t):
    """
        Calcul de la valeur de marche de l'obligation, avec interpolation de la courbe taux zero par spline cubique.

        :param tx_coupon: taux de coupon
        :param nominal: montant du nominal de l'obligation
        :param courbe: courbe des taux
        :param maturite: maturité de l'obligation
        :param t:

        :returns: valeur de marché d'une obligation
    """
    cs = CubicSpline(x = np.array(courbe.loc[:,'maturities']), y = np.array(courbe.loc[:,'rates']))
    crb_taux = np.apply_along_axis(cs, 0, np.arange(0.5, maturite, 1, dtype=np.float))
    return np.sum(tx_coupon * nominal * (1 / np.power((1 + crb_taux), np.arange(0.5, maturite, 1, dtype=np.float)))) + (nominal / np.power((1 + 0.025), maturite))


def duration_obligatioin(tx_coupon, nominal, courbe, maturite, t):
    """ 
        Calcul de la duration de l'obligation, avec interpolation de la courbe taux zero par spline cubique.
        Utilise la fonction *valeur_marche_oblig*

        :param tx_coupon: taux de coupon
        :param nominal: montant du nominal de l'obligation
        :param courbe: courbe des taux
        :param maturite: maturité de l'obligation
        :param t:

        :returns: valeur de duration d'une obligation
    """
    cs = CubicSpline(x = np.array(courbe.loc[:,'maturities']), y = np.array(courbe.loc[:,'rates']))
    crb_taux = np.apply_along_axis(cs, 0, np.arange(0.5, maturite, 1, dtype=np.float))
    return (np.sum(tx_coupon * nominal * np.arange(0.5, maturite, 1, dtype=np.float) * (1 / np.power((1 + crb_taux), np.arange(0.5, maturite, 1, dtype=np.float)))) + (nominal / np.power((1 + 0.025), maturite))) / valeur_marche_oblig(tx_coupon, nominal, courbe, maturite, t)