import pandas as pd
import datetime


## 1) Read fire damage data
fire_df = pd.read_csv('nfd-property-losses-from-fires-en-fr-3.csv', encoding='latin-1') # latin-1 encoding generally works for french characters.
columns_to_drop = ['Année', 'Juridiction', 'ISO', 'Protection zone', 'Zone de protection', 'Dollars (Fr)', 'Data qualifier', 'Qualificatifs de données']
fire_df = fire_df.drop(columns_to_drop, axis=1) # axis=1 tells it to look at columns instead of rows (axis=0)


## 2) Read population data
pop_df = pd.read_csv('population_transposed.csv', thousands=',')


## 3) Create a year column in the population dataframe
def year_and_quarter_to_year(year_and_quarter):
    # converts year and quarter to year
    year = year_and_quarter.split(" ")[1]
    year = int(year)
    return year    
pop_df['year'] = pop_df.apply(lambda x: year_and_quarter_to_year(x['Quarter']), axis=1)
pop_df = pop_df.drop("Quarter", axis=1)


## 4) Average four quarters into a single year value in population dataframe
pop_df = pop_df.groupby('year').mean()


## 5) Standardize province names across both files
pop_df = pop_df.rename(columns={"Northwest Territories 5": "Northwest Territories"})


## 6) Move population data to fire dataframe
def get_population_for_prov_and_year(prov, year):
    if prov not in pop_df.columns:
        return None
    year_row = pop_df[pop_df.index==year]
    if year_row.empty:
        return None
    population = year_row[prov].values[0]
    return population
fire_df['population'] = fire_df.apply(lambda x: get_population_for_prov_and_year(x['Jurisdiction'],x['Year']), axis=1)


## 7) Calculate cost-per-person of fire damage for each province and year
fire_df['cost_per_person'] = fire_df['Dollars (En)']/fire_df['population']
fire_df = fire_df[~fire_df['cost_per_person'].isnull()]
fire_df = fire_df.sort_values('cost_per_person', ascending=False)


## 8) Save result to csv file
fire_df.to_csv('fire_cost_per_person.csv', encoding='latin-1')