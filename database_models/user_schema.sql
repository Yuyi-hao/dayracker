-- Account Table
DROP TABLE IF EXISTS accounts;

CREATE TABLE accounts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE NOT NULL ,
    email TEXT UNIQUE NOT NULL CHECK (email LIKE '%_@__%.__%'),
    password TEXT NOT NULL,
    "username" TEXT UNIQUE NOT NULL  CHECK(typeof("username") = "text" AND length("username") <= 100),

    -- auto field
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Location Table
DROP TABLE IF EXISTS locations;

CREATE TABLE locations(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    country TEXT NOT NULL,

    -- auto field
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (city, country)
);

-- Profile Table
DROP TABLE IF EXISTS user_profiles;

CREATE TABLE user_profiles(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    "user_id"      TEXT    NOT NULL UNIQUE CHECK(typeof("user_id") = "text"),
    "first_name"   TEXT    NOT NULL    CHECK(typeof("first_name") = "text" AND length("first_name") <= 100),
    "last_name"    TEXT                CHECK(typeof("last_name") = "text" AND length("last_name") <= 100),
    profile_pic    TEXT,
    date_of_birth  DATE,
    location_id    INTEGER,

    -- auto field
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES accounts(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (location_id) REFERENCES locations(id)  ON DELETE SET NULL
);


--- Triggers to update modified at

-- Accounts  
CREATE TRIGGER trigger_accounts_updated
AFTER UPDATE ON accounts
FOR EACH ROW
WHEN NEW.modified_at <= OLD.modified_at
BEGIN
    UPDATE accounts
    SET modified_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

-- User Profiles
CREATE TRIGGER trigger_user_profiles_updated
AFTER UPDATE ON user_profiles
FOR EACH ROW
WHEN NEW.modified_at <= OLD.modified_at
BEGIN
    UPDATE user_profiles
    SET modified_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

-- Locations
CREATE TRIGGER trigger_locations_updated
AFTER UPDATE ON locations
FOR EACH ROW
WHEN NEW.modified_at <= OLD.modified_at
BEGIN
    UPDATE locations
    SET modified_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;
