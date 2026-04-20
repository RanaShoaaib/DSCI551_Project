INSERT INTO users(name, created_at)
SELECT
    first_names[(floor(random() * array_length(first_names, 1)) + 1)::int]
    || ' ' ||
    last_names[(floor(random() * array_length(last_names, 1)) + 1)::int],
    NOW() - interval '30 days' - (random() * interval '30 days')
FROM generate_series(1, 100),
(
    SELECT
        ARRAY[
            'John','Mary','Peter','Lisa','Anna','David','Sarah','Michael','Emma','Daniel',
            'James','Olivia','Noah','Sophia','William','Ava','Benjamin','Mia','Lucas','Grace'
        ] AS first_names,
        ARRAY[
            'Smith','Johnson','Brown','Taylor','Anderson','Thomas','Jackson','White','Harris','Martin',
            'Lee','Clark','Lewis','Walker','Hall','Allen','Young','King','Scott','Green'
        ] AS last_names
) AS name_pool;


INSERT INTO items(user_id, category, status, created_at, title, body)
SELECT
    user_id,
    CASE
        WHEN r < 0.70 THEN 'traffic'
        WHEN r < 0.90 THEN 'crime'
        WHEN r < 0.98 THEN 'maintenance'
        ELSE 'miscellaneous'
    END,
    CASE
        WHEN s < 0.80 THEN 'open'
        ELSE 'closed'
    END,
    created_at,
    title,
    body
FROM (
    SELECT
        (floor(random() * 100) + 1)::int AS user_id,
        random() AS r,
        random() AS s,
        NOW() - (random() * interval '30 days') AS created_at,
        'title_' || gs::text AS title,
        md5(random()::text) AS body
    FROM generate_series(1, 50000) AS gs
) AS item_data;