import json
import os
import urllib.parse
from datetime import datetime
import pandas as pd
import streamlit as st
from PIL import Image
from supabase import create_client

# --- إعدادات الصفحة العامة ---
st.set_page_config(
    page_title="RepairBag Pro Enterprise Cloud © 2026",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ربط قاعدة البيانات السحابية (Supabase) ---
SUPABASE_URL = "https://aarksbtetlwjzicmzoql.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFhcmtzYnRldGx3anppY216b3FsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkzNjI2NzcsImV4cCI6MjA2NDkzODY3N30.i96O02ZfKjVpE9SAn8gEOf0vU5FfA7vXjXN7v6vH9_w"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

OLD_JSON_FILE = "repair_bags.json"
IMAGE_DIR = "uploaded_images"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR, exist_ok=True

SUPER_ADMIN_PASSWORD = "9999" # باسورد الإدمن العام الخاصة بأحمد
ADMIN_PASSWORD = "1234"
COUNTRY_CODES = ["+971", "+20", "+966", "+965", "+974", "+973", "+968", "+1", "+44"]
STATUS_OPTIONS = ["Received", "Out for Repair", "Received Back", "Delivered"]

# --- دالات التعامل مع السيرفر السحابي بدلاً من ملفات الـ JSON القديمة ---
def db_load_branches():
    try:
        res = supabase.table("branch_settings").select("*").execute()
        return {item["branch_name"]: {"password": item["password"]} for item in res.data}
    except:
        return {}

def db_update_branch_password(branch_name, new_pass):
    supabase.table("branch_settings").update({"password": new_pass}).eq("branch_name", branch_name).execute()

def db_add_new_branch(branch_name, password):
    supabase.table("branch_settings").insert({"branch_name": branch_name, "password": password}).execute()

def db_load_bags():
    try:
        res = supabase.table("repair_bags").select("*").order("id", desc=False).execute()
        return res.data
    except:
        return []

def db_save_bag(bag_data):
    if "id" in bag_data: del bag_data["id"]
    supabase.table("repair_bags").insert(bag_data).execute()

def db_update_bag(bag_id, bag_data):
    if "id" in bag_data: del bag_data["id"]
    supabase.table("repair_bags").update(bag_data).eq("id", bag_id).execute()

def db_delete_bag(bag_id):
    supabase.table("repair_bags").delete().eq("id", bag_id).execute()

def db_load_logs():
    try:
        res = supabase.table("actions_log").select("*").execute()
        return res.data
    except: return []

def db_add_to_log(bag_number, customer_name, action, branch_name):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {"time": now, "bag": str(bag_number), "customer": customer_name, "action": action, "branch": branch_name}
    supabase.table("actions_log").insert(log_entry).execute()

def db_load_login_history():
    try:
        res = supabase.table("login_history").select("*").execute()
        return res.data
    except: return []

def db_add_login_history(branch_name, login_type):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    supabase.table("login_history").insert({"time": now_str, "branch": branch_name, "type": login_type}).execute()

# --- إدارة حالة التطبيق الجارية (Session State) ---
if "language" not in st.session_state: st.session_state.language = "en"
if "current_edit_index" not in st.session_state: st.session_state.current_edit_index = None
if "selected_row_idx" not in st.session_state: st.session_state.selected_row_idx = 0
if "active_menu" not in st.session_state: st.session_state.active_menu = "Add Bag"
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_branch" not in st.session_state: st.session_state.current_branch = None
if "last_branch_selection" not in st.session_state: st.session_state.last_branch_selection = "Yas Mall"

# تحميل بيانات الفروع السحابية حياً
branches_data_cloud = db_load_branches()

# --- قاموس الترجمة الموحد ---
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
        "Customer ID": "رقم هوية الزبون", "Receipt Image": "صورة الاستلام",
        "Manage & Details 📝": "إدارة وتفاصيل الباج 📝", "Branch Settings": "إعدادات الفرع الأمنية",
        "Change Password": "تغيير كلمة المرور الخاصة بالفرع", "Old Password": "كلمة المرور القديمة",
        "New Password": "كلمة المرور الجديدة", "Save Password": "حفظ كلمة المرور الجديدة",
        "Login History": "سجل دخول الأجهزة للفروع", "Branch": "الفرع", "Logout": "تسجيل الخروج 🚪",
        "Add New Branch": "إضافة فرع جديد للسيستم 🏢", "Branch Name": "اسم الفرع الجديد", "Branch Password": "باسورد الفرع الجديد",
        "Super Backup": "نسخة احتياطية كاملة للشركة 📥"
    }
    return translations.get(text, text) if st.session_state.language == "ar" else text

