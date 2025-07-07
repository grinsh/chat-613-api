from flask import Flask, request, jsonify, Response
from openai import OpenAI
import os
from dotenv import load_dotenv
from json_convert import make_utf8_json_response
import httpx




load_dotenv()  
api_key = os.getenv("OPENAI_API_KEY")  
client = OpenAI(
    api_key=api_key,
    http_client=httpx.Client(verify=False)
)  # או השתמשי ב־os.getenv("OPENAI_API_KEY")


app = Flask(__name__)


# תיאור התחום
DOMAIN_DESCRIPTION = "הצ'אט מתמקד במתמטיקה לתלמידי בית ספר יסודי בלבד."

# פונקציה לבדיקת אם השאלה רלוונטית למתמטיקה יסודית
def is_valid_math_question(question):
    keywords = ['חיבור', 'חיסור', 'כפל', 'חילוק', 'שברים', 'אחוזים', 'מספרים טבעיים', 'בעיות מילוליות', 'גאומטריה בסיסית']
    return any(keyword in question for keyword in keywords)

# תחליף לתשובה מ-GPT לצורך דוגמה
def get_mock_gpt_response(question):
    return make_utf8_json_response(f"שאלה מצוינת על מתמטיקה יסודית: {question}.\nפתרון: (תשובה לדוגמה)")

def get_gpt_response(question):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "אתה מורה למתמטיקה לתלמידי בית ספר יסודי."},
            {"role": "user", "content": question}
        ],
        max_tokens=30
    )
    return(response.choices[0].message.content)

# נקודת קצה לקבלת תיאור התחום
@app.route('/api/domain', methods=['GET'])
def get_domain():
    return make_utf8_json_response({"domain": DOMAIN_DESCRIPTION})

# נקודת קצה לשליחת שאלה וקבלת תשובה
@app.route('/api/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    question = data.get("question", "")

    # if not is_valid_math_question(question):
    #     return make_utf8_json_response({"error": "השאלה לא קשורה למתמטיקה לבית ספר יסודי"}), 400

    # כאן אפשר לשלב קריאה אמיתית ל-GPT אם רוצים
    answer = get_gpt_response(question)

    return make_utf8_json_response({"question": question, "answer": answer})

# נקודת קצה לתיעוד ה-API
@app.route('/api/docs', methods=['GET'])
def api_docs():
    return make_utf8_json_response({
        "endpoints": {
            "/api/domain": {
                "method": "GET",
                "description": "קבלת תיאור התחום שבו עוסק הצ'אט"
            },
            "/api/ask": {
                "method": "POST",
                "description": "שליחת שאלה וקבלת תשובה (רק מתמטיקה ליסודי)",
                "body": {
                    "question": "string"
                }
            },
            "/api/docs": {
                "method": "GET",
                "description": "קבלת תיעוד של נקודות הקצה"
            }
        }
    })
from flask import Response

@app.route('/api/docs/html', methods=['GET'])
def api_docs_html():
    html_content = """
    <!DOCTYPE html>
    <html lang="he">
    <head>
        <meta charset="UTF-8">
        <title>תיעוד ה-API</title>
        <style>
            body { font-family: Arial, sans-serif; direction: rtl; background-color: #f9f9f9; padding: 20px; }
            h1 { color: #333; }
            .endpoint { margin-bottom: 30px; padding: 15px; background-color: #fff; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            .endpoint h2 { margin: 0; color: #0056b3; }
            .endpoint p, .endpoint pre { margin: 10px 0; }
            pre { background: #f1f1f1; padding: 10px; border-radius: 5px; direction: ltr; overflow-x: auto; }
        </style>
    </head>
    <body>
        <h1>📘 תיעוד ה-API - מתמטיקה לבית ספר יסודי</h1>

        <div class="endpoint">
            <h2>GET /api/domain</h2>
            <p>מתאר את תחום הפעילות של ה-API.</p>
            <p><strong>URL:</strong> <code>/api/domain</code></p>
            <p><strong>תגובה לדוגמה:</strong></p>
            <pre>{
    "domain": "הצ'אט מתמקד במתמטיקה לתלמידי בית ספר יסודי בלבד."
}</pre>
        </div>

        <div class="endpoint">
            <h2>POST /api/ask</h2>
            <p>שולח שאלה ומחזיר תשובה אם היא רלוונטית למתמטיקה לכיתות יסוד.</p>
            <p><strong>URL:</strong> <code>/api/ask</code></p>
            <p><strong>פרמטרים בגוף הבקשה (JSON):</strong></p>
            <pre>{
    "question": "כמה זה 8 כפול 7?"
}</pre>
            <p><strong>תגובה לדוגמה:</strong></p>
            <pre>{
    "question": "כמה זה 8 כפול 7?",
    "answer": "שאלה מצוינת על מתמטיקה יסודית: כמה זה 8 כפול 7?.\\nפתרון: (תשובה לדוגמה)"
}</pre>
        </div>

        <div class="endpoint">
            <h2>GET /api/docs</h2>
            <p>מחזיר תיעוד בפורמט JSON.</p>
            <p><strong>URL:</strong> <code>/api/docs</code></p>
            <p><strong>תגובה לדוגמה:</strong> אובייקט JSON עם רשימת נקודות הקצה.</p>
        </div>

        <div class="endpoint">
            <h2>GET /api/docs/html</h2>
            <p>מציג תיעוד זהה ב-HTML.</p>
            <p><strong>URL:</strong> <code>/api/docs/html</code></p>
        </div>
    </body>
    </html>
    """
    return Response(html_content, content_type='text/html; charset=utf-8')


if __name__ == '__main__':
    app.run(debug=True)
