DROP TABLE IF EXISTS experiment CASCADE;
DROP TABLE IF EXISTS drug_synonym CASCADE;
DROP TABLE IF EXISTS drug_target CASCADE;
DROP TABLE IF EXISTS drug CASCADE;
DROP TABLE IF EXISTS cell_line CASCADE;
DROP TABLE IF EXISTS tissue_subtype CASCADE;


CREATE TABLE tissue_subtype (
    tissue_descriptor_2 TEXT PRIMARY KEY,
    tissue_descriptor_1 TEXT NOT NULL
);

CREATE TABLE cell_line (
    cosmic_id INTEGER PRIMARY KEY,
    cell_line_name TEXT NOT NULL,
    tissue_descriptor_2 TEXT NOT NULL,
    growth_properties TEXT,
    microsatellite_status TEXT,
    screen_medium TEXT,
    CONSTRAINT fk_cell_line_tissue
        FOREIGN KEY  (tissue_descriptor_2)
        REFERENCES tissue_subtype(tissue_descriptor_2)
);

CREATE TABLE drug(
    drug_name TEXT PRIMARY KEY,
    brand_name TEXT,
    action TEXT,
    clinical_stage TEXT
);

CREATE TABLE drug_target(
    drug_name TEXT NOT NULL,
    target TEXT NOT NULL,
    pathway TEXT NULL,
    PRIMARY KEY (drug_name , target),
    FOREIGN KEY (drug_name) REFERENCES drug(drug_name)
);

CREATE TABLE drug_synonym (
    drug_name TEXT NOT NULL,
    synonym TEXT NOT NULL,
    PRIMARY KEY (drug_name , synonym),
    FOREIGN KEY (drug_name) REFERENCES drug(drug_name)
);

CREATE TABLE experiment (
    cosmic_id INTEGER NOT NULL ,
    drug_name  TEXT NOT NULL,
    ln_ic50 NUMERIC NULL,
    auc NUMERIC NULL,
    PRIMARY KEY (cosmic_id , drug_name),
    FOREIGN KEY (cosmic_id) REFERENCES cell_line(cosmic_id),
    FOREIGN KEY (drug_name) REFERENCES drug(drug_name)
);


CREATE INDEX idx_experiment_cosmic_id ON experiment(cosmic_id);
CREATE INDEX idx_experiment_drug_name ON experiment(drug_name);
CREATE INDEX idx_cell_line_tissue2 ON cell_line(tissue_descriptor_2);