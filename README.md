# Downloads Warden - MCP Server

שרת MCP לניהול אוטומטי ואינטליגנטי של תיקיית ההורדות דרך Claude Desktop.

## 📋 תוכן עניינים
- [יכולות](#יכולות)
- [התקנה](#התקנה)
- [הגדרת Claude Desktop](#הגדרת-claude-desktop)
- [בדיקה עם MCP Inspector](#בדיקה-עם-mcp-inspector)
- [שימוש](#שימוש)
- [כלים זמינים](#כלים-זמינים)

---

## 🎯 יכולות

Downloads Warden מספק 8 כלים חזקים לניהול תיקיית ההורדות:

### 1. **ניתוח תיקייה** 📊
- סריקת כל הקבצים בתיקיית ההורדות
- סטטיסטיקות מפורטות: מספר קבצים, גודל כולל
- פילוח לפי קטגוריות וסוגי קבצים

### 2. **מיון חכם לפי סוג** 📁
- מיון אוטומטי לקטגוריות:
  - **Documents**: PDF, Word, Excel, PowerPoint
  - **Media**: תמונות, וידאו, אודיו
  - **Installers**: קבצי התקנה (EXE, MSI, DMG)
  - **Code**: קבצי קוד (Python, JavaScript, Java, וכו')
  - **Archives**: קבצי דחיסה (ZIP, RAR, 7Z)
  - **Other**: כל השאר

### 3. **מיון לפי תאריכים** 📅
- ארגון קבצים לתיקיות לפי שנה-חודש (2025-01, 2024-12)
- מבוסס על תאריך השינוי האחרון של הקובץ

### 4. **מחיקת כפילויות** 🔍
- זיהוי קבצים זהים באמצעות SHA-256 hash
- שמירת הקובץ הראשון, מחיקת שאר העותקים
- חיסכון במקום דיסק

### 5. **מחיקת תיקיות כפולות** 📂
- זיהוי תיקיות עם תוכן זהה לחלוטין
- השוואה מבוססת hash של כל הקבצים

### 6. **חילוץ ארכיונים אוטומטי** 📦
- חילוץ אוטומטי של קבצי ZIP
- מחיקת הארכיון לאחר חילוץ מוצלח
- חיסכון במקום ושמירה על סדר

### 7. **ניקוי קבצי התקנה ישנים** 🗑️
- מחיקת קבצי EXE, MSI, DMG ישנים
- ברירת מחדל: קבצים מעל 30 יום
- ניתן להגדיר מספר ימים מותאם אישית

### 8. **איתור קבצים גדולים** 💾
- מציאת קבצים שתופסים הרבה מקום
- ברירת מחדל: 500MB ומעלה
- ניתן להגדיר גודל מינימלי מותאם אישית

---

## 🚀 התקנה

### דרישות מקדימות
- Python 3.8 ומעלה
- Claude Desktop

### שלבי התקנה

1. **שכפל את הפרויקט**
```bash
cd C:\Users\User\Desktop
git clone <repository-url> downloads-warden
cd downloads-warden
```

2. **צור סביבה וירטואלית**
```bash
python -m venv .venv
```

3. **הפעל את הסביבה הוירטואלית**
```bash
.venv\Scripts\activate
```

4. **התקן תלויות**
```bash
pip install -r requirements.txt
```

5. **בדוק שהשרת עובד**
```bash
python -m src.server
```

אם הכל עובד, תראה:
```
╭──────────────────────────────────────────────────────────────────────────────╮
│                         ▄▀▀ ▄▀█ █▀▀ ▀█▀ █▀▄▀█ █▀▀ █▀█                        │
│                         █▀  █▀█ ▄▄█  █  █ ▀ █ █▄▄ █▀▀                        │
│                                FastMCP 3.0.2                                 │
│                   🖥  Server:      Downloads Warden, 3.0.2                    │
╰──────────────────────────────────────────────────────────────────────────────╯
```

לחץ `Ctrl+C` לעצירה.

---

## 🔧 הגדרת Claude Desktop

### שלב 1: מצא את קובץ ההגדרות

פתח את קובץ ההגדרות של Claude Desktop:
```bash
notepad %APPDATA%\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json
```

### שלב 2: הוסף את השרת

אם הקובץ ריק או מכיל רק `preferences`, הוסף את `mcpServers`:

```json
{
  "preferences": {
    "coworkScheduledTasksEnabled": false,
    "sidebarMode": "chat",
    "coworkWebSearchEnabled": true
  },
  "mcpServers": {
    "downloads-warden": {
      "command": "C:\\Users\\User\\Desktop\\downloads-warden\\.venv\\Scripts\\python.exe",
      "args": ["C:\\Users\\User\\Desktop\\downloads-warden\\run_server.py"]
    }
  }
}
```

**⚠️ חשוב:** שנה את הנתיבים בהתאם למיקום שלך!

### שלב 3: הפעל מחדש את Claude Desktop

1. סגור את Claude Desktop **לגמרי** (כולל מה-System Tray)
2. פתח מחדש
3. עבור להגדרות → Developer → Local MCP servers
4. אמור להופיע "downloads-warden" עם סטטוס ירוק ✓

---

## 🔍 בדיקה עם MCP Inspector

לפני חיבור ל-Claude, מומלץ לבדוק עם Inspector:

### התקנת Inspector
```bash
npm install -g @modelcontextprotocol/inspector
```

### הרצת Inspector
```bash
npx @modelcontextprotocol/inspector
```

### הגדרות חיבור
- **Transport Type:** STDIO
- **Command:** `C:\Users\User\Desktop\downloads-warden\.venv\Scripts\python.exe`
- **Arguments:** `C:\Users\User\Desktop\downloads-warden\run_server.py`
- **Environment Variables:** (השאר ריק)

**⚠️ חשוב:** שנה את הנתיבים בהתאם למיקום שלך!

לחץ **Connect** ובדוק שכל 8 הכלים מופיעים.

---

## 💡 שימוש

### דוגמאות לשימוש ב-Claude Desktop

#### ניתוח תיקייה
```
סרוק את תיקיית ההורדות שלי ותן לי סטטיסטיקות
```

#### מיון חכם
```
מיין את כל הקבצים בהורדות לפי סוג (dry_run: true)
```
לאחר אישור:
```
מיין את כל הקבצים בהורדות לפי סוג (dry_run: false)
```

#### מיון לפי תאריכים
```
ארגן את הקבצים שלי לפי חודשים
```

#### מחיקת כפילויות
```
מצא ומחק קבצים כפולים (dry_run: true)
```

#### חילוץ ארכיונים
```
חלץ את כל קבצי ה-ZIP ומחק אותם
```

#### ניקוי קבצי התקנה
```
מחק קבצי התקנה ישנים מעל 60 יום
```

#### איתור קבצים גדולים
```
מצא קבצים מעל 1GB
```

---

## 🛠️ כלים זמינים

| כלי | תיאור | פרמטרים |
|-----|--------|----------|
| `scan_downloads_tool` | ניתוח תיקיית הורדות | `folder_path` (אופציונלי) |
| `smart_sort_files_tool` | מיון לפי סוג קובץ | `folder_path`, `dry_run` |
| `sort_by_date_tool` | מיון לפי תאריך | `folder_path`, `dry_run` |
| `deduplicate_by_hash_tool` | מחיקת כפילויות | `folder_path`, `dry_run` |
| `deduplicate_folders_tool` | מחיקת תיקיות כפולות | `folder_path`, `dry_run` |
| `auto_extract_and_cleanup_tool` | חילוץ ZIP | `folder_path`, `dry_run` |
| `clear_installers_tool` | מחיקת installers | `folder_path`, `days_old`, `dry_run` |
| `find_large_files_tool` | איתור קבצים גדולים | `folder_path`, `min_size_mb` |

### פרמטרים נפוצים

- **folder_path**: נתיב לתיקייה (ברירת מחדל: תיקיית ההורדות של המשתמש)
- **dry_run**: `true` = סימולציה בלבד, `false` = ביצוע אמיתי
- **days_old**: מספר ימים (ברירת מחדל: 30)
- **min_size_mb**: גודל מינימלי במגה-בייט (ברירת מחדל: 500)

---

## ⚠️ אזהרות

1. **תמיד השתמש ב-dry_run=true תחילה** לפני פעולות הרסניות
2. **גבה קבצים חשובים** לפני מחיקה המונית
3. **בדוק את התוצאות** לפני אישור פעולות סופיות
4. השרת עובד על תיקיית ההורדות שלך אוטומטית - אין צורך להזין נתיב

---

## 🐛 פתרון בעיות

### השרת לא מתחבר ב-Claude Desktop
1. בדוק שהנתיבים בקובץ ההגדרות נכונים
2. ודא שהסביבה הוירטואלית קיימת (`.venv`)
3. בדוק את הלוגים: Settings → Developer → Local MCP servers → לחץ על השרת

### "ModuleNotFoundError: No module named 'src'"
- ודא שאתה משתמש ב-`run_server.py` ולא ב-`-m src.server`

### הכלים לא מופיעים ב-Inspector
- עשה Disconnect ואז Connect מחדש
- בדוק שהשרת רץ ללא שגיאות

---

## 📝 רישיון

MIT License

---

## 🤝 תרומה

Pull requests מתקבלים בברכה! לשינויים גדולים, אנא פתח issue תחילה.

---

**נוצר עם ❤️ באמצעות FastMCP**
