from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.clock import Clock
from plyer import notification
import sqlite3, random

# ===== إعدادات واجهة =====
Window.size = (360, 640)
Window.clearcolor = (0.1, 0.1, 0.1, 1)  # Dark mode افتراضي
dark_mode = True

# تسجيل الخط العربي
LabelBase.register(name="Arabic", fn_regular="Cairo-Regular.ttf")

# ===== قاعدة البيانات =====
db = sqlite3.connect("study.db")
c = db.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS study (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT,
    time TEXT
)
""")
db.commit()

motivations = [
    "إنت قدها 💪",
    "ركز وهتوصل 🔥",
    "كل يوم خطوة 👣",
    "مستقبلك بين إيديك 🚀"
]

# ===== Pomodoro Timer =====
POMODORO_MIN = 25  # دقائق مذاكرة
BREAK_MIN = 5      # دقائق راحة

class StudyApp(TabbedPanel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.do_default_tab = False

        # ===== تبويب الدراسة =====
        study = BoxLayout(orientation="vertical", padding=15, spacing=10)
        study.add_widget(Label(text="منظم دراستي", font_name="Arabic", font_size=26))

        self.subject = TextInput(hint_text="اسم المادة", font_name="Arabic", multiline=False)
        self.time = TextInput(hint_text="وقت المذاكرة", font_name="Arabic", multiline=False)
        add_btn = Button(text="إضافة 📚", font_name="Arabic", background_color=(0,0.5,1,1))
        add_btn.bind(on_press=self.add_study)

        self.list_label = Label(font_name="Arabic")
        study.add_widget(self.subject)
        study.add_widget(self.time)
        study.add_widget(add_btn)
        study.add_widget(self.list_label)
        self.refresh_list()
        self.add_widget(self.make_tab("الدراسة", study))

        # ===== تبويب التحفيز =====
        motivate = BoxLayout(orientation="vertical", padding=20)
        self.motivation_label = Label(text=random.choice(motivations), font_name="Arabic", font_size=22)
        mot_btn = Button(text="تحفيز جديد ✨", font_name="Arabic", background_color=(0.3,0.3,0.3,1))
        mot_btn.bind(on_press=self.new_motivation)
        motivate.add_widget(self.motivation_label)
        motivate.add_widget(mot_btn)
        self.add_widget(self.make_tab("تحفيز", motivate))

        # ===== تبويب الشات =====
        chat = BoxLayout(orientation="vertical", padding=20)
        self.chat_log = Label(text="اسألني أي حاجة 📘", font_name="Arabic")
        self.chat_input = TextInput(hint_text="اكتب سؤالك", multiline=False)
        chat_btn = Button(text="إرسال", font_name="Arabic", background_color=(0,0.5,1,1))
        chat_btn.bind(on_press=self.chat)
        chat.add_widget(self.chat_log)
        chat.add_widget(self.chat_input)
        chat.add_widget(chat_btn)
        self.add_widget(self.make_tab("اسألني", chat))

        # ===== تبويب الآلة الحاسبة =====
        calc = BoxLayout(orientation="vertical", padding=20)
        self.calc_input = TextInput(hint_text="مثال: 5*6+2", multiline=False)
        calc_btn = Button(text="احسب", font_name="Arabic", background_color=(0.3,0.3,0.3,1))
        calc_btn.bind(on_press=self.calculate)
        self.calc_result = Label(text="", font_name="Arabic")
        calc.add_widget(self.calc_input)
        calc.add_widget(calc_btn)
        calc.add_widget(self.calc_result)
        self.add_widget(self.make_tab("آلة حاسبة", calc))

        # ===== تبويب Pomodoro =====
        pomodoro_tab = BoxLayout(orientation="vertical", padding=20)
        self.timer_label = Label(text="Pomodoro Timer: جاهز", font_name="Arabic", font_size=22)
        self.start_pomo_btn = Button(text="ابدأ مذاكرة ⏱️", font_name="Arabic", background_color=(0,0.5,1,1))
        self.start_pomo_btn.bind(on_press=self.start_pomodoro)
        self.stop_pomo_btn = Button(text="أوقف المؤقت", font_name="Arabic", background_color=(0.5,0.5,0.5,1))
        self.stop_pomo_btn.bind(on_press=self.stop_pomodoro)
        pomodoro_tab.add_widget(self.timer_label)
        pomodoro_tab.add_widget(self.start_pomo_btn)
        pomodoro_tab.add_widget(self.stop_pomo_btn)
        self.add_widget(self.make_tab("Pomodoro", pomodoro_tab))
        self.pomodoro_event = None
        self.pomo_time = 0

        # ===== تبويب الإعدادات =====
        settings_tab = BoxLayout(orientation="vertical", padding=20)
        self.mode_btn = Button(text="تبديل Dark/Light Mode", font_name="Arabic", background_color=(0.3,0.3,0.3,1))
        self.mode_btn.bind(on_press=self.toggle_mode)
        settings_tab.add_widget(self.mode_btn)
        self.add_widget(self.make_tab("الإعدادات", settings_tab))

        # ===== تبويب عن التطبيق =====
        about = BoxLayout(orientation="vertical", padding=20)
        about.add_widget(Label(text="تطبيق منظم الدراسة\n\nإعداد: مصطفى محمود 💙", font_name="Arabic", font_size=20))
        self.add_widget(self.make_tab("عن التطبيق", about))

    def make_tab(self, title, content):
        tab = TabbedPanelItem(text=title)
        tab.add_widget(content)
        return tab

    # ===== وظائف الدراسة =====
    def add_study(self, instance):
        c.execute("INSERT INTO study (subject,time) VALUES (?,?)",(self.subject.text,self.time.text))
        db.commit()
        self.subject.text=self.time.text=""
        self.refresh_list()
        notification.notify(title="📚 مذاكرة", message="تم إضافة موعد مذاكرة", timeout=5)

    def refresh_list(self):
        c.execute("SELECT subject,time FROM study")
        self.list_label.text="\n".join([f"• {s[0]} - {s[1]}" for s in c.fetchall()])

    # ===== وظائف التحفيز =====
    def new_motivation(self, instance):
        self.motivation_label.text=random.choice(motivations)

    # ===== وظائف الشات =====
    def chat(self, instance):
        q = self.chat_input.text.lower()
        if "مذاكرة" in q:
            self.chat_log.text="نصيحة: حاول تقسم وقت المذاكرة وخد راحة منتظمة."
        elif "راحة" in q:
            self.chat_log.text="نصيحة: 5 دقائق راحة بعد كل 25 دقيقة Pomodoro."
        else:
            self.chat_log.text="نصيحة: ركّز واستمر، كل يوم خطوة 👣"
        self.chat_input.text=""

    # ===== الآلة الحاسبة =====
    def calculate(self, instance):
        try:
            self.calc_result.text=f"النتيجة: {eval(self.calc_input.text)}"
        except:
            self.calc_result.text="عملية غير صحيحة ❌"

    # ===== Pomodoro Timer =====
    def start_pomodoro(self, instance):
        self.pomo_time = POMODORO_MIN*60
        if self.pomodoro_event:
            self.pomodoro_event.cancel()
        self.pomodoro_event = Clock.schedule_interval(self.update_timer,1)
        notification.notify(title="⏱️ Pomodoro", message="ابدأ المذاكرة!", timeout=5)

    def stop_pomodoro(self, instance):
        if self.pomodoro_event:
            self.pomodoro_event.cancel()
            self.timer_label.text="Pomodoro Timer: متوقف"
            notification.notify(title="⏱️ Pomodoro", message="تم إيقاف المؤقت", timeout=5)

    def update_timer(self, dt):
        if self.pomo_time>0:
            self.pomo_time -= 1
            mins, secs = divmod(self.pomo_time,60)
            self.timer_label.text=f"Pomodoro Timer: {mins:02d}:{secs:02d}"
        else:
            self.pomodoro_event.cancel()
            self.timer_label.text="Pomodoro Timer: انتهى الوقت!"
            notification.notify(title="⏱️ Pomodoro", message="انتهى وقت المذاكرة! خذ استراحة", timeout=5)

    # ===== Dark / Light Mode =====
    def toggle_mode(self, instance):
        global dark_mode
        dark_mode = not dark_mode
        if dark_mode:
            Window.clearcolor=(0.1,0.1,0.1,1)
        else:
            Window.clearcolor=(1,1,1,1)

class MyApp(App):
    def build(self):
        self.title = "منظم دراستي - مصطفى محمود"
        return StudyApp()

MyApp().run()
