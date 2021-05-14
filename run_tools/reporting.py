# %%
import os
import pandas as pd

# %%
abs_path = os.path.abspath(os.pardir)
results_global_projection = pd.read_csv(abs_path + "/tests/output_test_data/mp_global_projection.csv", delimiter=",", decimal=".")
results_global_projection.columns

report_results = ['t','arr_charg','chgt','credit','dc','debit',
'delta_pm','ech','enc_charg_stock',
'flux_fin_passif','frais','frais_fin','frais_fixe_enc',
'frais_fixe_prest','frais_fixe_prime','frais_var_enc',
'frais_var_prest','frais_var_prime','nb_contr_fin','nb_dc',
'nb_debut','nb_ech','nb_rach_tot','nb_sortie','pm_deb','pm_fin_ap_pb','prest',
'pri_brut', 'pri_chgt','pri_net','Produit','rach_charg','rach_part','rach_tot','rente',
'resultat','simulation','soc_stock_ap_pb']

#results_global_projection.groupby()
#results_global_projection.to_csv(abs_path + "/tests/output_test_data/results_global_projection.csv")
#results_global_projection
# %%
