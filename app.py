import streamlit as st
import requests
import io
import re
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from streamlit_gsheets import GSheetsConnection

# 1. PREMIUM DARK MODE & BRANDING CONFIGURATION
st.set_page_config(
    page_title="Smart Nutrition Coach - Karavas Gym", 
    page_icon="🥑", 
    layout="centered"
)

# Custom CSS για Premium Dark Aesthetic (Karavas Gym Style)
# Custom CSS για Premium Dark Aesthetic με Καθαρή Αντίθεση
# Custom CSS για Premium Dark Aesthetic με Καθαρή Αντίθεση σε Γράμματα και Κουμπιά
st.markdown("""
<style>
    /* Φόντο και βασικά χρώματα */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF !important;
    }
    /* Εξασφάλιση ότι όλα τα απλά κείμενα, labels και Markdown φαίνονται πεντακάθαρα */
    .stMarkdown, p, span, label, .stDataFrame {
        color: #E0E2E6 !important;
    }
    /* Τίτλοι και Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    /* Highlight χρυσό/neon για το Gym Branding */
    .highlight-text {
        color: #FFD700 !important;
        font-weight: bold;
    }
    /* Στυλ για τα Tabs */
    .stTabs [data-baseweb="tab"] {
        color: #8A99AD !important;
        font-size: 16px;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #FFD700 !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #FFD700 !important;
        border-bottom-color: #FFD700 !important;
    }
    /* Στυλ Φόρμας και Κουτιών */
    div[data-testid="stForm"] {
        background-color: #1A1F2C;
        border: 1px solid #2D3748;
        border-radius: 10px;
        padding: 25px;
    }
    
  
    /* ΔΙΟΡΘΩΣΗ ΓΙΑ ΟΛΑ ΤΑ ΚΟΥΜΠΙΑ (BUTTONS) */
    div.stButton > button, div.stDownloadButton > button, div[data-testid="stFormSubmitButton"] > button {
        color: #FFFFFF !important;
        background-color: #262730 !important;
        border: 1px solid #FFD700 !important;
        font-weight: 900 !important; /* Μέγιστο πάχος γραμματοσειράς */
        font-size: 16px !important; /* Ελαφρώς μεγαλύτερο μέγεθος */
        text-transform: uppercase !important; /* Κεφαλαία γράμματα για στυλ */
        letter-spacing: 1px !important; /* Απόσταση στα γράμματα */
        transition: all 0.2s ease-in-out;
    }
    
    /* Εξασφάλιση έντονης γραφής για το κείμενο ΜΕΣΑ στο κουμπί */
    div.stButton > button p, div.stDownloadButton > button p, div[data-testid="stFormSubmitButton"] > button p {
        font-weight: 900 !important;
        color: #FFFFFF !important;
    }
    
    /* Εφέ Hover, Active και Focus - Χρυσό φόντο με κατάμαυρα έντονα γράμματα */
    div.stButton > button:hover, div.stDownloadButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover,
    div.stButton > button:active, div.stDownloadButton > button:active, div[data-testid="stFormSubmitButton"] > button:active,
    div.stButton > button:focus, div.stDownloadButton > button:focus, div[data-testid="stFormSubmitButton"] > button:focus {
        color: #0E1117 !important;
        background-color: #FFD700 !important;
        border: 1px solid #FFD700 !important;
        box-shadow: 0px 0px 15px #FFD700;
    }

    /* Διόρθρωση χρώματος κειμένου στο hover για τα εσωτερικά στοιχεία <p> */
    div.stButton > button:hover p, div.stDownloadButton > button:hover p, div[data-testid="stFormSubmitButton"] > button:hover p {
        color: #0E1117 !important;
        font-weight: 900 !important;
    }

    /* Custom Box για το AI Plan Output */
    .premium-response-box {
        background-color: #161B22;
        border-left: 5px solid #FFD700;
        padding: 25px;
        border-radius: 5px;
        margin-top: 20px;
        line-height: 1.7;
        color: #FFFFFF !important;
    }
    /* Διόρθρωση για τα Markdown στοιχεία ΜΕΣΑ στο response box */
    .premium-response-box * {
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# Κεντρικός Τίτλος με Premium Visualς
st.title("Smart Nutrition Coach 🥑")
st.markdown('<p style="font-size:20px; color:#FFD700; font-weight:bold; margin-top:-15px;">Karavas Gym Fighting & Fitness</p>', unsafe_allow_html=True)

# Δημιουργία Tabs
tab1, tab2 = st.tabs(["✨ Δημιουργία Premium Πλάνου", "📈 Tracking Προόδου & Check-in"])

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

# 2. ADVANCED PREMIUM PDF CREATION (ReportLab)
def create_pdf(text_content):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter, 
        rightMargin=45, 
        leftMargin=45, 
        topMargin=50, 
        bottomMargin=50
    )
    
    # Χρήση των εγγενών core γραμματοσειρών της ReportLab (Δεν χρειάζονται αρχεία ή download)
    font_reg = 'Helvetica'
    font_bold = 'Helvetica-Bold'
    
    styles = getSampleStyleSheet()
    
    # Custom Premium Στυλ για το PDF
    title_style = ParagraphStyle(
        'PDFTitle',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=22,
        textColor=colors.HexColor('#1A1F2C'),
        spaceAfter=15,
        alignment=1
    )
    
    subtitle_style = ParagraphStyle(
        'PDFSubtitle',
        parent=styles['Normal'],
        fontName=font_reg,
        fontSize=12,
        textColor=colors.HexColor('#FFD700'),
        spaceAfter=25,
        alignment=1
    )
    
    h1_style = ParagraphStyle(
        'PDFH1',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=14,
        textColor=colors.HexColor('#1A1F2C'),
        spaceBefore=18,
        spaceAfter=8
    )
    
    body_style = ParagraphStyle(
        'PDFBody',
        parent=styles['Normal'],
        fontName=font_reg,
        fontSize=10,
        leading=15,
        textColor=colors.HexColor('#333333'),
        spaceAfter=8
    )

    story = []
    
    # Header του PDF
    story.append(Paragraph("KARAVAS GYM – SMART NUTRITION", title_style))
    story.append(Paragraph("Εξατομικευμένο Πλάνο Διατροφής & Αθλητικής Απόδοσης", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1A1F2C'), spaceAfter=20))
    
    # Επεξεργασία και Δομή του Κειμένου της AI
    lines = text_content.split('\n')
    for line in lines:
        clean_line = line.replace('**', '').replace('$', '').strip()
        
        # Ανίχνευση Τίτλων (π.χ. 1., 2., 3. ή ##) για εφαρμογή Bold Στυλ
        if line.startswith('###') or line.startswith('##') or re.match(r'^\d+\.', clean_line):
            clean_line = clean_line.replace('###', '').replace('##', '').strip()
            story.append(Spacer(1, 10))
            story.append(Paragraph(clean_line, h1_style))
            story.append(HRFlowable(width="30%", thickness=1, color=colors.HexColor('#FFD700'), hAlign='LEFT', spaceAfter=10))
        elif clean_line:
            story.append(Paragraph(clean_line, body_style))
        else:
            story.append(Spacer(1, 6))
            
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# ==========================================
# TAB 1: ΔΗΜΙΟΥΡΓΙΑ ΠΛΑΝΟΥ
# ==========================================
# ==========================================
# TAB 1: ΔΗΜΙΟΥΡΓΙΑ ΠΛΑΝΟΥ
# ==========================================
with tab1:
    with st.form("nutrition_form"):
        # ΠΡΟΣΩΠΟΠΟΙΗΜΕΝΟΣ & ΔΥΝΑΜΙΚΟΣ ΤΙΤΛΟΣ LEAD GENERATION
        st.markdown('### ⚡ ΠΟΥ ΝΑ ΣΟΥ ΣΤΕΙΛΟΥΜΕ ΤΟ ΠΛΑΝΟ ΣΟΥ;', unsafe_allow_html=True)
        st.markdown('<p style="font-size:14px; color:#FFD700; margin-top:-10px; margin-bottom:15px;">Κλείδωσε τη θέση σου και ξεκίνα τη μεταμόρφωσή σου σήμερα.</p>', unsafe_allow_html=True)
        
        col_lead1, col_lead2 = st.columns(2)
        with col_lead1:
            full_name = st.text_input("Ονοματεπώνυμο *")
            user_email = st.text_input("Email *")
        with col_lead2:
            user_phone = st.text_input("Κινητό Τηλέφωνο *")

        st.markdown("---")
        # ΠΙΑΣΑΡΙΚΟΣ ΤΙΤΛΟΣ ΓΙΑ ΤΑ ΦΥΣΙΚΑ ΧΑΡΑΚΤΗΡΙΣΤΙΚΑ
        st.markdown('### 📊 Η ΑΚΤΙΝΟΓΡΑΦΙΑ ΤΟΥ ΣΤΟΧΟΥ ΣΟΥ', unsafe_allow_html=True)
        st.markdown('<p style="font-size:14px; color:gray; margin-top:-10px; margin-bottom:15px;">Δώσε στην AI τα ακριβή σου δεδομένα για να "ράψει" το πλάνο στα μέτρα σου.</p>', unsafe_allow_html=True)
        
        gender = st.radio("Φύλο", ["Άνδρας", "Γυναίκα"], horizontal=True)
        col1, col2 = st.columns(2)
        
        with col1:
            weight = st.number_input("Βάρος (kg)", min_value=30.0, max_value=200.0, value=75.0, step=0.1)
            height = st.number_input("Ύψος (cm)", min_value=100.0, max_value=250.0, value=175.0, step=1.0)
            age = st.number_input("Ηλικία", min_value=14, max_value=100, value=25, step=1)
        
        with col2:
            goal = st.selectbox("Στόχος", ["Απώλεια λίπους", "Μυϊκή υπερτροφία", "Συντήρηση / Σύσφιξη"])
            diet_type = st.selectbox("Τύπος Διατροφής", ["Ισορρομημένη (Balanced)", "Υψηλή σε Πρωτεΐνη (High Protein)", "Κετογονική (Keto)", "Χορτοφαγική (Vegetarian)", "Αυστηρά Χορτοφαγική (Vegan)"])
            activity_level = st.selectbox("Επίπεδο Γενικής Δραστηριότητας", ["Καθιστική ζωή (γραφείο)", "Ήπια άσκηση (1-3 μέρες/βδομάδα)", "Έντονη άσκηση (4-7 μέρες/βδομάδα)"])
            
        available_activities = ["Γυμναστήριο (Βάρη)", "Τρέξιμο / Jogging", "Κολύμβηση", "Ποδηλασία", "Crossfit", "Ποδόσφαιρο", "Μπάσκετ", "Τένις", "Γιόγκα / Πιλάτες", "Πολεμικές Τέχνες / BJJ", "Πεζοπορία (Hiking)"]
        selected_activities = st.multiselect("Επίλεξε αθλητικές δραστηριότητες (1 έως 3)", options=available_activities, max_selections=3)
            
        allergies = st.text_input("Αλλεργίες / Τροφές που αποφεύγεις", value="Καμία")
        include_supplements = st.checkbox("Θέλω να συμπεριληφθούν προτάσεις για νόμιμα συμπληρώματα διατροφής 💊")
        
        submit_button = st.form_submit_button(label="Έκδοση Premium Πλάνου ✨")

    if submit_button:
        if not full_name.strip() or not validate_email(user_email) or len(user_phone.strip()) < 10 or not selected_activities:
            st.error("Παρακαλώ συμπληρώστε σωστά όλα τα υποχρεωτικά πεδία και επιλέξτε τουλάχιστον 1 άθλημα!")
        else:
            payload = {"gender": gender, "weight": weight, "height": height, "age": age, "goal": goal, "activity_level": activity_level, "diet_type": diet_type, "allergies": allergies, "activities": selected_activities, "include_supplements": include_supplements}
            
            with st.spinner("🔄 Η AI του Karavas Gym σχεδιάζει το πλάνο σου..."):
                try:
                    # Καταγραφή Lead στα Google Sheets
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
                    
                    # Κλήση του Backend API στο Render
                    BACKEND_URL = "https://karavas-api.onrender.com/generate-plan"
                    response = requests.post(BACKEND_URL, json=payload)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"Ευχαριστούμε {full_name}! Το premium πλάνο σου εκδόθηκε με επιτυχία! 🎉")
                        
                        # Κατέβασμα Premium PDF Κουμπί (Πρώτο για ευκολία)
                        pdf_bytes = create_pdf(result["plan"])
                        st.download_button(label="📥 Κατέβασμα Πλάνου σε Premium PDF", data=pdf_bytes, file_name=f"Karavas_Gym_{full_name.replace(' ', '_')}.pdf", mime="application/pdf")
                        
                        # Εμφάνιση αποτελέσματος στην οθόνη με Premium Box
                        st.markdown('<div class="premium-response-box">', unsafe_allow_html=True)
                        st.markdown(result["plan"])
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.error(f"Σφάλμα Backend: {response.text}")
                except Exception as e:
                    st.error(f"Σφάλμα: {e}")

# ==========================================
# TAB 2: INTERACTIVE CHECK-IN & TRACKING
# ==========================================
with tab2:
    st.markdown("### 📈 Εβδομαδιαίο Check-in Προόδου")
    st.write("Καταχώρησε το νέο σου βάρος για να παρακολουθείς την πορεία σου.")
    
    checkin_email = st.text_input("Δώσε το Email σου για αναζήτηση:")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        btn_search = st.button("🔍 Εμφάνιση Προόδου & Ιστορικού")
    
    st.markdown("---")
    current_weight = st.number_input("Νέο Βάρος (kg) για καταχώρηση:", min_value=30.0, max_value=200.0, value=75.0, step=0.1)
    btn_checkin = st.button("⚖️ Καταχώρηση Νέου Βάρους")
    
    if btn_search or btn_checkin:
        if not checkin_email.strip():
            st.error("Παρακαλώ συμπληρώστε το email σας!")
        else:
            try:
                with st.spinner("🔄 Σύνδεση με τη βάση δεδομένων..."):
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    df = conn.read(ttl=0)
                    
                    user_history = df[df['Email'].str.strip().str.lower() == checkin_email.strip().lower()]
                    
                    if btn_checkin:
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
                        
                        df = conn.read(ttl=0)
                        user_history = df[df['Email'].str.strip().str.lower() == checkin_email.strip().lower()]
                    
                    if not user_history.empty:
                        user_goal = user_history['Στόχος'].iloc[0]
                        st.markdown(f"**Ο Στόχος σου:** <span class='highlight-text'>{user_goal}</span>", unsafe_allow_html=True)
                        
                        st.markdown("#### Η πορεία του βάρους σου:")
                        user_history = user_history.copy()
                        user_history['Βάρος Check-in'] = pd.to_numeric(user_history['Βάρος Check-in'], errors='coerce')
                        chart_data = user_history[['Ημερομηνία', 'Βάρος Check-in']].dropna()
                        
                        if not chart_data.empty:
                            chart_data = chart_data.set_index('Ημερομηνία')
                            st.line_chart(chart_data)
                            
                            weights_list = chart_data['Βάρος Check-in'].tolist()
                            if len(weights_list) >= 2:
                                diff = weights_list[-1] - weights_list[-2]
                                
                                if "Απώλεια λίπους" in user_goal:
                                    if diff < 0:
                                        st.success(f"📉 Μειώθηκε το βάρος σου κατά {abs(diff):.1f} kg. Εξαιρετική δουλειά! Χάνεις λίπος σύμφωνα με τον στόχο σου! 🔥")
                                    elif diff > 0:
                                        st.warning(f"📈 Το βάρος σου αυξήθηκε κατά {diff:.1f} kg. Έλεγξε ξανά τη διατροφή σου!")
                                    else:
                                        st.info("⚖️ Το βάρος σου παρέμεινε σταθερό. Η συνέπεια θα φέρει το αποτέλεσμα!")
                                        
                                elif "Μυϊκή υπερτροφία" in user_goal:
                                    if diff > 0:
                                        st.success(f"📈 Το βάρος σου αυξήθηκε κατά {diff:.1f} kg. Μπράβο! Χτίζεις μυϊκή μάζα! 💪")
                                    elif diff < 0:
                                        st.error(f"📉 Χάνουμε κιλά ({abs(diff):.1f} kg)! Αυξήστε ελαφρώς τις θερμίδες σας.")
                                    else:
                                        st.info("⚖️ Το βάρος σου παρέμεινε σταθερό.")
                        else:
                            st.warning("Δεν βρέθηκαν έγκυρα δεδομένα βάρους.")
                    else:
                        st.warning("Δεν βρέθηκε ιστορικό για αυτό το email.")
            except Exception as e:
                st.error(f"Σφάλμα κατά τη σύνδεση: {e}")