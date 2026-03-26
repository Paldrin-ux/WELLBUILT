# Well-Built Specialty Contractors — V2 Website
## Premium Flask Web Application

---

## 🚀 QUICK START (5 minutes)

### 1. Prerequisites
- Python 3.9+ installed
- pip (Python package manager)

### 2. Set Up Project

```bash
# Navigate to the project folder
cd wellbuilt_v2

# Create a virtual environment (recommended)
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the App

```bash
python app.py
```

Visit: **http://localhost:5000**

The database (`instance/wellbuilt.db`) is created automatically on first run with sample data.

---

## 🔐 ADMIN PANEL

URL: **http://localhost:5000/admin**

Default credentials:
- **Username:** `admin`
- **Password:** `wellbuilt2025`

> ⚠️ Change the password in `app.py` → `init_db()` before deploying to production.

### Admin Features:
| Section | What You Can Do |
|---------|----------------|
| Dashboard | View stats, recent submissions at a glance |
| Applications | View, filter, update status, delete, open detail modal |
| Projects | Add, edit, delete projects with image upload |
| Media | Upload images/videos, organize by section |

---

## 📁 PROJECT STRUCTURE

```
wellbuilt_v2/
│
├── app.py                     # Flask routes + database logic
├── requirements.txt           # Python dependencies
├── README.md                  # This file
│
├── instance/
│   └── wellbuilt.db           # SQLite database (auto-created)
│
├── static/
│   ├── css/
│   │   ├── style.css          # Public website styles
│   │   └── admin.css          # Admin panel styles
│   ├── js/
│   │   ├── main.js            # Public animations & interactions
│   │   └── admin.js           # Admin panel JS
│   └── uploads/               # Uploaded files (auto-created)
│       ├── projects/          # Project images
│       └── documents/         # Application files (CVs, docs)
│
└── templates/
    ├── base.html              # Shared navbar + footer
    ├── index.html             # Homepage (hero, services, projects, etc.)
    ├── services.html          # Services detail page
    ├── about.html             # About + milestone timeline
    ├── projects.html          # Portfolio with category filter
    ├── contact.html           # Contact info + map placeholder
    ├── apply.html             # Job application / service inquiry form
    └── admin/
        ├── base_admin.html    # Admin sidebar + topbar layout
        ├── login.html         # Admin login page
        ├── dashboard.html     # Stats + recent entries
        ├── applications.html  # All form submissions
        ├── projects.html      # Project list
        ├── project_form.html  # Add / edit project form
        └── media.html         # Media upload + gallery
```

---

## 🗄️ DATABASE TABLES

### `applications`
| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary key |
| full_name | TEXT | Applicant name |
| email | TEXT | Email address |
| phone | TEXT | Phone number |
| type | TEXT | `service` or `job` |
| position_service | TEXT | Selected service or position |
| message | TEXT | Message body |
| file_path | TEXT | Path to uploaded file |
| status | TEXT | `new`, `reviewed`, `closed` |
| created_at | TIMESTAMP | Submission date |

### `projects`
| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary key |
| title | TEXT | Project name |
| category | TEXT | Service category |
| description | TEXT | Project summary |
| image_path | TEXT | Image file path |
| client | TEXT | Client name |
| year | INTEGER | Project year |
| featured | INTEGER | 1 = show on homepage |

### `media`
| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary key |
| title | TEXT | File label |
| file_path | TEXT | Stored path |
| media_type | TEXT | `image` or `video` |
| section | TEXT | hero, projects, about, general |

### `admins`
| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary key |
| username | TEXT | Login username |
| password | TEXT | Login password (plain — hash for production) |

---

## 🌐 ALL ROUTES

### Public
| Route | Template | Description |
|-------|----------|-------------|
| `GET /` | index.html | Homepage |
| `GET /services` | services.html | Services detail |
| `GET /about` | about.html | About + timeline |
| `GET /projects` | projects.html | Portfolio w/ filter |
| `GET /contact` | contact.html | Contact page |
| `GET /apply` | apply.html | Inquiry form |
| `POST /apply` | — | Submit form → saves to DB |

### Admin
| Route | Description |
|-------|-------------|
| `GET /admin` | Redirect to dashboard |
| `GET/POST /admin/login` | Login page |
| `GET /admin/logout` | Logout, clear session |
| `GET /admin` | Dashboard with stats |
| `GET /admin/applications` | All submissions |
| `POST /admin/applications/<id>/status` | Update status |
| `POST /admin/applications/<id>/delete` | Delete record |
| `GET /admin/projects` | All projects |
| `GET/POST /admin/projects/add` | Add new project |
| `GET/POST /admin/projects/<id>/edit` | Edit project |
| `POST /admin/projects/<id>/delete` | Delete project |
| `GET /admin/media` | Media library |
| `POST /admin/media/upload` | Upload media file |
| `POST /admin/media/<id>/delete` | Delete media |

---

## 🏭 PRODUCTION DEPLOYMENT

### 1. Security Hardening
```python
# In app.py — change before going live:
app.secret_key = 'your-strong-random-secret-here'

# Hash passwords (install: pip install werkzeug)
from werkzeug.security import generate_password_hash, check_password_hash
# Store: generate_password_hash('yourpassword')
# Check: check_password_hash(stored_hash, input_password)
```

### 2. Use Gunicorn (Linux/macOS)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### 3. Nginx Reverse Proxy (recommended)
```nginx
server {
    listen 80;
    server_name wellbuiltph.com www.wellbuiltph.com;

    location /static {
        alias /path/to/wellbuilt_v2/static;
        expires 1y;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. Environment Variables (optional)
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-here
```

---

## ✨ DESIGN SYSTEM

### Color Palette
| Token | Value | Use |
|-------|-------|-----|
| `--c-bg` | `#0a0d12` | Main background |
| `--c-bg2` | `#111520` | Section backgrounds |
| `--c-surface` | `#1e2535` | Cards, inputs |
| `--c-gold` | `#c9a84c` | Accent, CTAs, highlights |
| `--c-text` | `#e8ecf4` | Primary text |
| `--c-text-muted` | `#8892a4` | Secondary text |

### Typography
- **Display / Headings:** `Barlow Condensed` — Bold, condensed, industrial authority
- **Body / UI:** `DM Sans` — Clean, readable, modern

### Aesthetic Direction
**Industrial Luxury** — Dark steel backgrounds, sharp gold accents, tight geometry, condensed type. Projects confidence and precision — appropriate for a structural engineering firm.

---

## 📧 OPTIONAL: Add Real Email Notifications

Install Flask-Mail:
```bash
pip install flask-mail
```

Add to `app.py`:
```python
from flask_mail import Mail, Message

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-app-password'
mail = Mail(app)

# In the /apply POST route, after saving to DB:
msg = Message('New Inquiry Received', sender='your@gmail.com', recipients=['admin@wellbuiltph.com'])
msg.body = f"New submission from {full_name} ({email})\nService: {position_service}"
mail.send(msg)
```

---

Built with ❤️ for Well-Built Specialty Contractors, Inc.
#   W E L L B U I L T  
 