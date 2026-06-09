import sqlite3

def fetch_saved_data():
    # الاتصال بنفس ملف قاعدة البيانات
    conn = sqlite3.connect('cyber_platform.db')
    cursor = conn.cursor()
    
    print("================ 👥 جدول المستخدمين (Users) ================")
    cursor.execute("SELECT * FROM Users")
    users = cursor.fetchall()
    for user in users:
        print(f"رقم المستخدم: {user[0]} | الاسم: {user[1]} | البريد: {user[2]} | الدور: {user[3]}")
        
    print("\n================ 🖥️ جدول جلسات الفحص (Sandboxes) ================")
    cursor.execute("SELECT * FROM Sandboxes")
    sessions = cursor.fetchall()
    for session in sessions:
        print(f"رقم الجلسة: {session[0]} | رقم المخترق: {session[1]} | السيناريو: {session[2]}")
        print(f"📜 سجل الأوامر المنفذة:\n{session[3]}")
        print("-" * 50)

    print("\n================ 🤖 جدول التقييمات الذكية (AI_Evaluations) ================")
    cursor.execute("SELECT evaluation_id, skill_level, efficiency_score FROM AI_Evaluations")
    evaluations = cursor.fetchall()
    for eval_item in evaluations:
        print(f"رقم التقييم: {eval_item[0]} | مستوى المهارة: {eval_item[1]} | درجة الكفاءة: {eval_item[2]}/100")
    
    conn.close()

# تشغيل الفحص
fetch_saved_data()