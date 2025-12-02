-- ========================
-- USER DAY
-- ========================
DROP TABLE IF EXISTS user_day;
CREATE TABLE user_day(
    id INTEGER  PRIMARY KEY AUTOINCREMENT,
    "user_id"      TEXT    NOT NULL CHECK(typeof("user_id") = "text"),
    date  DATE NOT NULL,

    -- diary
    short_note TEXT NOT NULL,
    long_entry TEXT,

    -- auto field
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, date),
    FOREIGN KEY (user_id) REFERENCES accounts(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TRIGGER trigger_user_day_updated
AFTER UPDATE ON user_day
FOR EACH ROW
WHEN NEW.modified_at <= OLD.modified_at
BEGIN
    UPDATE user_day
    SET modified_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

-- ========================
-- TRACKER CATEGORY
-- ========================
DROP TABLE IF EXISTS tracker_category;
CREATE TABLE tracker_category(
    id INTEGER  PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,

    -- auto field
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER trigger_tracker_category_updated
AFTER UPDATE ON tracker_category
FOR EACH ROW
WHEN NEW.modified_at <= OLD.modified_at
BEGIN
    UPDATE tracker_category
    SET modified_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

-- ========================
-- TRACKER TYPE
-- ========================
DROP TABLE IF EXISTS tracker_type;
CREATE TABLE tracker_type(
    id INTEGER  PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,

    -- if user_id IS NULL → system tracker (basic/wellness)
    -- if user_id NOT NULL → belongs to a specific user
    "user_id"   TEXT CHECK("user_id" IS NULL OR typeof("user_id") = 'text'),

    name TEXT NOT NULL,
    data_type TEXT NOT NULL, -- "number", "text", "boolean", "time", "enum"
    unit TEXT,
    options TEXT,

    is_system BOOLEAN DEFAULT FALSE,

    -- auto field
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES accounts(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (category_id) REFERENCES tracker_category(id) ON DELETE NO ACTION
);

CREATE TRIGGER trigger_tracker_type_updated
AFTER UPDATE ON tracker_type
FOR EACH ROW
WHEN NEW.modified_at <= OLD.modified_at
BEGIN
    UPDATE tracker_type
    SET modified_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;



-- ========================
-- TRACKER ENTRIES
-- ========================
DROP TABLE IF EXISTS tracker_entries;
CREATE TABLE tracker_entries(
    id INTEGER  PRIMARY KEY AUTOINCREMENT,
    user_day_id INTEGER NOT NULL,
    tracker_type_id INTEGER NOT NULL,

    -- only one of these is used depending on tracker type
    value_number    REAL,
    value_text      TEXT,
    value_time      TEXT,     -- e.g. "07:30"
    value_boolean   INTEGER,  -- 0/1
    value_enum      TEXT,     -- must be one of tracker_type.options

    -- auto field
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_day_id) REFERENCES user_day(id) ON DELETE CASCADE,
    FOREIGN KEY (tracker_type_id) REFERENCES tracker_type(id)
);

CREATE TRIGGER trigger_tracker_entries_updated
AFTER UPDATE ON tracker_entries
FOR EACH ROW
WHEN NEW.modified_at <= OLD.modified_at
BEGIN
    UPDATE tracker_entries
    SET modified_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;


-- ========================
-- DEFAULT CATEGORY DATA
-- ========================

INSERT INTO tracker_category (name) VALUES
("basic"),
("work"),
("personal"),
("custom"),
("incident");


-- ========================
-- DEFAULT SYSTEM TRACKERS
-- ========================

INSERT INTO tracker_type (category_id, name, data_type, unit, is_system)
VALUES
((SELECT id FROM tracker_category WHERE name='basic'), 'Wakeup Time', 'time', NULL, 1),
((SELECT id FROM tracker_category WHERE name='basic'), 'Sleep Time', 'time', NULL, 1),
((SELECT id FROM tracker_category WHERE name='basic'), 'Water Intake', 'number', 'ml', 1),
((SELECT id FROM tracker_category WHERE name='basic'), 'Screen Time', 'number', 'hours', 1),
((SELECT id FROM tracker_category WHERE name='work'), 'Meetings', 'number', NULL, 1),
((SELECT id FROM tracker_category WHERE name='work'), 'Commute Time', 'number', 'minutes', 1),
((SELECT id FROM tracker_category WHERE name='personal'), 'Reading', 'number', 'minutes', 1);
