from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from typing import List
import os

app = FastAPI(title="Smart Nutrition API")

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

class UserProfile(BaseModel):
    gender: str
    weight: float
    height: float
    age: int
    goal: str
    activity_level: str
    diet_type: str
    allergies: str
    activities: List[str] # Νέο πεδίο για τις αθλητικές δραστηριότητες

@app.get("/")
def read_root():
    return {"status": "Smart Nutrition API is running!"}

@app.post("/generate-plan")
def generate_plan(profile: UserProfile):
    try:
        # Μετατροπή της λίστας δραστηριοτήτων σε κείμενο
        activities_str = ", ".join(profile.activities) if profile.activities else "Καμία συγκεκριμένη"

        prompt = f"""
        Λειτούργησε ως κορυφαίος κλινικός διατροφολόγος και έμπειρος personal trainer. 
        Δημιούργησε ένα εξαιρετικά αναλυτικό, πλήρες και επαγγελματικό 7ήμερο πλάνο διατροφής και προπόνησης βασισμένο στα εξής στοιχεία:
        - Φύλο: {profile.gender}
        - Βάρος: {profile.weight} kg
        - Ύψος: {profile.height} cm
        - Ηλικία: {profile.age} ετών
        - Στόχος: {profile.goal}
        - Επίπεδο Γενικής Δραστηριότητας: {profile.activity_level}
        - Συγκεκριμένα Αθλήματα/Δραστηριότητες: {activities_str} (ΣΥΝΥΠΟΛΟΓΙΣΕ τα ενεργειακά και προπονητικά προαπαιτούμενα αυτών των αθλημάτων!)
        - Τύπος Διατροφής: {profile.diet_type}
        - Περιορισμοί / Αλλεργίες: {profile.allergies}
        
        Το πλάνο ΠΡΕΠΕΙ να περιλαμβάνει αυστηρά τα παρακάτω:
        1. ΥΠΟΛΟΓΙΣΜΟΣ ΘΕΡΜΙΔΩΝ & MACROS: Αναλυτικό στόχο θερμίδων και γραμμάρια (Πρωτεΐνες, Υδατάνθρακες, Λίπη), λαμβάνοντας υπόψη τις καύσεις από τα αθλήματα που επιλέχθηκαν ({activities_str}).
        2. ΑΝΑΛΥΤΙΚΟ 7ΗΜΕΡΟ ΠΛΑΝΟ ΔΙΑΤΡΟΦΗΣ: Για κάθε ημέρα ξεχωριστά (Ημέρα 1 έως Ημέρα 7), με Πρωινό, Μεσημεριανό, Δείπνο και Σνακ, ιδανικά χρονικά τοποθετημένα γύρω από τις αθλητικές δραστηριότητες.
        3. ΕΒΔΟΜΑΔΙΑΙΟ ΠΡΟΓΡΑΜΜΑ ΠΡΟΠΟΝΗΣΗΣ: Αναλυτικό πλάνο 7 ημερών που ενσωματώνει έξυπνα τα επιλεγμένα αθλήματα ({activities_str}) μαζί με τις απαραίτητες προπονήσεις ενδυνάμωσης, stretching ή ξεκούρασης.
        
        Δώσε έμφαση στη λεπτομέρεια και την επαγγελματική δομή.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Είσαι ένας εξειδικευμένος fitness & nutrition coach που μιλάει ελληνικά, γράφει αναλυτικά 7ήμερα προγράμματα και δίνει τεράστια έμφαση στη λεπτομέρεια."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2500,
            temperature=0.7
        )
        
        return {"plan": response.choices[0].message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))