# ==========================================
# --- 1. شاشة تسجيل الدخول (Login Screen) ---
# ==========================================
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color: #1f538d;'>💎 Jawhara Management System</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>RepairBag Pro Enterprise Cloud 2026</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.write("### 🔑 Branch Secure Login")
        branches_list = list(branches_data_cloud.keys()) if branches_data_cloud else ["Yas Mall"]
        
        try: last_idx = branches_list.index(st.session_state.last_branch_selection)
        except: last_idx = 0
            
        selected_branch = st.selectbox("Choose Branch / اختر الفرع", branches_list, index=last_idx)
        password_input = st.text_input("Enter Password / أدخل كلمة المرور", type="password")
        
        if st.button("Login / دخول", type="primary", use_container_width=True):
            correct_password = branches_data_cloud.get(selected_branch, {}).get("password", "0000")
            
            if password_input == correct_password or password_input == SUPER_ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.session_state.current_branch = selected_branch
                st.session_state.last_branch_selection = selected_branch
                
                login_type = "Super Admin Bypass" if password_input == SUPER_ADMIN_PASSWORD else "Standard Branch Login"
                db_add_login_history(selected_branch, login_type)
                
                st.success(f"Welcome back, {selected_branch}!")
                st.rerun()
            else:
                st.error("Incorrect Password! Please try again.")
    st.stop()

# جلب البيانات الحية الحالية من السحاب بعد تسجيل الدخول المضمون
bags_data = db_load_bags()
actions_log = db_load_logs()

# التحقق هل المستخدم الحالي هو الإدمن العام أحمد
is_super_user = st.session_state.logged_in and (st.session_state.last_branch_selection in branches_data_cloud) and any(
    h.get("branch") == st.session_state.current_branch and h.get("type") == "Super Admin Bypass" 
    for h in db_load_login_history()
)

menu_mapping = {
    tr("Add Bag"): "Add Bag",
    tr("View / Stats"): "View / Stats",
    tr("Alerts"): "Alerts",
    tr("Stats"): "Stats"
}
menu_options = list(menu_mapping.keys())

try: current_idx = list(menu_mapping.values()).index(st.session_state.active_menu)
except: current_idx = 0

