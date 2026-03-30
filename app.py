from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, g
import sqlite3
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from werkzeug.utils import secure_filename
from functools import wraps

# ── Base directory ─────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))
app.secret_key = 'wellbuilt_secret_key_2025'

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'mp4', 'webm'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

for d in ['projects', 'documents', 'services', 'cms']:
    os.makedirs(os.path.join(UPLOAD_FOLDER, d), exist_ok=True)

DATABASE = os.path.join(BASE_DIR, 'instance', 'wellbuilt.db')

# ── Email config ───────────────────────────────────────────────────
EMAIL_SENDER   = 'paldrin724@gmail.com'
EMAIL_PASSWORD = 'ifpkrftcqgmzcpbg'
EMAIL_RECEIVER = 'norielcabacungan@gmail.com'
EMAIL_ENABLED  = True

# ══════════════════════════════════════════════════════════════════
#  CMS DEFAULT CONTENT — all hardcoded text lives here as seeds.
#  key format:  page.section.field
# ══════════════════════════════════════════════════════════════════
CMS_DEFAULTS = {
    # ── GLOBAL / NAVBAR ──────────────────────────────────────────
    'global.navbar.logo_image':     '',  # Set via CMS → Global Settings → logo_image
    'global.navbar.logo_text':      'WELL-BUILT',
    'global.navbar.logo_sub':       'SPECIALTY CONTRACTORS',
    'global.navbar.link_home':      'Home',
    'global.navbar.link_services':  'Services',
    'global.navbar.link_about':     'About',
    'global.navbar.link_projects':  'Projects',
    'global.navbar.link_contact':   'Contact',
    'global.navbar.cta_label':      'Get a Quote',

    # ── GLOBAL / FOOTER ──────────────────────────────────────────
    'global.footer.tagline':        'Your Concrete Surgeon and Retrofitting Specialists. Building structural confidence across the Philippines since 2009.',
    'global.footer.copyright':      '© 2025 Well-Built Specialty Contractors, Inc. All rights reserved.',
    'global.footer.cert_line':      'PCAB Licensed | ISO Certified',
    'global.footer.address':        'Metro Manila, Philippines',
    'global.footer.phone':          '+63 (2) 8XXX-XXXX',
    'global.footer.email':          'info@wellbuiltph.com',
    'global.footer.hours':          'Mon–Fri, 8AM–5PM',

    # ── HOME PAGE ─────────────────────────────────────────────────
    'home.hero.eyebrow':            "Philippines' #1 Structural Repair Specialists",
    'home.hero.title_line1':        'BUILT TO',
    'home.hero.title_line2':        'LAST FOREVER.',
    'home.hero.subtitle':           "We don't just fix structures — we fortify them. Trusted by LRTA, SM Prime, Ateneo, and 700+ clients nationwide for concrete repair, retrofitting, and structural strengthening.",
    'home.hero.cta_primary':        'Request a Free Quote',
    'home.hero.cta_secondary':      'View Our Projects',
    'home.hero.badge':              'PCAB Licensed Specialty Contractor',
    'home.hero.stat1_num':          '15',
    'home.hero.stat1_label':        'Years in Business',
    'home.hero.stat2_num':          '700',
    'home.hero.stat2_label':        'Projects Delivered',
    'home.hero.stat3_num':          '50',
    'home.hero.stat3_label':        'Expert Engineers',
    'home.hero.stat4_num':          '200',
    'home.hero.stat4_label':        'Happy Clients',
    'home.hero.bg_image':           '',

    'home.services.eyebrow':        'What We Do',
    'home.services.title':          'Specialized Engineering Services',
    'home.services.desc':           'From initial assessment to full structural restoration — end-to-end solutions backed by decades of certified expertise.',

    'home.about.eyebrow':           'Who We Are',
    'home.about.title':             'The Concrete Surgeons of the Philippines',
    'home.about.body1':             'Founded and led by engineers with deep expertise in structural repair and retrofitting, Well-Built Specialty Contractors has earned the trust of the country\'s most recognized institutions.',
    'home.about.body2':             'Our Technical Team holds active membership in the International Concrete Repair Institute (ICRI) and regularly attends seminars by the American Concrete Institute (ACI).',
    'home.about.cta_story':         'Our Full Story →',
    'home.about.cta_contact':       'Talk to an Engineer',

    'home.projects.eyebrow':        'Our Work',
    'home.projects.title':          'Featured Projects',
    'home.projects.desc':           'A selection of our landmark structural repair and retrofitting projects across the Philippines.',
    'home.projects.cta':            'View All Projects →',

    'home.why.eyebrow':             'Why Well-Built',
    'home.why.title':               'What Sets Us Apart',
    'home.why.card1_num':           '01',
    'home.why.card1_title':         'Technical Excellence',
    'home.why.card1_body':          'Our engineers are certified by international bodies including ICRI and ACI, bringing global best practices to every Philippine project.',
    'home.why.card2_num':           '02',
    'home.why.card2_title':         'Proven Track Record',
    'home.why.card2_body':          '700+ successfully completed projects across industrial, commercial, and infrastructure sectors with zero structural failures.',
    'home.why.card3_num':           '03',
    'home.why.card3_title':         'Innovative Technology',
    'home.why.card3_body':          'We deploy cutting-edge materials including Carbon Fiber Reinforced Polymer (CFRP) and advanced repair systems.',
    'home.why.card4_num':           '04',
    'home.why.card4_title':         'End-to-End Solutions',
    'home.why.card4_body':          'From initial assessment and design to construction and quality assurance — one trusted partner for the entire lifecycle.',

    'home.clients.eyebrow':         'Trusted By',
    'home.clients.title':           'Our Satisfied Clients',
    'home.clients.desc':            "Proudly serving the Philippines' most recognized institutions and corporations.",
    'home.clients.list':            'Ateneo de Manila University|Far Eastern University|LRTA|SM Prime Holdings|Universal Robina Corp.|Robinsons Land Corp.|National Teachers College|MIRDC',

    'home.cta.title':               'Ready to strengthen your structure?',
    'home.cta.body':                'Get a free consultation from our expert engineers. We\'ll assess, design, and deliver the right solution.',
    'home.cta.btn_primary':         'Request a Free Quote',
    'home.cta.btn_secondary':       'Contact Our Team',

    # ── ABOUT PAGE ────────────────────────────────────────────────
    'about.header.eyebrow':         'Our Story',
    'about.header.title':           'About Well-Built',
    'about.header.subtitle':        'A team of engineers with a singular mission — building structural confidence across the Philippines.',
    'about.story.title':            'Who We Are',
    'about.story.body1':            'Well-Built Specialty Contractors, Inc. is a corporation organized, founded, and managed by engineers who possess deep expertise in the finance, operations, and technical aspects of concrete repair — including restoration, retrofitting, and structural strengthening across the Philippines.',
    'about.story.body2':            'With the advent of new technologies and diversification in the construction industry, Well-Built chose to focus on specialized, innovative structural repair technology for industrial, commercial, and residential buildings, bridges, and port facilities.',
    'about.story.body3':            'Our Technical Team of Engineers are active members of the International Concrete Repair Institute (ICRI) and regular attendees of seminars conducted by the American Concrete Institute (ACI).',
    'about.stats.years':            '15+',
    'about.stats.years_label':      'Years in Business',
    'about.stats.projects':         '700+',
    'about.stats.projects_label':   'Projects Delivered',
    'about.stats.engineers':        '50+',
    'about.stats.engineers_label':  'Expert Engineers',
    'about.stats.clients':          '200+',
    'about.stats.clients_label':    'Satisfied Clients',
    'about.timeline.eyebrow':       'Our Journey',
    'about.timeline.title':         'Company Milestones',

    # ── CONTACT PAGE ──────────────────────────────────────────────
    'contact.header.eyebrow':       'Get In Touch',
    'contact.header.title':         'Contact Our Team',
    'contact.header.subtitle':      "We're ready to help. Reach out through any channel below and we'll respond promptly.",
    'contact.info.address':         'No. 43 Turquoise St., Northview 1, Batasan Hills 1126 Quezon City',
    'contact.info.phone1':          '+63 (2) 8XXX-XXXX',
    'contact.info.phone2':          '+63 9XX XXX XXXX',
    'contact.info.email1':          'info@wellbuiltph.com',
    'contact.info.email2':          'projects@wellbuiltph.com',
    'contact.info.hours':           'Monday – Friday: 8:00 AM – 5:00 PM\nSaturday: 8:00 AM – 12:00 PM',
    'contact.map.url':              'https://www.google.com/maps/place/WELL-BUILT+SPECIALTY+CONTRACTORS+INC/@14.6766337,121.128817,17z',
    'contact.cta.title':            'Ready to start a project?',
    'contact.cta.body':             'Use our full inquiry form for faster project assessment and quote generation.',
    'contact.cta.btn':              'Submit an Inquiry →',

    # ── APPLY PAGE ────────────────────────────────────────────────
    'apply.header.eyebrow':         'Get Started',
    'apply.header.title':           'Apply or Request a Service',
    'apply.header.subtitle':        'Fill out the form below and our team will respond within 24–48 business hours.',
    'apply.info.title':             'Why Contact Us?',
    'apply.info.feat1_icon':        '⚡',
    'apply.info.feat1_title':       'Fast Response',
    'apply.info.feat1_body':        'Our team responds within 24-48 hours on business days.',
    'apply.info.feat2_icon':        '🔬',
    'apply.info.feat2_title':       'Expert Assessment',
    'apply.info.feat2_body':        'Certified engineers evaluate your needs personally.',
    'apply.info.feat3_icon':        '📋',
    'apply.info.feat3_title':       'Free Consultation',
    'apply.info.feat3_body':        'Initial site assessment and proposal at no cost.',
    'apply.info.feat4_icon':        '🏆',
    'apply.info.feat4_title':       'Proven Expertise',
    'apply.info.feat4_body':        '15+ years, 700+ completed projects nationwide.',
    'apply.info.phone':             '+63 (2) 8XXX-XXXX',
    'apply.info.email':             'info@wellbuiltph.com',

    # ── SERVICES PAGE ─────────────────────────────────────────────
    'services.header.eyebrow':      'What We Offer',
    'services.header.title':        'Our Services',
    'services.header.subtitle':     'Specialized structural engineering solutions backed by international certifications and two decades of Philippine project experience.',
    'services.cta.title':           'Need a structural assessment or repair?',
    'services.cta.body':            'Talk to our certified engineers. Free initial consultation for qualified projects.',
    'services.cta.btn':             'Request a Free Quote',

    # ── PROJECTS PAGE ─────────────────────────────────────────────
    'projects.header.eyebrow':      'Our Portfolio',
    'projects.header.title':        'Projects & Work',
    'projects.header.subtitle':     'Structural repair, retrofitting, and concrete restoration projects delivered across the Philippines.',
    'projects.cta.title':           'Have a project in mind?',
    'projects.cta.body':            'Our team is ready to assess your structure and deliver the right solution.',
    'projects.cta.btn_primary':     'Request a Quote',
    'projects.cta.btn_secondary':   'Contact Us',

    # ── SECTION VISIBILITY ────────────────────────────────────────
    'home.section.hero.visible':       '1',
    'home.section.trustbar.visible':   '1',
    'home.section.services.visible':   '1',
    'home.section.about.visible':      '1',
    'home.section.projects.visible':   '1',
    'home.section.why.visible':        '1',
    'home.section.clients.visible':    '1',
    'home.section.cta.visible':        '1',
}

