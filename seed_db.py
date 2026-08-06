import os
from dotenv import load_dotenv
import MySQLdb

load_dotenv()

# Connect to the database
conn = MySQLdb.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    passwd=os.getenv("MYSQL_PASSWORD"),
    db=os.getenv("MYSQL_DB")
)

cur = conn.cursor()

# Disable foreign key checks to safely clear references
cur.execute("SET FOREIGN_KEY_CHECKS = 0")

# Clear existing tables first to prevent duplication
cur.execute("DELETE FROM disease_symptoms")
cur.execute("DELETE FROM symptoms")
cur.execute("DELETE FROM diseases")

# Reset auto-increments
cur.execute("ALTER TABLE diseases AUTO_INCREMENT = 1")
cur.execute("ALTER TABLE symptoms AUTO_INCREMENT = 1")

# Re-enable foreign key checks
cur.execute("SET FOREIGN_KEY_CHECKS = 1")

# Seed data definition
# Format: { animal_type: [ { disease_name, description, treatment, precautions, symptoms: [symptom_names] } ] }
seed_data = {
    "Dog": [
        {
            "disease_name": "Parvovirus",
            "description": "A highly contagious viral disease that causes severe gastrointestinal illness. It is extremely dangerous for young puppies.",
            "treatment": "Intensive supportive care including IV fluids, anti-nausea medications, antibiotics to prevent secondary infections, and nutritional support.",
            "precautions": "Ensure timely puppy vaccinations. Isolate infected dogs immediately, and sanitize contaminated surfaces with diluted bleach.",
            "symptoms": ["Vomiting", "Severe Diarrhea", "Lethargy", "Loss of Appetite"]
        },
        {
            "disease_name": "Canine Influenza",
            "description": "A highly contagious viral respiratory infection, also known as dog flu, affecting the respiratory tract of dogs.",
            "treatment": "Supportive care including rest, hydration, good nutrition, and anti-inflammatory medications. Antibiotics may be prescribed for secondary bacterial infections.",
            "precautions": "Vaccinate high-risk dogs (who visit kennels or dog parks frequently). Keep infected pets isolated from other dogs for at least 21 days.",
            "symptoms": ["Coughing", "Fever", "Runny Nose", "Lethargy"]
        }
    ],
    "Cat": [
        {
            "disease_name": "Feline Leukemia (FeLV)",
            "description": "A retrovirus that infects cats, severely impairing their immune system and predisposing them to cancer and other chronic infections.",
            "treatment": "No cure exists. Treatment focuses on supportive care, routine veterinary visits, prompt use of antibiotics for secondary infections, and dietary support.",
            "precautions": "Keep cats indoors to avoid exposure. Vaccinate cats that are at higher risk. Test new cats before introducing them to household companions.",
            "symptoms": ["Weight Loss", "Fever", "Lethargy", "Poor Coat Condition", "Loss of Appetite"]
        },
        {
            "disease_name": "Cat Flu (FURI)",
            "description": "Upper respiratory tract infection caused by herpesvirus or calicivirus, common in multi-cat environments.",
            "treatment": "Nasal decongestants, antibiotics for secondary infections, eye drops for discharge, feeding warming aromatic foods, and keeping face/nose clean.",
            "precautions": "Keep vaccinations up to date. Quarantine infected cats. Maintain a clean, stress-free environment.",
            "symptoms": ["Sneezing", "Runny Nose", "Fever", "Eye Discharge"]
        }
    ],
    "Rabbit": [
        {
            "disease_name": "Myxomatosis",
            "description": "A severe viral infection caused by the myxoma virus, primarily spread through biting insects like fleas and mosquitoes.",
            "treatment": "Supportive care (hydration, syringe-feeding, pain relief). The prognosis is unfortunately poor for unvaccinated rabbits.",
            "precautions": "Vaccinate rabbits annually. Install insect screens on outdoor cages and use rabbit-safe flea preventatives.",
            "symptoms": ["Swollen Eyes", "Fever", "Lethargy", "Discharge from Nose"]
        }
    ],
    "Bird": [
        {
            "disease_name": "Psittacosis (Parrot Fever)",
            "description": "A bacterial zoonotic infection caused by Chlamydia psittaci. It can be transmitted from infected pet birds to humans.",
            "treatment": "A course of antibiotic treatment, typically doxycycline, administered in water, food, or via injection under veterinary guidance.",
            "precautions": "Avoid buying birds from crowded or unhygienic facilities. Quarantine new birds for at least 30 days. Wear masks when cleaning cages of infected birds.",
            "symptoms": ["Feather Plucking", "Runny Nose", "Lethargy", "Loss of Appetite", "Diarrhea"]
        }
    ]
}

# Insert records
for animal_type, diseases in seed_data.items():
    for d in diseases:
        # Insert disease
        cur.execute(
            "INSERT INTO diseases (animal_type, disease_name, description, treatment, precautions) VALUES (%s, %s, %s, %s, %s)",
            (animal_type, d["disease_name"], d["description"], d["treatment"], d["precautions"])
        )
        disease_id = cur.lastrowid
        
        for symptom_name in d["symptoms"]:
            # Check if symptom exists for this type
            cur.execute("SELECT symptom_id FROM symptoms WHERE symptom_name = %s AND animal_type = %s", (symptom_name, animal_type))
            row = cur.fetchone()
            if row:
                symptom_id = row[0]
            else:
                # Insert symptom
                cur.execute("INSERT INTO symptoms (symptom_name, animal_type) VALUES (%s, %s)", (symptom_name, animal_type))
                symptom_id = cur.lastrowid
            
            # Map disease to symptom
            cur.execute("INSERT INTO disease_symptoms (disease_id, symptom_id) VALUES (%s, %s)", (disease_id, symptom_id))

conn.commit()
cur.close()
conn.close()
print("Database seeded successfully with diseases and symptoms!")
