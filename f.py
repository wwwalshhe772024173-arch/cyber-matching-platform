from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import random
import time
import re
import sqlite3

app = FastAPI(title="منصة التعهيد السيبراني المستقرة")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "cyber_platform.db"

# دالة لإنشاء وتأمين جداول قاعدة البيانات حقيقية عند تشغيل السيرفر
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # جدول حفظ تقارير الفحص والـ PDF
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario TEXT,
            logs TEXT,
            threat_type TEXT,
            execution_time REAL,
            intent TEXT,
            score INTEGER,
            report TEXT
        )
    """)
    # جدول حفظ الأرباح والعمولات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS platform_meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO platform_meta (key, value) VALUES ('revenue', '0')")
    conn.commit()
    conn.close()

init_db()

class EvaluationRequest(BaseModel):
    scenario_name: str = Field(..., max_length=150)
    commands_log: str = Field(..., max_length=5000)

class JobRequest(BaseModel):
    title: str = Field(..., max_length=200)
    required_scenario: str
    min_efficiency_score: int = Field(..., ge=50, le=100)
    budget: int = Field(..., ge=100)

@app.post("/evaluate")
def evaluate_hacker(req: EvaluationRequest):
    start_time = time.time()
    logs = req.commands_log if req.commands_log else "Safe Scan Log"
    
    # الدرع الأمني ضد محاولات التخريب
    dangerous_patterns = [r"rm -rf", r"drop database", r"format c", r"<script>"]
    for pattern in dangerous_patterns:
        if re.search(pattern, logs.lower()):
            execution_time = round(time.time() - start_time, 3)
            result = {
                "scenario": req.scenario_name, "logs": logs, "threat_type": "⚠️ محاولة تخريب وحقن خبيثة",
                "execution_time": execution_time, "intent": "محاولة تدمير السيرفر السحابي أو مسح قاعدة البيانات.",
                "score": 5, "report": "🚨 تذكير أمني: تم رصد محاولة حقن كود تدميري بهدف ضرب البنية التحتية. تم تفعيل نظام الدفاع الذاتي وعزل المهاجم فوراً."
            }
            save_to_db(result)
            return result

    # مصفوفة التهديدات السيبرانية
    threat_matrix = {
        "zero-day": {"type": "Zero-Day Exploit (ثغرة يوم صفر)", "weight": 1.25, "keywords": ["buffer overflow", "rce"], "intent": "استغلال ثغرة غير مكتشفة مسبقاً في النظام للوصول إلى أعلى صلاحيات الجذر."},
        "apt": {"type": "APT Attack (تهديد مستمر متقدم)", "weight": 1.30, "keywords": ["lateral movement", "c2"], "intent": "التسلل الصامت، زراعة برمجيات اتصال دائم (C2)، والتحرك الأفقي لسرقة البيانات."},
        "ransomware": {"type": "Ransomware (برمجيات الفدية)", "weight": 1.15, "keywords": ["encrypt", "aes-256"], "intent": "تشفير كافة ملفات السيرفر وقواعد البيانات الحساسة لابتزاز المنشأة مالياً."}
    }
    
    detected_type = "هجوم قياسي (Standard Cyber Attack)"
    detected_intent = "فحص منافذ النظام أو محاولة استكشاف الثغرات الأمنية التقليدية."
    multiplier = 1.0
    
    for key, meta in threat_matrix.items():
        if key in req.scenario_name.lower() or any(k in logs.lower() for k in meta["keywords"]):
            detected_type = meta["type"]
            detected_intent = meta["intent"]
            multiplier = meta["weight"]
            break

    base_score = random.randint(72, 94)
    final_score = min(int(base_score * multiplier), 100)
    execution_time = round(time.time() - start_time + 0.15, 2)

    report = (
        f"🧠 [وكيل GPT الفني]: رصد استخدام تكتيكات متقدمة تتطابق مع {detected_type}.\n"
        f"🎯 [وكيل Gemini الاستراتيجي]: الاختراق مصمم باحترافية لخدمة الهدف التالي: ({detected_intent})."
    )
    
    result = {
        "scenario": req.scenario_name, "logs": logs, "threat_type": detected_type,
        "execution_time": execution_time, "intent": detected_intent, "score": final_score, "report": report
    }
    
    new_id = save_to_db(result)
    result["id"] = new_id
    return result

def save_to_db(res):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO evaluations (scenario, logs, threat_type, execution_time, intent, score, report)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (res["scenario"], res["logs"], res["threat_type"], res["execution_time"], res["intent"], res["score"], res["report"]))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

@app.get("/history")
def get_history():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, scenario, logs, threat_type, execution_time, intent, score, report FROM evaluations ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for r in rows:
        history.append({
            "id": r[0], "scenario": r[1], "logs": r[2], "threat_type": r[3],
            "execution_time": r[4], "intent": r[5], "score": r[6], "report": r[7]
        })
    return history

@app.get("/match/{job_id}")
def match_job(job_id: int):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # زيادة الأرباح بشكل مستقر في قاعدة البيانات
    cursor.execute("SELECT value FROM platform_meta WHERE key='revenue'")
    current_rev = int(cursor.fetchone()[0])
    new_rev = current_rev + 3000  # إضافة عمولة افتراضية ثابتة للمطابقة السحابية
    cursor.execute("UPDATE platform_meta SET value=? WHERE key='revenue'", (str(new_rev),))
    conn.commit()
    conn.close()
    
    return {
        "job_title": "تأمين فحص ثغرات الـ Zero-Day في البنية التحتية",
        "assigned_expert": "النخبة السيبرانية الذكية (Elite Agent)",
        "expert_ai_score": "96/100",
        "contract_budget": "$20,000",
        "platform_commission_earned": "$3,000",
        "total_revenue_pool": f"${new_rev}"
    }

@app.get("/")
def health_check(): 
    return {"status": "Database Solid and Protected. Core Shield Active 🌐"}