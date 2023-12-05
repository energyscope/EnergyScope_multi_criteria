import pandas as pd

# Charger le premier fichier Excel
df1 = pd.read_excel(r'C:\Users\ghuysn\GIT_Projects\EnergyScope_multi_criteria\energyscope\preprocessing\lca_pre\lca_outdated.xlsx', header=None, names=['Technology', 'Value'])
# Charger le deuxième fichier Excel
df2 = pd.read_excel(r'C:\Users\ghuysn\GIT_Projects\EnergyScope_multi_criteria\energyscope\preprocessing\lca_pre\lca_processed.xlsx', header=None, names=['Technology', 'Value'])

# Convertir le deuxième DataFrame en dictionnaire
dict_df2 = dict(zip(df2['Technology'], df2['Value']))

# Parcourir le premier DataFrame et mettre à jour les valeurs si la technologie correspond
for index, row in df1.iterrows():
    tech = row['Technology']
    if tech in dict_df2:
        df1.at[index, 'Value'] = dict_df2[tech]
    else:
        print(f"La technologie '{tech}' n'est pas trouvée dans le deuxième fichier.")

# Sauvegarder le résultat dans un nouveau fichier Excel
df1.to_excel('lca_updated.xlsx', index=False, header=False)
