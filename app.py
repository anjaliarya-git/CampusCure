import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import hashlib
import os

st.set_page_config(page_title="CampusCure", layout="wide", page_icon="🩺")

# ---------------- SESSION ----------------
if "complaints" not in st.session_state:
    st.session_state.complaints = pd.DataFrame(columns=[
        "Complaint ID","Student Name","Category","Description",
        "Priority","Status","Admin Remark","Date Submitted","SLA Deadline","Uploaded Image"
    ])
if "role" not in st.session_state:
    st.session_state.role = None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "splash_done" not in st.session_state:
    st.session_state.splash_done = False

# ---------------- HELPERS ----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_admin_credentials():
    if not os.path.exists("admin_users.csv"):
        default = pd.DataFrame([{"username":"admin","password_hash":hash_password("admin123")}])
        default.to_csv("admin_users.csv", index=False)
    return pd.read_csv("admin_users.csv")

def verify_admin(username,password):
    admins = load_admin_credentials()
    password_hash = hash_password(password)
    return ((admins['username']==username) & (admins['password_hash']==password_hash)).any()

def check_escalation():
    if not st.session_state.complaints.empty:
        now = datetime.now()
        for i in range(len(st.session_state.complaints)):
            deadline = st.session_state.complaints.loc[i,"SLA Deadline"]
            status = st.session_state.complaints.loc[i,"Status"]
            if now > deadline and status in ["Pending","In Review"]:
                st.session_state.complaints.loc[i,"Status"]="Escalated"
check_escalation()

# ---------------- STYLES ----------------
st.markdown("""
<style>
body {background: linear-gradient(to right,#0072ff,#00c6ff); font-family:'Segoe UI', sans-serif; color:white;}
.stButton>button {background-color:#6a0dad; color:white; font-weight:bold; border-radius:10px; height:3em; width:220px; transition: transform 0.2s, box-shadow 0.2s;}
.stButton>button:hover {transform:translateY(-3px); box-shadow:0 8px 15px rgba(0,0,0,0.3);}
.card {background-color:rgba(255,255,255,0.1); padding:20px; border-radius:15px; text-align:center; box-shadow:0 4px 10px rgba(0,0,0,0.2); color:white;}
</style>
""", unsafe_allow_html=True)

