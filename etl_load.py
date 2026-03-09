import re
import pandas as pd
from sqlalchemy import  text,create_engine

PATH_A = r"./GDSC2_fitted_dose_response_27Oct23.xlsx" 
PATH_B = r"./TableS1E.xlsx" 
PATH_C = r"./C_Preprocessed.xlsx"  

ENGINE = create_engine("postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/gdsc")

def clean_headers(df):
    df.columns = [
        re.sub(r"\s+", " ", str(c).replace("\n", " ")).strip()
        for c in df.columns]
    return df

#normalization
def norm_name(x):
    
    if x is None or (isinstance(x,float)and pd.isna(x)):
        return None
    
    s = str(x).strip().lower()
    s = re.sub(r"\s+" , " " , s )
    return s 


#strings to array
def split_csv_list(s):
    if s is None or (isinstance(s,float)and pd.isna(s)):
        return []
    return [p.strip() for p in re.split(r"[;,]", str(s)) if p.strip()]


def clear_tables():
    with ENGINE.begin() as con:
        con.execute(text("TRUNCATE TABLE experiment RESTART IDENTITY CASCADE;"))
        con.execute(text("TRUNCATE TABLE drug_synonym RESTART IDENTITY CASCADE;"))
        con.execute(text("TRUNCATE TABLE drug_target RESTART IDENTITY CASCADE;"))
        con.execute(text("TRUNCATE TABLE drug RESTART IDENTITY CASCADE;"))
        con.execute(text("TRUNCATE TABLE cell_line RESTART IDENTITY CASCADE;"))
        con.execute(text("TRUNCATE TABLE tissue_subtype RESTART IDENTITY CASCADE;"))


def load_tissue_subtype():
    
    df = pd.read_excel(PATH_B, sheet_name = 0, skiprows = 2)
    df = clean_headers(df)
    
    df = df.rename(columns={
        "GDSC Tissue descriptor 1": "tissue_descriptor_1",
        "GDSC Tissue descriptor 2": "tissue_descriptor_2",
    })
    
    df = df[["tissue_descriptor_2", "tissue_descriptor_1"]].dropna()
    df = df.drop_duplicates(subset=["tissue_descriptor_2"])
    
    with ENGINE.begin() as con:
        df.to_sql("tissue_subtype", con, if_exists="append", index=False, method="multi")

    print(f"Loaded tissue_subtype: {len(df)} rows")


def load_cell_lines():

    df = pd.read_excel(PATH_B, sheet_name = 0, skiprows = 2)
    df = clean_headers(df)

    df = df.rename(columns={
        "COSMIC identifier": "cosmic_id",
        "Sample Name": "cell_line_name",
        "GDSC Tissue descriptor 2": "tissue_descriptor_2",
        "Growth Properties": "growth_properties",
        "Microsatellite (MS) instability (I) Status = (S)table, (L)ow, (H)igh": "microsatellite_status",
        "Screen Medium": "screen_medium", 
    })

    keep = ["cosmic_id", "cell_line_name", "tissue_descriptor_2",
            "growth_properties", "microsatellite_status", "screen_medium"]
    
    #if something is missing,added as None
    for col in keep:
        if col not in df.columns:
            df[col] = None 
            
    df = df[keep].dropna(subset=["cosmic_id", "tissue_descriptor_2", "cell_line_name"]).copy()
    df["cosmic_id"] = df["cosmic_id"].astype(int)

    with ENGINE.begin() as con:
        df.to_sql("cell_line", con, if_exists="append", index=False, method="multi")

    print(f"Loaded cell_line: {len(df)} rows")
        

