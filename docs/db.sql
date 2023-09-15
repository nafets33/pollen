CREATE TABLE IF NOT EXISTS pollen_store (
    key TEXT PRIMARY KEY NOT NULL,
    data JSONB NOT NULL
)

ALTER TABLE pollen_store 
ADD COLUMN last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

CREATE OR REPLACE FUNCTION update_last_update_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_update = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_set_last_update
BEFORE INSERT OR UPDATE 
ON pollen_store
FOR EACH ROW 
EXECUTE FUNCTION update_last_update_column();
