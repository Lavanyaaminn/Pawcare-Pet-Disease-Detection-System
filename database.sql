-- ============================================================
-- PawCare – Pet Disease Detection System
-- Relational Database Schema
-- Database : pawcare_db
-- Engine   : InnoDB
-- Charset  : utf8mb4
-- ============================================================

USE pawcare_db;

-- Drop existing tables in reverse dependency order (safe re-run)
DROP TABLE IF EXISTS prediction_history;
DROP TABLE IF EXISTS disease_symptoms;
DROP TABLE IF EXISTS pets;
DROP TABLE IF EXISTS symptoms;
DROP TABLE IF EXISTS diseases;
DROP TABLE IF EXISTS users;


-- ============================================================
-- TABLE 1: users
-- Purpose: Stores registered pet owner accounts.
--          Each user can own multiple pets (one-to-many).
-- ============================================================
CREATE TABLE users (
    user_id     INT           NOT NULL AUTO_INCREMENT,
    full_name   VARCHAR(100)  NOT NULL,
    email       VARCHAR(100)  NOT NULL,
    password    VARCHAR(255)  NOT NULL,
    created_at  TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id),
    UNIQUE KEY uq_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
  COMMENT='Registered pet owner accounts';


-- ============================================================
-- TABLE 2: pets
-- Purpose: Stores individual pet profiles.
--          Each pet belongs to one user via user_id foreign key.
-- ============================================================
CREATE TABLE pets (
    pet_id      INT                                     NOT NULL AUTO_INCREMENT,
    user_id     INT                                     NOT NULL,
    pet_name    VARCHAR(100)                            NOT NULL,
    animal_type ENUM('Dog','Cat','Rabbit','Bird')       NOT NULL,
    breed       VARCHAR(100)                            DEFAULT NULL,
    age         INT                                     DEFAULT NULL,
    gender      ENUM('Male','Female')                   DEFAULT NULL,
    weight      DECIMAL(5,2)                            DEFAULT NULL,

    PRIMARY KEY (pet_id),

    CONSTRAINT fk_pets_user
        FOREIGN KEY (user_id)
        REFERENCES users (user_id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
  COMMENT='Pet profiles linked to their owners';


-- ============================================================
-- TABLE 3: diseases
-- Purpose: Master catalog of diseases grouped by animal type.
--          Used by the prediction engine and history records.
-- ============================================================
CREATE TABLE diseases (
    disease_id   INT                                    NOT NULL AUTO_INCREMENT,
    animal_type  ENUM('Dog','Cat','Rabbit','Bird')      NOT NULL,
    disease_name VARCHAR(150)                           NOT NULL,
    description  TEXT                                   DEFAULT NULL,
    treatment    TEXT                                   DEFAULT NULL,
    precautions  TEXT                                   DEFAULT NULL,

    PRIMARY KEY (disease_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
  COMMENT='Disease reference data by animal type';


-- ============================================================
-- TABLE 4: symptoms
-- Purpose: Master catalog of symptoms grouped by animal type.
--          Symptoms are linked to diseases via disease_symptoms.
-- ============================================================
CREATE TABLE symptoms (
    symptom_id   INT                                    NOT NULL AUTO_INCREMENT,
    symptom_name VARCHAR(100)                           NOT NULL,
    animal_type  ENUM('Dog','Cat','Rabbit','Bird')      NOT NULL,

    PRIMARY KEY (symptom_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
  COMMENT='Symptom reference data by animal type';


-- ============================================================
-- TABLE 5: disease_symptoms
-- Purpose: Junction (bridge) table for many-to-many relationship
--          between diseases and symptoms.
--          One disease can have many symptoms; one symptom can
--          appear in multiple diseases.
-- ============================================================
CREATE TABLE disease_symptoms (
    disease_id INT NOT NULL,
    symptom_id INT NOT NULL,

    PRIMARY KEY (disease_id, symptom_id),

    CONSTRAINT fk_disease_symptoms_disease
        FOREIGN KEY (disease_id)
        REFERENCES diseases (disease_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_disease_symptoms_symptom
        FOREIGN KEY (symptom_id)
        REFERENCES symptoms (symptom_id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
  COMMENT='Maps diseases to their related symptoms';


-- ============================================================
-- TABLE 6: prediction_history
-- Purpose: Logs every disease prediction made for a pet.
--          Stores which disease was predicted, confidence level,
--          and the date/time of prediction.
-- ============================================================
CREATE TABLE prediction_history (
    prediction_id    INT           NOT NULL AUTO_INCREMENT,
    pet_id             INT           NOT NULL,
    disease_id         INT           NOT NULL,
    confidence_score   DECIMAL(5,2)  DEFAULT NULL,
    prediction_date    TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (prediction_id),

    CONSTRAINT fk_prediction_history_pet
        FOREIGN KEY (pet_id)
        REFERENCES pets (pet_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_prediction_history_disease
        FOREIGN KEY (disease_id)
        REFERENCES diseases (disease_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
  COMMENT='Historical record of disease predictions per pet';
