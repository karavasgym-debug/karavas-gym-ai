import streamlit as st
import requests
import io
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

st.set_page_config(page_title="Smart Nutrition Coach", page_icon="🥑", layout="centered")

st.title("Smart Nutrition Coach 🥑")
st.write("Συμπλήρωσε τα στοιχεία σου για να δημιουργήσουμε το ιδανικό πλάνο διατροφής και προπόνησης.")

# Σύνδεση με το Google Sheets (Χρησιμοποιεί τα secrets σου)
conn = st.connection("gsheets", type=GSheetsConnection)

with st.form("nutrition_form"):
    # 🆕 Στοιχεία Επικοινωνίας & Lead Generation
    col_lead1, col_lead2 = st.columns(2)
    with col_lead1:
        full_name = st.text_input("Ονοματεπώνυμο *")
        user_email = st.text_input("Email *")
    with col_lead2:
        user_phone = st.text_input("Κινητό Τηλέφωνο *")
        # 🆕 Η ερώτηση διαχωρισμού για τα αυτόματα emails
        is_member = st.radio("Είσαι ήδη μέλος του Karavas Gym;", ["Όχι, ενδιαφέρομαι να ξεκινήσω!", "Ναι, είμαι ενεργό μέλος!"], horizontal=True)

    st.markdown("---")
    
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
        "Πολεμικές Τέχνες", "Πεζοπορία (Hiking)"
    ]
    selected_activities = st.multiselect(
        "Επίλεξε αθλητικές δραστηριότητες (1 έως 3)", 
        options=available_activities,
        max_selections=3
    )
        
    allergies = st.text_input("Αλλεργίες / Τροφές που αποφεύγεις", value="Καμία")
    submit_button = st.form_submit_button(label="Δημιουργία Πλάνου ✨")

def create_pdf(text_content):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
    styles = getSampleStyleSheet()
    
    greek_style = ParagraphStyle(
        'GreekStyle',
        parent=styles['Normal'],
        fontName='DejaVuSans',
        fontSize=11,
        leading=16,
        spaceAfter=10
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
    if not full_name or not user_email or not user_phone:
        st.error("Παρακαλώ συμπλήρωσε όλα τα υποχρεωτικά πεδία (Όνομα, Email, Κινητό)!")
    elif "@" not in user_email:
        st.error("Παρακαλώ βάλε ένα έγκυρο Email!")
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
            "activities": selected_activities
        }
        
        with st.spinner("🔄 Το AI σχεδιάζει το αναλυτικό 7ήμερο πλάνο διατροφής και προπόνησής σου..."):
            try:
                # 1. ΔΙΑΒΑΖΟΥΜΕ ΤΑ ΥΠΑΡΧΟΝΤΑ ΔΕΔΟΜΕΝΑ ΑΠΟ ΤΟ GOOGLE SHEET
                existing_data = conn.read(worksheet="Sheet1", ttl=0)
                
                # Καθορίζουμε τον τύπο (New Plan ή Member Plan) ανάλογα με την απάντηση
                plan_type = "Member Plan" if "Ναι" in is_member else "New Plan"
                
                # Δημιουργούμε τη νέα γραμμή με κατάσταση "Σε αναμονή"
                new_lead = pd.DataFrame([{
                    "Ημερομηνία": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Ονοματεπώνυμο": full_name.strip(),
                    "Email": user_email.strip(),
                    "Κινητό": user_phone.strip(),
                    "Στόχος": goal,
                    "Τύπος": plan_type,
                    "Βάρος Check-in": weight,
                    "Κατάσταση Email": "Σε αναμονή"
                }])
                
                # Ενώνουμε τα δεδομένα και κάνουμε το 1ο update στο Sheet
                updated_df = pd.concat([existing_data, new_lead], ignore_index=True)
                conn.update(worksheet="Sheet1", data=updated_df)
                
                # 2. ΚΑΝΟΥΜΕ ΤΗΝ ΚΛΗΣΗ ΣΤΟ API ΤΟΥ RENDER
                BACKEND_URL = "https://karavas-api.onrender.com/generate-plan"
                response = requests.post(BACKEND_URL, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("Το πλάνο σου είναι έτοιμο! 🎉")
                    st.markdown("---")
                    st.markdown(result["plan"])
                    
                    pdf_bytes = create_pdf(result["plan"])
                    st.download_button(
                        label="📥 Κατέβασμα Πλάνου σε PDF",
                        data=pdf_bytes,
                        file_name="my_nutrition_plan.pdf",
                        mime="application/pdf"
                    )
                    
                    # 3. ΑΦΟΥ ΠΗΡΑΜΕ 200 OK, ΑΛΛΑΖΟΥΜΕ ΤΗΝ ΚΑΤΑΣΤΑΣΗ ΣΕ "Εκδόθηκε"
                    # Αλλάζουμε την τιμή στην τελευταία γραμμή που μόλις προσθέσαμε
                    updated_df.iloc[-1, updated_df.columns.get_loc("Κατάσταση Email")] = "Εκδόθηκε"
                    conn.update(worksheet="Sheet1", data=updated_df)
                    
                else:
                    st.error(f"Σφάλμα Backend: {response.text}")
                    # Αν αποτύχει το API, ενημερώνουμε το Sheet με το σφάλμα
                    updated_df.iloc[-1, updated_df.columns.get_loc("Κατάσταση Email")] = "Σφάλμα API"
                    conn.update(worksheet="Sheet1", data=updated_df)
                    
            except Exception as e:
                st.error(f"Αδυναμία σύνδεσης με τον server: {e}")
