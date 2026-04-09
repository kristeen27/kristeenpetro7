# Hospital Appointment SaaS (FastAPI + Streamlit)

Production-ready starter template for a **multi-clinic AI-enabled appointment system**.

## 1) Project structure

```text
.
├── app
│   ├── core
│   │   └── config.py
│   ├── routers
│   │   ├── appointments.py
│   │   ├── clinics.py
│   │   ├── doctors.py
│   │   ├── users.py
│   │   └── vapi.py
│   ├── services
│   │   ├── appointment_service.py
│   │   └── notification_service.py
│   ├── auth.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── frontend
│   └── streamlit_app.py
├── scripts
│   └── seed_sample_data.py
├── tests
│   └── test_health.py
├── requirements.txt
└── README.md
```

## 2) Environment variables

Create a `.env` file in project root:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/hospital_saas
JWT_SECRET_KEY=replace_with_strong_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
ENVIRONMENT=dev
WHATSAPP_ACCESS_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=
```

## 3) Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# start api
uvicorn app.main:app --reload

# seed demo data
python scripts/seed_sample_data.py

# streamlit dashboard
streamlit run frontend/streamlit_app.py
```

## 4) API summary

- `POST /users` -> create user within clinic (requires `X-Clinic-API-Key`)
- `POST /users/login` -> mobile + password login (requires `X-Clinic-API-Key`)
- `GET /users/me` -> current user using JWT
- `POST /doctors` -> create doctor (admin only)
- `GET /doctors` -> list doctors for clinic
- `POST /appointments` -> schedule
- `POST /appointments/{id}/cancel` -> cancel
- `GET /appointments` -> filter by `date_from`, `date_to`, `doctor_id`, `status`
- `POST /vapi/schedule` -> AI webhook scheduling
- `POST /vapi/cancel` -> AI webhook cancellation

## 5) Multi-tenant data isolation

This project uses **clinic-scoped tenancy**:

1. Every major table has `clinic_id` foreign key.
2. User login requires clinic API key header (`X-Clinic-API-Key`) + phone/password.
3. JWT stores `clinic_id` claim.
4. Every business query filters by authenticated user's `clinic_id`.
5. Vapi webhook requests must include `clinic_api_key`, mapped to exactly one clinic.

Result: users and AI webhooks can only view/mutate appointments from their own clinic.

## 6) WhatsApp notification design

`app/services/notification_service.py` is the integration seam. Currently logs events (`appointment_booked`, `appointment_canceled`).
Replace logger implementation with Meta Graph API call using environment variables.

## 7) Testing

```bash
pytest -q
```

## 8) Deployment

### Render
1. Create PostgreSQL instance in Render.
2. Create Web Service from repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add env vars (`DATABASE_URL`, `JWT_SECRET_KEY`, etc.).
6. Run migration strategy (this template uses startup `create_all`; for advanced production use Alembic).

### AWS (ECS/Fargate high-level)
1. Containerize app with Python 3.11 image.
2. Use RDS PostgreSQL.
3. Store secrets in AWS Secrets Manager or SSM.
4. Run FastAPI behind ALB.
5. Configure autoscaling + CloudWatch logs.
6. Deploy Streamlit separately (ECS or EC2) or replace with React frontend.

## 9) Security checklist

- Strong `JWT_SECRET_KEY`
- Force HTTPS in load balancer
- Rotate clinic API keys on compromise
- Rate-limit login and webhook endpoints
- Replace `create_all` with migrations (Alembic)
- Add audit logs and Sentry in production
