.echo on
.mode column
.headers on
.nullvalue NULL
.bail on
PRAGMA foreign_keys = ON;


BEGIN  TRANSACTION;
DELETE from user_day;
DELETE from diary_entry;
DELETE from custom_trackers;
DELETE from custom_trackers_data;
DELETE from personal_trackers_data;
DELETE from work_trackers_data;
DELETE FROM sqlite_sequence WHERE name="user_day";
DELETE FROM sqlite_sequence WHERE name="diary_entry";
DELETE FROM sqlite_sequence WHERE name="custom_trackers";
DELETE FROM sqlite_sequence WHERE name="custom_trackers_data";
DELETE FROM sqlite_sequence WHERE name="personal_trackers_data";
DELETE FROM sqlite_sequence WHERE name="work_trackers_data";
COMMIT;

WITH data as (
    SELECT json_each.value AS item
    FROM json_each(readfile('./dummy_data/custom_trackers.json'))
)
INSERT INTO custom_trackers (id, user_id, name, data_type, unit, enum_options, is_active, created_at, modified_at)
SELECT
    json_extract(item, '$.id'),
    json_extract(item, '$.user_id'),
    json_extract(item, '$.name'),
    json_extract(item, '$.data_type'),
    json_extract(item, '$.unit'),
    json_extract(item, '$.enum_options'),
    json_extract(item, '$.is_active'),
    json_extract(item, '$.created_at'),
    json_extract(item, '$.modified_at')
FROM data;
SELECT * FROM custom_trackers;

WITH data as (
    SELECT json_each.value AS item
    FROM json_each(readfile('./dummy_data/custom_trackers_data.json'))
)
INSERT INTO custom_trackers_data (id, user_id, tracker_id, date, value, created_at, modified_at)
SELECT
    json_extract(item, '$.id'),
    json_extract(item, '$.user_id'),
    json_extract(item, '$.tracker_id'),
    json_extract(item, '$.date'),
    json_extract(item, '$.value'),
    json_extract(item, '$.created_at'),
    json_extract(item, '$.modified_at')
FROM data;
SELECT * FROM custom_trackers_data;

WITH data as (
    SELECT json_each.value AS item
    FROM json_each(readfile('./dummy_data/diary_entry.json'))
)
INSERT INTO diary_entry (id, user_id, date, short_note, long_entry, attachments, created_at, modified_at)
SELECT
    json_extract(item, '$.id'),
    json_extract(item, '$.user_id'),
    json_extract(item, '$.date'),
    json_extract(item, '$.short_note'),
    json_extract(item, '$.long_entry'),
    json_extract(item, '$.attachments'),
    json_extract(item, '$.created_at'),
    json_extract(item, '$.modified_at')
FROM data;
SELECT * FROM diary_entry;

WITH data as (
    SELECT json_each.value AS item
    FROM json_each(readfile('./dummy_data/personal_trackers_data.json'))
)
INSERT INTO personal_trackers_data (id, user_id, date, wakeup_time, sleep_time, screen_time, water_intake, exercise, outgoing, mood, created_at, modified_at)
SELECT
    json_extract(item, '$.id'),
    json_extract(item, '$.user_id'),
    json_extract(item, '$.date'),
    json_extract(item, '$.wakeup_time'),
    json_extract(item, '$.sleep_time'),
    json_extract(item, '$.screen_time'),
    json_extract(item, '$.water_intake'),
    json_extract(item, '$.exercise'),
    json_extract(item, '$.outgoing'),
    json_extract(item, '$.mood'),
    json_extract(item, '$.created_at'),
    json_extract(item, '$.modified_at')
FROM data;
SELECT * FROM personal_trackers_data;

WITH data as (
    SELECT json_each.value AS item
    FROM json_each(readfile('./dummy_data/work_trackers_data.json'))
)
INSERT INTO work_trackers_data (id, user_id, date, commute_time, return_time, break_time, given_work, completed_work, is_off, workload, created_at, modified_at)
SELECT
    json_extract(item, '$.id'),
    json_extract(item, '$.user_id'),
    json_extract(item, '$.date'),
    json_extract(item, '$.commute_time'),
    json_extract(item, '$.return_time'),
    json_extract(item, '$.break_time'),
    json_extract(item, '$.given_work'),
    json_extract(item, '$.completed_work'),
    json_extract(item, '$.is_off'),
    json_extract(item, '$.workload'),
    json_extract(item, '$.created_at'),
    json_extract(item, '$.modified_at')
FROM data;
SELECT * FROM work_trackers_data;


WITH data as (
    SELECT json_each.value AS item
    FROM json_each(readfile('./dummy_data/user_day.json'))
)
INSERT INTO user_day (
    id, user_id, date, diary_entry_id, personal_trackers_id, work_trackers_id, custom_tracker_data_list_ids, created_at, modified_at
)
SELECT
    json_extract(item, '$.id'),
    json_extract(item, '$.user_id'),
    json_extract(item, '$.date'),
    json_extract(item, '$.diary_entry_id'),
    json_extract(item, '$.personal_trackers_id'),
    json_extract(item, '$.work_trackers_id'),
    json_extract(item, '$.custom_tracker_data_list_ids'),
    json_extract(item, '$.created_at'),
    json_extract(item, '$.modified_at')
FROM data;
SELECT * FROM user_day;


