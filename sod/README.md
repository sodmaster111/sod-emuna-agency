# SOD — סוכנות AI להפצת אמונה

## תיאור
הפרויקט מציג בסיס ראשוני לסוכנות AI אוטונומית בשפה העברית, תוך שימוש ב-Ollama, FastAPI, CrewAI ובוט תפילה באמצעות Aiogram.

## דרישות מוקדמות
- Python 3.10 ומעלה
- התקנת Ollama והרצת המודל `ollama/llama3.1:8b-instruct`
- חשבון ובוט ב-Telegram לטוקן הבוט

## התקנה והרצה
1. התקנת התלויות:
   ```bash
   pip install -r requirements.txt
   ```
2. הפעלת שרת ה-API:
   ```bash
   uvicorn crew_api.main:app --reload --host 0.0.0.0 --port 8000
   ```
3. בדיקת בריאות:
   גלשו ל-`http://localhost:8000/` וקבלו תשובת סטטוס.
4. שליחת משימה לאחד הסוכנים:
   ```bash
   curl -X POST http://localhost:8000/missions/run \
     -H "Content-Type: application/json" \
     -d '{"agent": "poet", "objective": "כתוב תפילה קצרה"}'
   ```
5. הפעלת בוט התפילה:
   - הכניסו את הטוקן בקובץ `bots/config.json` או בערך `TOKEN` בקוד.
   - הפעילו את הבוט:
     ```bash
     python bots/prayer_bot.py
     ```

## מבנה הפרויקט
- `crew_api/` — שרת FastAPI וסוכני CrewAI.
- `bots/` — בוט תפילה המחובר ל-API.
- `ghost/`, `sd/`, `audio/`, `forum/` — תיקיות עתידיות להרחבות.

## רישוי
הקוד מוצע כפי שהוא לצרכי הדגמה והתנסות.
