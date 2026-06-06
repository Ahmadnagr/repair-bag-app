import json
import os
import urllib.parse
from datetime import datetime
import streamlit as st
from PIL import Image

# --- إعدادات الصفحة العامة ---
st.set_page_config(
    page_title="RepairBag Pro © 2026",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- المجلدات والملفات ---
DATA_FILE = "repair_bags.json"
LOG_FILE = "actions_log.json"
CONFIG_FILE = "app_config.json"
IMAGE_DIR = "uploaded_images"

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# --- إدارة حالة التطبيق (Session State) ---
if "language" not in st.session_state:
    st.session_state.language = "en"
if "current_edit_index" not in st.session_state:
    st.session_state.current_edit_index = None
if "selected_row_idx" not in st.session_state:
    st.session_state.selected_row_idx = 0
if "active_menu" not in st.session_state:
    st.session_state.active_menu = "Add Bag"

# --- إدارة البيانات والإعدادات ---
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return {"store_name": "Jawhara Yas Mall"}
    return {"store_name": "Jawhara Yas Mall"}

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return []
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_logs():
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return []
    return []

def add_to_log(bag_number, customer_name, action):
    logs = load_logs()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {"time": now, "bag": bag_number, "customer": customer_name, "action": action}
    logs.append(log_entry)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=4)

# تحميل البيانات الحالية
app_config = load_config()
bags_data = load_data()
actions_log = load_logs()

ADMIN_PASSWORD = "1234"
COUNTRY_CODES = ["+971", "+20", "+966", "+965", "+974", "+973", "+968", "+1", "+44"]
STATUS_OPTIONS = ["Received", "Out for Repair", "Received Back", "Delivered"]

# --- قاموس الترجمة ---
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
        "Manage & Details 📝": "إدارة وتفاصيل الباج 📝"
    }
    return translations.get(text, text) if st.session_state.language == "ar" else text

# تحضير القواميس والخيارات
menu_mapping = {
    tr("Add Bag"): "Add Bag",
    tr("View / Stats"): "View / Stats",
    tr("Alerts"): "Alerts",
    tr("Stats"): "Stats"
}
menu_options = list(menu_mapping.keys())

# حساب الـ Index الحالي بناءً على القيمة المحفوظة في السيسشن ستيت دايماً
try:
    current_idx = list(menu_mapping.values()).index(st.session_state.active_menu)
except:
    current_idx = 0

# --- القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.title(app_config["store_name"])
    st.subheader("RepairBag Management Pro")
    st.markdown("---")
    
    # تم إزالة الـ key والـ on_change لضمان استجابة الـ index الفورية للتغيير البرمجي
    choice_translated = st.radio(
        "Navigation", 
        menu_options, 
        index=current_idx,
        label_visibility="collapsed"
    )
    
    # تحديث الـ active_menu بناءً على اختيار المستخدم اليدوي
    st.session_state.active_menu = menu_mapping[choice_translated]
    choice = st.session_state.active_menu
    
    st.markdown("---")
    lang_choice = st.selectbox("Language / اللغة", ["English", "العربية"], index=0 if st.session_state.language == "en" else 1)
    new_lang = "ar" if lang_choice == "العربية" else "en"
    if new_lang != st.session_state.language:
        st.session_state.language = new_lang
        st.rerun()
        
    st.markdown("---")
    with st.expander(tr("Store Name Settings")):
        new_store_name = st.text_input(tr("Change Store Name"), value=app_config["store_name"])
        if st.button(tr("Save Settings")):
            app_config["store_name"] = new_store_name
            save_config(app_config)
            st.success("Store name updated!")
            st.rerun()

