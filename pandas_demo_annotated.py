import pandas as pd
import datetime


# goal: Calculate cost-per-person of fire damage for each province and year


## 1) Read fire damage data
fire_df = pd.read_csv('nfd-property-losses-from-fires-en-fr-3.csv', encoding='latin-1') # latin-1 encoding generally works for french characters.
# print(fire_df.head())

columns_to_drop = ['Année', 'Juridiction', 'ISO', 'Protection zone', 'Zone de protection', 'Dollars (Fr)', 'Data qualifier', 'Qualificatifs de données']
fire_df = fire_df.drop(columns_to_drop, axis=1) # axis=1 tells it to look at columns instead of rows (axis=0)
# print(fire_df.head())


## 2) Read population data
pop_df = pd.read_csv('population_transposed.csv', thousands=',')
# print(pop_df.head())


## 3) Create a year column in the population dataframe
pop_df['A NEW COLUMN'] = "skfsdlkjfbsdkjfb"
# print(pop_df.head())

pop_df = pop_df.drop("A NEW COLUMN", axis=1)

def year_and_quarter_to_year(year_and_quarter):
    # converts year and quarter to year
    year = year_and_quarter.split(" ")[1]
    year = int(year)
    return year    
# print(year_and_quarter_to_year("Q4 2005"))

pop_df['year'] = pop_df.apply(lambda x: year_and_quarter_to_year(x['Quarter']), axis=1)
pop_df = pop_df.drop("Quarter", axis=1)
# print(pop_df.head())


## 4) Average four quarters into a single year value in population dataframe
pop_df = pop_df.groupby('year').mean()
# print(pop_df.head())


## 5) Standardize province names across both files
fire_provs = fire_df['Jurisdiction'].unique()
pop_provs = pop_df.columns

# for prov in fire_provs:
    # if prov not in pop_provs:
        # print(prov)

# for prov in pop_provs:
    # if prov not in fire_provs:
        # print(prov)

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
# print(get_population_for_prov_and_year('Ontario', 2019))

fire_df['population'] = fire_df.apply(lambda x: get_population_for_prov_and_year(x['Jurisdiction'],x['Year']), axis=1)
# print(fire_df)


## 7) Calculate cost-per-person of fire damage for each province and year
fire_df['cost_per_person'] = fire_df['Dollars (En)']/fire_df['population']
# print(fire_df)

fire_df = fire_df[~fire_df['cost_per_person'].isnull()]
# print(fire_df)

fire_df = fire_df.sort_values('cost_per_person', ascending=False)
print(fire_df)


## 8) Save result to csv file
# fire_df.to_csv('fire_cost_per_person.csv', encoding='latin-1')