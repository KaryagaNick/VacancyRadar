CREATE TABLE IF NOT EXISTS vacancies (
    id BIGSERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    source_id TEXT NOT NULL,
    direction TEXT NOT NULL,
    search_query TEXT NOT NULL,
    name TEXT NOT NULL,
    company TEXT,
    region TEXT,
    location TEXT,
    remote BOOLEAN NOT NULL DEFAULT FALSE,
    remote_scope TEXT,
    timezone_restrictions TEXT,
    seniority TEXT,
    experience SMALLINT,
    salary_from NUMERIC(15, 2),
    salary_to NUMERIC(15, 2),
    currency VARCHAR(10),
    salary_period TEXT,
    employment TEXT,
    schedule TEXT,
    description TEXT,
    published_at DATE,
    expires_at DATE,
    loaded_at TIMESTAMPTZ NOT NULL,
    url TEXT NOT NULL,
    CONSTRAINT vacancies_source_id_unique UNIQUE (source, source_id)
);

CREATE INDEX IF NOT EXISTS vacancies_direction_idx
    ON vacancies (direction);

CREATE INDEX IF NOT EXISTS vacancies_published_at_idx
    ON vacancies (published_at DESC);
