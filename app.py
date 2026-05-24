import streamlit as st
import requests
import io
import re
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Smart Nutrition Coach - Karavas Gym", page_icon="🥑", layout="centered")

st.title("Smart Nutrition Coach 🥑")
st.markdown('<p style="font-size:20px; color:#gray; margin-top:-15px;">Karavas Gym Fighting & Fitness</p>', unsafe_allow_html=True)

# Δημιουργία Tabs για διαχωρισμό των λειτουργιών
tab1, tab2 = st.tabs(["✨ Δημιουργία Πλάνου", "📈 Tracking Προόδου & Check-in"])

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

def create_pdf(text_content):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
    styles = getSampleStyleSheet()
    greek_style = ParagraphStyle('GreekStyle', parent=styles['Normal'], fontName='DejaVuSans', fontSize=11, leading=16, spaceAfter=10)
    story = []
    lines = text_content.split('\n')
    for line in lines:
        clean_line = line.replace('**', '').replace('###', '').replace('##', '').replace('$', '').strip()
        if clean_line:
            clean_line = clean_line.replace('\\[', '').replace('\\]', '')
            p = Paragraph(clean_line, greek_style)
            story.append(p)
        else:
            story.append(Spacer(1, 10))
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# ==========================================
# TAB 1: ΔΗΜΙΟΥΡΓΙΑ ΠΛΑΝΟΥ (Lead Generation)
# ==========================================
with tab1:
    with st.form("nutrition_form"):
        st.markdown('<p style="font-size:18px; font-weight:bold; margin-bottom:0px;">1. Στοιχεία Επικοινωνίας (Για την αποστολή του πλάνου)</p>', unsafe_allow_html=True)
        col_lead1, col_lead2 = st.columns(2)
        with col_lead1:
            full_name = st.text_input("Ονοματεπώνυμο *")
            user_email = st.text_input("Email *")
        with col_lead2:
            user_phone = st.text_input("Κινητό Τηλέφωνο *")

        st.markdown("---")
        st.markdown('<p style="font-size:18px; font-weight:bold; margin-bottom:0px;">2. Φυσικά Χαρακτηριστικά & Στόχοι</p>', unsafe_allow_html=True)
        gender = st.radio("Φύλο", ["Άνδρας", "Γυναίκα"], horizontal=True)
        col1, col2 = st.columns(2)
        
        with col1:
            weight = st.number_input("Βάρος (kg)", min_value=30.0, max_value=200.0, value=75.0, step=0.1)
            height = st.number_input("Ύψος (cm)", min_value=100.0, max_value=250.0, value=175.0, step=1.0)
            age = st.number_input("Ηλικία", min_value=14, max_value=100, value=25, step=1)
        
        with col2:
            goal = st.selectbox("Στόχος", ["Απώλεια λίπους", "Μυϊκή υπερτροφία", "Συντήρηση / Σύσφιξη"])
            diet_type = st.selectbox("Τύπος Διατροφής", ["Ισορροπημένη (Balanced)", "Υψηλή σε Πρωτεΐνη (High Protein)", "Κετογονική (Keto)", "Χορτοφαγική (Vegetarian)", "Αυστηρά Χορτοφαγική (Vegan)"])
            activity_level = st.selectbox("Επίπεδο Γενικής Δραστηριότητας", ["Καθιστική ζωή (γραφείο)", "Ήπια άσκηση (1-3 μέρες/βδομάδα)", "Έντονη άσκηση (4-7 μέρες/βδομάδα)"])
            
        available_activities = ["Γυμναστήριο (Βάρη)", "Τρέξιμο / Jogging", "Κολύμβηση", "Ποδηλασία", "Crossfit", "Ποδόσφαιρο", "Μπάσκετ", "Τένις", "Γιόγκα / Πιλάτες", "Πολεμικές Τέχνες / BJJ", "Πεζοπορία (Hiking)"]
        selected_activities = st.multiselect("Επίλεξε αθλητικές δραστηριότητες (1 έως 3)", options=available_activities, max_selections=3)
            
        allergies = st.text_input("Αλλεργίες / Τροφές που αποφεύγεις", value="Καμία")
        include_supplements = st.checkbox("Θέλω να συμπεριληφθούν προτάσεις για νόμιμα συμπληρώματα διατροφής 💊")
        
        submit_button = st.form_submit_button(label="Λήψη Πλάνου ✨")

    if submit_button:
        if not full_name.strip() or not validate_email(user_email) or len(user_phone.strip()) < 10 or not selected_activities:
            st.error("Παρακαλώ συμπληρώστε σωστά όλα τα υποχρεωτικά πεδία!")
        else:
            payload = {"gender": gender, "weight": weight, "height": height, "age": age, "goal": goal, "activity_level": activity_level, "diet_type": diet_type, "allergies": allergies, "activities": selected_activities, "include_supplements": include_supplements}
            
            with st.spinner("🔄 Το AI σχεδιάζει το πλάνο σου και καταχωρεί τα στοιχεία σου..."):
                try:
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    existing_data = conn.read(ttl=0)
                    new_lead = pd.DataFrame([{
                        "Ημερομηνία": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Ονοματεπώνυμο": full_name,
                        "Email": user_email,
                        "Κινητό": user_phone,
                        "Στόχος": goal,
                        "Τύπος": "New Plan",
                        "Βάρος Check-in": weight
                    }])
                    updated_data = pd.concat([existing_data, new_lead], ignore_index=True)
                    conn.update(data=updated_data)
                    
                    BACKEND_URL = "https://karavas-api.onrender.com/generate-plan"
                    response = requests.post(BACKEND_URL, json=payload)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"Ευχαριστούμε {full_name}! Το πλάνο σου εκδόθηκε με επιτυχία! 🎉")
                        st.info("💡Αν θέλετε μπορείτε να επικοινωνήσετε μαζί μας για μια δωρεάν ενημέρωση!")
                        st.markdown("---")
                        st.markdown(result["plan"])
                        
                        pdf_bytes = create_pdf(result["plan"])
                        st.download_button(label="📥 Κατέβασμα Πλάνου σε PDF", data=pdf_bytes, file_name="karavas_gym_plan.pdf", mime="application/pdf")
                    else:
                        st.error(f"Σφάλμα Backend: {response.text}")
                except Exception as e:
                    st.error(f"Σφάλμα: {e}")

