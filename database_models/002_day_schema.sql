-- ========================
-- CUSTOM TRACKERS DATA TABLE
-- ========================
DROP TABLE IF EXISTS custom_trackers_data;
CREATE TABLE custom_trackers_data(
    id INTEGER  PRIMARY KEY AUTOINCREMENT,
    "user_id"   TEXT    NOT NULL CHECK(typeof("user_id") = "text"),
    tracker_id  INTEGER NOT NULL,
    date        DATE NOT NULL,

    -- stored as TEXT for flexibility
    value TEXT,

    -- auto field
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, tracker_id, date),
    FOREIGN KEY (user_id) REFERENCES accounts(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (tracker_id) REFERENCES custom_trackers(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TRIGGER custom_trackers_data_updated
AFTER UPDATE ON custom_trackers_data
FOR EACH ROW
WHEN NEW.modified_at <= OLD.modified_at
BEGIN
    UPDATE custom_trackers_data
    SET modified_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

-- ========================
-- CUSTOM TRACKERS TABLE
-- ========================
DROP TABLE IF EXISTS custom_trackers;
CREATE TABLE custom_trackers(
    id INTEGER  PRIMARY KEY AUTOINCREMENT,
    "user_id"      TEXT    NOT NULL CHECK(typeof("user_id") = "text"),
    
    name TEXT NOT NULL,
    data_type TEXT NOT NULL CHECK(data_type IN (
        'number', 'text', 'boolean', 'time', 'enum'
    )),
    unit TEXT,
    enum_options TEXT,             -- JSON list for enum types ["Light","Medium","Hard"]
    is_active BOOLEAN DEFAULT 1,   -- when off will no longer show in trackers

    -- auto field
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, name),
    FOREIGN KEY (user_id) REFERENCES accounts(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TRIGGER custom_trackers_updated
AFTER UPDATE ON custom_trackers
FOR EACH ROW
WHEN NEW.modified_at <= OLD.modified_at
BEGIN
    UPDATE custom_trackers
    SET modified_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

-- ========================
-- WORK TRACKERS DATA TABLE
-- ========================
DROP TABLE IF EXISTS work_trackers_data;
CREATE TABLE work_trackers_data(
    id INTEGER  PRIMARY KEY AUTOINCREMENT,
    "user_id"      TEXT    NOT NULL CHECK(typeof("user_id") = "text"),
    date  DATE NOT NULL,
    
    -- time fields in 24 hrs clock
    commute_time TIME,
    return_time TIME,
    break_time TIME,

    -- numeric fields
    given_work INTEGER,
    completed_work INTEGER,
    is_off BOOLEAN,

    -- enums
    workload INTEGER CHECK (workload BETWEEN 0 AND 5),   -- 0=none, 1=Ehh, 2=ok, 3=usual, 4=tiring, 5=hectic

    -- auto field
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, date),
    FOREIGN KEY (user_id) REFERENCES accounts(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TRIGGER work_trackers_data_updated
AFTER UPDATE ON work_trackers_data
FOR EACH ROW
WHEN NEW.modified_at <= OLD.modified_at
BEGIN
    UPDATE work_trackers_data
    SET modified_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

-- ========================
-- PERSONAL TRACKERS DATA TABLE
-- ========================
DROP TABLE IF EXISTS personal_trackers_data;
CREATE TABLE personal_trackers_data(
    id INTEGER  PRIMARY KEY AUTOINCREMENT,
    "user_id"      TEXT    NOT NULL CHECK(typeof("user_id") = "text"),
    date  DATE NOT NULL,
    
    -- time fields in 24 hrs clock
    wakeup_time TIME,
    sleep_time TIME,
    screen_time TIME,

    -- numeric fields
    water_intake REAL,  -- in liters

    -- enums
    exercise INTEGER CHECK (exercise IN (0,1,2,3)),  -- 0=None, 1=Light, 2=Medium, 3=Heavy
    outgoing INTEGER CHECK (outgoing IN (0,1,2,3)),  -- 0=None, 1=Essentials, 2=Walk, 3=Enjoy
    mood     INTEGER CHECK (mood BETWEEN 0 AND 5),   -- 0=none, 1=bad, 2=not good, 3=neutral, 4=good, 5=amazing

    -- auto field
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, date),
    FOREIGN KEY (user_id) REFERENCES accounts(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TRIGGER trigger_personal_trackers_data_updated
AFTER UPDATE ON personal_trackers_data
FOR EACH ROW
WHEN NEW.modified_at <= OLD.modified_at
BEGIN
    UPDATE personal_trackers_data
    SET modified_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

-- ========================
-- DAIRY ENTRY TABLE
-- ========================
DROP TABLE IF EXISTS diary_entry;
CREATE TABLE diary_entry(
    id INTEGER  PRIMARY KEY AUTOINCREMENT,
    "user_id"      TEXT    NOT NULL CHECK(typeof("user_id") = "text"),
    date  DATE NOT NULL,
    short_note TEXT,
    long_entry TEXT,
    attachments TEXT NOT NULL DEFAULT '()',

    -- auto field
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, date),
    FOREIGN KEY (user_id) REFERENCES accounts(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TRIGGER trigger_diary_entry_updated
AFTER UPDATE ON diary_entry
FOR EACH ROW
WHEN NEW.modified_at <= OLD.modified_at
BEGIN
    UPDATE diary_entry
    SET modified_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

-- ========================
-- USER DAY TABLE
-- ========================
DROP TABLE IF EXISTS user_day;
CREATE TABLE user_day(
    id INTEGER  PRIMARY KEY AUTOINCREMENT,
    "user_id"      TEXT    NOT NULL CHECK(typeof("user_id") = "text"),
    date  DATE NOT NULL,

    -- Trackers field
    diary_entry_id INTEGER,
    personal_trackers_id INTEGER,
    work_trackers_id INTEGER,
    custom_tracker_data_list_ids TEXT NOT NULL DEFAULT '()',

    -- auto field
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, date),
    -- TODO: need to attach foreign keys
    FOREIGN KEY (user_id) REFERENCES accounts(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (diary_entry_id) REFERENCES diary_entry(id) ON DELETE SET NULL,
    FOREIGN KEY (personal_trackers_id) REFERENCES personal_trackers_data(id) ON DELETE SET NULL,
    FOREIGN KEY (work_trackers_id) REFERENCES work_trackers_data(id) ON DELETE SET NULL
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