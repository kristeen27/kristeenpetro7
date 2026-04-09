import datetime as dt

import requests
import streamlit as st

API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Hospital SaaS Dashboard", layout="wide")

if "token" not in st.session_state:
    st.session_state.token = None
if "clinic_api_key" not in st.session_state:
    st.session_state.clinic_api_key = ""


st.title("Hospital Appointment Dashboard")

if not st.session_state.token:
    st.subheader("Login")
    clinic_api_key = st.text_input("Clinic API Key", type="password")
    phone = st.text_input("Phone Number")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        response = requests.post(
            f"{API_BASE_URL}/users/login",
            headers={"X-Clinic-API-Key": clinic_api_key},
            json={"phone_number": phone, "password": password},
            timeout=15,
        )
        if response.ok:
            st.session_state.token = response.json()["access_token"]
            st.session_state.clinic_api_key = clinic_api_key
            st.rerun()
        else:
            st.error(response.text)
else:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    st.success("Logged in")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Book appointment")
        doctor_id = st.number_input("Doctor ID", min_value=1, step=1)
        patient_name = st.text_input("Patient name")
        patient_phone = st.text_input("Patient phone")
        appointment_time = st.datetime_input("Appointment time", value=dt.datetime.utcnow() + dt.timedelta(hours=1))
        reason = st.text_area("Reason")

        if st.button("Create appointment"):
            payload = {
                "doctor_id": int(doctor_id),
                "patient_name": patient_name,
                "patient_phone": patient_phone,
                "appointment_time": appointment_time.isoformat(),
                "reason": reason or None,
            }
            response = requests.post(f"{API_BASE_URL}/appointments", headers=headers, json=payload, timeout=15)
            if response.ok:
                st.success("Appointment booked")
            else:
                st.error(response.text)

    with c2:
        st.subheader("Cancel appointment")
        appointment_id = st.number_input("Appointment ID", min_value=1, step=1, key="cancel_id")
        cancel_reason = st.text_input("Cancellation reason")
        if st.button("Cancel appointment"):
            response = requests.post(
                f"{API_BASE_URL}/appointments/{int(appointment_id)}/cancel",
                headers=headers,
                json={"reason": cancel_reason or None},
                timeout=15,
            )
            if response.ok:
                st.success("Appointment canceled")
            else:
                st.error(response.text)

    st.subheader("Appointments")
    response = requests.get(f"{API_BASE_URL}/appointments", headers=headers, timeout=15)
    if response.ok:
        st.dataframe(response.json(), use_container_width=True)
    else:
        st.error(response.text)

    if st.button("Logout"):
        st.session_state.token = None
        st.rerun()
