import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

ENGINE = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/gdsc")

print("\n---- 3.1 Simple Retrieval : Drug Responses for a specific cell line ----")
COSMIC_ID = 683667 # any valid cosmic_id

query_simple = f"""
   SELECT d.drug_name , e.ln_ic50 , e.auc
   FROM experiment e 
   JOIN drug d ON e.drug_name = d.drug_name
   WHERE e.cosmic_id = {COSMIC_ID};"""

df_simple = pd.read_sql(query_simple,ENGINE)
print(df_simple)
print(f"Total rows: {len(df_simple)}")


print("\n---- 3.2 Join/Complex Retrieval : Average IC50 for a specific drug across breast cancer cell lines ----")
DRUG_NAME = "Camptothecin"  # any valid DRUG_NAME

query_join =  """
SELECT AVG(e.ln_ic50) AS avg_ic50
FROM experiment e 
JOIN  cell_line c ON e.cosmic_id = c.cosmic_id
WHERE e.drug_name = %(drug)s 
 AND c.tissue_descriptor_2 ILIKE '%%breast%%';"""
   
df_join = pd.read_sql(query_join , ENGINE , params = {"drug" : DRUG_NAME})
print(df_join)  

print("\n---- 3.3 Aggregation/Grouping : Top 10 drugs by average AUC ----")

query_top10 = """
SELECT drug_name, AVG(auc) AS avg_auc
FROM experiment
GROUP BY drug_name
ORDER BY avg_auc DESC
LIMIT 10;"""

df_top10 = pd.read_sql(query_top10 , ENGINE )
print(df_top10)

print("\n---- 3.4 Analytical Query : IC50 by pathway for leukemia cell lines (Box Plot) ----")

query_boxplot = """
SELECT dt.pathway, e.ln_ic50
FROM experiment e
JOIN cell_line c ON e.cosmic_id = c.cosmic_id
JOIN drug_target dt ON e.drug_name = dt.drug_name
WHERE c.tissue_descriptor_2 ILIKE %(tissue)s;"""

df_box = pd.read_sql(query_boxplot , ENGINE , params = {"tissue" : "%leukemia"})
df_box = df_box.dropna(subset=["pathway", "ln_ic50"])

plt.figure(figsize=(12,6))
df_box.boxplot(column="ln_ic50", by="pathway", rot=90)
plt.title("IC50 Distribution by Target Pathway (Leukemia Cell Lines)")
plt.suptitle("")
plt.ylabel("LN(IC50)")
plt.tight_layout()
plt.show()