# --- القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.title(st.session_state.current_branch)
    st.caption("Connected Securely to Cloud ☁️ 🟢")
    st.markdown("---")
    
    choice_translated = st.radio("Navigation", menu_options, index=current_idx, label_visibility="collapsed")
    st.session_state.active_menu = menu_mapping[choice_translated]
    choice = st.session_state.active_menu
    
    st.markdown("---")
    lang_choice = st.selectbox(tr("Language"), ["English", "العربية"], index=0 if st.session_state.language == "en" else 1)
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
            actual_old = branches_data_cloud[st.session_state.current_branch]["password"]
            if old_p == actual_old or old_p == SUPER_ADMIN_PASSWORD:
                if len(new_p.strip()) > 0:
                    db_update_branch_password(st.session_state.current_branch, new_p.strip())
                    st.success("Password updated successfully!")
                else: st.error("Password cannot be empty!")
            else: st.error("Incorrect Old Password!")
            
        st.markdown("---")
        st.write(tr("Add New Branch"))
        super_p = st.text_input("Enter Super Admin Password", type="password", key="super_add")
        new_b_name = st.text_input(tr("Branch Name"))
        new_b_pass = st.text_input(tr("Branch Password"), type="password")
        if st.button(tr("Add Bag") + " Branch"):
            if super_p == SUPER_ADMIN_PASSWORD:
                if new_b_name.strip() and new_b_pass.strip():
                    db_add_new_branch(new_b_name.strip(), new_b_pass.strip())
                    st.success(f"Branch '{new_b_name}' added successfully!")
                    st.rerun()
                else: st.error("Please fill in branch name and password!")
            else: st.error("Only Super Admin can add new branches!")

    st.markdown("---")
    if st.button(tr("Logout"), type="primary", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_branch = None
        st.rerun()

# --- نافذة التفاصيل والبيانات الإضافية ---
@st.dialog("Bag Extra Details & Management")
def show_bag_details_dialog(index, bag_db_id):
    bags_fresh = db_load_bags()
    b = next((item for item in bags_fresh if item["id"] == bag_db_id), bags_fresh[index])
    
    st.write(f"### 💎 {tr('Bag Number')}: {b['bag_number']}")
    st.write(f"**{tr('Customer Name')}:** {b['customer_name']}")
    st.markdown("---")
    
    cust_id = st.text_input(tr("Customer ID"), value=b.get("customer_id", ""))
    uploaded_file = st.file_uploader(tr("Receipt Image"), type=["jpg", "jpeg", "png"])
    
    img_path = b.get("image_path", "")
    if img_path and os.path.exists(img_path):
        st.write(f"**{tr('Receipt Image')}:**")
        image = Image.open(img_path)
        st.image(image, width=200, caption="Click upper-right arrow to expand")
        with st.expander("🔍 View Large Size Directly Here"):
            st.image(image, use_container_width=True)
            
    if st.button(tr("Add") + " / " + tr("Update"), type="primary"):
        updated_extra = {
            "customer_id": cust_id.strip(),
            "customer_name": b["customer_name"], "bag_number": b["bag_number"], "cost": b["cost"],
            "is_urgent": b["is_urgent"], "country_code": b["country_code"], "customer_mobile": b["customer_mobile"],
            "status": b["status"], "status_date": b["status_date"], "notes": b["notes"],
            "branch_owner": b.get("branch_owner", st.session_state.current_branch), "image_path": b.get("image_path", "")
        }
        if uploaded_file is not None:
            file_ext = os.path.splitext(uploaded_file.name)[1]
            saved_img_name = f"bag_{b['bag_number']}{file_ext}"
            full_save_path = os.path.join(IMAGE_DIR, saved_img_name)
            with open(full_save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            updated_extra["image_path"] = full_save_path
            
        db_update_bag(bag_db_id, updated_extra)
        db_add_to_log(b['bag_number'], b['customer_name'], "Extra details/Image updated", st.session_state.current_branch)
        st.success("Details updated in cloud successfully!")
        st.rerun()

# --- القسم الأول: إضافة وتعديل باج (Add Bag) ---
if choice == "Add Bag":
    st.header(tr("Add Bag") if st.session_state.current_edit_index is None else tr("Update"))
    edit_idx = st.session_state.current_edit_index
    default_rec = bags_data[edit_idx] if (edit_idx is not None and edit_idx < len(bags_data)) else {}
    
    with st.form("bag_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            cust_name = st.text_input(tr("Customer Name"), value=default_rec.get("customer_name", ""))
            bag_no = st.text_input(tr("Bag Number"), value=default_rec.get("bag_number", ""))
            cost = st.text_input(tr("Cost"), value=default_rec.get("cost", "0"))
        with c2:
            is_urgent = st.checkbox(tr("Urgent"), value=default_rec.get("is_urgent", False))
            try: def_date = datetime.strptime(default_rec.get("status_date", ""), "%Y-%m-%d").date()
            except: def_date = datetime.today().date()
            status_date = st.date_input(tr("Date"), value=def_date)
            
            mob_col1, mob_col2 = st.columns([1, 2])
            with mob_col1:
                try: def_code_idx = COUNTRY_CODES.index(default_rec.get("country_code", "+971"))
                except: def_code_idx = 0
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
                    st.error("Bag Number already exists in database!")
                else:
                    rec = {
                        "customer_name": cust_name.strip(), "bag_number": bag_no.strip(), "cost": cost.strip() or "0",
                        "is_urgent": is_urgent, "country_code": country_code, "customer_mobile": mob_num.strip(),
                        "status": status, "status_date": str(status_date), "notes": notes.strip(),
                        "customer_id": default_rec.get("customer_id", ""), "image_path": default_rec.get("image_path", ""),
                        "branch_owner": default_rec.get("branch_owner", st.session_state.current_branch)
                    }
                    if edit_idx is None:
                        db_save_bag(rec)
                        db_add_to_log(bag_no.strip(), cust_name.strip(), "New Bag Added", st.session_state.current_branch)
                    else:
                        db_update_bag(default_rec["id"], rec)
                        st.session_state.current_edit_index = None
                        db_add_to_log(bag_no.strip(), cust_name.strip(), "Record Updated", st.session_state.current_branch)
                    st.success("Saved dynamically to Cloud Server!")
                    st.session_state.active_menu = "View / Stats"
                    st.rerun()
                    
    if edit_idx is not None:
        if st.button("Cancel Edit"):
            st.session_state.current_edit_index = None
            st.session_state.active_menu = "View / Stats"
            st.rerun()

# --- القسم الثاني: عرض البيانات والبحث الذكي (View / Stats) ---
elif choice == "View / Stats":
    st.header(tr("View / Stats"))
    
    f1, f2, f3, f4 = st.columns(4)
    with f1: q_name = st.text_input(tr("Search By Name")).lower()
    with f2: q_bag = st.text_input(tr("Search By Bag")).lower()
    with f3: q_mob = st.text_input(tr("Search By Mobile")).lower()
    with f4: filter_status = st.selectbox(tr("Filter Status:"), [tr("All"), "Received", "Out for Repair", "Received Back", "Delivered", tr("Urgent")])

    filtered_data = []
    today = datetime.today()
    
    for i, b in enumerate(bags_data):
        if b.get("branch_owner", "Yas Mall") != st.session_state.current_branch and not is_super_user:
            continue
            
        full_mob = f"{b.get('country_code', '')}{b['customer_mobile']}"
        bag_no_str = str(b["bag_number"])
        
        match_name = q_name in b["customer_name"].lower() if q_name else True
        match_bag = q_bag in bag_no_str.lower() if q_bag else True
        match_mob = q_mob in full_mob.lower() if q_mob else True
        match_filter = (filter_status == tr("All")) or (filter_status == tr("Urgent") and b.get("is_urgent", False)) or (b.get("status") == filter_status)
                       
        if match_name and match_bag and match_mob and match_filter:
            try:
                b_date = datetime.strptime(b["status_date"], "%Y-%m-%d")
                days = (today - b_date).days
            except: days = 0
            is_del = b.get("status") == "Delivered"
            
            tag = "⬜ Normal"
            if not is_del:
                if (b.get("is_urgent", False) and days >= 7) or (not b.get("is_urgent", False) and days >= 15): tag = "🚨 DELAYED"
                elif b.get("is_urgent", False): tag = "⚡ URGENT ACTIVE"
            elif b.get("is_urgent", False) and is_del: tag = "✅ URGENT DELIVERED"
                
            count = sum(1 for log in actions_log if str(log.get('bag')) == bag_no_str and log.get('action') == "Reminder Sent")
            check_marks = "✅" * count + "⬜" * (5 - count)
            
            row_entry = {
                "Index": i, "DB_ID": b["id"], "Type": tag, tr("Customer Name"): b["customer_name"], tr("Bag Number"): b["bag_number"],
                tr("Mobile"): full_mob, tr("Cost"): f"{b.get('cost', '0')} AED", tr("Status"): b["status"],
                tr("Date"): b["status_date"], tr("Reminders"): check_marks
            }
            if is_super_user:
                row_entry["Branch / الفرع"] = b.get("branch_owner", "Yas Mall")
            filtered_data.append(row_entry)

    if filtered_data:
        st.info("💡 Click anywhere on any row below to select it.")
        selection = st.dataframe(filtered_data, use_container_width=True, hide_index=True, selection_mode="single-row", on_select="rerun")
        
        if selection and selection.get("selection", {}).get("rows"):
            st.session_state.selected_row_idx = selection["selection"]["rows"][0]
        if st.session_state.selected_row_idx >= len(filtered_data):
            st.session_state.selected_row_idx = 0
            
        actual_bag_index = filtered_data[st.session_state.selected_row_idx]["Index"]
        bag_db_id = filtered_data[st.session_state.selected_row_idx]["DB_ID"]
        b_selected = bags_data[actual_bag_index]
        num = f"{b_selected.get('country_code','').replace('+','')}{b_selected.get('customer_mobile','')}"
        
        st.markdown(f"### 🎯 Active Selection: **Bag #{b_selected['bag_number']}** ({b_selected['customer_name']})")
        
        act_c1, act_c2 = st.columns(2)
        with act_c1:
            msg_ready = (
                f"السلام عليكم من {st.session_state.current_branch}.\n\n"
                f"يرجى العلم بأن التصليح الخاص بكم رقم (*{b_selected['bag_number']}*) جاهز للإستلام بالفرع.\n"
                f"التكلفة الإجمالية: *{b_selected.get('cost','0')}* درهم.\n\n"
                f"يرجى إحضار الإيصال الخاص بالاستلام.\n"
                f"شكراً لتعاملكم معنا 🌹\n\n"
                f"---------------------------\n\n"
                f"Greetings from {st.session_state.current_branch}.\n\n"
                f"Your repair bag (*{b_selected['bag_number']}*) is ready for collection at the store.\n"
                f"Total Cost: *{b_selected.get('cost','0')}* AED.\n\n"
                f"Kindly bring your repair receipt.\n"
                f"Thank you 🌹"
            )
            url_ready = f"https://api.whatsapp.com/send?phone={num}&text={urllib.parse.quote(msg_ready)}"
            if st.link_button("WhatsApp 📱 Ready Message", url_ready, use_container_width=True, type="primary"):
                db_add_to_log(b_selected['bag_number'], b_selected['customer_name'], "Ready Message Sent", st.session_state.current_branch)
                
        with act_c2:
            msg_remind = (
                f"السلام عليكم من {st.session_state.current_branch}.\n\n"
                f"نود تذكيركم بأن التصليح رقم (*{b_selected['bag_number']}*) لا يزال متاحاً للاستلام.\n"
                f"التكلفة الإجمالية: *{b_selected.get('cost','0')}* درهم.\n\n"
                f"يرجى إحضار الإيصال الخاص بالاستلام.\n"
                f"شكراً لتعاملكم معنا 🌹\n\n"
                f"---------------------------\n\n"
                f"Greetings from {st.session_state.current_branch}.\n\n"
                f"This is a friendly reminder that your repair bag (*{b_selected['bag_number']}*) is still waiting for collection.\n"
                f"Total Cost: *{b_selected.get('cost','0')}* AED.\n\n"
                f"Kindly bring your repair receipt.\n"
                f"Thank you 🌹"
            )
            url_remind = f"https://api.whatsapp.com/send?phone={num}&text={urllib.parse.quote(msg_remind)}"
            if st.link_button(tr("Send Reminder"), url_remind, use_container_width=True):
                db_add_to_log(b_selected['bag_number'], b_selected['customer_name'], "Reminder Sent", st.session_state.current_branch)
                
        st.markdown("---")
        btn_manage_col1, btn_manage_col2, btn_manage_col3, btn_manage_col4 = st.columns(4)
        
        with btn_manage_col1:
            if st.button(tr("Manage & Details 📝"), use_container_width=True, type="secondary"):
                show_bag_details_dialog(actual_bag_index, bag_db_id)
                
        with btn_manage_col2:
            password_input = st.text_input("Admin Password", type="password", label_visibility="collapsed", placeholder="Enter Password to Edit/Delete")
            
        with btn_manage_col3:
            if st.button(tr("Edit"), use_container_width=True):
                branch_pass = branches_data_cloud.get(st.session_state.current_branch, {}).get("password", "0000")
                if password_input == branch_pass or password_input == SUPER_ADMIN_PASSWORD:
                    st.session_state.current_edit_index = actual_bag_index
                    st.session_state.active_menu = "Add Bag"
                    st.rerun()
                else: st.error("Incorrect Password!")
                
        with btn_manage_col4:
            if st.button(tr("Delete"), use_container_width=True):
                branch_pass = branches_data_cloud.get(st.session_state.current_branch, {}).get("password", "0000")
                if password_input == branch_pass or password_input == SUPER_ADMIN_PASSWORD:
                    db_add_to_log(b_selected['bag_number'], b_selected['customer_name'], "Record Deleted", st.session_state.current_branch)
                    db_delete_bag(bag_db_id)
                    st.session_state.current_edit_index = None
                    st.session_state.selected_row_idx = 0
                    st.success("Deleted from cloud database!")
                    st.rerun()
                else: st.error("Incorrect Password!")
    else:
        st.info("No matching data found.")

# --- القسم الثالث: التنبيهات 📢 (Alerts) ---
elif choice == "Alerts":
    st.header(tr("Alerts"))
    today = datetime.today()
    urgent_alerts, normal_alerts = [], []
    
    for b in bags_data:
        if b.get("branch_owner", "Yas Mall") != st.session_state.current_branch and not is_super_user: continue
        if b.get("status") != "Delivered":
            try:
                d = datetime.strptime(b["status_date"], "%Y-%m-%d")
                days = (today - d).days
                if b.get("is_urgent", False) and days >= 7:
                    urgent_alerts.append({tr("Bag Number"): b["bag_number"], tr("Customer Name"): b["customer_name"], tr("Days Overdue"): days})
                elif not b.get("is_urgent", False) and days >= 15:
                    normal_alerts.append({tr("Bag Number"): b["bag_number"], tr("Customer Name"): b["customer_name"], tr("Days Overdue"): days})
            except: continue
                
    col_al1, col_al2 = st.columns(2)
    with col_al1:
        st.subheader(tr("Urgent Bags Overdue (7+ Days)"))
        if urgent_alerts: st.dataframe(urgent_alerts, use_container_width=True, hide_index=True)
        else: st.success("No critical urgent alerts.")
    with col_al2:
        st.subheader(tr("Normal Bags Overdue (15+ Days)"))
        if normal_alerts: st.dataframe(normal_alerts, use_container_width=True, hide_index=True)
        else: st.success("No normal alerts.")

# --- القسم الرابع: الإحصائيات وسجلات النظام (Stats) ---
elif choice == "Stats":
    st.header(tr("Stats"))
    
    visible_bags = [b for b in bags_data if b.get("branch_owner", "Yas Mall") == st.session_state.current_branch or is_super_user]
    income = sum(float(b.get("cost", 0)) for b in visible_bags if b.get("status") == "Delivered")
    
    counts = {
        "Total Bags": len(visible_bags), "Received": sum(1 for b in visible_bags if b["status"] == "Received"),
        "Out Repair": sum(1 for b in visible_bags if b["status"] == "Out for Repair"), "In Store": sum(1 for b in visible_bags if b["status"] == "Received Back"),
        "Delivered": sum(1 for b in visible_bags if b["status"] == "Delivered"), "Income": f"{income} AED"
    }
    
    m1, m2, m3 = st.columns(3)
    with m1: st.metric(tr("Total Bags"), counts["Total Bags"])
    with m2: st.metric(tr("Received"), counts["Received"])
    with m3: st.metric(tr("Out Repair"), counts["Out Repair"])
    m4, m5, m6 = st.columns(3)
    with m4: st.metric(tr("In Store"), counts["In Store"])
    with m5: st.metric(tr("Delivered"), counts["Delivered"])
    with m6: st.metric(tr("Income"), counts["Income"])
    
    st.markdown("---")
    st.subheader(tr("Monthly Performance"))
    m_stats = {}
    for b in visible_bags:
        try:
            m = datetime.strptime(b["status_date"], "%Y-%m-%d").strftime("%Y-%m (%B)")
            if m not in m_stats: m_stats[m] = {"count": 0, "income": 0}
            m_stats[m]["count"] += 1
            if b["status"] == "Delivered": m_stats[m]["income"] += float(b.get("cost", 0))
        except: continue
            
    if m_stats:
        monthly_table = [{"Month": m, "Bags Count": m_stats[m]['count'], "Income": f"{m_stats[m]['income']} AED"} for m in sorted(m_stats.keys(), reverse=True)]
        st.table(monthly_table)
        
    st.markdown("---")
    with st.expander(tr("View Action Logs 📜")):
        filtered_logs = [l for l in actions_log if l.get("branch") == st.session_state.current_branch or is_super_user]
        log_display = [{tr("Time"): e.get('time'), tr("Branch"): e.get('branch', 'Yas Mall'), tr("Bag #"): e.get('bag'), tr("Customer"): e.get('customer'), tr("Action"): e.get('action')} for e in reversed(filtered_logs)]
        if log_display: st.dataframe(log_display, use_container_width=True, hide_index=True)
        else: st.info("No logs found.")

    st.markdown("---")
    # شاشة تتبع الدخول وزر الاستيراد والسحب الاحتياطي
    with st.expander(f"🔐 {tr('Login History')} & {tr('Super Backup')} (Super Admin Only)"):
        if is_super_user:
            st.subheader("⚙️ Data Sync Tools")
            
            # زر سحب واستيراد البيانات القديمة من ملف الـ JSON لـ Supabase
            if os.path.exists(OLD_JSON_FILE):
                if st.button("⚙️ Import Data From Old JSON to Cloud", type="secondary"):
                    try:
                        with open(OLD_JSON_FILE, "r", encoding="utf-8") as f_old:
                            old_data = json.load(f_old)
                        if old_data:
                            imported_count = 0
                            for old_bag in old_data:
                                # حماية من التكرار بناء على رقم الباج
                                if not any(str(b["bag_number"]) == str(old_bag["bag_number"]) for b in bags_data):
                                    if "id" in old_bag: del old_bag["id"]
                                    if "branch_owner" not in old_bag: old_bag["branch_owner"] = "Yas Mall"
                                    db_save_bag(old_bag)
                                    imported_count += 1
                            st.success(f"Successfully imported {imported_count} record(s) to Supabase Cloud!")
                            st.rerun()
                        else:
                            st.warning("Old JSON file is empty.")
                    except Exception as e_mig:
                        st.error(f"Migration error: {str(e_mig)}")
            else:
                st.info("No legacy 'repair_bags.json' file detected on the Streamlit server to import.")

            st.markdown("---")
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
                
            st.markdown("---")
            st.subheader(tr("Login History"))
            history_display = [{tr("Time"): h["time"], tr("Branch"): h["branch"], "Access Type": h["type"]} for h in reversed(db_load_login_history())]
            st.dataframe(history_display, use_container_width=True, hide_index=True)
        else:
            st.warning("Access Denied. Only Super Admin can view core metrics and download backups.")
