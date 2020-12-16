import pandas as pd
import numpy as np

# Variable à configurer :
Date_t0="31/12/2019" # Jour j de projection
N = 40 # Nombre d'années de projections
oblig_path = "/Users/kevinbamouni/OneDrive/Modele_ALM/ptf_oblig.csv"
action_path = "/Users/kevinbamouni/OneDrive/Modele_ALM/ptf_action.csv"
treso_path = "/Users/kevinbamouni/OneDrive/Modele_ALM/ptf_treso.csv"
immo_path = "/Users/kevinbamouni/OneDrive/Modele_ALM/ptf_immo.csv"

# Chargement des données ESG


# Chargement des input.
oblig = pd.read_csv(oblig_path) # model point
action = pd.read_csv(action_path) #table de mortalite
treso = pd.read_csv(treso_path) # loi de rachat
immo = pd.read_csv(immo_path) # referentiel de frais par produit
