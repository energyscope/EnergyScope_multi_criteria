import pandas as pd

# Chargez les deux fichiers dans des DataFrames pandas
path = r'C:\Users\ghuysn\GIT_Projects\EnergyScope_multi_criteria\case_studies\Test_LCA_data_1\output\\'


df1 = pd.read_csv(path+'year_balance.txt', delimiter='\t')
df2 = pd.read_csv(path+'assets.txt', delimiter='\t')

#supprime les espaces dans les nom
df1['Tech'] = df1['Tech'].str.replace(r'\s+', '', regex=True)
df2['TECHNOLOGIES'] = df2['TECHNOLOGIES'].str.replace(r'\s+', '', regex=True)
df2.columns = df2.columns.str.strip()

# Extraire les colonnes de technologies
techs_file1 = set(df1['Tech'])
techs_file2 = set(df2['TECHNOLOGIES'])

# Trouver les technologies communes
common_techs = techs_file1.intersection(techs_file2)
# Créer un dataframe avec les technologies communes
df_common = df1[df1['Tech'].isin(common_techs)]

# Fusionner df_common avec df2 pour ajouter les valeurs lca_op
df_common = pd.merge(df_common, df2[['TECHNOLOGIES', 'lca_op']], left_on='Tech', right_on='TECHNOLOGIES', how='left')
# Supprimer les colonne dont on ne veut pas
df_common = df_common.drop(columns=['TECHNOLOGIES'])
df_common = df_common.drop(columns=['Unnamed: 30'])
#### Traitement des données

# Écrire les technologies communes dans un nouveau fichier
df_common.to_csv('tech_communes.txt', index=False)

# Créez une DataFrame pour stocker les informations résumées
df_summary = pd.DataFrame(columns=['Technologies', 'Quantite produite', 'Unite produite', 'Quantite consome', 'Unite consome'])

# Parcourez chaque ligne du DataFrame df_common
for index, row in df_common.iterrows():
    tech = row['Tech']

    # Sélectionnez les colonnes numériques (à partir de la deuxième colonne)
    values = pd.to_numeric(row[1:-1])  # Utilisez 'coerce' pour convertir les non-numériques en NaN

    # Vérifiez si toutes les valeurs sont NaN, si oui, ignorez cette ligne
    if values.isna().all():
        continue

    max_index = values.idxmax()
    max_value = values.max()
    min_index = values.idxmin()
    min_value = values.min()

    # Ajoutez ces informations à la DataFrame df_summary
    df_summary = pd.concat([df_summary, pd.DataFrame(
        {'Technologies': [tech], 'Quantite produite': [max_value], 'Unite produite': [max_index], 'Quantite consome': [min_value],
         'Unite consome': [min_index]})], ignore_index=True)
# Écrivez la DataFrame df_summary dans un nouveau fichier texte
df_summary.to_csv('tech_summary.txt', index=False)