# ── SERVICE IMAGE SLOTS ────────────────────────────────────────────
SERVICE_IMAGE_SLOTS = [
    {'key': 'sa-coring',      'label': 'Concrete Coring Works',          'section': 'Structural Assessment'},
    {'key': 'sa-chipping',    'label': 'Actual Chipping / Excavation',   'section': 'Structural Assessment'},
    {'key': 'sa-pulloff',     'label': 'Pull-Off Testing',               'section': 'Structural Assessment'},
    {'key': 'sa-rebound',     'label': 'Rebound Hammer',                 'section': 'Structural Assessment'},
    {'key': 'sa-rebar',       'label': 'Rebar Scanning',                 'section': 'Structural Assessment'},
    {'key': 'sa-ultrasonic',  'label': 'Ultrasonic Pulse Velocity',      'section': 'Structural Assessment'},
    {'key': 'rm-investigation','label': 'Site Investigation & Assessment','section': 'Retrofitting Management'},
    {'key': 'rm-planning',    'label': 'Planning & Scheduling',          'section': 'Retrofitting Management'},
    {'key': 'rm-methodology', 'label': 'Retrofit Methodology',           'section': 'Retrofitting Management'},
    {'key': 'rm-safety',      'label': 'Retrofitting Safety',            'section': 'Retrofitting Management'},
    {'key': 'rcd-jacketing',  'label': 'Steel Jacketing',                'section': 'Retrofitting Construction'},
    {'key': 'rcd-enlargement','label': 'Concrete Enlargement',           'section': 'Retrofitting Construction'},
    {'key': 'rcd-support',    'label': 'Additional Support',             'section': 'Retrofitting Construction'},
    {'key': 'rcd-bracing',    'label': 'Buckling Restrained Bracing',    'section': 'Retrofitting Construction'},
    {'key': 'rcd-carbonplate','label': 'Pre-Stressed Carbon Plate',      'section': 'Retrofitting Construction'},
    {'key': 'rcd-frp',        'label': 'Fiber Reinforced Polymer (FRP)', 'section': 'Retrofitting Construction'},
    {'key': 'cr-cracks',      'label': 'Crack Repair Systems',           'section': 'Concrete Repair'},
    {'key': 'cr-voids',       'label': 'Concrete Voids/Honeycombs',      'section': 'Concrete Repair'},
    {'key': 'cr-grouting',    'label': 'Concrete Grouting Systems',      'section': 'Concrete Repair'},
    {'key': 've-main',        'label': 'Value Engineering',              'section': 'Value Engineering'},
    {'key': 'other-sealant',  'label': 'Sealant Application',            'section': 'Other Services'},
    {'key': 'other-flooring', 'label': 'Industrial Floor Coating',       'section': 'Other Services'},
    {'key': 'other-seismic',  'label': 'Seismic Joint System',           'section': 'Other Services'},
]

