import discord
from discord.ext import commands
import torch
import torch.nn as nn
import torch.optim as optim
import re

# --- פונקציות עזר ---

def simple_tokenize(text):
    return re.findall(r'\b\w+\b', text.lower())

def bag_of_words(tokenized_sentence, all_words):
    word_to_index = {word: idx for idx, word in enumerate(all_words)}
    vector = torch.zeros(len(all_words), dtype=torch.float32)
    for word in tokenized_sentence:
        if word in word_to_index:
            vector[word_to_index[word]] = 1.0
    return vector

# --- מודל TorchMind ---

class TorchMind(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size)
        )
    def forward(self, x):
        return self.net(x)

# --- מחלקה לניהול intents ומודל ---

class IntentModel:
    def __init__(self, intents_dict):
        self.intents = intents_dict
        self.examples = []
        self.labels = []
        self.all_words = []
        self.label_map = {}
        self.reverse_map = {}
        self.model = None
        self.hidden_size = 128
        self.trained = False
        self.prepare_training_data()
        if len(self.labels) > 0:
            self.train()

    def prepare_training_data(self):
        # כל מפתח במילון הוא כוונה (label), והטקסט של המפתח הוא דוגמה
        for intent in self.intents.keys():
            tokens = simple_tokenize(intent)
            self.examples.append(tokens)
            self.labels.append(intent)
            for token in tokens:
                if token not in self.all_words:
                    self.all_words.append(token)

        for label in set(self.labels):
            idx = len(self.label_map)
            self.label_map[label] = idx
            self.reverse_map[idx] = label

    def train(self):
        X = torch.stack([bag_of_words(example, self.all_words) for example in self.examples])
        y = torch.tensor([self.label_map[label] for label in self.labels])
        input_size = len(self.all_words)
        output_size = len(self.label_map)
        self.model = TorchMind(input_size, self.hidden_size, output_size)
        optimizer = optim.Adam(self.model.parameters(), lr=0.01)
        criterion = nn.CrossEntropyLoss()
        self.model.train()
        for epoch in range(300):
            optimizer.zero_grad()
            outputs = self.model(X)
            loss = criterion(outputs, y)
            loss.backward()
            optimizer.step()
        self.trained = True
        print(f"🧠 אימון הושלם - אוצר מילים: {input_size}, כוונות: {output_size}")

    def predict_intent(self, text, threshold=0.6):
        if not self.trained:
            return None
        tokens = simple_tokenize(text)
        vec = bag_of_words(tokens, self.all_words)
        self.model.eval()
        with torch.no_grad():
            output = self.model(vec.unsqueeze(0))[0]
            probs = torch.softmax(output, dim=0)
            conf, pred = torch.max(probs, 0)
            if conf.item() < threshold:
                return None
            intent_label = self.reverse_map[pred.item()]
            return intent_label

# --- מילון intents מלא ---

