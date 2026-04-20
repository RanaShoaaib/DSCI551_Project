DROP TABLE IF EXISTS phones;

CREATE TABLE phones(
id SERIAL PRIMARY KEY,
name VARCHAR(30) UNIQUE NOT NULL,
manufacturer VARCHAR(30) NOT NULL,
price DECIMAL(6,2) CHECK(price > 0)
);

INSERT INTO phones(name, manufacturer, price) VALUES
('iphone 16','Apple',1100),
('galaxy s25','Samsung',1200),
('pixel 10','Google',999.99);