import json
import os
import urllib.parse
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
from PIL import Image
import io

# ==========================================
# --- إعدادات الصفحة العامة ---
# ==========================================
st.set_page_config(
    page_title="Jawhara Repair System",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# --- CSS لتحسين الشكل بالكامل ---
# ==========================================
st.markdown("""
<style>
    /* إخفاء العناصر الزائدة */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* تنسيق الشريط الجانبي */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        padding-top: 2rem;
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] .stRadio label {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #FFD700 !important;
    }
    
    /* تنسيق الأزرار */
    .stButton > button {
        background: linear-gradient(90deg, #1f538d, #2c3e6d);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        background: linear-gradient(90deg, #2c3e6d, #1f538d);
    }
    
    /* تنسيق البطاقات */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
    }
    
    [data-testid="stMetric"] label {
        color: rgba(255,255,255,0.9);
        font-size: 0.9rem;
    }
    
    [data-testid="stMetric"] .stMetricValue {
        color: white;
        font-size: 2rem;
        font-weight: bold;
    }
    
    /* تنسيق حقول الإدخال */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #1f538d;
        box-shadow: 0 0 0 2px rgba(31,83,141,0.2);
    }
    
    /* تنسيق الجداول */
    [data-testid="stDataFrame"] table,
    [data-testid="stTable"] table {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    }
    
    [data-testid="stDataFrame"] th {
        background: linear-gradient(90deg, #1f538d, #2c3e6d);
        color: white;
        padding: 12px;
        font-weight: 600;
    }
    
    [data-testid="stDataFrame"] td {
        padding: 10px;
        border-bottom: 1px solid #eee;
    }
    
    /* تنسيق التنبيهات */
    .stAlert {
        border-radius: 12px;
        border-left: 5px solid;
        animation: slideIn 0.5s ease;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* رأس الصفحة */
    .main-header {
        background: linear-gradient(120deg, #1f538d, #2c3e6d, #1f538d);
        background-size: 200% 200%;
        animation: gradientBG 5s ease infinite;
        padding: 1.5rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .main-header h1 {
        color: white;
        font-size: 2rem;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1rem;
    }
    
    /* سكرول بار */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(90deg, #1f538d, #2c3e6d);
        border-radius: 10px;
    }
    
    /* تأثيرات حركية */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    [data-testid="stMetric"], 
    .stButton > button,
    .stAlert {
        animation: fadeInUp 0.5s ease forwards;
    }
    
    /* تنسيق الصور */
    .image-container {
        cursor: pointer;
        transition: transform 0.3s;
        display: inline-block;
    }
    
    .image-container:hover {
        transform: scale(1.02);
    }
    
    .fullscreen-img {
        max-width: 90vw;
        max-height: 80vh;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    /* أيقونة المتصفح */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
</style>

<head>
    <title>Jawhara Repair System</title>
    <link rel="icon" type="image/x-icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90' fill='%231f538d'>💎</text></svg>">
</head>
""", unsafe_allow_html=True)

# ==========================================
# --- إدارة الكوكيز (تذكر الدخول لمدة 3 أيام) ---
# ==========================================
def set_login_cookie(branch_name, is_super_admin=False):
    """حفظ بيانات الدخول في الكوكيز لمدة 3 أيام"""
    expiry_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
    cookie_data = {
        "branch": branch_name,
        "is_super_admin": is_super_admin,
        "expiry": expiry_date
    }
    st.session_state["login_cookie"] = cookie_data

def get_login_cookie():
    """استرجاع بيانات الدخول من الكوكيز إذا كانت صالحة"""
    if "login_cookie" in st.session_state:
        cookie = st.session_state["login_cookie"]
        try:
            expiry = datetime.strptime(cookie.get("expiry", "2000-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S")
            if datetime.now() < expiry:
                return cookie.get("branch"), cookie.get("is_super_admin", False)
        except:
            pass
    return None, False

def clear_login_cookie():
    """مسح الكوكيز عند تسجيل الخروج"""
    if "login_cookie" in st.session_state:
        del st.session_state["login_cookie"]

# ==========================================
# --- المجلدات والملفات المحلية ---
# ==========================================
DATA_FILE = "repair_bags.json"
LOG_FILE = "actions_log.json"
CONFIG_FILE = "app_config.json"
BRANCH_FILE = "branch_settings.json"
LOGIN_HIST_FILE = "login_history.json"
IMAGE_DIR = "uploaded_images"

for file in [DATA_FILE, LOG_FILE, CONFIG_FILE, LOGIN_HIST_FILE]:
    if not os.path.exists(file):
        with open(file, "w", encoding="utf-8") as f:
            json.dump([] if file != CONFIG_FILE else {"store_name": "Jawhara Yas Mall"}, f, ensure_ascii=False, indent=4)

if not os.path.exists(BRANCH_FILE):
    with open(BRANCH_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=4)

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR, exist_ok=True)

SUPER_ADMIN_PASSWORD = "9999"
COUNTRY_CODES = ["+971", "+20", "+966", "+965", "+974", "+973", "+968", "+1", "+44"]
STATUS_OPTIONS = ["Received", "Out for Repair", "Received Back", "Delivered"]

HARDCODED_BRANCHES = {
    "Yas Mall": {"password": "0000"}, "Al Dhafra Mall": {"password": "0000"}, "Khalidiyah Mall": {"password": "0000"},
    "Marina Mall": {"password": "0000"}, "Mushrif Mall": {"password": "0000"}, "Reem Mall": {"password": "0000"},
    "Galleria Mall": {"password": "0000"}, "Raha Mall": {"password": "0000"}, "Maqtaa Mall": {"password": "0000"},
    "Bawabat Al Sharq Mall": {"password": "0000"}, "Deerfields Mall": {"password": "0000"}, "Dalma Mall": {"password": "0000"},
    "Forsan Mall": {"password": "0000"}, "Al Wahda Mall": {"password": "0000"}, "Abu Dhabi Mall": {"password": "0000"},
    "MZ1 Shop": {"password": "0000"}, "MZ2 Shop": {"password": "0000"}, "Masdar CC Mall": {"password": "0000"},
    "Fairuz Dalma Mall": {"password": "0000"}, "Makani Shamkha Mall": {"password": "0000"}, "Madinati Mall": {"password": "0000"}
}

# ==========================================
# --- دوال مساعدة ---
# ==========================================
def safe_float_convert(val):
    try:
        return float(str(val).replace(',', ''))
    except (ValueError, TypeError):
        return 0.0

def safe_int_convert(val):
    try:
        return int(str(val).replace(',', ''))
    except (ValueError, TypeError):
        return 0

def parse_date(date_string):
    try:
        return datetime.strptime(date_string, "%Y-%m-%d").date() if date_string else datetime.today().date()
    except (ValueError, TypeError):
        return datetime.today().date()

def format_whatsapp_number(country_code, mobile):
    mobile_clean = str(mobile).strip().lstrip('0')
    return f"{country_code.replace('+', '')}{mobile_clean}"

def load_json_pure(file_path, default_val=[]):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default_val

def save_json_pure(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def db_load_branches():
    branches = load_json_pure(BRANCH_FILE, {})
    if not branches:
        save_json_pure(BRANCH_FILE, HARDCODED_BRANCHES)
        return HARDCODED_BRANCHES
    return branches

def db_update_branch_password(branch_name, new_pass):
    branches = db_load_branches()
    if branch_name in branches:
        branches[branch_name]["password"] = new_pass
        save_json_pure(BRANCH_FILE, branches)

def db_add_new_branch(branch_name, password):
    branches = db_load_branches()
    branches[branch_name] = {"password": password}
    save_json_pure(BRANCH_FILE, branches)

def load_config():
    return load_json_pure(CONFIG_FILE, {"store_name": "Jawhara Yas Mall"})

def save_config(config):
    save_json_pure(CONFIG_FILE, config)

def load_data():
    return load_json_pure(DATA_FILE, [])

def save_data(data):
    save_json_pure(DATA_FILE, data)

def load_logs():
    return load_json_pure(LOG_FILE, [])

def add_to_log(bag_number, customer_name, action, branch_name="System"):
    logs = load_logs()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logs.append({"time": now, "bag": str(bag_number), "customer": customer_name, "action": action, "branch": branch_name})
    save_json_pure(LOG_FILE, logs)

def db_load_login_history():
    return load_json_pure(LOGIN_HIST_FILE, [])

def db_add_login_history(branch_name, login_type):
    hist = db_load_login_history()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hist.append({"time": now_str, "branch": branch_name, "type": login_type})
    save_json_pure(LOGIN_HIST_FILE, hist)

# ==========================================
# --- إدارة حالة الجلسة ---
# ==========================================
if "language" not in st.session_state:
    st.session_state.language = "en"
if "current_edit_index" not in st.session_state:
    st.session_state.current_edit_index = None
if "selected_row_idx" not in st.session_state:
    st.session_state.selected_row_idx = 0
if "active_menu" not in st.session_state:
    st.session_state.active_menu = "Add Bag"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_branch" not in st.session_state:
    st.session_state.current_branch = None
if "last_branch_selection" not in st.session_state:
    st.session_state.last_branch_selection = "Yas Mall"
if "is_super_admin" not in st.session_state:
    st.session_state.is_super_admin = False
if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = False
if "delete_target_index" not in st.session_state:
    st.session_state.delete_target_index = None

# محاولة استرجاع بيانات الدخول المحفوظة
if not st.session_state.logged_in:
    saved_branch, saved_super = get_login_cookie()
    if saved_branch:
        branches_data_cloud = db_load_branches()
        if saved_branch in branches_data_cloud:
            st.session_state.logged_in = True
            st.session_state.current_branch = saved_branch
            st.session_state.last_branch_selection = saved_branch
            st.session_state.is_super_admin = saved_super

# تحميل البيانات
app_config = load_config()
branches_data_cloud = db_load_branches()

# ==========================================
# --- قاموس الترجمة ---
# ==========================================
def tr(text):
    translations = {
        "Customer Name": "اسم العميل", "Bag Number": "رقم الحقيبة", "Mobile": "رقم الهاتف",
        "Status": "الحالة", "Date": "التاريخ", "Notes": "ملاحظات", "Add": "إضافة / حفظ",
        "Cost": "التكلفة", "Urgent": "مستعجل ⚡", "Stats": "إحصائيات", "All": "الكل",
        "Edit": "تعديل", "Delete": "حذف", "Search By Name": "بحث بالاسم",
        "Search By Bag": "بحث بالرقم", "Search By Mobile": "بحث بالموبايل",
        "Alerts": "التنبيهات 📢", "Filter Status:": "تصفية الحالة:", "Update": "تحديث البيانات",
        "Send Reminder": "إرسال تذكير 🔔", "Reminders": "التذكيرات", "Total Bags": "إجمالي الباجات",
        "Collected": "تم تحصيله", "Received": "استلام", "Out Repair": "خروج تصليح",
        "Back in Store": "وصل المحل", "Delivered": "تم التسليم", "Add Bag": "إضافة باج",
        "View / Stats": "عرض / تصفية", "Income": "الدخل", "In Store": "في المحل",
        "Monthly Performance": "الأداء الشهري", "View Action Logs 📜": "عرض سجل العمليات 📜",
        "System Logs": "سجلات النظام", "All Actions History": "تاريخ كل العمليات",
        "Time": "الوقت", "Bag #": "رقم الباج", "Customer": "العميل", "Action": "العملية",
        "Days Overdue": "الأيام المتأخرة", "Urgent Bags Overdue (7+ Days)": "الباجات المستعجلة المتأخرة (7+ أيام)",
        "Normal Bags Overdue (15+ Days)": "الباجات العادية المتأخرة (15+ يوم)",
        "Store Name Settings": "إعدادات اسم المحل", "Change Store Name": "تغيير اسم المحل / الفرع",
        "Save Settings": "حفظ الإعدادات", "Customer ID": "رقم هوية الزبون", "Receipt Image": "صورة الاستلام",
        "Manage & Details 📝": "إدارة وتفاصيل الباج 📝", "Branch Settings": "إعدادات الفرع الأمنية",
        "Change Password": "تغيير كلمة المرور الخاصة بالفرع", "Old Password": "كلمة المرور القديمة",
        "New Password": "كلمة المرور الجديدة", "Save Password": "حفظ كلمة المرور الجديدة",
        "Login History": "سجل دخول الأجهزة للفروع", "Branch": "الفرع", "Logout": "تسجيل الخروج 🚪",
        "Add New Branch": "إضافة فرع جديد للسيستم 🏢", "Branch Name": "اسم الفرع الجديد", "Branch Password": "باسورد الفرع الجديد",
        "Super Backup": "نسخة احتياطية كاملة للشركة 📥", "Confirm Delete": "تأكيد الحذف",
        "Are you sure you want to delete this bag?": "هل أنت متأكد من حذف هذه الحقيبة؟",
        "Yes, Delete": "نعم، احذف", "Cancel": "إلغاء"
    }
    return translations.get(text, text) if st.session_state.language == "ar" else text

# ==========================================
# --- نافذة عرض الصورة بحجم كامل ---
# ==========================================
@st.dialog("📸 الصورة بحجم كامل", width="large")
def show_fullscreen_image(image_path):
    """عرض الصورة بحجم كامل عند الضغط عليها"""
    if os.path.exists(image_path):
        image = Image.open(image_path)
        st.image(image, use_container_width=True)
        st.caption("🔍 يمكنك الضغط على الصورة لتكبيرها أكثر في المتصفح")
    else:
        st.error("الصورة غير موجودة")

def display_image_with_click(img_path):
    """عرض صورة قابلة للضغط لفتحها بحجم كامل"""
    if img_path and os.path.exists(img_path):
        image = Image.open(img_path)
        # عرض صورة مصغرة للضغط عليها
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(image, width=250, caption="📸 اضغط على الصورة لتكبيرها")
            if st.button("🔍 فتح الصورة بحجم كامل", key=f"view_full_{img_path}"):
                show_fullscreen_image(img_path)
    else:
        st.info("لا توجد صورة مرفقة")

# ==========================================
# --- نافذة تأكيد الحذف ---
# ==========================================
@st.dialog(tr("Confirm Delete"))
def confirm_delete_dialog(bag_index, bag_number, customer_name):
    st.warning(f"{tr('Are you sure you want to delete this bag?')}\n\n**{tr('Bag Number')}:** {bag_number}\n**{tr('Customer Name')}:** {customer_name}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button(tr("Yes, Delete"), type="primary", use_container_width=True):
            add_to_log(bag_number, customer_name, "Record Deleted", st.session_state.current_branch)
            bags_data = load_data()
            if bag_index < len(bags_data):
                bags_data.pop(bag_index)
                save_data(bags_data)
            st.session_state.selected_row_idx = 0
            st.session_state.confirm_delete = False
            st.session_state.delete_target_index = None
            st.success("Deleted successfully!")
            st.rerun()
    with col2:
        if st.button(tr("Cancel"), use_container_width=True):
            st.session_state.confirm_delete = False
            st.session_state.delete_target_index = None
            st.rerun()

# ==========================================
# --- نافذة تفاصيل الباج (جودة عالية للصور) ---
# ==========================================
@st.dialog("Bag Extra Details & Management", width="large")
def show_bag_details_dialog(index_in_json):
    bags_fresh = load_data()
    if index_in_json >= len(bags_fresh):
        st.error("Bag not found!")
        return
    b = bags_fresh[index_in_json]
    st.write(f"### 💎 {tr('Bag Number')}: {b['bag_number']}")
    st.write(f"**{tr('Customer Name')}:** {b['customer_name']}")
    st.markdown("---")
    
    cust_id = st.text_input(tr("Customer ID"), value=b.get("customer_id", ""))
    
    st.write("📸 **اختر مصدر الصورة (بدقة عالية):**")
    img_source = st.radio("Source", ["رفع ملف (من الجهاز)", "تصوير بالكاميرا"], label_visibility="collapsed")
    
    uploaded_file = None
    camera_file = None
    if img_source == "رفع ملف (من الجهاز)":
        uploaded_file = st.file_uploader(tr("Receipt Image"), type=["jpg", "jpeg", "png"])
    else:
        camera_file = st.camera_input("تصوير الإيصال")
    
    # عرض الصورة الحالية مع إمكانية تكبيرها
    img_path = b.get("image_path", "")
    if img_path and os.path.exists(img_path):
        st.write(f"**{tr('Receipt Image')}:**")
        display_image_with_click(img_path)
            
    if st.button(tr("Add") + " / " + tr("Update"), type="primary"):
        b["customer_id"] = cust_id.strip()
        
        # حفظ الصورة بجودة عالية
        if camera_file is not None:
            saved_img_name = f"bag_{b['bag_number']}.png"
            full_save_path = os.path.join(IMAGE_DIR, saved_img_name)
            # حفظ بجودة عالية
            image = Image.open(camera_file)
            image.save(full_save_path, "PNG", quality=100, optimize=False)
            b["image_path"] = full_save_path
        elif uploaded_file is not None:
            file_ext = os.path.splitext(uploaded_file.name)[1]
            saved_img_name = f"bag_{b['bag_number']}{file_ext}"
            full_save_path = os.path.join(IMAGE_DIR, saved_img_name)
            # حفظ بجودة عالية
            image = Image.open(uploaded_file)
            if file_ext.lower() in ['.jpg', '.jpeg']:
                image.save(full_save_path, "JPEG", quality=100, optimize=False)
            else:
                image.save(full_save_path, "PNG", quality=100, optimize=False)
            b["image_path"] = full_save_path
            
        bags_fresh[index_in_json] = b
        save_data(bags_fresh)
        add_to_log(b['bag_number'], b['customer_name'], "Extra details/Image updated", st.session_state.current_branch)
        st.success("Saved successfully with high quality!")
        st.rerun()

# ==========================================
# --- شاشة تسجيل الدخول ---
# ==========================================
if not st.session_state.logged_in:
    st.markdown('<div class="main-header"><h1>💎 Jawhara Management System</h1><p>RepairBag Pro Enterprise Multi-Branch 2026</p></div>', unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.write("### 🔑 Branch Secure Login")
        branches_list = list(branches_data_cloud.keys())
        try:
            last_idx = branches_list.index(st.session_state.last_branch_selection)
        except:
            last_idx = 0
        selected_branch = st.selectbox("Choose Branch / اختر الفرع", branches_list, index=last_idx)
        password_input = st.text_input("Enter Password / أدخل كلمة المرور", type="password")
        
        col_rem1, col_rem2 = st.columns(2)
        with col_rem1:
            remember_me = st.checkbox("تذكرني لمدة 3 أيام", value=True)
        
        if st.button("Login / دخول", type="primary", use_container_width=True):
            correct_password = branches_data_cloud.get(selected_branch, {}).get("password", "0000")
            if password_input == correct_password or password_input == SUPER_ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.session_state.current_branch = selected_branch
                st.session_state.last_branch_selection = selected_branch
                st.session_state.is_super_admin = (password_input == SUPER_ADMIN_PASSWORD)
                
                if remember_me:
                    set_login_cookie(selected_branch, st.session_state.is_super_admin)
                
                db_add_login_history(selected_branch, "Super Admin Bypass" if st.session_state.is_super_admin else "Standard Branch Login")
                st.success(f"Welcome back, {selected_branch}!")
                st.rerun()
            else:
                st.error("Incorrect Password! Please try again.")
    st.stop()

# تحميل البيانات بعد شاشة الدخول
bags_data = load_data()
actions_log = load_logs()
is_super_user = st.session_state.is_super_admin

menu_mapping = {
    tr("Add Bag"): "Add Bag",
    tr("View / Stats"): "View / Stats",
    tr("Alerts"): "Alerts",
    tr("Stats"): "Stats"
}
menu_options = list(menu_mapping.keys())

try:
    current_idx = list(menu_mapping.values()).index(st.session_state.active_menu)
except:
    current_idx = 0

# ==========================================
# --- القائمة الجانبية ---
# ==========================================
with st.sidebar:
    st.markdown(f"## 💎 {st.session_state.current_branch}")
    st.caption("Connected to Secure Local JSON Database 📂")
    st.markdown("---")
    
    choice_translated = st.radio("Navigation", menu_options, index=current_idx, label_visibility="collapsed")
    st.session_state.active_menu = menu_mapping[choice_translated]
    choice = st.session_state.active_menu
    
    st.markdown("---")
    lang_choice = st.selectbox("Language / اللغة", ["English", "العربية"], index=0 if st.session_state.language == "en" else 1)
    new_lang = "ar" if lang_choice == "العربية" else "en"
    if new_lang != st.session_state.language:
        st.session_state.language = new_lang
        st.rerun()
        
    st.markdown("---")
    with st.expander(tr("Branch Settings")):
        st.write(f"**{tr('Branch')}:** {st.session_state.current_branch}")
        old_p = st.text_input(tr("Old Password"), type="password")
        new_p = st.text_input(tr("New Password"), type="password")
        if st.button(tr("Save Password"), use_container_width=True):
            actual_old = branches_data_cloud.get(st.session_state.current_branch, {}).get("password", "0000")
            if old_p == actual_old or old_p == SUPER_ADMIN_PASSWORD:
                if len(new_p.strip()) > 0:
                    db_update_branch_password(st.session_state.current_branch, new_p.strip())
                    st.success("Password updated successfully!")
                else:
                    st.error("Password cannot be empty!")
            else:
                st.error("Incorrect Old Password!")
            
        if is_super_user:
            st.markdown("---")
            st.write(tr("Add New Branch"))
            new_b_name = st.text_input(tr("Branch Name"))
            new_b_pass = st.text_input(tr("Branch Password"), type="password")
            if st.button(tr("Add") + " Branch", use_container_width=True):
                if new_b_name.strip() and new_b_pass.strip():
                    db_add_new_branch(new_b_name.strip(), new_b_pass.strip())
                    st.success(f"Branch '{new_b_name}' added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill in branch name and password!")

    st.markdown("---")
    if st.button(tr("Logout"), type="primary", use_container_width=True):
        clear_login_cookie()
        st.session_state.logged_in = False
        st.session_state.current_branch = None
        st.session_state.is_super_admin = False
        st.session_state.current_edit_index = None
        st.session_state.selected_row_idx = 0
        st.rerun()

# ==========================================
# --- عرض الهيدر الجميل ---
# ==========================================
st.markdown('<div class="main-header"><h1>💎 Jawhara Management System</h1><p>RepairBag Pro Enterprise | Multi-Branch Solution 2026</p></div>', unsafe_allow_html=True)

# ==========================================
# --- القسم الأول: إضافة وتعديل باج ---
# ==========================================
if choice == "Add Bag":
    st.header(tr("Add Bag") if st.session_state.current_edit_index is None else tr("Update"))
    edit_idx = st.session_state.current_edit_index
    default_rec = bags_data[edit_idx] if edit_idx is not None and edit_idx < len(bags_data) else {}
    
    with st.form("bag_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            cust_name = st.text_input(tr("Customer Name"), value=default_rec.get("customer_name", ""))
            bag_no = st.text_input(tr("Bag Number"), value=default_rec.get("bag_number", ""))
            cost = st.text_input(tr("Cost"), value=str(default_rec.get("cost", "0")))
        with c2:
            is_urgent = st.checkbox(tr("Urgent"), value=bool(default_rec.get("is_urgent", False)))
            status_date = st.date_input(tr("Date"), value=parse_date(default_rec.get("status_date", "")))
            
            mob_col1, mob_col2 = st.columns([1, 2])
            with mob_col1:
                try:
                    def_code_idx = COUNTRY_CODES.index(default_rec.get("country_code", "+971"))
                except:
                    def_code_idx = 0
                country_code = st.selectbox("Code", COUNTRY_CODES, index=def_code_idx)
            with mob_col2:
                mob_num = st.text_input(tr("Mobile"), value=default_rec.get("customer_mobile", ""))
                
        status = st.selectbox(tr("Status"), STATUS_OPTIONS, index=STATUS_OPTIONS.index(default_rec.get("status", "Received")) if edit_idx is not None else 0)
        notes = st.text_area(tr("Notes"), value=default_rec.get("notes", ""))
        
        submit_btn = st.form_submit_button(tr("Add") if edit_idx is None else tr("Update"))
        
        if submit_btn:
            if not cust_name.strip() or not bag_no.strip():
                st.error("Please fill in Customer Name and Bag Number!")
            else:
                if edit_idx is None and any(str(b["bag_number"]) == bag_no.strip() for b in bags_data):
                    st.error("Bag Number already exists!")
                else:
                    rec = {
                        "customer_name": cust_name.strip(),
                        "bag_number": bag_no.strip(),
                        "cost": cost.strip() or "0",
                        "is_urgent": is_urgent,
                        "country_code": country_code,
                        "customer_mobile": mob_num.strip(),
                        "status": status,
                        "status_date": str(status_date),
                        "notes": notes.strip(),
                        "customer_id": default_rec.get("customer_id", ""),
                        "image_path": default_rec.get("image_path", ""),
                        "reminders_count": default_rec.get("reminders_count", 0),
                        "branch_owner": default_rec.get("branch_owner", st.session_state.current_branch)
                    }
                    if edit_idx is None:
                        bags_data.append(rec)
                        add_to_log(bag_no.strip(), cust_name.strip(), "New Bag Added", st.session_state.current_branch)
                    else:
                        bags_data[edit_idx] = rec
                        st.session_state.current_edit_index = None
                        add_to_log(bag_no.strip(), cust_name.strip(), "Record Updated", st.session_state.current_branch)
                    save_data(bags_data)
                    st.success("Saved perfectly!")
                    st.session_state.active_menu = "View / Stats"
                    st.rerun()
                    
    if edit_idx is not None:
        if st.button("Cancel Edit"):
            st.session_state.current_edit_index = None
            st.session_state.active_menu = "View / Stats"
            st.rerun()

# ==========================================
# --- القسم الثاني: عرض البيانات والبحث ---
# ==========================================
elif choice == "View / Stats":
    st.header(tr("View / Stats"))
    
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        q_name = st.text_input(tr("Search By Name")).lower()
    with f2:
        q_bag = st.text_input(tr("Search By Bag")).lower()
    with f3:
        q_mob = st.text_input(tr("Search By Mobile")).lower()
    with f4:
        filter_status = st.selectbox(tr("Filter Status:"), [tr("All"), "Received", "Out for Repair", "Received Back", "Delivered", tr("Urgent")])

    filtered_data = []
    today = datetime.today()
    
    for i, b in enumerate(bags_data):
        if b.get("branch_owner", "Yas Mall") != st.session_state.current_branch and not is_super_user:
            continue
            
        full_mob = f"{b.get('country_code', '')}{b.get('customer_mobile', '')}"
        bag_no_str = str(b.get("bag_number", ""))
        
        match_name = q_name in b.get("customer_name", "").lower() if q_name else True
        match_bag = q_bag in bag_no_str.lower() if q_bag else True
        match_mob = q_mob in full_mob.lower() if q_mob else True
        match_filter = (filter_status == tr("All")) or (filter_status == tr("Urgent") and b.get("is_urgent", False)) or (b.get("status") == filter_status)
                       
        if match_name and match_bag and match_mob and match_filter:
            try:
                b_date = datetime.strptime(b["status_date"], "%Y-%m-%d")
                days = (today - b_date).days
            except:
                days = 0
            is_del = b.get("status") == "Delivered"
            
            tag = "⬜ Normal"
            if not is_del:
                if (b.get("is_urgent", False) and days >= 7) or (not b.get("is_urgent", False) and days >= 15):
                    tag = "🚨 DELAYED"
                elif b.get("is_urgent", False):
                    tag = "⚡ URGENT ACTIVE"
            elif b.get("is_urgent", False) and is_del:
                tag = "✅ URGENT DELIVERED"
                
            count = safe_int_convert(b.get("reminders_count", 0))
            check_marks = "✅" * count + "⬜" * max(0, (5 - count))
            
            filtered_data.append({
                "Index": i,
                "Type": tag,
                tr("Customer Name"): b.get("customer_name", ""),
                tr("Bag Number"): b.get("bag_number", ""),
                tr("Mobile"): full_mob,
                tr("Cost"): f"{safe_float_convert(b.get('cost', 0)):.2f} AED",
                tr("Status"): b.get("status", ""),
                tr("Date"): b.get("status_date", ""),
                tr("Reminders"): check_marks
            })

    if filtered_data:
        st.info("💡 اختر الباج من القائمة المنسدلة أدناه")
        
        # عمل قائمة بالباجات
        bag_options = []
        for idx, row in enumerate(filtered_data):
            bag_options.append(f"{row[tr('Bag Number')]} - {row[tr('Customer Name')]} ({row[tr('Status')]})")
        
        bag_options.insert(0, "-- اختر باج --")
        
        selected_option = st.selectbox(
            "اختر الباج / Select a bag",
            options=bag_options,
            index=0,
            key="bag_selector"
        )
        
        if selected_option != "-- اختر باج --":
            selected_index_in_filtered = bag_options.index(selected_option) - 1
            
            if 0 <= selected_index_in_filtered < len(filtered_data):
                actual_bag_index = filtered_data[selected_index_in_filtered]["Index"]
                
                if actual_bag_index < len(bags_data):
                    b_selected = bags_data[actual_bag_index]
                    
                    whatsapp_num = format_whatsapp_number(b_selected.get('country_code', '+971'), b_selected.get('customer_mobile', ''))
                    
                    st.markdown("---")
                    st.markdown(f"### 🎯 الباج المختار: **Bag #{b_selected['bag_number']}** ({b_selected['customer_name']})")
                    
                    col_info1, col_info2, col_info3 = st.columns(3)
                    with col_info1:
                        st.metric(tr("Status"), b_selected.get('status', 'Unknown'))
                    with col_info2:
                        st.metric(tr("Cost"), f"{safe_float_convert(b_selected.get('cost', 0)):.2f} AED")
                    with col_info3:
                        st.metric(tr("Mobile"), f"{b_selected.get('country_code', '')}{b_selected.get('customer_mobile', '')}")
                    
                    # عرض الصورة إذا وجدت
                    img_path = b_selected.get("image_path", "")
                    if img_path and os.path.exists(img_path):
                        st.markdown("---")
                        st.write("📸 **صورة الإيصال:**")
                        display_image_with_click(img_path)
                    
                    st.markdown("---")
                    
                    act_c1, act_c2 = st.columns(2)
                    with act_c1:
                        msg_ready = (
                            f"السلام عليكم من {st.session_state.current_branch}.\n\n"
                            f"يرجى العلم بأن التصليح الخاص بكم رقم (*{b_selected['bag_number']}*) جاهز للإستلام بالفرع.\n"
                            f"التكلفة الإجمالية: *{safe_float_convert(b_selected.get('cost', 0)):.2f}* درهم.\n\n"
                            f"يرجى إحضار الإيصال الخاص بالاستلام.\n"
                            f"شكراً لتعاملكم معنا 🌹"
                        )
                        url_ready = f"https://api.whatsapp.com/send?phone={whatsapp_num}&text={urllib.parse.quote(msg_ready)}"
                        st.markdown(f'<a href="{url_ready}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; padding:0.5rem; border:none; border-radius:0.5rem; cursor:pointer;">📱 رسالة جاهز للواتساب</button></a>', unsafe_allow_html=True)
                        
                    with act_c2:
                        msg_remind = (
                            f"السلام عليكم من {st.session_state.current_branch}.\n\n"
                            f"نود تذكيركم بأن التصليح رقم (*{b_selected['bag_number']}*) لا يزال متاحاً للإستلام.\n"
                            f"التكلفة الإجمالية: *{safe_float_convert(b_selected.get('cost', 0)):.2f}* درهم.\n\n"
                            f"يرجى إحضار الإيصال الخاص بالاستلام.\n"
                            f"شكراً لتعاملكم معنا 🌹"
                        )
                        url_remind = f"https://api.whatsapp.com/send?phone={whatsapp_num}&text={urllib.parse.quote(msg_remind)}"
                        st.markdown(f'<a href="{url_remind}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; padding:0.5rem; border:none; border-radius:0.5rem; cursor:pointer;">🔔 إرسال تذكير</button></a>', unsafe_allow_html=True)
                        
                        bags_data[actual_bag_index]["reminders_count"] = safe_int_convert(b_selected.get("reminders_count", 0)) + 1
                        save_data(bags_data)
                        add_to_log(b_selected['bag_number'], b_selected['customer_name'], "Reminder Sent", st.session_state.current_branch)
                    
                    st.markdown("---")
                    
                    btn_manage_col1, btn_manage_col2, btn_manage_col3, btn_manage_col4 = st.columns(4)
                    
                    with btn_manage_col1:
                        if st.button(tr("Manage & Details 📝"), use_container_width=True, type="secondary"):
                            show_bag_details_dialog(actual_bag_index)
                            
                    with btn_manage_col2:
                        password_input = st.text_input("Admin Password", type="password", label_visibility="collapsed", placeholder="Password to Edit/Delete", key="admin_panel_p")
                        
                    with btn_manage_col3:
                        if st.button(tr("Edit"), use_container_width=True):
                            branch_pass = branches_data_cloud.get(st.session_state.current_branch, {}).get("password", "0000")
                            if password_input == branch_pass or password_input == SUPER_ADMIN_PASSWORD:
                                st.session_state.current_edit_index = actual_bag_index
                                st.session_state.active_menu = "Add Bag"
                                st.rerun()
                            else:
                                st.error("Incorrect Password!")
                                
                    with btn_manage_col4:
                        if st.button(tr("Delete"), use_container_width=True):
                            branch_pass = branches_data_cloud.get(st.session_state.current_branch, {}).get("password", "0000")
                            if password_input == branch_pass or password_input == SUPER_ADMIN_PASSWORD:
                                confirm_delete_dialog(actual_bag_index, b_selected['bag_number'], b_selected['customer_name'])
                            else:
                                st.error("Incorrect Password!")
    else:
        st.info("لا توجد بيانات مطابقة للبحث")

# ==========================================
# --- القسم الثالث: التنبيهات ---
# ==========================================
elif choice == "Alerts":
    st.header(tr("Alerts"))
    today = datetime.today()
    urgent_alerts, normal_alerts = [], []
    
    for b in bags_data:
        if b.get("branch_owner", "Yas Mall") != st.session_state.current_branch and not is_super_user:
            continue
        if b.get("status") != "Delivered":
            try:
                d = datetime.strptime(b["status_date"], "%Y-%m-%d")
                days = (today - d).days
                if b.get("is_urgent", False) and days >= 7:
                    urgent_alerts.append({tr("Bag Number"): b["bag_number"], tr("Customer Name"): b["customer_name"], tr("Days Overdue"): days})
                elif not b.get("is_urgent", False) and days >= 15:
                    normal_alerts.append({tr("Bag Number"): b["bag_number"], tr("Customer Name"): b["customer_name"], tr("Days Overdue"): days})
            except:
                continue
                
    col_al1, col_al2 = st.columns(2)
    with col_al1:
        st.subheader(tr("Urgent Bags Overdue (7+ Days)"))
        if urgent_alerts:
            st.dataframe(urgent_alerts, use_container_width=True, hide_index=True)
        else:
            st.success("No critical urgent alerts.")
    with col_al2:
        st.subheader(tr("Normal Bags Overdue (15+ Days)"))
        if normal_alerts:
            st.dataframe(normal_alerts, use_container_width=True, hide_index=True)
        else:
            st.success("No normal alerts.")

# ==========================================
# --- القسم الرابع: الإحصائيات ---
# ==========================================
elif choice == "Stats":
    st.header(tr("Stats"))
    
    visible_bags = [b for b in bags_data if b.get("branch_owner", "Yas Mall") == st.session_state.current_branch or is_super_user]
    
    income = sum(safe_float_convert(b.get("cost", 0)) for b in visible_bags if b.get("status") == "Delivered")
    
    counts = {
        "Total Bags": len(visible_bags),
        "Received": sum(1 for b in visible_bags if b["status"] == "Received"),
        "Out Repair": sum(1 for b in visible_bags if b["status"] == "Out for Repair"),
        "In Store": sum(1 for b in visible_bags if b["status"] == "Received Back"),
        "Delivered": sum(1 for b in visible_bags if b["status"] == "Delivered"),
        "Income": f"{income:.2f} AED"
    }
    
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric(tr("Total Bags"), counts["Total Bags"])
    with m2:
        st.metric(tr("Received"), counts["Received"])
    with m3:
        st.metric(tr("Out Repair"), counts["Out Repair"])
    m4, m5, m6 = st.columns(3)
    with m4:
        st.metric(tr("In Store"), counts["In Store"])
    with m5:
        st.metric(tr("Delivered"), counts["Delivered"])
    with m6:
        st.metric(tr("Income"), counts["Income"])
    
    st.markdown("---")
    st.subheader(tr("Monthly Performance"))
    m_stats = {}
    for b in visible_bags:
        try:
            m = datetime.strptime(b["status_date"], "%Y-%m-%d").strftime("%Y-%m (%B)")
            if m not in m_stats:
                m_stats[m] = {"count": 0, "income": 0}
            m_stats[m]["count"] += 1
            if b["status"] == "Delivered":
                m_stats[m]["income"] += safe_float_convert(b.get("cost", 0))
        except:
            continue
            
    if m_stats:
        monthly_table = [{"Month": m, "Bags Count": m_stats[m]['count'], "Income": f"{m_stats[m]['income']:.2f} AED"} for m in sorted(m_stats.keys(), reverse=True)]
        st.table(monthly_table)
        
    st.markdown("---")
    with st.expander(tr("View Action Logs 📜")):
        filtered_logs = [l for l in actions_log if l.get("branch") == st.session_state.current_branch or is_super_user]
        log_display = [{tr("Time"): e.get('time'), tr("Branch"): e.get('branch', 'Yas Mall'), tr("Bag #"): e.get('bag'), tr("Customer"): e.get('customer'), tr("Action"): e.get('action')} for e in reversed(filtered_logs)]
        if log_display:
            st.dataframe(log_display, use_container_width=True, hide_index=True)
        else:
            st.info("No logs found.")

    st.markdown("---")
    with st.expander(f"🔐 {tr('Login History')} & {tr('Super Backup')} (Super Admin Only)"):
        if is_super_user:
            st.subheader(tr("Super Backup"))
            if bags_data:
                df_backup = pd.DataFrame(bags_data)
                df_backup.to_excel("Jawhara_Full_Backup.xlsx", index=False)
                with open("Jawhara_Full_Backup.xlsx", "rb") as f_backup:
                    st.download_button(
                        label="📥 Download Full Database Excel Backup",
                        data=f_backup.read(),
                        file_name=f"Jawhara_Enterprise_Backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary"
                    )
            else:
                st.info("No data available to backup yet.")
            try:
                st.subheader(tr("Login History"))
                history_display = [{tr("Time"): h["time"], tr("Branch"): h["branch"], "Access Type": h["type"]} for h in reversed(db_load_login_history())]
                st.dataframe(history_display, use_container_width=True, hide_index=True)
            except:
                st.info("No history available.")
        else:
            st.warning("Access Denied. Only Super Admin can view core metrics and download backups.")
