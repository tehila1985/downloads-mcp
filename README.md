# Downloads Warden — MCP Server

שרת MCP לניהול אוטומטי ואינטליגנטי של תיקיית ההורדות דרך Claude Desktop.

---

## 📋 תוכן עניינים
- [יכולות](#יכולות)
- [ארכיטקטורה](#ארכיטקטורה)
- [התקנה](#התקנה)
- [הגדרת Claude Desktop](#הגדרת-claude-desktop)
- [בדיקה עם MCP Inspector](#בדיקה-עם-mcp-inspector)
- [הרצת בדיקות](#הרצת-בדיקות)
- [כלים זמינים](#כלים-זמינים)

---

## 🎯 יכולות

Downloads Warden מספק 8 כלים לניהול תיקיית ההורדות:

| # | כלי | תיאור |
|---|-----|--------|
| 1 | `scan_downloads_tool` | סריקה וסטטיסטיקות מפורטות |
| 2 | `smart_sort_files_tool` | מיון לפי סוג קובץ (Documents, Media, Installers, Code, Archives, Other) |
| 3 | `sort_by_date_tool` | מיון לתיקיות לפי שנה-חודש (YYYY-MM) |
| 4 | `deduplicate_by_hash_tool` | מחיקת כפילויות עם SHA-256 |
| 5 | `deduplicate_folders_tool` | מחיקת תיקיות עם תוכן זהה |
| 6 | `auto_extract_and_cleanup_tool` | חילוץ ZIP ומחיקת הארכיון |
| 7 | `clear_installers_tool` | מחיקת קבצי התקנה ישנים |
| 8 | `find_large_files_tool` | איתור קבצים גדולים |

---

## 🏗️ ארכיטקטורה

הפרויקט בנוי לפי ארכיטקטורת 4 שכבות:

```
src/
├── domain/               # שכבת הדומיין — לוגיקה עסקית טהורה
│   ├── config.py         # כל הקטגוריות, הסיומות, וה-thresholds (frozen dataclasses)
│   ├── exceptions.py     # היררכיית חריגות מותאמת (WardenError → ...)
│   ├── events.py         # Observer pattern — EventBus + אירועים
│   ├── strategies.py     # Strategy pattern — SortStrategy ABC + Factory
│   └── models.py         # מודלים בלתי-ניתנים לשינוי (frozen dataclasses)
│
├── infrastructure/       # שכבת התשתית — כל I/O של מערכת הקבצים
│   └── file_repository.py  # BaseFileRepository ABC + LocalFileRepository
│
├── application/          # שכבת היישום — Use Cases (ה-orchestrators)
│   ├── base_sort_use_case.py   # Template Method — שלד הסידור
│   ├── sort_use_case.py        # SmartSortUseCase + DateSortUseCase
│   ├── scan_use_case.py
│   ├── deduplicate_use_case.py
│   ├── extract_use_case.py
│   └── clean_use_case.py
│
├── container.py          # DI Container — חיבור כל התלויות
└── server.py             # MCP Interface — שכבה דקה בלבד
```

### עקרונות ועיצוב
- **Strategy Pattern** — `ExtensionSortStrategy` / `DateSortStrategy` עם `StrategyFactory` registry
- **Template Method** — `BaseSortUseCase` מגדיר את השלד; תתי-מחלקות מזריקות אסטרטגיה בלבד
- **Observer / EventBus** — Use Cases מפרסמים אירועים; logging נרשם בנפרד ב-container
- **Repository Pattern** — `BaseFileRepository` ABC מאפשר החלפת file system ב-mock בלי לשנות קוד
- **Immutability** — כל מודלי הדומיין וה-config הם `@dataclass(frozen=True)`
- **Custom Exceptions** — `WardenError → FolderNotFoundError / HashComputationError / ExtractionError / ...`

---

## 🚀 התקנה

### דרישות מקדימות
- Python 3.11 ומעלה
- Claude Desktop

### שלבי התקנה

```bash
# 1. כנס לתיקיית הפרויקט
cd downloads-warden

# 2. צור סביבה וירטואלית
python -m venv .venv

# 3. הפעל את הסביבה הווירטואלית
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 4. התקן את הפרויקט כולל תלויות פיתוח
pip install -e ".[dev]"

# 5. בדוק שהשרת עולה
python run_server.py
```

---

## 🔧 הגדרת Claude Desktop

פתח את קובץ ההגדרות:
```
%APPDATA%\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json
```

הוסף:
```json
{
  "mcpServers": {
    "downloads-warden": {
      "command": "C:\\path\\to\\downloads-warden\\.venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\downloads-warden\\run_server.py"]
    }
  }
}
```

> ⚠️ החלף `C:\\path\\to\\downloads-warden` בנתיב האמיתי אצלך.

הפעל מחדש את Claude Desktop, עבור להגדרות → Developer → Local MCP servers — צריך להופיע "downloads-warden" עם ✓ ירוק.

---

## 🔍 בדיקה עם MCP Inspector

```bash
npx @modelcontextprotocol/inspector
```

- **Transport Type:** STDIO
- **Command:** `.venv\Scripts\python.exe`
- **Arguments:** `run_server.py`

לחץ **Connect** ובדוק שכל 8 הכלים מופיעים.

---

## 🧪 הרצת בדיקות

```bash
# כל הבדיקות (unit + integration) עם coverage
python -m pytest

# רק unit tests (ללא disk I/O)
python -m pytest tests/unit

# רק integration tests
python -m pytest tests/integration
```

תוצאה צפויה: **41 passed**

---

## 🛠️ כלים זמינים

| כלי | פרמטרים עיקריים | ברירת מחדל |
|-----|-----------------|------------|
| `scan_downloads_tool` | `folder_path` | תיקיית ההורדות |
| `smart_sort_files_tool` | `folder_path`, `dry_run` | `dry_run=true` |
| `sort_by_date_tool` | `folder_path`, `dry_run` | `dry_run=true` |
| `deduplicate_by_hash_tool` | `folder_path`, `dry_run` | `dry_run=true` |
| `deduplicate_folders_tool` | `folder_path`, `dry_run` | `dry_run=true` |
| `auto_extract_and_cleanup_tool` | `folder_path`, `dry_run` | `dry_run=true` |
| `clear_installers_tool` | `folder_path`, `days_old`, `dry_run` | `days_old=30`, `dry_run=true` |
| `find_large_files_tool` | `folder_path`, `min_size_mb` | `min_size_mb=500` |

> ⚠️ **תמיד השתמש ב-`dry_run=true` תחילה** לפני כל פעולה הרסנית.

---

## ⚠️ פתרון בעיות

**השרת לא מתחבר ב-Claude Desktop**
- בדוק שהנתיבים ב-`claude_desktop_config.json` נכונים ושהסביבה הווירטואלית קיימת

**`ModuleNotFoundError: No module named 'src'`**
- ודא שהתקנת עם `pip install -e ".[dev]"` ולא רק `pip install -r requirements.txt`

**הכלים לא מופיעים ב-Inspector**
- עשה Disconnect → Connect מחדש ובדוק שהשרת עולה ללא שגיאות

---

## 📝 רישיון

MIT License

---

**נוצר עם ❤️ באמצעות FastMCP**
