import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Karavas Gym - AI Coach", page_icon="💪", layout="centered")

# Αρχικοποίηση OpenAI Client (Απευθείας στο Frontend)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("Karavas Gym AI Coach 🥑💪")
st.write("Καλώς ήρθες στον ψηφιακό Coach του Karavas Gym. Συμπλήρωσε τα στοιχεία σου για να λάβεις το εξατομικευμένο σου πλάνο.")

# Φόρμα Εισαγωγής Στοιχείων
with st.form("nutrition_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        weight = st.number_input("Βάρος (kg)", min_value=30.0, max_value=200.0, value=75.0, step=0.1)
        height = st.number_input("Ύψος (cm)", min_value=100.0, max_value=250.0, value=175.0, step=1.0)
        age = st.number_input("Ηλικία", min_value=14, max_value=100, value=25, step=1)
    
    with col2:
        goal = st.selectbox("Στόχος", ["Απώλεια λίπους", "Μυϊκή υπερτροφία", "Συντήρηση / Σύσφιξη"])
        activity_level = st.selectbox(
            "Επίπεδο Δραστηριότητας", 
            ["Καθιστική ζωή (γραφείο)", "Ήπια άσκηση (1-3 μέρες/βδομάδα)", "Έντονη άσκηση (4-7 μέρες/βδομάδα)"]
        )
        training_type = st.selectbox("Είδος Προπόνησης", ["Προπόνηση με Βάρη (Gym)", "Brazilian Jiu-Jitsu (BJJ) / MMA", "Calisthenics", "Cardio / Τρέξιμο"])
    
    submit_button = st.form_submit_button(label="Δημιουργία Πλάνου ✨")

if submit_button:
    with st.spinner("Ο Coach του Karavas Gym δημιουργεί το 7ήμερο πλάνο σου..."):
        try:
            # Μαθηματικοί Υπολογισμοί
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
            
            activity_multipliers = {
                "Καθιστική ζωή (γραφείο)": 1.2,
                "Ήπια άσκηση (1-3 μέρες/βδομάδα)": 1.375,
                "Έντονη άσκηση (4-7 μέρες/βδομάδα)": 1.55
            }
            multiplier = activity_multipliers.get(activity_level, 1.2)
            tdee = bmr * multiplier
            
            if "Απώλεια" in goal:
                target_calories = tdee - 500
                macro_notes = "Υψηλή πρωτεΐνη (2g ανά kg βάρους), ελεγχόμενος υδατάνθρακας, καλά λιπαρά."
            elif "Υπερτροφία" in goal:
                target_calories = tdee + 300
                macro_notes = "Πρωτεΐνη στο 1.8-2g ανά kg βάρους, υψηλός υδατάνθρακας για ενέργεια."
            else:
                target_calories = tdee
                macro_notes = "Ισορροπημένη κατανομή (40% Υδατάνθρακες, 30% Πρωτεΐνη, 30% Λίπη)."

            prompt = f"""
            Λειτούργησε ως Elite αθλητικός διατροφολόγος και Head Coach του Karavas Gym.
            Ασκούμενος: {weight}kg | {height}cm | {age} ετών.
            Στόχος: {goal} | Προπόνηση: {training_type}
            Θερμίδες Στόχου: {round(target_calories)} kcal ({macro_notes})

            Δημιούργησε ένα υπερ-αναλυτικό πλάνο σε 3 ενότητες:
            ## 1. ΜΑΚΡΟΘΡΕΠΤΙΚΑ ΣΥΣΤΑΤΙΚΑ
            Γραμμάρια για Πρωτεΐνη, Υδατάνθρακες, Λίπη για τις {round(target_calories)} θερμίδες.
            
            ## 2. ΠΛΑΝΟ ΔΙΑΤΡΟΦΗΣ 7 ΗΜΕΡΩΝ (ΔΕΥΤΕΡΑ ΕΩΣ ΚΥΡΙΑΚΗ)
            Αναλυτικό μενού μέρα προς μέρα (Πρωινό, Μεσημεριανό, Σνακ, Δείπνο) με ποικιλία.
            
            ## 3. ΟΛΟΚΛΗΡΩΜΕΝΟ ΑΣΚΗΣΙΟΛΟΓΙΟ
            Εβδομαδιαίο πρόγραμμα για '{training_type}'. Συγκεκριμένες ασκήσεις (5-7 ανά ημέρα), sets, reps, ξεκούραση και σημειώσεις τεχνικής.
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Είσαι ο Head Coach του Karavas Gym. Απαντάς με κορυφαίο επαγγελματισμό και χρησιμοποιείς πλούσιο Markdown (πίνακες, έντονα γράμματα, λίστες)."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            plan_output = response.choices[0].message.content
            
            st.success("Το πλάνο σου είναι έτοιμο! 🎉")
            
            tab1, tab2 = st.tabs(["📊 Μεταβολικοί Δείκτες", "📝 Ολοκληρωμένο Πλάνο"])
            with tab1:
                st.markdown("### Στατιστικά Μεταβολισμού")
                st.info(f"**Βασικός Μεταβολισμός (BMR):** {round(bmr)} θερμίδες")
                st.warning(f"**Θερμίδες Συντήρησης (TDEE):** {round(tdee)} θερμίδες")
                st.success(f"**Ημερήσιος Στόχος Θερμίδων:** {round(target_calories)} θερμίδες")
            with tab2:
                st.markdown(plan_output)
                st.markdown("---")
                st.download_button(
                    label="📥 Κατέβασε το Πλάνο σου (TXT)",
                    data=plan_output,
                    file_name="karavas_gym_plan.txt",
                    mime="text/plain"
                )
        except Exception as e:
            st.error(f"Σφάλμα κατά τη δημιουργία: {e}")