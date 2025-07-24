from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, CallbackQueryHandler
import json

def load_texts(lang):
    with open(f'lang/{lang}.json', 'r', encoding='utf-8') as f:
        return json.load(f)

async def show_apps_guide(update: Update, context: CallbackContext):
    """Shows the apps guide."""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "fa")
    texts = load_texts(lang)

    # For now, we use the same text for all languages.
    # This can be replaced with language-specific keys later.
    apps_guide_text = """
<b>📲 اپلیکیشن‌های کاربردی + راهنمای ورود به ایتالیا 🇮🇹</b>

🎓 <b>اپلیکیشن‌های دانشگاه و خدمات:</b>
🔹 MyUnipg – اپ دانشگاه: <a href="https://play.google.com/store/apps/details?id=it.cineca.app.myunipg">دانلود</a>
🔹 MyUnipg Job – فرصت‌های شغلی: <a href="https://play.google.com/store/apps/details?id=com.myjobunipg.app">دانلود</a>
🔹 Adisu Card – برای منسا: <a href="https://play.google.com/store/apps/details?id=it.in4matic.adisuumbriacard">دانلود</a>
🔹 FortiClient VPN – اتصال به شبکه دانشگاه: <a href="https://play.google.com/store/apps/details?id=com.fortinet.forticlient_vpn">دانلود</a>

🛍️ <b>خرید و تخفیف:</b>
🔹 University Box – تخفیف دانشجویی: <a href="https://play.google.com/store/apps/details?id=com.ubox.universitybox.app">دانلود</a>
🔹 Too Good To Go – غذا با تخفیف: <a href="https://play.google.com/store/apps/details?id=com.app.tgtg">دانلود</a>
🔹 The Fork – تخفیف رستوران: <a href="https://play.google.com/store/apps/details?id=com.lafourchette.lafourchette">دانلود</a>
🔹 Everli – سوپرمارکت آنلاین: <a href="https://play.google.com/store/apps/details?id=it.supermercato24.supermercato24">دانلود</a>

🚍 <b>حمل‌ونقل:</b>
🔹 Moovit – مسیر اتوبوس: <a href="https://play.google.com/store/apps/details?id=com.tranzmate">دانلود</a>
🔹 Salgo – اتوبوس شهری: <a href="https://play.google.com/store/apps/details?id=net.pluservice.busitaumbria">دانلود</a>
🔹 Flixbus – اتوبوس بین‌شهری: <a href="https://play.google.com/store/apps/details?id=de.flixbus.app">دانلود</a>
🔹 Weelo – دوچرخه شهری: <a href="https://play.google.com/store/apps/details?id=it.weelo.weelo">دانلود</a>
🔹 OMIO – رزرو سفر: <a href="https://play.google.com/store/apps/details?id=com.goeuro.rosie">دانلود</a>
🔹 Trenitalia – قطار: <a href="https://play.google.com/store/apps/details?id=com.lynxspa.prontotreno">دانلود</a>
🔹 InTaxi – تاکسی اینترنتی: <a href="https://play.google.com/store/apps/details?id=it.ud.microtek.InTaxi">دانلود</a>

🏠 <b>اقامت:</b>
🔹 Immobiliare – جستجوی خانه: <a href="https://play.google.com/store/apps/details?id=it.immobiliare.android">دانلود</a>
🔹 Idealista – اجاره خانه/اتاق: <a href="https://play.google.com/store/apps/details?id=com.idealista.android">دانلود</a>

💳 <b>مالی و بانکی:</b>
🔹 Revolut – کارت بانکی: <a href="https://play.google.com/store/apps/details?id=com.revolut.revolut">دانلود</a>
🔹 Wise – انتقال پول: <a href="https://play.google.com/store/apps/details?id=com.transferwise.android">دانلود</a>
🔹 Aruba PEC – ایمیل رسمی: <a href="https://play.google.com/store/apps/details?id=it.aruba.pec.mobile">دانلود</a>

🗺️ <b>گردشگری و کاربردی:</b>
🔹 Visit a City – جاذبه‌ها: <a href="https://play.google.com/store/apps/details?id=com.visitacity.visitacityapp">دانلود</a>
🔹 Radical Storage – امانت چمدان: <a href="https://play.google.com/store/apps/details?id=com.bagbnb">دانلود</a>
🔹 دوربین زنده چنترو پروجا: <a href="https://www.youtube.com/live/8TZ8YRt9nYc?feature=shared">مشاهده</a>

🌐 <b>راهنمای مراحل ورود به ایتالیا:</b>

1️⃣ <b>کدیچه فیسکاله:</b>
📍 <a href="https://maps.app.goo.gl/9y5QdviWmW8QDBNd8">Agenzia delle Entrate</a>
یا آنلاین: <a href="http://zip-codes.nonsolocap.it/codice-fiscale/">ایجاد</a>

2️⃣ <b>پرمسو:</b>
📍 <a href="https://maps.app.goo.gl/4SfaSnCCxwwMQk6CA">Questura Principale</a>
📍 <a href="https://maps.app.goo.gl/BXV6vtgn71Mdwvne7">Questura دانشجویی</a>

3️⃣ <b>ثبت‌نام دانشگاه:</b>
📍 <a href="https://unipg.esse3.cineca.it/Home.do">سایت Esse3</a>
📍 <a href="https://maps.app.goo.gl/qxkedASxBypsqNNq9">Segreteria Studenti</a>
📍 <a href="https://maps.app.goo.gl/piVCi88DubSGaHoW7">بانک Unicredit</a>

4️⃣ <b>بیمه:</b>
🔗 <a href="https://www.waitaly.net">WAI Insurance – 125 یورو</a>

5️⃣ <b>افتتاح حساب بانکی:</b>
📍 <a href="https://maps.app.goo.gl/YMN6yTA92123Ka319">Poste Italiane</a>

6️⃣ <b>واکسن / تست / گرین پس:</b>
مراجعه به داروخانه‌های محلی

7️⃣ <b>نوبت از CAF برای ISEE:</b>
🔗 <a href="https://areapersonale.mycaf.it/myCAF20/public/login">رزرو وقت</a>

✳️ نکته: پیشنهاد میشه بلیت ۱۰تایی اتوبوس از Tabaccheria بخرید (~۱۳€) و اپ Moovit نصب کنید.
"""

    await query.message.reply_text(
        text=apps_guide_text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

apps_guide_handler = CallbackQueryHandler(show_apps_guide, pattern='^apps_guide$')