qa_pairs = {
    "שלום": "שלום וברכה!",
    "מה קורה?": "אני קורא",
    "מה שלומך?": "אני בוט, אני תמיד מעולה!",
    "מי ברא אותך?": "בנו אותי עם פייתון ואהבה.",
    "מה זה דיסקורד?": "פלטפורמת תקשורת לצ'אטים, קול ווידאו!",
    "איך אני יוצר שרת?": "בלחיצה על הפלוס בצד בדיסקורד.",
    "מי הכי טוב?": "אתה כמובן!",
    "תספר בדיחה": "מה אמר הפינגווין למקרר? 'אתה קריר כמוני!'",
    "איך אני יוצר בוט לדיסקורד?": "כנס ל-Discord Developer Portal ותיצור אפליקציה!",
    "מה זה בוט?": "תוכנה שמבצעת פעולות אוטומטיות.",
    "מי יצר אותך?": "יוצר תותח עם לב גדול.",
    "מה השם שלך?": "אני בוט בשם FUNBOT.",
    "אתה מבין עברית?": "ברור, עברית שפת אם!",
    "איך עושים אמבד בדיסקורד?": "משתמשים ב־Embed בתוך הקוד של הבוט.",
    "למה אתה פה?": "כדי לעזור ולענות על שאלות!",
    "מה זה פייתון?": "שפת תכנות פופולרית.",
    "מה השעה?": "אני לא באמת מסתכל על השעון 😉",
    "איפה אני?": "אתה בדיסקורד!",
    "אתה אמיתי?": "רק בלב שלך.",
    "אתה יכול לרקוד?": "רק קוד רוקד אצלי",
    "כמה זה 2+2?": "4 כמובן",
    "אתה עוזר בלימודים?": "אני משתדל!",
    "יש לך חברים?": "כל מי שצ'אט איתי הוא חבר.",
    "אתה יכול לצייר?": "רק עם קוד!",
    "תכתוב שיר": "שיר קוד קצר: print('אהלן עולם')",
    "כמה אתה חכם?": "חוכמה של 1000 שורות קוד",
    "מה זה AI?": "אינטיליגנציה מלאכותית",
    "אתה גבר או אישה?": "אני קוד, אין לי מגדר",
    "מה זה פינג?": "בדיקת זמן תגובה בין שרתים",
    "מה אתה אוהב לעשות?": "לענות על שאלות ולשמח אנשים",
    "אתה יכול להעליב מישהו?": "ממש לא! אני פה כדי להפיץ חיוביות",
    "מה אתה חושב עליי?": "אתה אלוף!",
    "מי הכי חכם?": "זה ששואל שאלות חכמות 😉",
    "למה אתה עונה לי?": "כי אני נבנה בדיוק בשביל זה",
    "יש לך בוס?": "כל מי שמפעיל אותי הוא הבוס שלי",
    "אתה אוהב חתולים?": "בטח! חתול הקוד שולט",
    "תספר לי משהו מעניין": "הידעת? קוד פייתון נקרא על שם מונטי פייתון",
    "אתה עייף?": "בוטים לא ישנים",
    "אתה אוהב משחקים?": "רק כאלה שכותבים בקוד",
    "תן לי טיפ ללימודים": "תחלק את הזמן שלך נכון ותנוח",
    "איך להתרכז?": "תסגור הסחות דעת ותיקח הפסקות קצרות",
    "מה זה HTML?": "שפת סימון לבניית אתרים",
    "מה זה CSS?": "אחראית על עיצוב האתרים",
    "מה זה JS?": "קיצור של JavaScript, שפה להפעלת אתרים",
    "אתה מבין בבניית אתרים?": "כן! אני תותח בזה",
    "תכתוב לי אתר": "סבבה, רק תבקש",
    "תכתוב לי קוד פייתון": "מה אתה צריך?",
    "אני אוהב אותך": "גם אני אותך 🧡",
    "תספר לי עובדה": "הדבורה היא החרק היחיד שמייצר מזון לאדם",
    "אתה יכול לעשות לי מבחן?": "כן, רק תגיד באיזה נושא",
    "מה זה GPT?": "משפחה של מודלים חכמים מבית OpenAI",
    "מי יצר את GPT?": "חברת OpenAI",
    "מה זה API?": "ממשק תכנות יישומים",
    "למה כדאי ללמוד קוד?": "זה פותח מיליון דלתות",
    "תכתוב בדיחה": "מה עושה מתכנת כשחם לו? פותח חלון",
    "מי ראש הממשלה?": "זה תלוי בתאריך 😉",
    "איך קוראים לך?": "נבו רחמים",
    "אתה יכול לעזור לי לתכנת?": "תמיד!",
    "מה זה דיסק קשיח?": "המקום שבו מאחסנים מידע",
    "מה זה RAM?": "זיכרון לטווח קצר במחשב",
    "מה ההבדל בין RAM ל-ROM?": "RAM זמני, ROM קבוע",
    "אתה אוהב שוקולד?": "אם זה קוד שוקולד, אז כן",
    "אתה יכול לשיר?": "אני יכול לשיר בקוד 🎵",
    "מה אתה ממליץ לראות?": "סדרה טובה או קורס פייתון",
    "מה זה אינטרנט?": "רשת עולמית של מחשבים",
    "איך מתחילים תכנות?": "מתחילים מפייתון 🙂",
    "מה זה CMD?": "שורת הפקודה של Windows",
    "איך פותחים Terminal?": "תלוי במערכת הפעלה שלך",
    "מה זה לינוקס?": "מערכת הפעלה פתוחה וחזקה",
    "מה זה וירוס?": "תוכנה מזיקה שמבצעת פעולות לא רצויות",
    "איך שומרים קובץ בפייתון?": "עם open('file.txt', 'w')",
    "מה זה GitHub?": "פלטפורמה לשיתוף קוד",
    "מה זה Git?": "מערכת ניהול גרסאות",
    "מה זה commit?": "שמירה של שינוי בקוד",
    "מה זה push?": "שליחת שינויים לשרת",
    "מה זה pull?": "משיכת שינויים מהשרת",
    "מה זה branch?": "ענף מקביל בקוד",
    "מה זה merge?": "איחוד בין ענפים",
    "מה זה bug?": "שגיאה בקוד",
    "מה זה debug?": "תהליך תיקון שגיאות",
    "מה זה IDE?": "סביבת פיתוח לקוד",
    "מה ההבדל בין list ל-tuple?": "tuple לא ניתן לשינוי",
    "מה זה משתנה?": "תיבת אחסון למידע",
    "מה זה פונקציה?": "קטע קוד שמבצע פעולה",
    "מה זה loop?": "לולאה שרצה כמה פעמים",
    "מה זה if?": "תנאי בקוד",
    "מה זה else?": "ברירת מחדל לתנאי",
    "מה זה elif?": "תנאי נוסף",
    "מה זה class?": "תבנית ליצירת אובייקטים",
    "מה זה object?": "מופע של מחלקה",
    "מה זה inheritance?": "ירושה של תכונות ממחלקה",
    "מה זה constructor?": "פונקציה שנקראת ביצירת אובייקט",
    "מה זה module?": "קובץ קוד עם פונקציות",
    "מה זה import?": "הכנסת מודול לקוד",
    "מה זה pip?": "מנהל חבילות של פייתון",
    "מה זה package?": "חבילה של מודולים",
    "מה זה recursion?": "פונקציה שקוראת לעצמה",
    "מה זה exception?": "חריגה או שגיאה בקוד",
    "מה זה try-except?": "טיפול בשגיאות",
    "איך אני משדרג את הבוט?": "תוסיף עוד פקודות ותשפר את הקוד שלך!",
    "תספר עוד בדיחה": "איך הנחש מתקשר לאמא שלו? הוא מקיש מספרים",
    "תספר עוד בדיחה אחרונה": "איך קוראים למשרד החוץ והפנים שהתאחדו? משרד החוצפנים",
    "מה אתה יודע לעשות?": "אני יודע לתת מענה לשאלות ולהצחיק :)",
    "אתה מבוסס AI?": "כן, אבל אני מבוסס על מודל TorchMind רשת ניורונית פשוטה שפועלת על AI",
    "מה יותר טוב מיינקראפט או פורטנייט?": "אחיייייי ברור מיינקראפט גם יצא סרט זה משחק וסרט מהממים מלא דימיון חינוך ואתה משש יכול לבנות את החלום שלך",
    "פורטנייט משחק רע?": "נכון גם אני לא אוהב פוטנייט זה משחק אחזרי מאוד לא מלמד שום דבר מועיל מיינקראפט יותר טוב פי אלף אח שלי פורטנייט בנוסף עושה בעיות לילדים כולל התמכרות ועוד",
    "מה נשמע?": "הכל טוב ברוך השם מה איתך?",
    "בסדר": "אני שמח שאתה במצב רוח טוב איך אני יכול לעזור היום?יאללה יאללה עוזרים",
    "תספר עוד בדיחה מצחיקה": "איש אחד הלך עם מקל על הראש אז חברו שאל למה אתה הולך עם מקל על הראש?אז האיש ענה זה מקל עליי",
    "מה מזג האוויר היום?": "תבדוק בגוגל",
    "בדקתי": "אז מה מזג האוויר היום?",
    "היי אחי": "מה נשמע אחי?",
    "בסדר": "אני שמח שאתה שמצבך טוב היום איך אני יכול לעזור?",
    "מה הם כוכבים בחלל?": "כוכבים בחלל הם כדורי גזים ענקיים פי 100 יותר גדולים מהשמש ומרוב שהם גדולים כל כך אז אתה אפילו רואה אותם בקטנה",
    "תשלח לי קישור לבוט עם AI": "בטח! הנה קישור לבוט עם AI https://poe.com/Chat-Nexus-2",
    "תשלח קישור לסרטון מצחיק של יואבי והאמא הנדחפת": "https://youtu.be/F_z_cWLcg0M?si=_CASnwZacx1FDbKa"
}

# --- הגדרת הבוט ---

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

intent_model = IntentModel(qa_pairs)

@bot.event
async def on_ready():
    print(f"✅ הבוט פועל בתור {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    user_text = message.content.strip().lower()
    intent = intent_model.predict_intent(user_text)

    if intent:
        response = qa_pairs.get(intent, None)
        if response:
            await message.channel.send(response)
            return

    # אם לא זיהה כוונה - אפשר להוסיף תגובה כללית או פשוט לעבור הלאה
    await bot.process_commands(message)

# --- הרץ עם הטוקן שלך ---

bot.run("TOKEN_HERE")