def load_drugs(engine):
     
    #drug names used in the experiment
    a = pd.read_excel(PATH_A , usecols = ["DRUG_NAME"])
    a = a.dropna(subset = ["DRUG_NAME"]).copy()
    a["drug_name"] = a["DRUG_NAME"].astype(str)
    a["drug_norm"] = a["drug_name"].apply(norm_name)
    a_drugs = a.drop_duplicates(subset=["drug_norm"])[["drug_name", "drug_norm"]]

    #read table C (Preprocessed)
    c = pd.read_excel(PATH_C , header = 2)
    
    #unuseful unnamed columns
    c = c.loc[:, ~c.columns.astype(str).str.startswith("Unnamed")].copy()
    
    c = c.rename(columns = {
        "Name": "drug_name",
        "Synonyms": "synonyms_raw",
        "Brand name": "brand_name",
        "Action": "action",
        "Clinical Stage": "clinical_stage",
        "Putative Target": "putative_target",
        "Targeted process/pathway": "pathway", 
    })
   
    c = c.dropna(subset=["drug_name"]).copy()
    c["drug_norm"] = c["drug_name"].apply(norm_name)
    c = c.drop_duplicates(subset=["drug_norm"], keep="first")
    
    #LEFT JOIN (A drugs) -> (C metadata)
    merged = a_drugs.merge(
        c[["drug_norm", "brand_name", "action", "clinical_stage", "synonyms_raw", "putative_target", "pathway"]],
        on="drug_norm",
        how="left"
    )
     
    #drug table
    drug_rows = merged[["drug_name", "brand_name", "action", "clinical_stage"]].copy()
    drug_rows = drug_rows.drop_duplicates(subset=["drug_name"])
    
    syn_rows = []
    tgt_rows = []
    
    for _, r in merged.iterrows():
        dn = r["drug_name"]
        
        for syn in split_csv_list(r.get("synonyms_raw", None)):
            syn_rows.append({"drug_name": dn, "synonym": syn})
            
        pathway = r.get("pathway", None)
        for tgt in split_csv_list(r.get("putative_target", None)):
            tgt_rows.append({"drug_name": dn, "target": tgt, "pathway": pathway})
            
      
    drug_syn_df = pd.DataFrame(syn_rows).drop_duplicates()
    drug_tgt_df = pd.DataFrame(tgt_rows).drop_duplicates()

    with engine.begin() as con:
     drug_rows.to_sql("drug", con, if_exists="append", index=False, method="multi")

     if len(drug_syn_df) > 0:
        drug_syn_df.to_sql("drug_synonym", con, if_exists="append", index=False, method="multi")

     if len(drug_tgt_df) > 0:
        drug_tgt_df.to_sql("drug_target", con, if_exists="append", index=False, method="multi")

    print(f"Loaded drug (from A): {len(drug_rows)} rows")
    print(f"Loaded drug_synonym: {len(drug_syn_df)} rows")
    print(f"Loaded drug_target: {len(drug_tgt_df)} rows")



def load_experiment():
    usecols = ["COSMIC_ID", "DRUG_NAME", "LN_IC50", "AUC"]
    df = pd.read_excel(PATH_A , usecols = usecols)
    
    df = df.rename(columns={
        "COSMIC_ID": "cosmic_id",
        "DRUG_NAME": "drug_name",
        "LN_IC50": "ln_ic50",
        "AUC": "auc",
    })
    
    df = df.dropna(subset=["cosmic_id", "drug_name"]).copy()
    df["cosmic_id"] = df["cosmic_id"].astype(int)
    df["drug_name"] = df["drug_name"].astype(str)
    
    df = df.drop_duplicates(subset=["cosmic_id", "drug_name"], keep="first")
    
    with ENGINE.begin() as con:
     valid_drugs = pd.read_sql("SELECT drug_name FROM drug", con)

    df = df.merge(valid_drugs, on="drug_name", how="inner")

    with ENGINE.begin() as con:
     df.to_sql("experiment", con, if_exists="append", index=False, method="multi")

    print(f"Loaded experiment: {len(df)} rows")


def main():
    clear_tables()
    load_tissue_subtype()
    load_cell_lines()
    load_drugs(ENGINE)
    load_experiment()
    print("ETL complete")


if __name__ == "__main__":
    main()   