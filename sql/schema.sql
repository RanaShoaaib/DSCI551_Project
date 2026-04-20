DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS users;


CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    category TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    body TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    CHECK (status IN ('open', 'closed'))
);

CREATE INDEX idx_category_created ON items(category, created_at DESC);
CREATE INDEX idx_status ON items(status);