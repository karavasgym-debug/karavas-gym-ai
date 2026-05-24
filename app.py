import streamlit as st
import requests
import io
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

st.set_page_config(page_title="Smart Nutrition Coach - Karavas Gym", page_icon="🥑", layout="centered")

st.title("Smart Nutrition Coach 🥑")
st.subheader("Karavas Gym Fighting & Fitness")
st.write("Συμπλήρωσε τα στοιχεία σου για να λάβεις το εξατομικευμένο 7ήμερο πλάνο διατροφής & προπόνησης.")

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
        activity_level = st.selectbox(
            "Επίπεδο Γενικής Δραστηριότητας", 
            ["Καθιστική ζωή (γραφείο)", "Ήπια άσκηση (1-3 μέρες/βδομάδα)", "Έντονη άσκηση (4-7 μέρες/βδομάδα)"]
        )
        
    available_activities = [
        "Γυμναστήριο (Βάρη)", "Τρέξιμο / Jogging", "Κολύμβηση", "Ποδηλασία", 
        "Crossfit", "Ποδόσφαιρο", "Μπάσκετ", "Τένις", "Γιόγκα / Πιλάτες", 
        "Πολεμικές Τέχνες / BJJ", "Πεζοπορία (Hiking)"
    ]
    selected_activities = st.multiselect(
        "Επίλεξε αθλητικές δραστηριότητες (1 έως 3)", 
        options=available_activities,
        max_selections=3
    )
        
    allergies = st.text_input("Αλλεργίες / Τροφές που αποφεύγεις", value="Καμία")
    include_supplements = st.checkbox("Θέλω να συμπεριληφθούν προτάσεις για νόμιμα συμπληρώματα διατροφής 💊")
    
    submit_button = st.form_submit_button(label="Λήψη Πλάνου ✨")

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

def create_pdf(text_content):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
    styles = getSampleStyleSheet()
    
    greek_style = ParagraphStyle(
        'GreekStyle', parent=styles['Normal'], fontName='DejaVuSans', fontSize=11, leading=16, spaceAfter=10
    )
    
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

if submit_button:
    if not full_name.strip():
        st.error("Παρακαλώ συμπλήρωσε το Ονοματεπώνυμό σου!")
    elif not validate_email(user_email):
        st.error("Παρακαλώ βάλε ένα έγκυρο Email!")
    elif len(user_phone.strip()) < 10:
        st.error("Παρακαλώ βάλε ένα έγκυρο Κινητό Τηλέφωνο!")
    elif not selected_activities:
        st.warning("Παρακαλώ επίλεξε τουλάχιστον 1 αθλητική δραστηριότητα!")
    else:
        payload = {
            "gender": gender,
            "weight": weight,
            "height": height,
            "age": age,
            "goal": goal,
            "activity_level": activity_level,
            "diet_type": diet_type,
            "allergies": allergies,
            "activities": selected_activities,
            "include_supplements": include_supplements
        }
        
        with st.spinner("🔄 Το AI σχεδιάζει το πλάνο σου και καταχωρεί τα στοιχεία σου..."):
            try:
                # 1. Καταχώρηση στο Google Sheet
                from streamlit_gsheets import GSheetsConnection
                import pandas as pd
                from datetime import datetime
                
                conn = st.connection("gsheets", type=GSheetsConnection)
                
                # Διαβάζουμε τα υπάρχοντα δεδομένα
                existing_data = conn.read(ttl=0)
                
                # Φτιάχνουμε τη νέα γραμμή
                new_lead = pd.DataFrame([{
                    "Ημερομηνία": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Ονοματεπώνυμο": full_name,
                    "Email": user_email,
                    "Κινητό": user_phone,
                    "Στόχος": goal
                }])
                
                # Ενώνουμε τα δεδομένα και τα αποθηκεύουμε
                updated_data = pd.concat([existing_data, new_lead], ignore_index=True)
                conn.update(data=updated_data)
                
                # 2. Κλήση του Backend για το πλάνο
                BACKEND_URL = "https://karavas-api.onrender.com/generate-plan"
                response = requests.post(BACKEND_URL, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"Ευχαριστούμε {full_name}! Το πλάνο σου εκδόθηκε με επιτυχία! 🎉")
                    st.info("💡 Ένας προπονητής του Karavas Gym θα εξετάσει το πλάνο σου και θα επικοινωνήσει μαζί σου για μια δωρεάν λιπομέτρηση!")
                    st.markdown("---")
                    st.markdown(result["plan"])
                    
                    pdf_bytes = create_pdf(result["plan"])
                    st.download_button(
                        label="📥 Κατέβασμα Πλάνου σε PDF",
                        data=pdf_bytes,
                        file_name="karavas_gym_plan.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error(f"Σφάλμα Backend: {response.text}")
            except Exception as e:
                st.error(f"Σφάλμα κατά την καταχώρηση ή τη σύνδεση: {e}")