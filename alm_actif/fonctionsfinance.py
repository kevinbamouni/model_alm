import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline

# %%
def valeur_marche_oblig(tx_coupon, nominal, courbe, maturite, t):
    """
        Calcul de la valeur de marche de l'obligation, avec interpolation de la courbe taux zero par spline cubique
    """
    cs = CubicSpline(x = courbe.iloc[:,1], y = courbe.iloc[:,t])
    crb_taux = np.apply_along_axis(cs, 0, np.arange(0.5, maturite, 1, dtype=np.float))
    return np.sum(tx_coupon * nominal * (1 / np.power((1 + crb_taux), np.arange(0.5, maturite, 1, dtype=np.float)))) + (nominal / np.power((1 + 0.025), maturite))


def duration_obligatioin(tx_coupon, nominal, courbe, maturite, t):
    """ 
                Calcul de la duration de l'obligation, avec interpolation de la courbe taux zero par spline cubique
    """
    cs = CubicSpline(x = courbe.iloc[:,1], y = courbe.iloc[:,t])
    crb_taux = np.apply_along_axis(cs, 0, np.arange(0.5, maturite, 1, dtype=np.float))
    return (np.sum(tx_coupon * nominal * np.arange(0.5, maturite, 1, dtype=np.float) * (1 / np.power((1 + crb_taux), np.arange(0.5, maturite, 1, dtype=np.float)))) + (nominal / np.power((1 + 0.025), maturite))) / valeur_marche_oblig(tx_coupon, nominal, courbe, maturite, t)