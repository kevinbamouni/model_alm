
#%%
import pandas as pd
import numpy as np
from alm_actif.fonctionsfinance import valeur_marche_oblig, duration_obligatioin

# Variable à configurer :
Date_t0="31/12/2019" # Jour j de projection
N = 40 # Nombre d'années de projections
oblig_path = "/Users/kevinbamouni/OneDrive/Modele_ALM/input_test_data/ptf_oblig.csv"
action_path = "/Users/kevinbamouni/OneDrive/Modele_ALM/input_test_data/ptf_action.csv"
treso_path = "/Users/kevinbamouni/OneDrive/Modele_ALM/input_test_data/ptf_treso.csv"
immo_path = "/Users/kevinbamouni/OneDrive/Modele_ALM/input_test_data/ptf_immo.csv"

# Chargement des données ESG

# Chargement des input.
oblig = pd.read_csv(oblig_path) # model point
action = pd.read_csv(action_path) #table de mortalite
treso = pd.read_csv(treso_path) # loi de rachat
immo = pd.read_csv(immo_path) # referentiel de frais par produit

# %%

class portefeuille_financier():
    """"
        Class de portefeuille financier pour modelisation l'actif, sa projection et ses interaction
    """
    
    def __init__(self, portefeuille_action, portefeuille_oblig, portefeuille_immo, 
    portefeuille_treso, scena_eco_action, scena_eco_oblig, scena_eco_immo, scena_eco_treso, allocation_cible):
        self.portefeuile_action = portefeuille_action
        self.portefeuille_oblig = portefeuille_oblig
        self.portefeuille_immo = portefeuille_immo
        self.portefeuille_treso = portefeuille_treso

        self.scena_eco_action = scena_eco_action
        self.scena_eco_oblig = scena_eco_oblig
        self.scena_eco_immo = scena_eco_immo
        self.scena_eco_treso = scena_eco_treso
        
        self.allocation_courante = {}
        self.allocation_cible = allocation_cible

        self.reserve_capitalisation = 0

    def initialisation_action(df, t, df_rendement):
        """
            Fonction d'initialisaiton du portefeuille d'action en début de période de projection t
        """
        
        variables = ['num_mp', 'val_marche_fin', 'val_nc_fin', 'val_achat_fin', 'cessible',
        'nb_unit_fin', 'dur_det', 'pdd', 'num_index', 'div', 'ind_invest']
        
        if t==0 :
            df = df[:,variables] 
            df['t'] = t
            df = df.rename(columns={"val_marche": "val_marche_fin"})
            df = df.rename(columns={"val_nc": "val_nc_fin"})
            df = df.rename(columns={"val_achat": "val_achat_fin"})
            df = df.rename(columns={"nb_unit": "nb_unit_fin"})

        elif t == 1:
            df = df.loc[(df['t'] == (t-1)) & (df['dur_det'] < t), variables]
            df['t'] = t
            df['dur_det'] = df['dur_det'] + 1
            df['nb_unit_deb '] = df['nb_unit_fin']
            df = recup_rendement_action(df, df_rendement, t)

        elif t >= 2:
            df = df.loc[(df['t'] == (t-1)) & (df['dur_det'] < t), variables]
            df['t'] = t
            df['dur_det'] = np.maximum(0, df['dur_det'] - 1)
            df['nb_unit_deb '] = df['nb_unit_fin']
            df = recup_rendement_action(df, df_rendement, t)
    

    def veillissement_treso(self, t):
        """
            Vieillisement du portefeuille de trésorerie par projection 
            sur un an avec calcul du rendement
        """
        self.portefeuille_treso['t'] = t
        self.portefeuille_treso['rdt'] = (1 + self.scena_eco_treso.iloc[1,t]) / (1 + self.scena_eco_treso.iloc[1,t-1]) - 1
        self.portefeuille_treso['val_marche'] = self.portefeuille_treso['val_marche'] * self.portefeuille_treso['rdt'] 


    def veillissement_immo(self, t):
        """
            Vieillisement du portefeuille immobilier par projection 
            sur un an avec calcul des loyers versés et du rendement
        """
        self.portefeuille_immo['t'] = t
        self.portefeuille_immo['rdt'] = (self.scena_eco_immo.iloc[1,t] / self.scena_eco_immo.iloc[1,t-1]) / (1 + self.portefeuille_immo['loyer'] * self.portefeuille_immo['ind_invest']) - 1
        self.portefeuille_immo['loyer'] = self.portefeuille_immo['val_marche'] * np.sqrt(1 + self.portefeuille_immo['rdt']) * self.portefeuille_immo['loyer']
        self.portefeuille_immo['val_marche'] = self.portefeuille_immo['val_marche'] * self.portefeuille_immo['rdt'] 
        self.portefeuille_immo['dur_det'] = self.portefeuille_immo['dur_det'] + 1
        self.portefeuille_immo['pvl'] = self.portefeuille_immo.loc[self.portefeuille_immo['val_nc']<=self.portefeuille_immo['val_marche'],'val_marche'] - \
        self.portefeuille_immo.loc[self.portefeuille_immo['val_nc']>self.portefeuille_immo['val_marche'],'val_nc']
        self.portefeuille_immo['mvl'] = self.portefeuille_immo.loc[self.portefeuille_immo['val_nc']>self.portefeuille_immo['val_marche'],'val_marche'] - \
        self.portefeuille_immo.loc[self.portefeuille_immo['val_nc']<=self.portefeuille_immo['val_marche'],'val_nc']


    def veillissement_obligation(self, t):
        """
            Vieillisement du portefeuille obligation par projection 
            sur un an avec calcul des coupons versés et du rendement
        """
        self.portefeuille_oblig['t'] = t
        self.portefeuille_oblig['coupon'] = self.portefeuille_oblig['tx_coupon'] * self.portefeuille_oblig['nominal'] * self.portefeuille_oblig['par'] * self.portefeuille_oblig['nb_unit']  
        self.portefeuille_oblig['val_marche'] = self.portefeuille_oblig.apply(lambda row : valeur_marche_oblig(row['tx_coupon'], row['nominal'], row['courbe'], row['mat_res'], t), axis = 1)
        self.portefeuille_oblig['duration'] = self.portefeuille_oblig.apply(lambda row : duration_obligatioin(row['tx_coupon'], row['nominal'], row['courbe'], row['mat_res'], t), axis = 1)
        self.portefeuille_oblig['zspread'] = 0
        self.portefeuille_oblig['dur_det'] = self.portefeuille_oblig['dur_det'] + 1
        self.portefeuille_oblig['mat_res'] = self.portefeuille_oblig['mat_res'] + 1
        self.portefeuille_oblig['surcote_decote'] = (self.portefeuille_oblig['nominal'] - self.portefeuille_oblig['vnc']) / self.portefeuille_oblig['mat_res']
        self.portefeuille_oblig['pvl'] = self.portefeuille_oblig.loc[self.portefeuille_oblig['val_nc']<=self.portefeuille_oblig['val_marche'],'val_marche'] - \
            self.portefeuille_oblig.loc[self.portefeuille_oblig['val_nc']>self.portefeuille_oblig['val_marche'],'val_nc']
        self.portefeuille_oblig['mvl'] = self.portefeuille_oblig.loc[self.portefeuille_oblig['val_nc']>self.portefeuille_oblig['val_marche'],'val_marche'] - \
            self.portefeuille_oblig.loc[self.portefeuille_oblig['val_nc']<=self.portefeuille_oblig['val_marche'],'val_nc']
        


    def veillissement_action(self, t):
        """
            Vieillisement du portefeuille action par projection 
            sur un an avec calcul des dividendes versées et des du rendement
        """
        self.portefeuile_action['t'] = t
        self.portefeuile_action['rdt'] = (self.scena_eco_action.iloc[1,t] / self.scena_eco_action.iloc[1,t-1]) / (1 + self.portefeuile_action['div'] * self.portefeuile_action['ind_invest']) - 1
        self.portefeuile_action['dividende'] = self.portefeuile_action['val_marche'] * np.sqrt(1 + self.portefeuile_action['rdt']) * self.portefeuile_action['div']
        self.portefeuile_action['val_marche'] = self.portefeuile_action['val_marche'] * self.portefeuile_action['rdt'] 
        self.portefeuile_action['dur_det'] = self.portefeuile_action['dur_det'] + 1
        self.portefeuile_action['pvl'] = self.portefeuile_action.loc[self.portefeuile_action['val_nc']<=self.portefeuile_action['val_marche'],'val_marche'] - \
            self.portefeuile_action.loc[self.portefeuile_action['val_nc']>self.portefeuile_action['val_marche'],'val_nc']
        self.portefeuile_action['mvl'] = self.portefeuile_action.loc[self.portefeuile_action['val_nc']>self.portefeuile_action['val_marche'],'val_marche'] - \
            self.portefeuile_action.loc[self.portefeuile_action['val_nc']<=self.portefeuile_action['val_marche'],'val_nc']
        

    def reallocation_tactique(self):
        pass

    def calcu_allocation_courante(self):
        """
            Calcul allocation courante du portefeuille financier
        """
        self.allocation_courante  = {'somme_action': sum(self.portefeuile_action['val_marche']),
        'somme_oblig': sum(self.portefeuille_oblig['val_marche']),
        'somme_immo': sum(self.portefeuille_immo['val_marche']),
        'somme_treso': sum(self.portefeuille_treso['val_marche']),
        'propo_action': sum(self.portefeuile_action['val_marche']) / (sum(self.portefeuile_action['val_marche'])+sum(self.portefeuille_obli['val_marche'])+sum(self.portefeuille_immo['val_marche'])+sum(self.portefeuille_treso['val_marche'])),
        'propo_oblig': sum(self.portefeuille_oblig['val_marche']) / (sum(self.portefeuile_action['val_marche'])+sum(self.portefeuille_obli['val_marche'])+sum(self.portefeuille_immo['val_marche'])+sum(self.portefeuille_treso['val_marche'])),
        'propo_immo': sum(self.portefeuille_immo['val_marche']) / (sum(self.portefeuile_action['val_marche'])+sum(self.portefeuille_obli['val_marche'])+sum(self.portefeuille_immo['val_marche'])+sum(self.portefeuille_treso['val_marche'])),
        'propo_treso': sum(self.portefeuille_treso['val_marche']) / (sum(self.portefeuile_action['val_marche'])+sum(self.portefeuille_obli['val_marche'])+sum(self.portefeuille_immo['val_marche'])+sum(self.portefeuille_treso['val_marche'])),
        'total': sum(self.portefeuile_action['val_marche']) + sum(self.portefeuille_obli['val_marche']) + sum(self.portefeuille_immo['val_marche']) + sum(self.portefeuille_treso['val_marche']) }


    def calcul_de_reserve_capitation(self, t):
        self.reserve_capitalisation = max(self.reserve_capitalisation + pmvr_oblig, 0)

    def calcul_provision_risque_exigibilite(self, t):
        pass