# ══════════════════════════════════════════════════════════════════
#  DATABASE
# ══════════════════════════════════════════════════════════════════
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.join(BASE_DIR, 'instance'), exist_ok=True)
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL, email TEXT NOT NULL, phone TEXT NOT NULL,
        type TEXT NOT NULL, position_service TEXT NOT NULL,
        message TEXT, file_path TEXT, status TEXT DEFAULT 'new',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL UNIQUE, category TEXT NOT NULL, description TEXT,
        image_path TEXT, client TEXT, year INTEGER, featured INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL, password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS media (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, file_path TEXT NOT NULL, media_type TEXT NOT NULL,
        section TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS service_images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slot_key TEXT UNIQUE NOT NULL,
        image_path TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    # ── CMS content table ─────────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS cms_content (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content_key TEXT UNIQUE NOT NULL,
        content_value TEXT,
        content_type TEXT DEFAULT 'text',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    # ── About timeline ────────────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS about_timeline (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        year TEXT NOT NULL,
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        sort_order INTEGER DEFAULT 0)''')

    # Seed admins
    c.execute("INSERT OR IGNORE INTO admins (username, password) VALUES (?, ?)", ('admin', 'wellbuilt2025'))

    # Seed CMS defaults
    for key, value in CMS_DEFAULTS.items():
        c.execute("INSERT OR IGNORE INTO cms_content (content_key, content_value) VALUES (?, ?)", (key, value))

    # Seed service image slots
    for slot in SERVICE_IMAGE_SLOTS:
        c.execute("INSERT OR IGNORE INTO service_images (slot_key, image_path) VALUES (?, NULL)", (slot['key'],))

    # Seed sample projects — only runs if the projects table is completely empty
    existing_projects = conn.execute("SELECT COUNT(*) as c FROM projects").fetchone()['c']
    if existing_projects == 0:
        sample_projects = [
            ('LRT-1 Abad Santos Station', 'Retrofitting', 'Concrete repair and structural assessment for the LRT-1 Abad Santos Station.', None, 'LRTA', 2022, 1),
            ('Metro Star Complex', 'Concrete Repair', 'Full concrete restoration and waterproofing services.', None, 'Metrostar', 2021, 1),
            ('MIRDC Building', 'Structural Assessment', 'Comprehensive structural assessment and retrofitting works.', None, 'MIRDC', 2020, 1),
            ('National Teachers College', 'Retrofitting', 'Seismic retrofitting and structural strengthening project.', None, 'NTC', 2023, 1),
            ('Waterfront Hotel', 'Concrete Repair', 'Facade concrete repair and restoration works.', None, 'Waterfront', 2022, 0),
            ('SM Mall Expansion', 'Value Engineering', 'Value engineering consultation for mall expansion project.', None, 'SM Prime', 2023, 1),
        ]
        for p in sample_projects:
            c.execute("INSERT INTO projects (title,category,description,image_path,client,year,featured) VALUES (?,?,?,?,?,?,?)", p)

    # Seed about timeline
    timeline_rows = conn.execute("SELECT COUNT(*) as c FROM about_timeline").fetchone()['c']
    if timeline_rows == 0:
        milestones = [
            ('2009', 'Founded',         'Well-Built Specialty Contractors, Inc. incorporated and began operations in Metro Manila.', 1),
            ('2012', 'ICRI Membership', 'Technical team joined the International Concrete Repair Institute, aligning with global best practices.', 2),
            ('2015', '100th Project',   'Completed our 100th structural repair project, serving clients across Luzon, Visayas, and Mindanao.', 3),
            ('2018', 'FRP Expertise',   'Expanded into Fiber Reinforced Polymer (FRP) and CFRP structural strengthening solutions.', 4),
            ('2022', 'LRTA Partnership','Awarded major retrofitting contract for the LRT-1 infrastructure modernization program.', 5),
            ('2025', '700+ Projects',   'Surpassed 700 completed projects with a team of 50+ certified professional engineers.', 6),
        ]
        for m in milestones:
            c.execute("INSERT INTO about_timeline (year,title,body,sort_order) VALUES (?,?,?,?)", m)

    conn.commit()
    conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

# ══════════════════════════════════════════════════════════════════
#  CMS HELPERS
# ══════════════════════════════════════════════════════════════════
def get_cms(page_prefix=None):
    """Return CMS dict. If page_prefix given, only returns keys for that page + global."""
    conn = get_db()
    if page_prefix:
        rows = conn.execute(
            "SELECT content_key, content_value FROM cms_content WHERE content_key LIKE ? OR content_key LIKE 'global.%'",
            (f'{page_prefix}.%',)
        ).fetchall()
    else:
        rows = conn.execute("SELECT content_key, content_value FROM cms_content").fetchall()
    conn.close()
    result = {}
    for row in rows:
        # Build nested dict: 'home.hero.title' → result['home']['hero']['title']
        parts = row['content_key'].split('.')
        d = result
        for part in parts[:-1]:
            d = d.setdefault(part, {})
        d[parts[-1]] = row['content_value'] or ''
    # Also expose flat dict as cms_flat for simple {{ cms.flat['key'] }} access
    result['_flat'] = {row['content_key']: (row['content_value'] or '') for row in
                       conn.execute("SELECT content_key, content_value FROM cms_content").fetchall()
                       if False}  # placeholder; we requery below
    conn = get_db()
    flat = {row['content_key']: (row['content_value'] or '')
            for row in conn.execute("SELECT content_key, content_value FROM cms_content").fetchall()}
    conn.close()
    result['_flat'] = flat
    return result

def cms_val(key, fallback=''):
    """Quick single-key lookup."""
    conn = get_db()
    row = conn.execute("SELECT content_value FROM cms_content WHERE content_key=?", (key,)).fetchone()
    conn.close()
    return row['content_value'] if row and row['content_value'] is not None else fallback

def get_service_images():
    conn = get_db()
    rows = conn.execute("SELECT slot_key, image_path FROM service_images").fetchall()
    conn.close()
    return {row['slot_key']: row['image_path'] for row in rows}

# ── Inject CMS into every template via context processor ──────────
@app.context_processor
def inject_cms():
    """Makes `cms` and `c` available in ALL templates automatically."""
    flat = {}
    try:
        conn = get_db()
        rows = conn.execute("SELECT content_key, content_value FROM cms_content").fetchall()
        conn.close()
        flat = {row['content_key']: (row['content_value'] or '') for row in rows}
    except Exception:
        pass
    return {'cms': flat, 'c': flat}   # `c` is shorthand alias

# ══════════════════════════════════════════════════════════════════
#  EMAIL
# ══════════════════════════════════════════════════════════════════
def send_notification_email(full_name, email, phone, app_type, position_service, message):
    if not EMAIL_ENABLED:
        return
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'[Well-Built] New {"Service Inquiry" if app_type == "service" else "Job Application"} from {full_name}'
        msg['From']    = EMAIL_SENDER
        msg['To']      = EMAIL_RECEIVER
        type_label  = 'Service Inquiry' if app_type == 'service' else 'Job Application'
        field_label = 'Service Needed'  if app_type == 'service' else 'Position Applied'
        msg_block = f'<div style="margin-top:24px;padding:16px;background:#f9f9f9;border-left:3px solid #c9a84c;border-radius:4px"><p style="font-size:0.78rem;font-weight:bold;color:#888;margin:0 0 8px;letter-spacing:0.1em;text-transform:uppercase">Message</p><p style="color:#333;font-size:0.9rem;line-height:1.65;margin:0">{message}</p></div>' if message else ''
        html_body = f"""<div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f9f9f9;border-radius:8px;overflow:hidden"><div style="background:#0a0d12;padding:28px 32px;text-align:center"><h1 style="color:#c9a84c;font-size:1.4rem;margin:0">WELL-BUILT</h1><p style="color:#8892a4;font-size:0.8rem;margin:6px 0 0">SPECIALTY CONTRACTORS, INC.</p></div><div style="background:#fff;padding:32px"><h2 style="color:#0a0d12;font-size:1.15rem;margin:0 0 6px">New {type_label} Received</h2><p style="color:#888;font-size:0.82rem;margin:0 0 28px">Submitted on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p><table style="width:100%;border-collapse:collapse"><tr style="background:#f5f5f5"><td style="padding:13px 16px;font-size:0.8rem;font-weight:bold;color:#666;width:150px">Full Name</td><td style="padding:13px 16px;font-size:0.9rem;color:#111;font-weight:600">{full_name}</td></tr><tr><td style="padding:13px 16px;font-size:0.8rem;font-weight:bold;color:#666">Email</td><td style="padding:13px 16px;font-size:0.9rem"><a href="mailto:{email}" style="color:#c9a84c">{email}</a></td></tr><tr style="background:#f5f5f5"><td style="padding:13px 16px;font-size:0.8rem;font-weight:bold;color:#666">Phone</td><td style="padding:13px 16px;font-size:0.9rem;color:#111">{phone}</td></tr><tr><td style="padding:13px 16px;font-size:0.8rem;font-weight:bold;color:#666">{field_label}</td><td style="padding:13px 16px;font-size:0.9rem;color:#111">{position_service}</td></tr></table>{msg_block}<div style="margin-top:32px;text-align:center"><a href="http://localhost:5000/admin/applications" style="background:#c9a84c;color:#0a0d12;padding:13px 32px;border-radius:6px;font-weight:bold;font-size:0.9rem;text-decoration:none;display:inline-block">View in Admin Panel →</a></div></div></div>"""
        msg.attach(MIMEText(html_body, 'html'))
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=15) as server:
            server.ehlo(); server.starttls(); server.ehlo()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
    except Exception as e:
        print(f'[Email ERROR] {e}')

# ══════════════════════════════════════════════════════════════════
#  PUBLIC ROUTES
# ══════════════════════════════════════════════════════════════════
@app.route('/')
def index():
    conn     = get_db()
    projects = conn.execute("SELECT * FROM projects WHERE featured=1 ORDER BY year DESC LIMIT 6").fetchall()
    conn.close()
    return render_template('index.html', projects=projects)

@app.route('/services')
def services():
    svc_images = get_service_images()
    return render_template('services.html', svc_images=svc_images)

@app.route('/about')
def about():
    conn     = get_db()
    timeline = conn.execute("SELECT * FROM about_timeline ORDER BY sort_order ASC").fetchall()
    conn.close()
    return render_template('about.html', timeline=timeline)

@app.route('/projects')
def projects():
    conn     = get_db()
    category = request.args.get('category', 'all')
    if category == 'all':
        projs = conn.execute("SELECT * FROM projects ORDER BY year DESC").fetchall()
    else:
        projs = conn.execute("SELECT * FROM projects WHERE category=? ORDER BY year DESC", (category,)).fetchall()
    conn.close()
    return render_template('projects.html', projects=projs, active_category=category)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/apply', methods=['GET', 'POST'])
def apply():
    if request.method == 'POST':
        full_name        = request.form.get('full_name')
        email            = request.form.get('email')
        phone            = request.form.get('phone')
        app_type         = request.form.get('type')
        position_service = request.form.get('position_service')
        message          = request.form.get('message')
        file_path        = None
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename and allowed_file(file.filename):
                filename  = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
                file.save(os.path.join(UPLOAD_FOLDER, 'documents', filename))
                file_path = 'static/uploads/documents/' + filename
        conn = get_db()
        conn.execute("INSERT INTO applications (full_name,email,phone,type,position_service,message,file_path) VALUES (?,?,?,?,?,?,?)",
                     (full_name, email, phone, app_type, position_service, message, file_path))
        conn.commit()
        conn.close()
        send_notification_email(full_name, email, phone, app_type, position_service, message)
        flash('Your submission was received! We will get back to you within 24-48 hours.', 'success')
        return redirect(url_for('apply'))
    return render_template('apply.html')

# ══════════════════════════════════════════════════════════════════
#  ADMIN — AUTH
# ══════════════════════════════════════════════════════════════════
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn     = get_db()
        admin    = conn.execute("SELECT * FROM admins WHERE username=? AND password=?", (username, password)).fetchone()
        conn.close()
        if admin:
            session['admin_logged_in'] = True
            session['admin_username']  = username
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials.', 'error')
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

# ══════════════════════════════════════════════════════════════════
#  ADMIN — DASHBOARD
# ══════════════════════════════════════════════════════════════════
@app.route('/admin')
@login_required
def admin_dashboard():
    conn       = get_db()
    total_apps = conn.execute("SELECT COUNT(*) as c FROM applications").fetchone()['c']
    new_apps   = conn.execute("SELECT COUNT(*) as c FROM applications WHERE status='new'").fetchone()['c']
    total_proj = conn.execute("SELECT COUNT(*) as c FROM projects").fetchone()['c']
    recent     = conn.execute("SELECT * FROM applications ORDER BY created_at DESC LIMIT 5").fetchall()
    conn.close()
    return render_template('admin/dashboard.html',
        total_apps=total_apps, new_apps=new_apps,
        total_projects=total_proj, recent_apps=recent)

# ══════════════════════════════════════════════════════════════════
#  ADMIN — CMS EDITOR
# ══════════════════════════════════════════════════════════════════
@app.route('/admin/cms')
@login_required
def admin_cms():
    """CMS hub — shows all pages."""
    return render_template('admin/cms_hub.html')

@app.route('/admin/cms/<page>', methods=['GET', 'POST'])
@login_required
def admin_cms_page(page):
    """Edit all CMS content for a specific page (e.g. 'home', 'about')."""
    allowed_pages = ['global', 'home', 'about', 'contact', 'apply', 'services', 'projects']
    if page not in allowed_pages:
        flash('Invalid page.', 'error')
        return redirect(url_for('admin_cms'))

    if request.method == 'POST':
        conn = get_db()
        updated = 0
        for key, value in request.form.items():
            if key.startswith(f'{page}.') or key.startswith('global.'):
                conn.execute(
                    "UPDATE cms_content SET content_value=?, updated_at=CURRENT_TIMESTAMP WHERE content_key=?",
                    (value, key)
                )
                updated += 1
        conn.commit()
        conn.close()
        flash(f'Saved {updated} fields successfully.', 'success')
        return redirect(url_for('admin_cms_page', page=page))

    # Load all keys for this page + global
    conn   = get_db()
    rows   = conn.execute(
        "SELECT content_key, content_value FROM cms_content WHERE content_key LIKE ? OR content_key LIKE 'global.%' ORDER BY content_key",
        (f'{page}.%',)
    ).fetchall()
    conn.close()

    # Group by section (e.g. home.hero.*, home.about.*)
    sections = {}
    for row in rows:
        parts   = row['content_key'].split('.')
        section = '.'.join(parts[:2])   # e.g. 'home.hero'
        sections.setdefault(section, []).append({
            'key':   row['content_key'],
            'field': parts[-1],
            'value': row['content_value'] or '',
        })

    return render_template('admin/cms_page.html', page=page, sections=sections)

@app.route('/admin/cms/image-upload', methods=['POST'])
@login_required
def admin_cms_image_upload():
    """Upload a CMS background/section image and save the path to a CMS key."""
    cms_key = request.form.get('cms_key')
    if not cms_key:
        return jsonify({'error': 'No key provided'}), 400
    if 'image' not in request.files:
        return jsonify({'error': 'No file'}), 400
    file = request.files['image']
    if not file or not file.filename or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400
    filename  = secure_filename(f"cms_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
    save_path = os.path.join(UPLOAD_FOLDER, 'cms', filename)
    file.save(save_path)
    db_path   = 'static/uploads/cms/' + filename
    conn = get_db()
    conn.execute(
        "UPDATE cms_content SET content_value=?, updated_at=CURRENT_TIMESTAMP WHERE content_key=?",
        (db_path, cms_key)
    )
    conn.commit()
    conn.close()
    return jsonify({'path': db_path, 'url': '/' + db_path})

# ══════════════════════════════════════════════════════════════════
#  ADMIN — ABOUT TIMELINE
# ══════════════════════════════════════════════════════════════════
@app.route('/admin/cms/timeline')
@login_required
def admin_cms_timeline():
    conn      = get_db()
    timeline  = conn.execute("SELECT * FROM about_timeline ORDER BY sort_order").fetchall()
    conn.close()
    return render_template('admin/cms_timeline.html', timeline=timeline)

@app.route('/admin/cms/timeline/add', methods=['POST'])
@login_required
def admin_cms_timeline_add():
    conn = get_db()
    max_order = conn.execute("SELECT MAX(sort_order) as m FROM about_timeline").fetchone()['m'] or 0
    conn.execute("INSERT INTO about_timeline (year,title,body,sort_order) VALUES (?,?,?,?)",
                 (request.form.get('year'), request.form.get('title'),
                  request.form.get('body'), max_order + 1))
    conn.commit()
    conn.close()
    flash('Milestone added.', 'success')
    return redirect(url_for('admin_cms_timeline'))

@app.route('/admin/cms/timeline/<int:tid>/edit', methods=['POST'])
@login_required
def admin_cms_timeline_edit(tid):
    conn = get_db()
    conn.execute("UPDATE about_timeline SET year=?,title=?,body=? WHERE id=?",
                 (request.form.get('year'), request.form.get('title'),
                  request.form.get('body'), tid))
    conn.commit()
    conn.close()
    flash('Milestone updated.', 'success')
    return redirect(url_for('admin_cms_timeline'))

@app.route('/admin/cms/timeline/<int:tid>/delete', methods=['POST'])
@login_required
def admin_cms_timeline_delete(tid):
    conn = get_db()
    conn.execute("DELETE FROM about_timeline WHERE id=?", (tid,))
    conn.commit()
    conn.close()
    flash('Milestone deleted.', 'success')
    return redirect(url_for('admin_cms_timeline'))

# ══════════════════════════════════════════════════════════════════
#  ADMIN — EXISTING ROUTES (unchanged)
# ══════════════════════════════════════════════════════════════════
@app.route('/admin/applications')
@login_required
def admin_applications():
    conn = get_db()
    apps = conn.execute("SELECT * FROM applications ORDER BY created_at DESC").fetchall()
    conn.close()
    return render_template('admin/applications.html', applications=apps)

@app.route('/admin/applications/<int:app_id>/status', methods=['POST'])
@login_required
def update_app_status(app_id):
    conn = get_db()
    conn.execute("UPDATE applications SET status=? WHERE id=?", (request.form.get('status'), app_id))
    conn.commit(); conn.close()
    return redirect(url_for('admin_applications'))

@app.route('/admin/applications/<int:app_id>/delete', methods=['POST'])
@login_required
def delete_application(app_id):
    conn = get_db()
    conn.execute("DELETE FROM applications WHERE id=?", (app_id,))
    conn.commit(); conn.close()
    flash('Application deleted.', 'success')
    return redirect(url_for('admin_applications'))

@app.route('/admin/projects')
@login_required
def admin_projects():
    conn     = get_db()
    projects = conn.execute("SELECT * FROM projects ORDER BY created_at DESC").fetchall()
    conn.close()
    return render_template('admin/projects.html', projects=projects)

@app.route('/admin/projects/add', methods=['GET', 'POST'])
@login_required
def admin_add_project():
    if request.method == 'POST':
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename  = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
                file.save(os.path.join(UPLOAD_FOLDER, 'projects', filename))
                image_path = 'static/uploads/projects/' + filename
        conn = get_db()
        conn.execute("INSERT INTO projects (title,category,description,image_path,client,year,featured) VALUES (?,?,?,?,?,?,?)",
                     (request.form.get('title'), request.form.get('category'), request.form.get('description'),
                      image_path, request.form.get('client'), request.form.get('year'),
                      1 if request.form.get('featured') else 0))
        conn.commit(); conn.close()
        flash('Project added.', 'success')
        return redirect(url_for('admin_projects'))
    return render_template('admin/project_form.html', project=None)

@app.route('/admin/projects/<int:proj_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_project(proj_id):
    conn    = get_db()
    project = conn.execute("SELECT * FROM projects WHERE id=?", (proj_id,)).fetchone()
    if request.method == 'POST':
        image_path = project['image_path']
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename  = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
                file.save(os.path.join(UPLOAD_FOLDER, 'projects', filename))
                image_path = 'static/uploads/projects/' + filename
        conn.execute("UPDATE projects SET title=?,category=?,description=?,image_path=?,client=?,year=?,featured=? WHERE id=?",
                     (request.form.get('title'), request.form.get('category'), request.form.get('description'),
                      image_path, request.form.get('client'), request.form.get('year'),
                      1 if request.form.get('featured') else 0, proj_id))
        conn.commit(); conn.close()
        flash('Project updated.', 'success')
        return redirect(url_for('admin_projects'))
    conn.close()
    return render_template('admin/project_form.html', project=project)

@app.route('/admin/projects/<int:proj_id>/delete', methods=['POST'])
@login_required
def admin_delete_project(proj_id):
    conn = get_db()
    conn.execute("DELETE FROM projects WHERE id=?", (proj_id,))
    conn.commit(); conn.close()
    flash('Project deleted.', 'success')
    return redirect(url_for('admin_projects'))

@app.route('/admin/media')
@login_required
def admin_media():
    conn  = get_db()
    media = conn.execute("SELECT * FROM media ORDER BY created_at DESC").fetchall()
    conn.close()
    return render_template('admin/media.html', media=media)

@app.route('/admin/media/upload', methods=['POST'])
@login_required
def admin_upload_media():
    if 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename   = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
            ext        = filename.rsplit('.', 1)[1].lower()
            media_type = 'video' if ext in ['mp4', 'webm'] else 'image'
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            conn = get_db()
            conn.execute("INSERT INTO media (title,file_path,media_type,section) VALUES (?,?,?,?)",
                         (request.form.get('title', file.filename), 'static/uploads/'+filename,
                          media_type, request.form.get('section', 'general')))
            conn.commit(); conn.close()
            flash('Media uploaded.', 'success')
    return redirect(url_for('admin_media'))

@app.route('/admin/media/<int:media_id>/delete', methods=['POST'])
@login_required
def admin_delete_media(media_id):
    conn = get_db()
    conn.execute("DELETE FROM media WHERE id=?", (media_id,))
    conn.commit(); conn.close()
    flash('Media deleted.', 'success')
    return redirect(url_for('admin_media'))

# ── Service images ─────────────────────────────────────────────────
@app.route('/admin/service-images')
@login_required
def admin_service_images():
    conn      = get_db()
    rows      = conn.execute("SELECT slot_key, image_path FROM service_images").fetchall()
    conn.close()
    db_images = {row['slot_key']: row['image_path'] for row in rows}
    slots     = [{'key': s['key'], 'label': s['label'], 'section': s['section'],
                  'image_path': db_images.get(s['key'])} for s in SERVICE_IMAGE_SLOTS]
    sections  = {}
    for slot in slots:
        sections.setdefault(slot['section'], []).append(slot)
    return render_template('admin/service_images.html', sections=sections)

@app.route('/admin/service-images/<slot_key>/upload', methods=['POST'])
@login_required
def admin_upload_service_image(slot_key):
    valid_keys = {s['key'] for s in SERVICE_IMAGE_SLOTS}
    if slot_key not in valid_keys:
        flash('Invalid slot.', 'error')
        return redirect(url_for('admin_service_images'))
    file = request.files.get('image')
    if not file or not file.filename or not allowed_file(file.filename):
        flash('Invalid file.', 'error')
        return redirect(url_for('admin_service_images'))
    filename  = secure_filename(f"svc_{slot_key}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
    file.save(os.path.join(UPLOAD_FOLDER, 'services', filename))
    conn = get_db()
    conn.execute("UPDATE service_images SET image_path=?,updated_at=CURRENT_TIMESTAMP WHERE slot_key=?",
                 ('static/uploads/services/'+filename, slot_key))
    conn.commit(); conn.close()
    flash('Image updated.', 'success')
    return redirect(url_for('admin_service_images') + f'#{slot_key}')

@app.route('/admin/service-images/<slot_key>/delete', methods=['POST'])
@login_required
def admin_delete_service_image(slot_key):
    conn = get_db()
    conn.execute("UPDATE service_images SET image_path=NULL WHERE slot_key=?", (slot_key,))
    conn.commit(); conn.close()
    flash('Image removed.', 'success')
    return redirect(url_for('admin_service_images'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)