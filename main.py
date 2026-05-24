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
    activities: List[str]
    include_supplements: bool # Νέο πεδίο: True ή False

@app.get("/")
def read_root():
    return {"status": "Smart Nutrition API is running!"}

@app.post("/generate-plan")
def generate_plan(profile: UserProfile):
    try:
        activities_str = ", ".join(profile.activities) if profile.activities else "Καμία συγκεκριμένη"
        supplements_instruction = (
            "Πρότεινε κατάλληλα, ασφαλή και νόμιμα συμπληρώματα διατροφής (π.χ. πρωτεΐνη ορού γάλακτος, κρεατίνη, ωμέγα-3, πολυβιταμίνες) που θα υποβοηθήσουν τον στόχο του."
            if profile.include_supplements else 
            "ΜΗΝ συμπεριλάβεις καθόλου συμπληρώματα διατροφής στο πλάνο."
        )

        prompt = f"""
        Λειτούργησε ως κορυφαίος κλινικός διατροφολόγος και έμπειρος personal trainer. 
        Δημιούργησε ένα εξαιρετικά αναλυτικό, πλήρες και επαγγελματικό 7ήμερο πλάνο διατροφής και προπόνησης βασισμένο στα εξής στοιχεία:
        - Φύλο: {profile.gender}
        - Βάρος: {profile.weight} kg
        - Ύψος: {profile.height} cm
        - Ηλικία: {profile.age} ετών
        - Στόχος: {profile.goal}
        - Επίπεδο Γενικής Δραστηριότητας: {profile.activity_level}
        - Συγκεκριμένα Αθλήματα/Δραστηριότητες: {activities_str}
        - Τύπος Διατροφής: {profile.diet_type}
        - Περιορισμοί / Αλλεργίες: {profile.allergies}
        
        Οδηγία για Συμπληρώματα: {supplements_instruction}

        Το πλάνο ΠΡΕΠΕΙ να περιλαμβάνει αυστηρά τα παρακάτω ενότητες δομημένα με καθαρούς τίτλους:
        1. ΥΠΟΛΟΓΙΣΜΟΣ ΘΕΡΜΙΔΩΝ & MACROS: Στόχος θερμίδων και γραμμάρια (Πρωτεΐνες, Υδατάνθρακες, Λίπη).
        2. ΑΝΑΛΥΤΙΚΟ 7ΗΜΕΡΟ ΠΛΑΝΟ ΔΙΑΤΡΟΦΗΣ: Για κάθε ημέρα (Ημέρα 1 έως 7), με όλα τα γεύματα.
        3. ΕΒΔΟΜΑΔΙΑΙΟ ΠΡΟΓΡΑΜΜΑ ΠΡΟΠΟΝΗΣΗΣ: Πλάνο 7 ημερών που ενσωματώνει τα αθλήματα {activities_str}.
        4. ΠΡΟΤΑΣΕΙΣ ΣΥΜΠΛΗΡΩΜΑΤΩΝ (Αν ζητήθηκε): Δοσολογία και χρονισμός.
        5. ΛΙΣΤΑ SUPER MARKET & ΚΟΣΤΟΣ: Φτιάξε μια συγκεντρωτική λίστα αγορών για όλη την εβδομάδα (π.χ. Πηγές Πρωτεΐνης, Υδατανθράκων, Λαχανικά/Φρούτα). Δίπλα από κάθε βασικό τρόφιμο βάλε μια ενδεικτική τιμή αγοράς σε Ευρώ (€) με βάση την ελληνική αγορά (π.χ. Κοτόπουλο στήθος 1kg: ~9.00€). Στο τέλος, υπολόγισε και εμφάνισε το ΣΥΝΟΛΙΚΟ ΕΚΤΙΜΩΜΕΝΟ ΚΟΣΤΟΣ της εβδομάδας για το super market.
        
        Δώσε τεράστια έμφαση στη λεπτομέρεια, την ακρίβεια των τιμών και την επαγγελματική δομή.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Είσαι ένας εξειδικευμένος fitness & nutrition coach που μιλάει ελληνικά, γράφει αναλυτικά 7ήμερα προγράμματα και δίνει τεράστια έμφαση στη λεπτομέρεια και το σωστό κοστολόγιο."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000, # Αυξήθηκε για να χωρέσει τη λίστα super market
            temperature=0.7
        )
        
        return {"plan": response.choices[0].message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))