# ---------------- SPLASH / WELCOME ----------------
if not st.session_state.splash_done:
    st.markdown(f"""
    <div style="
    position: relative;
    height: 400px;
    background-image: url('https://i.pinimg.com/originals/1w/6d/uN/1w6duNpWR.jpg');
    background-size: cover; background-position: center;
    border-radius: 20px; overflow: hidden;">
        <div style="position:absolute;top:0;left:0;width:100%;height:100%;background-color: rgba(0,0,0,0.5);
            display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center;">
            <h2 style='color:#FFD700; font-size:40px; font-weight:500; margin:0;'>Guru Jambheshwar University of Science & Technology</h2>
            <h1 style='color:#FFFFFF; font-size:70px; font-weight:bold; margin-top:10px;'>CampusCure</h1>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Proceed to Login"):
        st.session_state.splash_done = True
    st.stop()

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:
    st.markdown("### Login to CampusCure")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username.strip()=="" or password.strip()=="":
            st.error("Enter both username and password")
        elif verify_admin(username.strip(),password.strip()):
            st.session_state.role="Admin"
            st.session_state.logged_in=True
            st.success("Logged in as Admin")
        else:
            st.session_state.role="Student"
            st.session_state.user_name=username.title()
            st.session_state.logged_in=True
            st.success(f"Logged in as Student: {st.session_state.user_name}")
    st.stop()

# ---------------- SIDEBAR ----------------
menu = st.sidebar.radio("Navigation", ["Home","Raise Grievance","Track Status","Profile"] if st.session_state.role=="Student" else ["Home","Admin Panel"])

# ---------------- HOME ----------------
if menu=="Home":
    st.markdown("<h1 style='text-align:center; color:white;'>Welcome to CampusCure</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:22px; color:#e0f7fa;'>AI-Powered, Transparent, Time-Bound Grievance Resolution</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.markdown("<div class='card'><h3>Smart</h3><p>AI-based categorization</p></div>", unsafe_allow_html=True)
    col2.markdown("<div class='card'><h3>Transparent</h3><p>Track grievances openly</p></div>", unsafe_allow_html=True)
    col3.markdown("<div class='card'><h3>Time-Bound</h3><p>Resolved within SLA deadlines</p></div>", unsafe_allow_html=True)

# ---------------- RAISE GRIEVANCE ----------------
elif menu=="Raise Grievance":
    st.subheader("Raise a New Complaint")
    name = st.text_input("Student Name")
    category = st.selectbox("Complaint Category", ["Academic","Hostel","Transport","Administration","Other"])
    description = st.text_area("Describe your Issue in Detail")
    uploaded_file = st.file_uploader("Optional: Upload an image (jpg/png)", type=["jpg","png","jpeg"])
    if st.button("Submit Complaint"):
        if name and description:
            complaint_id = f"CMP{len(st.session_state.complaints)+1:03d}"
            priority = "High" if "urgent" in description.lower() else "Medium"
            date_submitted = datetime.now()
            deadline = date_submitted + timedelta(days=3)
            new_row = {
                "Complaint ID": complaint_id,
                "Student Name": name,
                "Category": category,
                "Description": description,
                "Priority": priority,
                "Status": "Pending",
                "Admin Remark": "Not Reviewed Yet",
                "Date Submitted": date_submitted,
                "SLA Deadline": deadline,
                "Uploaded Image": uploaded_file.name if uploaded_file else None
            }
            st.session_state.complaints = pd.concat([st.session_state.complaints, pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"Complaint Submitted! Your ID is {complaint_id}")
        else:
            st.error("Please fill all fields!")

# ---------------- TRACK STATUS ----------------
elif menu=="Track Status":
    st.subheader("Track Your Complaint")
    complaint_id_search = st.text_input("Enter Complaint ID")
    if complaint_id_search:
        result = st.session_state.complaints[st.session_state.complaints["Complaint ID"]==complaint_id_search]
        if not result.empty:
            complaint = result.iloc[0]
            st.markdown(f"<div class='card'><h3>{complaint['Complaint ID']}</h3><p>Status: {complaint['Status']}</p><p>Priority: {complaint['Priority']}</p><p>Admin Remark: {complaint['Admin Remark']}</p></div>", unsafe_allow_html=True)
        else:
            st.warning("Invalid Complaint ID")

# ---------------- ADMIN PANEL ----------------
elif menu=="Admin Panel":
    st.subheader("Admin Dashboard")
    if not st.session_state.complaints.empty:
        selected_id = st.selectbox("Select Complaint ID", st.session_state.complaints["Complaint ID"].tolist())
        new_status = st.selectbox("Update Status", ["Pending","In Review","Resolved","Escalated"])
        admin_remark = st.text_area("Admin Remark")
        if st.button("Update Complaint"):
            st.session_state.complaints.loc[st.session_state.complaints["Complaint ID"]==selected_id,"Status"]=new_status
            st.session_state.complaints.loc[st.session_state.complaints["Complaint ID"]==selected_id,"Admin Remark"]=admin_remark
            st.success("Updated Successfully!")
        st.dataframe(st.session_state.complaints)
    else:
        st.info("No complaints available yet.")

# ---------------- PROFILE ----------------
elif menu=="Profile":
    st.subheader("Profile")
    st.write("Name:", st.session_state.user_name)
    st.write("Role: Student")
    st.write("### Grievance History")
    user_history = st.session_state.complaints[st.session_state.complaints["Student Name"]==st.session_state.user_name]
    if not user_history.empty:
        st.dataframe(user_history)
    else:
        st.info("No grievances submitted yet.")

    st.write("---")
    st.write("## Account Settings")
    new_password = st.text_input("Enter New Password", type="password", key="pw1")
    confirm_password = st.text_input("Confirm Password", type="password", key="pw2")
    if st.button("Update Password"):
        if new_password==confirm_password and new_password!="":
            st.success("Password Updated Successfully (Demo Mode)")
        else:
            st.error("Passwords do not match")

    new_email = st.text_input("Enter New Email", key="email")
    if st.button("Update Email"):
        if new_email!="":
            st.success("Email Updated Successfully (Demo Mode)")
        else:
            st.error("Please enter a valid email")

    st.write("---")
    st.write("## Help & Support")
    st.info("Contact: support@campuscure.com")

    # Logout moved at the **end**
    st.write("---")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.user_name = None
        st.session_state.splash_done = False
        st.experimental_rerun()