# ==========================================
# TAB 2: INTERACTIVE CHECK-IN & TRACKING
# ==========================================
with tab2:
    st.markdown("### 📈 Εβδομαδιαίο Check-in Προόδου")
    st.write("Βάλε το email σου για να καταγράψεις το τρέχον βάρος σου και να δεις το διάγραμμα της προόδου σου.")
    
    checkin_email = st.text_input("Δώσε το Email σου για αναζήτηση:")
    current_weight = st.number_input("Νέο Βάρος (kg):", min_value=30.0, max_value=200.0, value=75.0, step=0.1)
    
    btn_checkin = st.button("Καταχώρηση Νέου Βάρους ⚖️")
    
    if checkin_email:
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            df = conn.read(ttl=0)
            
            # Φιλτράρουμε τις καταχωρήσεις του συγκεκριμένου χρήστη
            user_history = df[df['Email'].str.strip().str.lower() == checkin_email.strip().lower()]
            
            if btn_checkin:
                # Αν πατήσει το κουμπί, αποθηκεύουμε τη νέα μέτρηση στο Google Sheet
                new_row = pd.DataFrame([{
                    "Ημερομηνία": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Ονοματεπώνυμο": user_history['Ονοματεπώνυμο'].iloc[0] if not user_history.empty else "Υπάρχων Πελάτης",
                    "Email": checkin_email.strip(),
                    "Κινητό": user_history['Κινητό'].iloc[0] if not user_history.empty else "-",
                    "Στόχος": user_history['Στόχος'].iloc[0] if not user_history.empty else "-",
                    "Τύπος": "Check-in",
                    "Βάρος Check-in": current_weight
                }])
                df_updated = pd.concat([df, new_row], ignore_index=True)
                conn.update(data=df_updated)
                st.success("Το νέο σου βάρος καταχωρήθηκε επιτυχώς! 🥳")
                # Ξαναδιαβάζουμε για να ανανεωθεί το γράφημα
                df = conn.read(ttl=0)
                user_history = df[df['Email'].str.strip().str.lower() == checkin_email.strip().lower()]

            if not user_history.empty:
                st.markdown("#### Η πορεία του βάρους σου:")
                
                # Προετοιμασία δεδομένων για το διάγραμμα
                # Μετατρέπουμε τη στήλη σε αριθμητική και καθαρίζουμε τυχόν κενά
                user_history = user_history.copy()
                user_history['Βάρος Check-in'] = pd.to_numeric(user_history['Βάρος Check-in'], errors='coerce')
                chart_data = user_history[['Ημερομηνία', 'Βάρος Check-in']].dropna()
                
                if not chart_data.empty:
                    # Ορίζουμε την ημερομηνία ως index για το γράφημα
                    chart_data = chart_data.set_index('Ημερομηνία')
                    st.line_chart(chart_data)
                    
                    # Μικρό AI/Ημι-αυτόματο Feedback
                    weights_list = chart_data['Βάρος Check-in'].tolist()
                    if len(weights_list) >= 2:
                        diff = weights_list[-1] - weights_list[-2]
                        if diff < 0:
                            st.info(f"📉 Μειώθηκε το βάρος σου κατά {abs(diff):.1f} kg από την προηγούμενη μέτρηση. Εξαιρετική δουλειά!")
                        elif diff > 0:
                            st.warning(f"📈 Το βάρος σου αυξήθηκε κατά {diff:.1f} kg. Μείνε πιστός στο πλάνο σου!")
                        else:
                            st.info("⚖️ Το βάρος σου παρέμεινε σταθερό. Η συνέπεια είναι το κλειδί!")
                else:
                    st.warning("Δεν βρέθηκαν έγκυρα δεδομένα βάρους για αυτό το email.")
            else:
                st.warning("Δεν βρέθηκε ιστορικό για αυτό το email. Σιγουρέψου ότι έκανες πρώτα 'Δημιουργία Πλάνου'.")
                
        except Exception as e:
            st.error(f"Σφάλμα κατά τη φόρτωση του ιστορικού: {e}")