import pandas as pd

def preprocess_data_lca(data_xlsx) :
    # Lire le fichier XLSX
    df = pd.read_excel(data_xlsx, header=[0, 1])
    # Supprimez les espaces vides dans les noms de colonnes
    df.columns = df.columns.map(lambda x: ' - '.join(x) if x[0] and x[1] else x[0])
    # Définissez la première ligne comme index (technologies)
    df.set_index(df.columns[0], inplace=True)
    # Supprimez les espaces vides dans les noms d'index
    df.index = df.index.str.strip()
    return df

# VALIDATION #
df_lca = preprocess_data_lca(r"C:\Users\ghuysn\GIT_Projects\EnergyScope_multi_criteria\Data\pLCA_processed.xlsx")

annee = '2035'
categorie_LCA = 'LCA_LANDUSE'
scenario = 'remind - SSP2-PkBudg1150'
resultats = {}

for technologie in df_lca.index:
    # Sélectionner la valeur pour la catégorie, l'année et la technologie spécifiques
    valeur = df_lca.loc[technologie][categorie_LCA + ' - ' + scenario + ' - ' + annee]
    # Ajouter la valeur au dictionnaire
    resultats[technologie] = valeur
    # Convertir le dictionnaire en DataFrame
    df_resultats = pd.DataFrame(resultats, index=[categorie_LCA])


df_resultats = pd.DataFrame(list(resultats.items()), columns=['Technology', categorie_LCA])
# Enregistrer les résultats dans un fichier XLSX
df_resultats.to_excel('lca_processed.xlsx', index=False)

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