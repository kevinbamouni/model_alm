import os
import pandas as pd
import numpy as np
import json
from pathlib import Path

abs_path = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
results_global_projection = pd.read_csv(abs_path / "tests/output_test_data/mp_global_projection.csv", delimiter=",", decimal=".")

report_columns = ['t','pri_brut','pri_chgt','pri_net','enc_charg_stock','rach_charg','prest','dc',
'ech','rach_part','rach_tot','frais_fixe_enc','frais_fixe_prest','frais_fixe_prime','frais_var_enc',
'frais_var_prest','frais_var_prime','soc_stock_ap_pb','nb_sortie', 'nb_dc','nb_ech','nb_rach_tot','nb_contr_fin',
'pm_deb','pm_fin_ap_pb']

results_global_projection = results_global_projection.loc[:,report_columns]

# Chargement de l'allocaiton cible
report_json = abs_path / "run_tools/report.json"
with open(report_json) as json_file:
    report_rename = json.load(json_file)

results_global_projection = results_global_projection.rename(columns=report_rename, inplace=False)

# Rename : ancien nom : nouveau nom
results_global_projection = results_global_projection.groupby(by=["annee"]).sum()
results_global_projection = pd.pivot_table(data=results_global_projection, columns=["annee"], aggfunc=[np.sum])
results_global_projection.to_excel(abs_path / "tests/output_test_data/mp_global_projection_reporting.xlsx")