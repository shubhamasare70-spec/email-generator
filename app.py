import streamlit as st
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

# 1. Initialize Firebase (Check if already initialized to prevent errors)
if not firebase_admin._apps:
    # Make sure 'firebase_key.json' is in the same folder!
    cred = credentials.Certificate('firebase_key.json')
    firebase_admin.initialize_app(cred)
db = firestore.client()

# 2. Setup Gemini API
# Replace with your actual key for this quick prototype
genai.configure(api_key="AIzaSyBs0XKwESCuortI9P1yWd34xg0eCFEvCxw")

# NEW AUTO-DETECT CODE:
valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
model = genai.GenerativeModel(valid_models[0])# 3. Streamlit UI Build
st.set_page_config(page_title="AI Email Tailor", page_icon="📧")
st.title("Customised Cold Email Generator 🚀")

st.markdown("Match your skills perfectly to the role you want.")

# Sidebar for User Profile
st.sidebar.header("Your Profile")
user_skills = st.sidebar.text_area("Your Skills (e.g., Python, UI/UX, Data Analysis)", height=100)
user_projects = st.sidebar.text_area("Your Past Projects (Briefly)", height=150)

# Main Area for Target Role
st.header("The Target")
recipient_name = st.text_input("Recipient's Name (e.g., Prof. Smith or Hiring Manager)")
target_role = st.text_area("Job/Internship/Research Description", height=200)

if st.button("Generate Tailored Email"):
    if user_skills and target_role:
        with st.spinner("Analyzing overlap and crafting email..."):
            
            # 4. The Prompt Engineering
            prompt = f"""
            You are an expert career strategist. Write a highly professional, concise cold email.
            Recipient: {recipient_name}
            Target Role/Research: {target_role}
            My Skills: {user_skills}
            My Projects: {user_projects}
            
            Task: Write a cold email applying for this role. Do not list all my skills. ONLY highlight 
            the skills and projects that directly match the target role. Keep it confident, polite, 
            and under 150 words. Do not use placeholders like [Your Name], end it gracefully.
            """
            
            # 5. Get AI Response
            response = model.generate_content(prompt)
            generated_email = response.text
            
            st.subheader("Your Custom Email:")
            st.write(generated_email)
            
            # 6. Save to Firebase
            try:
                doc_ref = db.collection("generated_emails").document()
                doc_ref.set({
                    "recipient": recipient_name,
                    "target_role": target_role,
                    "email_draft": generated_email,
                    "timestamp": datetime.datetime.now()
                })
                st.success("Draft saved to Firebase!")
            except Exception as e:
                st.error(f"Could not save to database: {e}")
    else:
        st.warning("Please fill out your skills and the target role.")