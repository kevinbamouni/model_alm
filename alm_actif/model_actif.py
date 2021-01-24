
#%%
import pandas as pd
import numpy as np
import json
from fonctionsfinance import valeur_marche_oblig, duration_obligatioin



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

        self.plus_moins_value_realised = 0
        self.pmvr_oblig = 0
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
        self.portefeuille_immo['pvl'] = self.portefeuille_immo.apply(lambda row : row['val_marche']-row['val_nc'] if row['val_marche']>row['val_nc'] else 0, axis = 1)
        self.portefeuille_immo['mvl'] = self.portefeuille_immo.apply(lambda row : row['val_marche']-row['val_nc'] if row['val_marche']<=row['val_nc'] else 0, axis = 1)


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
        self.portefeuille_oblig['pvl'] = self.portefeuille_oblig.apply(lambda row : row['val_marche']-row['val_nc'] if row['val_marche']>row['val_nc'] else 0, axis = 1)
        self.portefeuille_oblig['mvl'] = self.portefeuille_oblig.apply(lambda row : row['val_marche']-row['val_nc'] if row['val_marche']<=row['val_nc'] else 0, axis = 1)
        


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
        self.portefeuile_action['pvl'] = self.portefeuile_action.apply(lambda row : row['val_marche']-row['val_nc'] if row['val_marche']>row['val_nc'] else 0, axis = 1)
        self.portefeuile_action['mvl'] = self.portefeuile_action.apply(lambda row : row['val_marche']-row['val_nc'] if row['val_marche']<=row['val_nc'] else 0, axis = 1)
        

    def calcul_alloc_strateg_crt(self):
        """
            Calcul allocation courante du portefeuille financier
        """
        self.allocation_courante  = {'somme_vm_action': sum(self.portefeuile_action['val_marche']),
        'somme_vm_oblig': sum(self.portefeuille_oblig['val_marche']),
        'somme_vm_immo': sum(self.portefeuille_immo['val_marche']),
        'somme_vm_treso': sum(self.portefeuille_treso['val_marche']),
        'propor_action': sum(self.portefeuile_action['val_marche']) / (sum(self.portefeuile_action['val_marche'])+sum(self.portefeuille_obli['val_marche'])+sum(self.portefeuille_immo['val_marche'])+sum(self.portefeuille_treso['val_marche'])),
        'propor_oblig': sum(self.portefeuille_oblig['val_marche']) / (sum(self.portefeuile_action['val_marche'])+sum(self.portefeuille_obli['val_marche'])+sum(self.portefeuille_immo['val_marche'])+sum(self.portefeuille_treso['val_marche'])),
        'propor_immo': sum(self.portefeuille_immo['val_marche']) / (sum(self.portefeuile_action['val_marche'])+sum(self.portefeuille_obli['val_marche'])+sum(self.portefeuille_immo['val_marche'])+sum(self.portefeuille_treso['val_marche'])),
        'propor_treso': sum(self.portefeuille_treso['val_marche']) / (sum(self.portefeuile_action['val_marche'])+sum(self.portefeuille_obli['val_marche'])+sum(self.portefeuille_immo['val_marche'])+sum(self.portefeuille_treso['val_marche'])),
        'total_vm_portfi': sum(self.portefeuile_action['val_marche']) + sum(self.portefeuille_obli['val_marche']) + sum(self.portefeuille_immo['val_marche']) + sum(self.portefeuille_treso['val_marche']) }


    def allocation_strategique(self, alloc_strat_cible_portfi, portfi_de_reference):
        """
        L'allocation stratégique vise à créer une clé de répartition sur différentes classes d’actifs : actions, obligations, liquidités, etc

        Cette fonction permet de faire l'allocation strategique du portefeuille suite à l'evolution des valeurs de marchés des actifs à l'an t en fonction
        de l'allocation strategique cible. Après évaluation des écarts par rapport à l'allocation cible des opérations d'achats-ventes sont effectuées afin
        de correspondre à l'allocation cible.

        """
        self.calcul_alloc_strateg_crt()
        calcul_operation_alm_vm = {'action' : alloc_strat_cible_portfi["propor_action_cible"] * self.allocation_courante.total_vm_portfi - self.allocation_courante.somme_vm_action,
        'oblig' : alloc_strat_cible_portfi["propor_oblig_cible"] * self.allocation_courante.total_vm_portfi - self.allocation_courante.somme_vm_oblig,
        'immo' : alloc_strat_cible_portfi["propor_immo_cible"] * self.allocation_courante.total_vm_portfi - self.allocation_courante.somme_vm_immo,
        'treso' : alloc_strat_cible_portfi["propor_treso_cible"] * self.allocation_courante.total_vm_portfi - self.allocation_courante.somme_vm_treso}
        
        if calcul_operation_alm_vm > 0:
            self.acheter_des_actions()
        else if calcul_operation_alm_vm < 0:
            self.vendres_des_actions()
    
    def allocation_strategique(self):
        """
        L'allocation stratégique
            Cette première étape, appelée l’allocation stratégique, vise à créer une clé de répartition sur différentes classes d’actifs : actions, obligations, liquidités, etc
        """

    def calcul_reserve_capitation(self, t):
        pass


    def calcul_provision_risque_exigibilite(self, t):
        pass


    def acheter_des_actions(self, calcul_operation_alm_vm, portfi_de_reference):
        """
            Fonction permettant d'acheter des actions et de mettre le
            portfeuille action automatiquement à jour.
        """
        # 1 - Calcul du nombre a acheter
        # POINT IMPORTANT : RAPPEL DE CONVENTION LE NB_UNIT DU PTF_REFERENCE (portfi_de_reference) 
        # EST LA PROPORTION DE CHAQUE ACTIF DANS LE PTF DE REF ce qui permet de calculer la VM_achat/vente pour chaque ligne action du
        # ptf_action.
        portfi_de_reference["coef_multi_action"] = calcul_operation_alm_vm.action * portfi_de_reference["nb_unit"] / portfi_de_reference["val_marche"]
        portfi_de_reference["nb_unit"] = portfi_de_reference["coef_multi_action"]
        portfi_de_reference["val_nc"] = portfi_de_reference["coef_multi_action"] * portfi_de_reference["val_nc"]
        portfi_de_reference["val_achat"] = portfi_de_reference["coef_multi_action"] * portfi_de_reference["val_achat"]
        portfi_de_reference["val_marche"] = portfi_de_reference["coef_multi_action"] * portfi_de_reference["val_marche"]

        # 2 - Calcul du nombre a acheter
        self.portefeuile_action["nb_unit"] = self.portefeuile_action["nb_unit"] + portfi_de_reference["nb_unit"]
        self.portefeuile_action["val_nc"] = self.portefeuile_action["val_nc"] + portfi_de_reference["val_nc"]
        self.portefeuile_action["val_achat"] = self.portefeuile_action["val_achat"] + portfi_de_reference["val_achat"]
        self.portefeuile_action["val_marche"] = self.portefeuile_action["val_marche"] + portfi_de_reference["val_marche"]


    def vendres_des_actions(self, ptf_action, montant_a_vendre):
        """
            Fonction permettant de vendre des actions et de mettre le portefeuille action
            automatiquement à jour.
        """
        ptf_action["alloc"] = ptf_action["val_marche"] / np.sum(ptf_action["val_marche"]) 
        ptf_action["nb_to_sold"] = (ptf_action["alloc"] * montant_a_vendre) / (ptf_action["val_marche"] / ptf_action["nb_unit"])
        ptf_action["pct_to_sold"] = ptf_action["nb_to_sold"] / ptf_action["nb_unit"]

        self.plus_moins_value_realised = self.plus_moins_value_realised + np.sum((ptf_action["val_achat"] - ptf_action["val_nc"]) * ptf_action["pct_to_sold"])

        # Actualisation des données de portefeuille
        ptf_action["val_achat"] = ptf_action["val_achat"] * (1 - ptf_action["pct_to_sold"])
        ptf_action["val_marche"] = ptf_action["val_marche"] * (1 - ptf_action["pct_to_sold"])
        ptf_action["val_nc"] = ptf_action["val_nc"] *  (1 - ptf_action["pct_to_sold"])
        ptf_action["nb_unit"] = ptf_action["nb_unit"] * (1 - ptf_action["pct_to_sold"])