# --- نافذة التفاصيل والبيانات الإضافية ---
@st.dialog("Bag Extra Details & Management")
def show_bag_details_dialog(index):
    b = bags_data[index]
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
        b["customer_id"] = cust_id.strip()
        
        if uploaded_file is not None:
            file_ext = os.path.splitext(uploaded_file.name)[1]
            saved_img_name = f"bag_{b['bag_number']}{file_ext}"
            full_save_path = os.path.join(IMAGE_DIR, saved_img_name)
            with open(full_save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            b["image_path"] = full_save_path
            
        bags_data[index] = b
        save_data(bags_data)
        add_to_log(b['bag_number'], b['customer_name'], "Extra details/Image updated")
        st.success("Details updated successfully!")
        st.rerun()

# --- القسم الأول: إضافة وتعديل باج (Add Bag) ---
if choice == "Add Bag":
    st.header(tr("Add Bag") if st.session_state.current_edit_index is None else tr("Update"))
    edit_idx = st.session_state.current_edit_index
    default_rec = bags_data[edit_idx] if edit_idx is not None else {}
    
    with st.form("bag_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            cust_name = st.text_input(tr("Customer Name"), value=default_rec.get("customer_name", ""))
            bag_no = st.text_input(tr("Bag Number"), value=default_rec.get("bag_number", ""))
            cost = st.text_input(tr("Cost"), value=default_rec.get("cost", "0"))
        with c2:
            is_urgent = st.checkbox(tr("Urgent"), value=default_rec.get("is_urgent", False))
            try:
                def_date = datetime.strptime(default_rec.get("status_date", ""), "%Y-%m-%d").date()
            except:
                def_date = datetime.today().date()
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
                    st.error("Bag Number already exists!")
                else:
                    rec = {
                        "customer_name": cust_name.strip(), "bag_number": bag_no.strip(), "cost": cost.strip() or "0",
                        "is_urgent": is_urgent, "country_code": country_code, "customer_mobile": mob_num.strip(),
                        "status": status, "status_date": str(status_date), "notes": notes.strip(),
                        "customer_id": default_rec.get("customer_id", ""), "image_path": default_rec.get("image_path", "")
                    }
                    if edit_idx is None:
                        bags_data.append(rec)
                        add_to_log(bag_no.strip(), cust_name.strip(), "New Bag Added")
                    else:
                        bags_data[edit_idx] = rec
                        st.session_state.current_edit_index = None
                        add_to_log(bag_no.strip(), cust_name.strip(), "Record Updated")
                    save_data(bags_data)
                    st.success("Saved successfully!")
                    st.session_state.active_menu = "View / Stats"  # بعد الحفظ يرجع لتبويب العرض تلقائياً
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
        full_mob = f"{b.get('country_code', '')}{b['customer_mobile']}"
        bag_no_str = str(b["bag_number"])
        
        match_name = q_name in b["customer_name"].lower() if q_name else True
        match_bag = q_bag in bag_no_str.lower() if q_bag else True
        match_mob = q_mob in full_mob.lower() if q_mob else True
        match_filter = (filter_status == tr("All")) or (filter_status == tr("Urgent") and b.get("is_urgent", False)) or (b.get("status") == filter_status)
                       
        if match_name && match_bag && match_mob && match_filter:
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
            
            filtered_data.append({
                "Index": i, "Type": tag, tr("Customer Name"): b["customer_name"], tr("Bag Number"): b["bag_number"],
                tr("Mobile"): full_mob, tr("Cost"): f"{b.get('cost', '0')} AED", tr("Status"): b["status"],
                tr("Date"): b["status_date"], tr("Reminders"): check_marks
            })

    if filtered_data:
        st.info("💡 Click anywhere on any row below to select it.")
        
        selection = st.dataframe(
            filtered_data, 
            use_container_width=True, 
            hide_index=True,
            selection_mode="single-row",
            on_select="rerun"
        )
        
        if selection and selection.get("selection", {}).get("rows"):
            st.session_state.selected_row_idx = selection["selection"]["rows"][0]
            
        if st.session_state.selected_row_idx >= len(filtered_data):
            st.session_state.selected_row_idx = 0
            
        actual_bag_index = filtered_data[st.session_state.selected_row_idx]["Index"]
        b_selected = bags_data[actual_bag_index]
        num = f"{b_selected.get('country_code','').replace('+','')}{b_selected.get('customer_mobile','')}"
        
        st.markdown(f"### 🎯 Active Selection: **Bag #{b_selected['bag_number']}** ({b_selected['customer_name']})")
        
        act_c1, act_c2 = st.columns(2)
        with act_c1:
            msg_ready = (
                f"السلام عليكم من {app_config['store_name']}.\n\n"
                f"يرجى العلم بأن التصليح الخاص بكم رقم (*{b_selected['bag_number']}*) جاهز للإستلام بالفرع.\n"
                f"التكلفة الإجمالية: *{b_selected.get('cost','0')}* درهم.\n\n"
                f"يرجى إحضار الإيصال الخاص بالاستلام.\n"
                f"شكراً لتعاملكم معنا 🌹\n\n"
                f"---------------------------\n\n"
                f"Greetings from {app_config['store_name']}.\n\n"
                f"Your repair bag (*{b_selected['bag_number']}*) is ready for collection at the store.\n"
                f"Total Cost: *{b_selected.get('cost','0')}* AED.\n\n"
                f"Kindly bring your repair receipt.\n"
                f"Thank you 🌹"
            )
            url_ready = f"https://api.whatsapp.com/send?phone={num}&text={urllib.parse.quote(msg_ready)}"
            if st.link_button("WhatsApp 📱 Ready Message", url_ready, use_container_width=True, type="primary"):
                add_to_log(b_selected['bag_number'], b_selected['customer_name'], "Ready Message Sent")
                
        with act_c2:
            msg_remind = (
                f"السلام عليكم من {app_config['store_name']}.\n\n"
                f"نود تذكيركم بأن التصليح رقم (*{b_selected['bag_number']}*) لا يزال متاحاً للاستلام.\n"
                f"التكلفة الإجمالية: *{b_selected.get('cost','0')}* درهم.\n\n"
                f"يرجى إحضار الإيصال الخاص بالاستلام.\n"
                f"شكراً لتعاملكم معنا 🌹\n\n"
                f"---------------------------\n\n"
                f"Greetings from {app_config['store_name']}.\n\n"
                f"This is a friendly reminder that your repair bag (*{b_selected['bag_number']}*) is still waiting for collection.\n"
                f"Total Cost: *{b_selected.get('cost','0')}* AED.\n\n"
                f"Kindly bring your repair receipt.\n"
                f"Thank you 🌹"
            )
            url_remind = f"https://api.whatsapp.com/send?phone={num}&text={urllib.parse.quote(msg_remind)}"
            if st.link_button(tr("Send Reminder"), url_remind, use_container_width=True):
                add_to_log(b_selected['bag_number'], b_selected['customer_name'], "Reminder Sent")
                
        st.markdown("---")
        btn_manage_col1, btn_manage_col2, btn_manage_col3, btn_manage_col4 = st.columns(4)
        
        with btn_manage_col1:
            if st.button(tr("Manage & Details 📝"), use_container_width=True, type="secondary"):
                show_bag_details_dialog(actual_bag_index)
                
        with btn_manage_col2:
            password_input = st.text_input("Admin Password", type="password", label_visibility="collapsed", placeholder="Enter Password to Edit/Delete")
            
        with btn_manage_col3:
            if st.button(tr("Edit"), use_container_width=True):
                if password_input == ADMIN_PASSWORD:
                    st.session_state.current_edit_index = actual_bag_index
                    st.session_state.active_menu = "Add Bag"  # التغيير المباشر والقاطع للسيسشن ستيت
                    st.rerun()
                else: st.error("Incorrect Admin Password!")
                
        with btn_manage_col4:
            if st.button(tr("Delete"), use_container_width=True):
                if password_input == ADMIN_PASSWORD:
                    add_to_log(b_selected['bag_number'], b_selected['customer_name'], "Record Deleted")
                    del bags_data[actual_bag_index]
                    save_data(bags_data)
                    st.session_state.current_edit_index = None
                    st.session_state.selected_row_idx = 0
                    st.success("Record deleted!")
                    st.rerun()
                else: st.error("Incorrect Admin Password!")
    else:
        st.info("No matching data found.")

# --- القسم الثالث: التنبيهات 📢 (Alerts) ---
elif choice == "Alerts":
    st.header(tr("Alerts"))
    today = datetime.today()
    urgent_alerts, normal_alerts = [], []
    
    for b in bags_data:
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
    income = sum(float(b.get("cost", 0)) for b in bags_data if b.get("status") == "Delivered")
    counts = {
        "Total Bags": len(bags_data), "Received": sum(1 for b in bags_data if b["status"] == "Received"),
        "Out Repair": sum(1 for b in bags_data if b["status"] == "Out for Repair"), "In Store": sum(1 for b in bags_data if b["status"] == "Received Back"),
        "Delivered": sum(1 for b in bags_data if b["status"] == "Delivered"), "Income": f"{income} AED"
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
    for b in bags_data:
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
        log_display = [{tr("Time"): e.get('time'), tr("Bag #"): e.get('bag'), tr("Customer"): e.get('customer'), tr("Action"): e.get('action')} for e in reversed(actions_log)]
        if log_display: st.dataframe(log_display, use_container_width=True, hide_index=True)
        else: st.info("No system logs found.")
