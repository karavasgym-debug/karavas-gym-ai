import streamlit as st
import requests
import io
import re
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 1. PREMIUM DARK MODE & BRANDING CONFIGURATION
st.set_page_config(
    page_title="Smart Nutrition Coach - Karavas Gym", 
    page_icon="🥑", 
    layout="centered"
)

# Custom CSS για Premium Dark Aesthetic με Καθαρή Αντίθεση σε Γράμματα και Κουμπιά
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF !important;
    }
    .stMarkdown, p, span, label, .stDataFrame {
        color: #E0E2E6 !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .highlight-text {
        color: #FFD700 !important;
        font-weight: bold;
    }
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
    div[data-testid="stForm"] {
        background-color: #1A1F2C;
        border: 1px solid #2D3748;
        border-radius: 10px;
        padding: 25px;
    }
    
    div.stButton > button, div.stDownloadButton > button, div[data-testid="stFormSubmitButton"] > button {
        color: #FFFFFF !important;
        background-color: #262730 !important;
        border: 1px solid #FFD700 !important;
        font-weight: 900 !important;
        font-size: 16px !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        transition: all 0.2s ease-in-out;
    }
    
    div.stButton > button p, div.stDownloadButton > button p, div[data-testid="stFormSubmitButton"] > button p {
        font-weight: 900 !important;
        color: #FFFFFF !important;
    }
    
    div.stButton > button:hover, div.stDownloadButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
        color: #0E1117 !important;
        background-color: #FFD700 !important;
        border: 1px solid #FFD700 !important;
        box-shadow: 0px 0px 15px #FFD700;
    }

    div.stButton > button:hover p, div.stDownloadButton > button:hover p, div[data-testid="stFormSubmitButton"] > button:hover p {
        color: #0E1117 !important;
        font-weight: 900 !important;
    }

    .premium-response-box {
        background-color: #161B22;
        border-left: 5px solid #FFD700;
        padding: 25px;
        border-radius: 5px;
        margin-top: 20px;
        line-height: 1.7;
        color: #FFFFFF !important;
    }
    .premium-response-box * {
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("Smart Nutrition Coach 🥑")
st.markdown('<p style="font-size:20px; color:#FFD700; font-weight:bold; margin-top:-15px;">Karavas Gym Fighting & Fitness</p>', unsafe_allow_html=True)

# Δημιουργία των Tabs
tab1, tab2 = st.tabs(["✨ Δημιουργία Premium Πλάνου", "📈 Tracking Προόδου & Check-in"])

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

# ==========================================
# 2. ADVANCED PREMIUM PDF CREATION (ReportLab)
# ==========================================
def create_pdf(text_content, full_name):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=45, leftMargin=45, topMargin=50, bottomMargin=50)
    
    try:
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf')) 
        font_reg = 'DejaVuSans'
        font_bold = 'DejaVuSans-Bold'
    except Exception as e:
        font_reg = 'Helvetica'
        font_bold = 'Helvetica-Bold'
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'PDFTitle', parent=styles['Normal'], fontName=font_bold, fontSize=20, leading=24,
        textColor=colors.HexColor('#1A1F2C'), spaceAfter=8, alignment=1
    )
    subtitle_style = ParagraphStyle(
        'PDFSubtitle', parent=styles['Normal'], fontName=font_reg, fontSize=12, leading=16,
        textColor=colors.HexColor('#D4AF37'), spaceAfter=25, alignment=1
    )
    h1_style = ParagraphStyle(
        'PDFH1', parent=styles['Normal'], fontName=font_bold, fontSize=14, leading=18,
        textColor=colors.HexColor('#1A1F2C'), spaceBefore=15, spaceAfter=10
    )
    body_style = ParagraphStyle(
        'PDFBody', parent=styles['Normal'], fontName=font_reg, fontSize=10, leading=16,
        textColor=colors.HexColor('#333333'), spaceAfter=8
    )
    
    story = []
    story.append(Paragraph("KARAVAS GYM – SMART NUTRITION", title_style))
    story.append(Paragraph("Εξατομικευμένο Πλάνο Διατροφής & Αθλητικής Απόδοσης", subtitle_style))
    story.append(Spacer(1, 10))
    
    lines = text_content.split('\n')
    for line in lines:
        clean_line = line.strip()
        if clean_line:
            if clean_line.startswith('#') or clean_line.startswith('1.') or clean_line.startswith('2.') or clean_line.startswith('3.') or clean_line.startswith('4.') or clean_line.startswith('5.'):
                formatted_title = clean_line.replace('#', '').strip()
                story.append(Paragraph(formatted_title, h1_style))
            else:
                story.append(Paragraph(clean_line, body_style))
        else:
            story.append(Spacer(1, 5))
            
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# Σύνδεση με το Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# ==========================================
# TAB 1: ΔΗΜΙΟΥΡΓΙΑ ΠΛΑΝΟΥ
# ==========================================
with tab1:
    with st.form("nutrition_form"):
        st.markdown('### ⚡ ΠΟΥ ΝΑ ΣΟΥ ΣΤΕΙΛΟΥΜΕ ΤΟ ΠΛΑΝΟ ΣΟΥ;', unsafe_allow_html=True)
        st.markdown('<p style="font-size:14px; color:#FFD700; margin-top:-10px; margin-bottom:15px;">Κλείδωσε τη θέση σου και ξεκίνα τη μεταμόρφωσή σου σήμερα.</p>', unsafe_allow_html=True)
        
        col_lead1, col_lead2 = st.columns(2)
        with col_lead1:
            full_name = st.text_input("Ονοματεπώνυμο *")
            user_email = st.text_input("Email *")
        with col_lead2:
            user_phone = st.text_input("Κινητό Τηλέφωνο *")
            is_member = st.radio("Είσαι ήδη μέλος του Karavas Gym;", ["Όχι, ενδιαφέρομαι να ξεκινήσω!", "Ναι, είμαι ενεργό μέλος!"], horizontal=True)

        st.markdown("---")
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
            payload = {
                "gender": gender, "weight": weight, "height": height, "age": age, "goal": goal, 
                "activity_level": activity_level, "diet_type": diet_type, "allergies": allergies, 
                "activities": selected_activities, "include_supplements": include_supplements
            }
            
            with st.spinner("🔄 Η AI του Karavas Gym σχεδιάζει το πλάνο σου..."):
                try:
                    # 1. Πρώτη εγγραφή στο Google Sheet με την κατάσταση "Σε αναμονή"
                    existing_data = conn.read(worksheet="Sheet1", ttl=0)
                    plan_type = "Member Plan" if "Ναι" in is_member else "New Plan"
                    
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
                    
                    updated_data = pd.concat([existing_data, new_lead], ignore_index=True)
                    conn.update(worksheet="Sheet1", data=updated_data)
                    
                    # Κλήση του API στο Render
                    BACKEND_URL = "https://karavas-api.onrender.com/generate-plan"
                    response = requests.post(BACKEND_URL, json=payload)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"Ευχαριστούμε {full_name}! Το premium πλάνο σου εκδόθηκε με επιτυχία! 🎉")
                        
                        # 2. Αλλαγή κατάστασης σε "Εκδόθηκε" (Αφού το Render απάντησε επιτυχώς)
                        try:
                            fresh_data = conn.read(worksheet="Sheet1", ttl=0)
                            idx = fresh_data[fresh_data['Email'].str.strip().str.lower() == user_email.strip().lower()].index
                            if not idx.empty:
                                fresh_data.loc[idx[-1], "Κατάσταση Email"] = "Εκδόθηκε"
                                conn.update(worksheet="Sheet1", data=fresh_data)
                        except Exception as sheet_update_err:
                            st.warning(f"Το πλάνο εκδόθηκε, αλλά απέτυχε η αυτόματη ενεργοποίηση του email: {sheet_update_err}")

                        # Δημιουργία PDF
                        pdf_bytes = create_pdf(result["plan"], full_name)
                        st.download_button(
                            label="📥 Κατέβασμα Πλάνου σε Premium PDF", 
                            data=pdf_bytes, 
                            file_name=f"Karavas_Gym_{full_name.replace(' ', '_')}.pdf", 
                            mime="application/pdf"
                        )
                        
                        st.markdown('<div class="premium-response-box">', unsafe_allow_html=True)
                        st.markdown(result["plan"])
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        # 🛠️ ΔΙΑΧΕΙΡΙΣΗ ΣΦΑΛΜΑΤΩΝ RENDER (π.χ. 502 Bad Gateway)
                        st.error("🔴 Ο server της AI προετοιμάζεται ή είναι προσωρινά υπερφορτωμένος. Παρακαλώ περιμένετε 1 λεπτό και ξαναπατήστε το κουμπί!")
                        
                        # Ενημέρωση του Sheet με καταγραφή του προβλήματος
                        try:
                            error_data = conn.read(worksheet="Sheet1", ttl=0)
                            idx = error_data[error_data['Email'].str.strip().str.lower() == user_email.strip().lower()].index
                            if not idx.empty:
                                error_data.loc[idx[-1], "Κατάσταση Email"] = "Σφάλμα Server (Render 502)"
                                conn.update(worksheet="Sheet1", data=error_data)
                        except:
                            pass
                except Exception as e:
                    st.error(f"Σφάλμα σύνδεσης: {e}")

# ==========================================
# TAB 2: INTERACTIVE CHECK-IN & TRACKING
# ==========================================
with tab2:
    st.markdown("### 📈 Εβδομαδιαίο Check-in Προόδου")
    st.write("Καταχώρησε το νέο σου βάρος για να παρακολουθείς την πορεία σου.")
    
    checkin_email = st.text_