# Execution main :
if __name__ == "__main__":
    # execute only if run as a script

    # Variable à configurer :
    Date_t0="31/12/2019" # Jour j de projection
    N = 40 # Nombre d'années de projections
    oblig_path = "/Users/kevinbamouni/OneDrive/Modele_ALM/input_test_data/ptf_oblig.csv"
    action_path = "/Users/kevinbamouni/OneDrive/Modele_ALM/input_test_data/ptf_action.csv"
    treso_path = "/Users/kevinbamouni/OneDrive/Modele_ALM/input_test_data/ptf_treso.csv"
    immo_path = "/Users/kevinbamouni/OneDrive/Modele_ALM/input_test_data/ptf_immo.csv"

    alloc_strat_cible_portfi_path = "/Users/kevinbamouni/OneDrive/Modele_ALM/input_test_data/alloc_strat_cible_portfi.json"

    # Chargement des données ESG

    # Chargement des input.
    oblig = pd.read_csv(oblig_path) # model point
    action = pd.read_csv(action_path) #table de mortalite
    treso = pd.read_csv(treso_path) # loi de rachat
    immo = pd.read_csv(immo_path) # referentiel de frais par produit

    # read file
    with open(alloc_strat_cible_portfi_path, 'r') as myfile:
        data=myfile.read()
    alloc_strat_cible_portfi = json.loads(data)