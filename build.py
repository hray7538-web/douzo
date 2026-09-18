#!/usr/bin/env python3
"""Douzo Nagoya — 정적 사이트 생성기.
언어 × 업종 조합으로 SEO 페이지를 찍어낸다. 의존성 없음.
  python3 build.py
"""
import os, json, shutil, html, datetime, urllib.parse

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
SITE = "https://yoyoi.jp"
TODAY = datetime.date.today().isoformat()
CONTACT = "hray7538@gmail.com"   # ← 접수받을 주소. 이 한 줄만 바꾸면 됩니다.

# 대화 창구. 계정을 만들면 여기만 채우면 사이트 전체(모든 언어·모든 페이지)에 버튼이 생깁니다.
#   line      : https://line.me/R/ti/p/@xxxxxxx
#   whatsapp  : https://wa.me/81xxxxxxxxxx
#   instagram : https://instagram.com/xxxxx
CHANNELS = {"line":"", "whatsapp":"", "instagram":""}
CH_LABEL = {"line":"LINE", "whatsapp":"WhatsApp", "instagram":"Instagram DM"}

LANGS = {
 "en": dict(name="English", hreflang="en", dir="en",
   tagline="Just write what you want.<br>We book it.",
   sub="Restaurants, hair salons, nails in Nagoya. Even the places that only take phone reservations in Japanese.",
   promise=["Write in your own language","Confirmed within a day","No app, no login"],
   steps=[("Tell us","Write it however you like. Any language."),
          ("We handle it","We find the place, check availability, and call in Japanese."),
          ("Done","You get the confirmation in your language.")],
   why_h="Why you need this",
   why=["Most good places in Nagoya take reservations <b>by phone, in Japanese only</b>.",
        "Japan's own booking sites are written in Japanese. You can't use them.",
        "You don't have to become fluent. Just tell us."],
   form_h="What do you want to book?",
   form_ph="e.g. Dinner for 2 on Friday around 7pm, near Sakae. No pork. Budget about 5,000 yen each.",
   btn_mail="Send by email", btn_copy="Copy", copied="Copied",
   note="We'll reply with the confirmation. If the first place is full, we try the next.",
   foot="ヨヨイ Yoyoi — Nagoya, Japan",
   trust_h='What we keep', trust=['<b>We check both sides.</b> We look at the places, and we look at the guests too.', '<b>Everything is agreed before you arrive.</b> Allergies, headcount, budget, time — we pass it all on in Japanese, so nothing breaks at the table.', "<b>We don't send the same problem twice.</b> No-shows and rudeness mean we stop booking for that person."],
   pay_h='Paying', pay=['<b>Pay what you think it was worth.</b> Guests pay. Shops pay. Either, both, or neither.', '<b>Paying more does not buy priority.</b> We will not put one guest ahead of another for money. If we did, none of this would be worth trusting.', 'It is a signal of trust, not a purchase.'],
   shop_h='For shops', shop_cta='For shops in Nagoya',
   kw="Nagoya reservation, book restaurant Nagoya English, Nagoya salon booking"),

 "ja": dict(name="日本語", hreflang="ja", dir="ja",
   tagline="書くだけ。<br>予約します。",
   sub="名古屋の飲食店・美容室・ネイル。電話予約しか受けていないお店も。",
   promise=["どの言語でもそのまま","1日以内に確定","アプリ不要・登録不要"],
   steps=[("書く","形式は自由です。どの言語でも。"),
          ("こちらで手配","お店を探し、空きを確認し、日本語で電話します。"),
          ("完了","確定内容をお客様の言語でお返しします。")],
   why_h="このサービスについて",
   why=["名古屋の良いお店の多くは、<b>電話・日本語のみ</b>で予約を受けています。",
        "日本の予約サイトは日本語で書かれています。訪日のお客様には使えません。",
        "日本語を覚える必要はありません。書いてください。"],
   form_h="ご希望をお書きください",
   form_ph="例：金曜19時ごろ、2名、栄の近く。豚肉なし。予算はお一人5,000円くらい。",
   btn_mail="メールで送る", btn_copy="コピー", copied="コピーしました",
   note="確定のご連絡をいたします。最初のお店が満席の場合は次をお探しします。",
   foot="ヨヨイ Yoyoi — 名古屋",
   trust_h='私たちが守ること', trust=['<b>両方を見ます。</b>お店を評価し、お客様も評価します。', '<b>到着前にすべて合意しておきます。</b>アレルギー・人数・予算・時間を日本語でお伝えするので、席で問題が起きません。', '<b>同じ問題を二度送りません。</b>無連絡キャンセルや失礼があった方には、以後お取り次ぎしません。'],
   pay_h='料金について', pay=['<b>価値があったと思う額をお支払いください。</b>お客様が払っても、お店が払っても、どちらでも、どちらでなくても構いません。', '<b>多く払っても優先されません。</b>お金で順番を売りません。売った時点で、信頼する意味がなくなります。', 'これは購入ではなく、信頼の合図です。'],
   shop_h='お店の方へ', shop_cta='名古屋のお店の方へ',
   kw="名古屋 予約代行, 名古屋 外国人 予約, 名古屋 飲食店 予約"),

 "ko": dict(name="한국어", hreflang="ko", dir="ko",
   tagline="쓰기만 하세요.<br>예약해 드립니다.",
   sub="나고야 음식점·미용실·네일. 전화로만 예약받는 가게까지.",
   promise=["한국어로 그냥 쓰세요","하루 안에 확정","앱도 로그인도 없습니다"],
   steps=[("쓰세요","형식은 자유입니다. 한국어로요."),
          ("저희가 합니다","가게를 찾고, 자리를 확인하고, 일본어로 전화합니다."),
          ("끝","확정 내용을 한국어로 보내드립니다.")],
   why_h="왜 필요한가",
   why=["나고야의 좋은 가게는 대부분 <b>전화로, 일본어로만</b> 예약을 받습니다.",
        "일본 예약 사이트는 일본어로 되어 있습니다. 외국인은 쓸 수 없습니다.",
        "일본어를 배우실 필요 없습니다. 그냥 말씀해 주세요."],
   form_h="무엇을 예약할까요?",
   form_ph="예: 금요일 저녁 7시쯤 2명, 사카에 근처. 돼지고기 빼고. 1인 5,000엔 정도.",
   btn_mail="메일로 보내기", btn_copy="복사", copied="복사했습니다",
   note="확정되면 연락드립니다. 첫 가게가 만석이면 다음 곳을 찾습니다.",
   foot="ヨヨイ Yoyoi — 나고야",
   trust_h='우리가 지키는 것', trust=['<b>양쪽을 봅니다.</b> 가게를 평가하고, 손님도 평가합니다.', '<b>도착하기 전에 다 합의해 둡니다.</b> 알레르기·인원·예산·시간을 일본어로 전달해서, 자리에서 문제가 생기지 않습니다.', '<b>같은 문제를 두 번 보내지 않습니다.</b> 노쇼나 무례가 있었던 분은 이후 중개하지 않습니다.'],
   pay_h='요금', pay=['<b>값이 있었다고 생각하는 만큼 내십니다.</b> 손님이 내도, 가게가 내도, 둘 다여도, 아니어도 괜찮습니다.', '<b>많이 내도 우선순위를 살 수 없습니다.</b> 돈으로 순서를 팔지 않습니다. 파는 순간 신뢰할 이유가 없어집니다.', '구매가 아니라 신뢰의 표시입니다.'],
   shop_h='가게 하시는 분께', shop_cta='나고야 가게 하시는 분께',
   kw="나고야 예약 대행, 나고야 맛집 예약, 나고야 미용실 예약"),

 "zh-hant": dict(name="繁體中文", hreflang="zh-Hant", dir="zh-hant",
   tagline="只要寫下來。<br>我們幫您訂。",
   sub="名古屋的餐廳、美容院、美甲。連只接受日語電話預約的店家也可以。",
   promise=["用您的語言直接寫","一天內確認","不用下載App、不用註冊"],
   steps=[("寫下來","格式自由，用任何語言都可以。"),
          ("我們處理","我們找店家、確認空位，並用日語打電話。"),
          ("完成","把確認結果用您的語言回覆您。")],
   why_h="為什麼需要",
   why=["名古屋大部分好店只接受<b>電話、日語</b>預約。",
        "日本的訂位網站是日文的，外國人無法使用。",
        "您不需要學日語。告訴我們就好。"],
   form_h="您想預約什麼？",
   form_ph="例如：星期五晚上7點左右2位，榮附近。不要豬肉。每人預算約5,000日圓。",
   btn_mail="用電子郵件寄出", btn_copy="複製", copied="已複製",
   note="確認後會通知您。如果第一家滿了，我們會找下一家。",
   foot="ヨヨイ Yoyoi — 名古屋",
   trust_h='我們堅持的事', trust=['<b>我們看兩邊。</b>我們評價店家，也評價客人。', '<b>到店前全部談好。</b>過敏、人數、預算、時間，我們用日語轉達，所以在座位上不會出問題。', '<b>同樣的問題不送第二次。</b>訂了不到、態度失禮的客人，之後我們不再代訂。'],
   pay_h='關於費用', pay=['<b>覺得值多少就付多少。</b>客人付、店家付、兩邊付、都不付，都可以。', '<b>付得多不會被優先。</b>我們不用錢賣順序。一旦賣了，就沒有信任的意義了。', '這不是購買，是信任的表示。'],
   shop_h='給店家', shop_cta='給名古屋的店家',
   kw="名古屋 訂位, 名古屋 餐廳 預約, 名古屋 美容院 預約"),

 "zh-hans": dict(name="简体中文", hreflang="zh-Hans", dir="zh-hans",
   tagline="只要写下来。<br>我们帮您订。",
   sub="名古屋的餐厅、美容院、美甲。连只接受日语电话预约的店也可以。",
   promise=["用您的语言直接写","一天内确认","无需下载App、无需注册"],
   steps=[("写下来","格式自由，用任何语言都可以。"),
          ("我们处理","我们找店家、确认空位，并用日语打电话。"),
          ("完成","把确认结果用您的语言回复您。")],
   why_h="为什么需要",
   why=["名古屋大部分好店只接受<b>电话、日语</b>预约。",
        "日本的订位网站是日文的，外国人无法使用。",
        "您不需要学日语。告诉我们就好。"],
   form_h="您想预约什么？",
   form_ph="例如：周五晚上7点左右2位，荣附近。不要猪肉。每人预算约5,000日元。",
   btn_mail="用邮件发送", btn_copy="复制", copied="已复制",
   note="确认后会通知您。如果第一家满了，我们会找下一家。",
   foot="ヨヨイ Yoyoi — 名古屋",
   trust_h='我们坚持的事', trust=['<b>我们看两边。</b>我们评价店家，也评价客人。', '<b>到店前全部谈好。</b>过敏、人数、预算、时间，我们用日语转达，所以在座位上不会出问题。', '<b>同样的问题不送第二次。</b>订了不到、态度失礼的客人，之后我们不再代订。'],
   pay_h='关于费用', pay=['<b>觉得值多少就付多少。</b>客人付、店家付、两边付、都不付，都可以。', '<b>付得多不会被优先。</b>我们不用钱卖顺序。一旦卖了，就没有信任的意义了。', '这不是购买，是信任的表示。'],
   shop_h='给店家', shop_cta='给名古屋的店家',
   kw="名古屋 订位, 名古屋 餐厅 预约, 名古屋 美容院 预约"),

 "th": dict(name="ไทย", hreflang="th", dir="th",
   tagline="แค่เขียนมา<br>เราจองให้",
   sub="ร้านอาหาร ร้านทำผม ร้านทำเล็บในนาโกยา รวมถึงร้านที่รับจองทางโทรศัพท์ภาษาญี่ปุ่นเท่านั้น",
   promise=["เขียนเป็นภาษาของคุณได้เลย","ยืนยันภายในหนึ่งวัน","ไม่ต้องโหลดแอป ไม่ต้องสมัคร"],
   steps=[("เขียนมา","รูปแบบอิสระ ภาษาอะไรก็ได้"),
          ("เราจัดการ","เราหาร้าน เช็กที่ว่าง และโทรเป็นภาษาญี่ปุ่น"),
          ("เสร็จ","เราส่งผลการยืนยันเป็นภาษาของคุณ")],
   why_h="ทำไมต้องใช้บริการนี้",
   why=["ร้านดีๆ ในนาโกยาส่วนใหญ่รับจอง<b>ทางโทรศัพท์ เป็นภาษาญี่ปุ่นเท่านั้น</b>",
        "เว็บจองของญี่ปุ่นเป็นภาษาญี่ปุ่น ชาวต่างชาติใช้ไม่ได้",
        "คุณไม่ต้องเรียนภาษาญี่ปุ่น บอกเรามาก็พอ"],
   form_h="ต้องการจองอะไร",
   form_ph="ตัวอย่าง: วันศุกร์ประมาณ 19:00 สองคน ใกล้ซาคาเอะ ไม่กินหมู งบประมาณคนละ 5,000 เยน",
   btn_mail="ส่งทางอีเมล", btn_copy="คัดลอก", copied="คัดลอกแล้ว",
   note="เราจะแจ้งผลการยืนยัน หากร้านแรกเต็ม เราจะหาร้านถัดไป",
   foot="ヨヨイ Yoyoi — นาโกยา",
   trust_h='สิ่งที่เรายึดถือ', trust=['<b>เราดูทั้งสองฝ่าย</b> เราประเมินร้าน และประเมินลูกค้าด้วย', '<b>ตกลงกันครบก่อนไปถึง</b> ภูมิแพ้ จำนวนคน งบประมาณ เวลา เราส่งต่อเป็นภาษาญี่ปุ่น จึงไม่มีปัญหาที่โต๊ะ', '<b>เราไม่ส่งปัญหาเดิมสองครั้ง</b> ผู้ที่จองแล้วไม่ไปหรือเสียมารยาท เราจะไม่จองให้อีก'],
   pay_h='เรื่องค่าบริการ', pay=['<b>จ่ายเท่าที่คุณคิดว่าคุ้ม</b> ลูกค้าจ่ายก็ได้ ร้านจ่ายก็ได้ ทั้งสองฝ่ายหรือไม่จ่ายเลยก็ได้', '<b>จ่ายมากไม่ได้สิทธิ์ก่อน</b> เราไม่ขายลำดับด้วยเงิน ถ้าขาย ก็ไม่มีเหตุให้เชื่อใจกันอีก', 'นี่ไม่ใช่การซื้อ แต่เป็นสัญญาณของความไว้ใจ'],
   shop_h='สำหรับร้านค้า', shop_cta='สำหรับร้านในนาโกยา',
   kw="จองร้านอาหาร นาโกยา, นาโกยา จองร้าน, นาโกยา ร้านทำผม จอง"),
}

# 업종 × 언어 SEO 페이지
CATS = [
 dict(slug="restaurant", t=dict(en="Restaurant reservations in Nagoya", ja="名古屋の飲食店予約", ko="나고야 음식점 예약",
      **{"zh-hant":"名古屋餐廳訂位","zh-hans":"名古屋餐厅订位","th":"จองร้านอาหารในนาโกยา"}),
      d=dict(en="Counter seats, small izakaya, places with no online booking. We call for you.",
             ja="カウンター席、小さな居酒屋、ネット予約のないお店。こちらから電話します。",
             ko="카운터석, 작은 이자카야, 온라인 예약이 없는 가게. 저희가 전화합니다.",
             **{"zh-hant":"吧檯座位、小居酒屋、沒有網路訂位的店家。我們幫您打電話。",
                "zh-hans":"吧台座位、小居酒屋、没有网络订位的店家。我们帮您打电话。",
                "th":"ที่นั่งเคาน์เตอร์ อิซากายะเล็กๆ ร้านที่ไม่มีระบบจองออนไลน์ เราโทรให้"})),
 dict(slug="sushi", t=dict(en="Sushi reservations in Nagoya", ja="名古屋の寿司店予約", ko="나고야 스시 예약",
      **{"zh-hant":"名古屋壽司店訂位","zh-hans":"名古屋寿司店订位","th":"จองร้านซูชิในนาโกยา"}),
      d=dict(en="Omakase counters often take phone bookings only, and only in Japanese.",
             ja="おまかせのカウンターは電話のみ・日本語のみのことが多いです。",
             ko="오마카세 카운터는 전화만, 일본어만 받는 곳이 많습니다.",
             **{"zh-hant":"主廚套餐的吧檯座位常常只接受電話、只用日語。",
                "zh-hans":"主厨套餐的吧台座位常常只接受电话、只用日语。",
                "th":"เคาน์เตอร์โอมากาเสะมักรับจองทางโทรศัพท์และเป็นภาษาญี่ปุ่นเท่านั้น"})),
 dict(slug="hitsumabushi", t=dict(en="Hitsumabushi & Nagoya food reservations", ja="ひつまぶし・名古屋めしの予約", ko="히츠마부시·나고야 명물 예약",
      **{"zh-hant":"鰻魚飯與名古屋美食訂位","zh-hans":"鳗鱼饭与名古屋美食订位","th":"จองฮิตสึมาบูชิและอาหารนาโกยา"}),
      d=dict(en="The famous ones have long waits. A reservation changes the whole day.",
             ja="有名店は待ち時間が長いです。予約があると一日が変わります。",
             ko="유명한 곳은 대기가 깁니다. 예약이 있으면 하루가 달라집니다.",
             **{"zh-hant":"名店等待時間很長。有訂位，一天完全不同。",
                "zh-hans":"名店等待时间很长。有订位，一天完全不同。",
                "th":"ร้านดังต้องรอนาน การจองเปลี่ยนทั้งวันของคุณ"})),
 dict(slug="hair-salon", t=dict(en="Hair salon booking in Nagoya", ja="名古屋の美容室予約", ko="나고야 미용실 예약",
      **{"zh-hant":"名古屋美容院預約","zh-hans":"名古屋美容院预约","th":"จองร้านทำผมในนาโกยา"}),
      d=dict(en="Cut, color, treatment. We pass on exactly what you want, in Japanese.",
             ja="カット・カラー・トリートメント。ご希望をそのまま日本語で伝えます。",
             ko="컷·컬러·트리트먼트. 원하시는 것을 그대로 일본어로 전달합니다.",
             **{"zh-hant":"剪髮、染髮、護髮。我們把您的需求原原本本用日語轉達。",
                "zh-hans":"剪发、染发、护发。我们把您的需求原原本本用日语转达。",
                "th":"ตัด ทำสี ทรีตเมนต์ เราส่งต่อความต้องการของคุณเป็นภาษาญี่ปุ่น"})),
 dict(slug="nail-salon", t=dict(en="Nail salon booking in Nagoya", ja="名古屋のネイルサロン予約", ko="나고야 네일 예약",
      **{"zh-hant":"名古屋美甲預約","zh-hans":"名古屋美甲预约","th":"จองร้านทำเล็บในนาโกยา"}),
      d=dict(en="Send a photo of the design you want. We'll ask if they can do it.",
             ja="やりたいデザインの写真を送ってください。できるか聞いておきます。",
             ko="원하는 디자인 사진을 보내주세요. 가능한지 물어봐 드립니다.",
             **{"zh-hant":"把想做的款式照片傳給我們，我們幫您問店家做不做。",
                "zh-hans":"把想做的款式照片发给我们，我们帮您问店家做不做。",
                "th":"ส่งรูปแบบที่ต้องการมา เราจะถามร้านให้ว่าทำได้ไหม"})),
 dict(slug="eyelash", t=dict(en="Eyelash extension booking in Nagoya", ja="名古屋のまつげエクステ予約", ko="나고야 아이래시 예약",
      **{"zh-hant":"名古屋接睫毛預約","zh-hans":"名古屋接睫毛预约","th":"จองต่อขนตาในนาโกยา"}),
      d=dict(en="Lash extensions and lash lifts, booked while you're still planning the trip.",
             ja="エクステ・パーマ。旅行の計画中に予約しておけます。",
             ko="연장·펌. 여행 계획 중에 미리 예약해 둘 수 있습니다.",
             **{"zh-hant":"接睫毛、睫毛燙。還在計畫旅行時就能先訂好。",
                "zh-hans":"接睫毛、睫毛烫。还在计划旅行时就能先订好。",
                "th":"ต่อขนตาและดัดขนตา จองไว้ได้ตั้งแต่ยังวางแผนทริป"})),
]


WHY = {'en': ('People can speak.', 'Say what you want to do. Say what you sell. We do the connecting.'), 'ja': ('人は、話せる。', 'したいことを言えばいい。売っているものを言えばいい。つなぐのは、こちらがやります。'), 'ko': ('사람은 말은 한다.', '하고 싶은 것을 말하면 됩니다. 파는 것을 말하면 됩니다. 잇는 것은 우리가 합니다.'), 'zh-hant': ('人，是會說話的。', '想做什麼，說出來就好。賣什麼，說出來就好。連起來，由我們來做。'), 'zh-hans': ('人，是会说话的。', '想做什么，说出来就好。卖什么，说出来就好。连起来，由我们来做。'), 'th': ('คนเราพูดได้', 'อยากทำอะไรก็บอกมา ขายอะไรก็บอกมา ส่วนการเชื่อมต่อ เราจัดการเอง')}

CSS = """*{box-sizing:border-box}
.chwrap{margin:.9rem 0 0;display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.chwrap span{color:var(--mut);font-size:.9rem;margin-right:.2rem}
.chwrap .ch{display:inline-block;padding:9px 16px;border:1.5px solid var(--acc);color:var(--acc);
 border-radius:999px;text-decoration:none;font-weight:700;font-size:.95rem}

:root{--bg:#fbfaf8;--fg:#1a1917;--mut:#6b6862;--line:#e6e2db;--card:#fff;--acc:#b8442e;--accs:#f5ede9}
:root:not([data-theme=light]){}
@media(prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#141311;--fg:#f0ede8;--mut:#a29c93;--line:#2b2926;--card:#1c1a18;--acc:#e5714f;--accs:#2a1f1b}}
:root[data-theme=dark]{--bg:#141311;--fg:#f0ede8;--mut:#a29c93;--line:#2b2926;--card:#1c1a18;--acc:#e5714f;--accs:#2a1f1b}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.7 -apple-system,BlinkMacSystemFont,"Hiragino Sans","Noto Sans JP","Noto Sans KR","Noto Sans Thai","Segoe UI",sans-serif}
.wrap{max-width:44rem;margin:0 auto;padding:0 1.25rem}
header{padding:1.1rem 0;border-bottom:1px solid var(--line)}
.hrow{display:flex;align-items:center;justify-content:space-between;gap:1rem}
.logo{font-weight:700;font-size:1.15rem;letter-spacing:.02em;text-decoration:none;color:var(--fg)}
.logo span{color:var(--acc)}
.langs{display:flex;flex-wrap:wrap;gap:.1rem .55rem;font-size:.8rem}
.langs a{color:var(--mut);text-decoration:none;white-space:nowrap}
.langs a:hover,.langs a[aria-current]{color:var(--acc)}
.why-hero{margin:2.4rem 0 .4rem;padding:1.1rem 0 1.2rem;border-top:2px solid var(--acc);border-bottom:1px solid var(--line)}
.why-hero b{display:block;font-size:clamp(1.3rem,4.5vw,1.75rem);line-height:1.35;letter-spacing:-.01em;margin-bottom:.5rem}
.why-hero span{color:var(--mut);font-size:.98rem;line-height:1.75}
h1{font-size:clamp(1.9rem,7vw,3rem);line-height:1.22;margin:2.6rem 0 1rem;letter-spacing:-.01em}
.sub{font-size:1.06rem;color:var(--mut);margin:0 0 1.6rem;max-width:32rem}
.chips{display:flex;flex-wrap:wrap;gap:.45rem;margin:0 0 2.4rem;padding:0;list-style:none}
.chips li{font-size:.82rem;padding:.3rem .7rem;border:1px solid var(--line);border-radius:2rem;color:var(--mut);background:var(--card)}
.box{background:var(--card);border:1px solid var(--line);border-radius:.9rem;padding:1.25rem;margin:0 0 2.6rem}
.box h2{font-size:1.02rem;margin:0 0 .7rem}
textarea{width:100%;min-height:7.5rem;padding:.8rem;border:1px solid var(--line);border-radius:.55rem;background:var(--bg);color:var(--fg);font:inherit;font-size:.97rem;resize:vertical}
textarea:focus{outline:2px solid var(--acc);outline-offset:1px}
.btns{display:flex;flex-wrap:wrap;gap:.55rem;margin-top:.8rem}
button{font:inherit;font-size:.95rem;padding:.62rem 1.15rem;border-radius:.5rem;border:1px solid var(--acc);cursor:pointer}
.p{background:var(--acc);color:#fff}
.s{background:transparent;color:var(--acc)}
.note{font-size:.83rem;color:var(--mut);margin:.75rem 0 0}
h2.sec{font-size:1.24rem;margin:2.8rem 0 1.1rem}
ol.steps{list-style:none;counter-reset:s;padding:0;margin:0 0 2.6rem}
ol.steps li{counter-increment:s;position:relative;padding-left:2.6rem;margin-bottom:1.15rem}
ol.steps li::before{content:counter(s);position:absolute;left:0;top:.05rem;width:1.75rem;height:1.75rem;border-radius:50%;background:var(--accs);color:var(--acc);display:grid;place-items:center;font-size:.85rem;font-weight:700}
ol.steps b{display:block}
ol.steps span{color:var(--mut);font-size:.94rem}
ul.why{padding-left:1.1rem;margin:0 0 2.6rem;color:var(--mut)}
ul.why li{margin-bottom:.6rem}
ul.why b{color:var(--fg)}
.cats{display:grid;gap:.6rem;grid-template-columns:1fr;margin:0 0 2.8rem;padding:0;list-style:none}
@media(min-width:34rem){.cats{grid-template-columns:1fr 1fr}}
.cats a{display:block;padding:.85rem 1rem;border:1px solid var(--line);border-radius:.6rem;background:var(--card);text-decoration:none;color:var(--fg);font-size:.94rem}
.cats a:hover{border-color:var(--acc)}
.cats small{display:block;color:var(--mut);font-size:.83rem;margin-top:.15rem}
footer{border-top:1px solid var(--line);margin-top:1rem;padding:1.6rem 0 3rem;color:var(--mut);font-size:.85rem}
footer a{color:var(--mut)}
.back{display:inline-block;margin:2rem 0 0;color:var(--acc);text-decoration:none;font-size:.9rem}
"""

JS = """(function(){
var t=document.getElementById('q'),m=document.getElementById('m'),c=document.getElementById('c');
if(!t)return;
function body(){return encodeURIComponent(t.value||'');}
if(m)m.addEventListener('click',function(){
  location.href='mailto:%s?subject='+encodeURIComponent('Yoyoi — booking request')+'&body='+body();});
if(c)c.addEventListener('click',function(){
  var d=c.getAttribute('data-done')||'Copied';
  navigator.clipboard.writeText(t.value||'').then(function(){var o=c.textContent;c.textContent=d;setTimeout(function(){c.textContent=o},1600)});});
})();""" % CONTACT

CSS += """
.prose p{margin:0 0 1rem;line-height:1.85}
.why-big{margin:2.4rem 0;padding:1.6rem 0;border-top:3px solid var(--acc);border-bottom:1px solid #e5e0da}
.why-big b{display:block;font-size:1.9rem;line-height:1.3;letter-spacing:-.01em}
.why-big span{display:block;margin-top:.7rem;color:var(--mut);line-height:1.8}
h1.lead{font-size:2.3rem;line-height:1.25}
ul.dl{list-style:none;padding:0;margin:0 0 1.6rem}
ul.dl li{padding:.7rem 0 .7rem 1.1rem;border-bottom:1px solid #eceae6;position:relative}
ul.dl li:before{content:"";position:absolute;left:0;top:1.25rem;width:5px;height:5px;border-radius:50%;background:var(--acc)}
a.cta{display:inline-block;padding:.85rem 1.5rem;background:var(--acc);color:#fff;border-radius:999px;text-decoration:none;font-weight:600}
a.cta:hover{opacity:.88}
footer a{color:inherit}
"""

def langbar(cur, sub="", only=None):
    """only: 그 하위페이지가 존재하는 언어. 없는 언어는 그 언어의 홈으로 보낸다(404 방지)."""
    out=[]
    for k,v in LANGS.items():
        tgt = sub if (only is None or k in only) else ""
        href = "%s/%s/%s" % (SITE, v["dir"], tgt)
        a = ' aria-current="page"' if k==cur else ''
        out.append('<a href="%s"%s>%s</a>' % (href, a, html.escape(v["name"])))
    return '<nav class="langs">%s</nav>' % "".join(out)

def alts(sub="", only=None):
    """only: 그 페이지가 실제로 존재하는 언어 키 목록. None이면 전 언어."""
    keys = list(LANGS.keys()) if only is None else [k for k in LANGS if k in only]
    r=['<link rel="alternate" hreflang="%s" href="%s/%s/%s">' % (LANGS[k]["hreflang"],SITE,LANGS[k]["dir"],sub) for k in keys]
    if "en" in keys:
        r.append('<link rel="alternate" hreflang="x-default" href="%s/en/%s">' % (SITE,sub))
    return "\n".join(r)

def shell(lang, title, desc, kw, canon, body, sub="", only=None, foot=None):
    v=LANGS[lang]
    footv = foot or v["foot"]
    return f"""<!doctype html>
<html lang="{v['hreflang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="keywords" content="{html.escape(kw)}">
<link rel="canonical" href="{canon}">
{alts(sub, only)}
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canon}">
<style>{CSS}</style>
</head>
<body>
<header><div class="wrap"><div class="hrow">
<a class="logo" href="{SITE}/{v['dir']}/">ヨヨイ<span>.</span></a>
{langbar(lang, sub, only)}
</div></div></header>
<main class="wrap">
{body}
</main>
<footer><div class="wrap">{html.escape(footv)} · <a href="{SITE}/{v['dir']}/about/">{"会社について" if lang=="ja" else ("회사 소개" if lang=="ko" else "About")}</a> · <a href="{SITE}/{v['dir']}/recruit/">{"採用" if lang=="ja" else ("채용" if lang=="ko" else ("徵才" if lang=="zh-hant" else ("招聘" if lang=="zh-hans" else ("ร่วมงาน" if lang=="th" else "Careers"))))}</a> · <a href="{SITE}/en/">English</a></div></footer>
<script>{JS}</script>
</body>
</html>
"""

# ══════════════════════════════════════════════════════════
#  회사 소개 · 채용
# ══════════════════════════════════════════════════════════

ABOUT = {
 "ja": dict(
  title="ヨヨイについて — つくった人と、つくった理由",
  desc="ソウル・江南で13年クリニックを運営してきた者が、名古屋で始めたサービスです。人は、話せる。つなぐのは、こちらがやります。",
  h="私たちが、これをやる理由",
  body=[
   "私たちはソウル・江南で、13年、美容クリニックを運営しています。お客様のほとんどは20〜40代の女性です。",
   "その方々が、日本へ行きます。そして向こうで何が起きるか、私たちは知っています。",
   "旅先で日本語が出てくる。翻訳をかけるとサイトが崩れる。ホームページから予約しようとしたら、日本の電話番号が要る。",
   "旅が、こうであってはいけない。旅は旅らしく——空を見て、人に会って、文化に触れる。",
   "お店も同じです。料理をつくり、お客様と笑っている時間に、ホームページを見つめていてはいけない。",
  ],
  ph="人は、話せる。",
  ps="したいことを言えばいい。売っているものを言えばいい。つなぐのは、こちらがやります。",
  who="つくった人",
  bio=[
   "<b>河恩煥（ハ・ウンファン）</b>　1982年生まれ。2008年、成均館大学校医科大学卒業。",
   "2013年からソウル・江南で美容クリニックを開業し、フランチャイズとして展開してきました。13年が経ちましたが、現在も運営を続けています。香港に3院、米国でも開業を準備しています。",
   "事業の中でAIを使う必要が生じ、そこから人文学と哲学を学ぶようになりました。順序が逆に見えるかもしれませんが——<b>「人間とは何か」を問わなければ、AIはつくれませんでした。</b>",
  ]),
 "ko": dict(
  title="요요이에 대하여 — 만든 사람과, 만든 이유",
  desc="서울 강남에서 13년 클리닉을 운영해온 사람이 나고야에서 시작한 서비스입니다. 사람은 말은 합니다. 잇는 것은 우리가 합니다.",
  h="우리가 이걸 하는 이유",
  body=[
   "우리는 서울 강남에서 13년째 미용클리닉을 하고 있습니다. 손님은 대부분 20~40대 여성입니다.",
   "그분들이 일본에 갑니다. 그리고 가서 겪는 일을 우리는 압니다.",
   "여행하다 일본어가 나옵니다. 번역기를 돌리면 웹이 깨집니다. 홈페이지로 예약했더니 일본 전화번호가 필요하다고 합니다.",
   "여행이 이러면 안 됩니다. 여행은 여행답게 — 하늘을 보고, 사람을 만나고, 문화를 겪는 것입니다.",
   "가게도 마찬가지입니다. 음식을 만들고 손님과 웃을 시간에 홈페이지를 쳐다보고 있으면 안 됩니다.",
  ],
  ph="사람은 말은 합니다.",
  ps="하고 싶은 것을 말하면 됩니다. 파는 것을 말하면 됩니다. 잇는 것은 우리가 합니다.",
  who="만든 사람",
  bio=[
   "<b>하은환</b>　1982년생. 2008년 성균관대학교 의과대학 졸업.",
   "2013년부터 서울 강남에서 미용클리닉을 열어 프랜차이즈로 전개해 왔습니다. 13년이 지났지만 지금도 운영하고 있습니다. 홍콩에 3개 원, 미국에서도 개원을 준비하고 있습니다.",
   "사업에 AI가 필요해져서, 거기서부터 인문학과 철학을 공부하게 되었습니다. 순서가 거꾸로 보일 수 있지만 — <b>「인간이 무엇인가」를 묻지 않으면 AI를 만들 수 없었습니다.</b>",
  ]),
 "en": dict(
  title="About Yoyoi — who made it, and why",
  desc="Built by someone who has run an aesthetic clinic in Gangnam, Seoul for 13 years. People can speak. We do the connecting.",
  h="Why we do this",
  body=[
   "We have run an aesthetic clinic in Gangnam, Seoul for thirteen years. Most of our guests are women in their twenties to forties.",
   "Those guests travel to Japan. And we know what happens to them there.",
   "Japanese appears. You run it through a translator and the page breaks. You try to book online and it asks for a Japanese phone number.",
   "Travel should not be like this. Travel should be travel — look at the sky, meet people, touch a culture.",
   "The same goes for the shops. The hours spent cooking and laughing with guests should not be spent staring at a booking page.",
  ],
  ph="People can speak.",
  ps="Say what you want to do. Say what you sell. We do the connecting.",
  who="Who made this",
  bio=[
   "<b>Ha EunHwan</b>　Born 1982. Graduated from Sungkyunkwan University School of Medicine in 2008.",
   "Opened an aesthetic clinic in Gangnam, Seoul in 2013 and grew it into a franchise. Thirteen years on, it is still running. Three clinics in Hong Kong; preparing to open in the United States.",
   "The work required AI, and that is how I came to study the humanities and philosophy. The order may look backwards, but it is what happened — <b>I could not build the AI without first asking what a human being is.</b>",
  ]),
 "zh-hant": dict(
  title="關於ヨヨイ — 是誰做的，為什麼做",
  desc="由在首爾江南經營美容診所十三年的人，在名古屋開始的服務。人，是會說話的。連起來，由我們來做。",
  h="我們為什麼做這件事",
  body=[
   "我們在首爾江南經營美容診所已經十三年。客人大多是二十到四十多歲的女性。",
   "那些客人會來日本。而她們在這裡會遇到什麼，我們知道。",
   "旅途中冒出日文。用翻譯一跑，網頁就壞了。想從官網訂位，卻要日本的電話號碼。",
   "旅行不該是這樣。旅行就該像旅行——看看天空，遇見人，碰觸文化。",
   "店家也一樣。做菜、和客人說笑的時間，不該花在盯著訂位頁面上。",
  ],
  ph="人，是會說話的。",
  ps="想做什麼，說出來就好。賣什麼，說出來就好。連起來，由我們來做。",
  who="做這件事的人",
  bio=[
   "<b>河恩煥（Ha EunHwan）</b>　1982年生。2008年畢業於成均館大學校醫科大學。",
   "2013年起在首爾江南開設美容診所，並發展為連鎖。十三年過去，現在仍在經營。香港有三間，也正在準備於美國開業。",
   "因為工作上需要用到AI，才開始研讀人文學與哲學。順序看起來或許是反的——但<b>不先問「人是什麼」，就做不出AI。</b>",
  ]),
 "zh-hans": dict(
  title="关于ヨヨイ — 是谁做的，为什么做",
  desc="由在首尔江南经营美容诊所十三年的人，在名古屋开始的服务。人，是会说话的。连起来，由我们来做。",
  h="我们为什么做这件事",
  body=[
   "我们在首尔江南经营美容诊所已经十三年。客人大多是二十到四十多岁的女性。",
   "那些客人会来日本。而她们在这里会遇到什么，我们知道。",
   "旅途中冒出日文。用翻译一跑，网页就坏了。想从官网订位，却要日本的电话号码。",
   "旅行不该是这样。旅行就该像旅行——看看天空，遇见人，触碰文化。",
   "店家也一样。做菜、和客人说笑的时间，不该花在盯着订位页面上。",
  ],
  ph="人，是会说话的。",
  ps="想做什么，说出来就好。卖什么，说出来就好。连起来，由我们来做。",
  who="做这件事的人",
  bio=[
   "<b>河恩焕（Ha EunHwan）</b>　1982年生。2008年毕业于成均馆大学校医科大学。",
   "2013年起在首尔江南开设美容诊所，并发展为连锁。十三年过去，现在仍在经营。香港有三间，也正在准备于美国开业。",
   "因为工作上需要用到AI，才开始研读人文学与哲学。顺序看起来或许是反的——但<b>不先问「人是什么」，就做不出AI。</b>",
  ]),
 "th": dict(
  title="เกี่ยวกับ Yoyoi — ใครสร้าง และทำไม",
  desc="บริการที่เริ่มต้นในนาโกย่า โดยผู้ที่เปิดคลินิกความงามในคังนัม กรุงโซล มาสิบสามปี คนเราพูดได้ ส่วนการเชื่อมต่อ เราจัดการเอง",
  h="ทำไมเราถึงทำสิ่งนี้",
  body=[
   "เราเปิดคลินิกความงามที่ย่านคังนัม กรุงโซล มาสิบสามปีแล้ว ลูกค้าส่วนใหญ่เป็นผู้หญิงวัยยี่สิบถึงสี่สิบปี",
   "ลูกค้าเหล่านั้นเดินทางมาญี่ปุ่น และเรารู้ดีว่าที่นั่นพวกเขาต้องเจอกับอะไร",
   "ภาษาญี่ปุ่นโผล่ขึ้นมา พอใช้ตัวแปลภาษา หน้าเว็บก็พัง จะจองผ่านเว็บไซต์ ก็ต้องมีเบอร์โทรญี่ปุ่น",
   "การเดินทางไม่ควรเป็นแบบนี้ การเดินทางควรเป็นการเดินทาง — มองท้องฟ้า พบผู้คน สัมผัสวัฒนธรรม",
   "ร้านค้าก็เช่นกัน เวลาที่ควรใช้ทำอาหารและหัวเราะกับลูกค้า ไม่ควรหมดไปกับการจ้องหน้าจอจองคิว",
  ],
  ph="คนเราพูดได้",
  ps="อยากทำอะไรก็บอกมา ขายอะไรก็บอกมา ส่วนการเชื่อมต่อ เราจัดการเอง",
  who="คนที่สร้างสิ่งนี้",
  bio=[
   "<b>Ha EunHwan</b>　เกิดปี 1982 จบแพทยศาสตร์จาก Sungkyunkwan University ในปี 2008",
   "เปิดคลินิกความงามที่คังนัม กรุงโซล ในปี 2013 และขยายเป็นแฟรนไชส์ ผ่านมาสิบสามปี ปัจจุบันยังดำเนินการอยู่ มีคลินิกในฮ่องกงสามแห่ง และกำลังเตรียมเปิดในสหรัฐอเมริกา",
   "งานที่ทำจำเป็นต้องใช้ AI จึงเริ่มศึกษามนุษยศาสตร์และปรัชญา ลำดับอาจดูกลับกัน แต่<b>ถ้าไม่ถามก่อนว่า “มนุษย์คืออะไร” ก็สร้าง AI ไม่ได้</b>",
  ]),
}


RECRUIT = {
 "ja": dict(title="採用情報 — AIと一緒に働く人を探しています｜ヨヨイ",
  desc="名古屋。AIが両方と話します。人にしかできないところに、人が行きます。AIに人のにおいを吹き込んでくれる人を探しています。正社員1名。",
  lead="AIと一緒に働く人を探しています。",
  sub="AIが両方と話します。お客様がしたいことを聞き、お店が売っているものを聞き、あいだをつなぎます。<br>人にしかできないところに、人が行きます。",
  wanted_h="探しているのは、こういう人です", wanted="AIに、人のにおいを吹き込んでくれる人",
  wanted_body=["AIは正確です。でも、あたたかくない。",
   "お客様が何を不安に思っているのか。お店が何に困っているのか。——それは、人が教えてあげないと分かりません。",
   "<b>技術は分からなくて大丈夫です。人が分かることが、技術です。</b>"],
  secs=[("仕事の内容",["AIがやりとりした内容を見て、ずれているところを直す","人が必要な場面で、人として応対する","お店との関係をつくる"]),
        ("応募資格",["在留資格に就労制限のない方","日本語で業務のやりとりができる方"]),
        ("条件",["正社員／常勤　1名","勤務地：名古屋市中区（栄）予定","給与・社会保険・休日：決まり次第、このページに掲載します"])],
  apply_h="応募・お問い合わせ",
  apply="下のボタンからメールが開きます。履歴書は不要です。<br>「なぜ興味を持ったか」を、ひとことだけ書いてください。",
  btn="メールで応募する", mail="ヨヨイ 採用応募"),

 "ko": dict(title="채용 — AI와 함께 일할 사람을 찾습니다｜요요이",
  desc="나고야. AI가 양쪽과 이야기합니다. 사람에게만 되는 곳에 사람이 갑니다. AI에게 인간의 향기를 불러줄 사람을 찾습니다. 정사원 1명.",
  lead="AI와 함께 일할 사람을 찾습니다.",
  sub="AI가 양쪽과 이야기합니다. 손님이 하고 싶은 것을 듣고, 가게가 파는 것을 듣고, 사이를 잇습니다.<br>사람에게만 되는 곳에, 사람이 갑니다.",
  wanted_h="우리가 찾는 사람은 이렇습니다", wanted="AI에게 인간의 향기를 불러줄 사람",
  wanted_body=["AI는 정확합니다. 그런데 따뜻하지 않습니다.",
   "손님이 무엇을 불안해하는지. 가게가 무엇을 곤란해하는지. — 그건 사람이 알려줘야 합니다.",
   "<b>기술은 몰라도 됩니다. 사람을 아는 것이 기술입니다.</b>"],
  secs=[("하는 일",["AI가 주고받은 내용을 보고, 어긋난 곳을 고칩니다","사람이 필요한 순간에 사람으로 응대합니다","가게와 관계를 만듭니다"]),
        ("응모 자격",["재류자격에 취로 제한이 없는 분","일본어로 업무 소통이 가능한 분"]),
        ("조건",["정사원／상근　1명","근무지: 나고야시 나카구(사카에) 예정","급여·사회보험·휴일: 정해지는 대로 이 페이지에 게재합니다"])],
  apply_h="응모·문의",
  apply="아래 버튼을 누르면 메일이 열립니다. 이력서는 필요 없습니다.<br>「왜 관심을 가졌는지」만 한 줄 써주세요.",
  btn="메일로 응모하기", mail="요요이 채용 응모"),

 "en": dict(title="Careers — someone to work alongside the AI｜Yoyoi",
  desc="Nagoya. The AI talks to both sides. Where only a person will do, a person goes. Looking for someone who can give the AI a human scent. One full-time position.",
  lead="We are looking for someone to work alongside the AI.",
  sub="The AI talks to both sides. It hears what the guest wants, hears what the shop sells, and connects them.<br>Where only a person will do, a person goes.",
  wanted_h="This is who we are looking for", wanted="Someone who can give the AI a human scent",
  wanted_body=["The AI is accurate. But it is not warm.",
   "What the guest is anxious about. What the shop is struggling with. — A person has to tell it.",
   "<b>You do not need to understand the technology. Understanding people is the technology.</b>"],
  secs=[("The work",["Read what the AI exchanged, and fix what is off","Step in as a person when a person is needed","Build relationships with the shops"]),
        ("Eligibility",["A status of residence with no work restrictions","Able to handle work communication in Japanese"]),
        ("Terms",["Full-time, permanent — one position","Location: Naka-ku, Nagoya (Sakae), planned","Salary, social insurance, holidays: posted here once decided"])],
  apply_h="Apply",
  apply="The button below opens an email. No resume needed.<br>Just write one line: why this caught your interest.",
  btn="Apply by email", mail="Yoyoi - application"),

 "zh-hant": dict(title="徵才 — 尋找與AI一起工作的人｜ヨヨイ",
  desc="名古屋。AI會和雙方對話。只有人才能做到的地方，由人去。尋找能為AI吹進人的氣味的人。正職1名。",
  lead="我們在尋找與AI一起工作的人。",
  sub="AI會和雙方對話。聽客人想做什麼，聽店家賣什麼，把兩邊連起來。<br>只有人才能做到的地方，由人去。",
  wanted_h="我們要找的是這樣的人", wanted="能為AI吹進人的氣味的人",
  wanted_body=["AI很準確。但不溫暖。",
   "客人在不安什麼。店家在困擾什麼。——這些要由人來告訴它。",
   "<b>不懂技術也沒關係。懂人，就是技術。</b>"],
  secs=[("工作內容",["看AI往來的內容，修正偏掉的地方","需要人的時候，以人的身分應對","與店家建立關係"]),
        ("應徵資格",["在留資格沒有就勞限制者","能以日語進行業務溝通者"]),
        ("條件",["正職／常勤　1名","工作地點：名古屋市中區（榮）預定","薪資・社會保險・休假：確定後刊登於本頁"])],
  apply_h="應徵・洽詢",
  apply="按下方按鈕會開啟郵件。不需要履歷。<br>只要寫一句「為什麼感興趣」。",
  btn="以郵件應徵", mail="ヨヨイ 應徵"),

 "zh-hans": dict(title="招聘 — 寻找与AI一起工作的人｜ヨヨイ",
  desc="名古屋。AI会和双方对话。只有人才能做到的地方，由人去。寻找能为AI吹进人的气味的人。正职1名。",
  lead="我们在寻找与AI一起工作的人。",
  sub="AI会和双方对话。听客人想做什么，听店家卖什么，把两边连起来。<br>只有人才能做到的地方，由人去。",
  wanted_h="我们要找的是这样的人", wanted="能为AI吹进人的气味的人",
  wanted_body=["AI很准确。但不温暖。",
   "客人在不安什么。店家在困扰什么。——这些要由人来告诉它。",
   "<b>不懂技术也没关系。懂人，就是技术。</b>"],
  secs=[("工作内容",["看AI往来的内容，修正偏掉的地方","需要人的时候，以人的身份应对","与店家建立关系"]),
        ("应聘资格",["在留资格没有就劳限制者","能以日语进行业务沟通者"]),
        ("条件",["正职／常勤　1名","工作地点：名古屋市中区（荣）预定","薪资・社会保险・休假：确定后刊登于本页"])],
  apply_h="应聘・咨询",
  apply="按下方按钮会打开邮件。不需要简历。<br>只要写一句「为什么感兴趣」。",
  btn="以邮件应聘", mail="ヨヨイ 应聘"),

 "th": dict(title="ร่วมงาน — ตามหาคนที่จะทำงานร่วมกับ AI｜Yoyoi",
  desc="นาโกย่า AI คุยกับทั้งสองฝ่าย ตรงไหนที่ต้องใช้คนเท่านั้น คนจะไป ตามหาคนที่จะเติมกลิ่นอายของมนุษย์ให้ AI พนักงานประจำ 1 อัตรา",
  lead="เรากำลังตามหาคนที่จะทำงานร่วมกับ AI",
  sub="AI คุยกับทั้งสองฝ่าย ฟังว่าลูกค้าอยากทำอะไร ฟังว่าร้านขายอะไร แล้วเชื่อมสองฝั่งเข้าด้วยกัน<br>ตรงไหนที่ต้องใช้คนเท่านั้น คนจะไป",
  wanted_h="เรากำลังตามหาคนแบบนี้", wanted="คนที่จะเติมกลิ่นอายของมนุษย์ให้ AI",
  wanted_body=["AI แม่นยำ แต่ไม่อบอุ่น",
   "ลูกค้ากังวลเรื่องอะไร ร้านลำบากใจเรื่องอะไร — สิ่งเหล่านี้ต้องมีคนบอกมัน",
   "<b>ไม่เข้าใจเทคโนโลยีก็ไม่เป็นไร การเข้าใจคน คือเทคโนโลยี</b>"],
  secs=[("เนื้องาน",["อ่านสิ่งที่ AI สนทนาไป แล้วแก้ตรงที่คลาดเคลื่อน","เข้ามาดูแลด้วยตัวเองเมื่อจำเป็นต้องใช้คน","สร้างความสัมพันธ์กับร้านค้า"]),
        ("คุณสมบัติ",["ผู้ที่มีสถานะพำนักซึ่งไม่มีข้อจำกัดในการทำงาน","ผู้ที่สื่อสารการทำงานเป็นภาษาญี่ปุ่นได้"]),
        ("เงื่อนไข",["พนักงานประจำ／เต็มเวลา　1 อัตรา","สถานที่ทำงาน: เขตนากะ เมืองนาโกย่า (ซาคาเอะ) ตามแผน","เงินเดือน ประกันสังคม วันหยุด: จะประกาศในหน้านี้เมื่อกำหนดแล้ว"])],
  apply_h="สมัคร・สอบถาม",
  apply="กดปุ่มด้านล่างเพื่อเปิดอีเมล ไม่ต้องใช้เรซูเม่<br>เขียนแค่บรรทัดเดียวว่า “ทำไมถึงสนใจ”",
  btn="สมัครทางอีเมล", mail="Yoyoi - สมัครงาน"),
}

def aboutpage(lang):
    v=LANGS[lang]; a=ABOUT[lang]
    paras="".join("<p>%s</p>"%x for x in a["body"])
    bio="".join("<p>%s</p>"%x for x in a["bio"])
    _rl={"ja":"採用情報を見る →","ko":"채용 안내 보기 →","en":"See careers →","zh-hant":"查看徵才資訊 →","zh-hans":"查看招聘信息 →","th":"ดูข้อมูลร่วมงาน →"}
    rec='<p style="margin-top:2rem"><a class="cta" href="%s/%s/recruit/">%s</a></p>'%(SITE,v["dir"],html.escape(_rl[lang])) if lang in RECRUIT else ""
    body=f"""<h1>{html.escape(a['h'])}</h1>
<div class="prose">{paras}</div>
<div class="why-big"><b>{html.escape(a['ph'])}</b><span>{html.escape(a['ps'])}</span></div>
<h2>{html.escape(a['who'])}</h2>
<div class="prose">{bio}</div>
{rec}"""
    return shell(lang, a["title"], a["desc"], "ヨヨイ,Yoyoi,名古屋,about", "%s/%s/about/"%(SITE,v["dir"]), body, "about/", only=list(ABOUT.keys()))

def recruitpage(lang):
    v=LANGS[lang]; r=RECRUIT[lang]
    wb="".join("<p>%s</p>"%x for x in r["wanted_body"])
    secs="".join('<h2>%s</h2><ul class="dl">%s</ul>'%(html.escape(t),
        "".join("<li>%s</li>"%html.escape(x) for x in items)) for t,items in r["secs"])
    jd=" ".join(x.replace("<b>","").replace("</b>","") for x in r["wanted_body"])
    ld=('{"@context":"https://schema.org/","@type":"JobPosting",'
        '"title":' + json.dumps(r["lead"], ensure_ascii=False) + ','
        '"description":' + json.dumps("<p>"+jd+"</p>", ensure_ascii=False) + ','
        '"datePosted":"' + TODAY + '","employmentType":"FULL_TIME",'
        '"hiringOrganization":{"@type":"Organization","name":"ヨヨイ（Yoyoi）","sameAs":"' + SITE + '"},'
        '"jobLocation":{"@type":"Place","address":{"@type":"PostalAddress",'
        '"addressLocality":"名古屋市中区","addressRegion":"愛知県","addressCountry":"JP"}}}') if lang=="ja" else ""
    ldtag = '<script type="application/ld+json">%s</script>'%ld if ld else ""
    body=f"""<h1 class="lead">{html.escape(r['lead'])}</h1>
<p class="sub">{r['sub']}</p>
<div class="why-big"><b>{html.escape(r['wanted'])}</b><span>{html.escape(r['wanted_h'])}</span></div>
<div class="prose">{wb}</div>
{secs}
<div class="box">
<h2>{html.escape(r['apply_h'])}</h2>
<p class="note">{r['apply']}</p>
<div class="btns"><a class="p" href="mailto:{CONTACT}?subject={urllib.parse.quote(r['mail'])}">{html.escape(r['btn'])}</a></div>
</div>
{ldtag}"""
    return shell(lang, r["title"], r["desc"], "名古屋,求人,正社員,採用,ヨヨイ,Yoyoi,recruit",
                 "%s/%s/recruit/"%(SITE,v["dir"]), body, "recruit/", only=list(RECRUIT.keys()))

def chbox(lang):
    on = [(k,u) for k,u in CHANNELS.items() if u]
    if not on: return ""
    head = {"ja":"チャットでも受け付けています","en":"Or message us","ko":"대화로도 받습니다",
            "zh-hant":"也可以用通訊軟體","zh-hans":"也可以用通讯软件","th":"ทักแชทก็ได้"}[lang]
    btns = "".join('<a class="ch" href="%s" rel="noopener" target="_blank">%s</a>' % (u, CH_LABEL[k]) for k,u in on)
    return '<div class="chwrap"><span>%s</span>%s</div>' % (html.escape(head), btns)

def formbox(v, lang=None):
    return f"""<div class="box">
<h2>{v['form_h']}</h2>
<textarea id="q" placeholder="{html.escape(v['form_ph'])}"></textarea>
<div class="btns">
<button class="p" id="m" type="button">{v['btn_mail']}</button>
<button class="s" id="c" type="button" data-done="{v['copied']}">{v['btn_copy']}</button>
</div>
<p class="note">{v['note']}</p>
{chbox(lang) if lang else ""}
</div>"""

def shoplang(lang):
    return LANGS["ja"]["dir"] if lang in ("ja",) else (LANGS[lang]["dir"] if lang in SHOP else LANGS["en"]["dir"])

def home(lang):
    v=LANGS[lang]
    cats="".join('<li><a href="%s/%s/%s/"><b>%s</b><small>%s</small></a></li>'%(
        SITE,v["dir"],c["slug"],html.escape(c["t"][lang]),html.escape(c["d"][lang])) for c in CATS)
    areas="".join('<li><a href="%s/%s/area/%s/"><b>%s</b><small>%s</small></a></li>'%(
        SITE,v["dir"],a["slug"],html.escape(a["t"][lang]),html.escape(a["d"][lang])) for a in AREAS)
    guides="".join('<li><a href="%s/%s/guide/%s/"><b>%s</b><small>%s</small></a></li>'%(
        SITE,v["dir"],g["slug"],html.escape(g["t"][lang]),html.escape(g["d"][lang])) for g in GUIDES)
    steps="".join("<li><b>%s</b><span>%s</span></li>"%(html.escape(a),html.escape(b)) for a,b in v["steps"])
    w=WHY[lang]
    body=f"""{citybar(lang,"nagoya")}
<div class="why-hero"><b>{html.escape(w[0])}</b><span>{html.escape(w[1])}</span></div>
<h1>{v['tagline']}</h1>
<p class="sub">{v['sub']}</p>
<ul class="chips">{"".join("<li>%s</li>"%html.escape(p) for p in v['promise'])}</ul>
{formbox(v,lang)}
<h2 class="sec">{html.escape(v['steps'][0][0]) and ''}</h2>
<ol class="steps">{steps}</ol>
<h2 class="sec">{html.escape(v['why_h'])}</h2>
<ul class="why">{"".join("<li>%s</li>"%w for w in v['why'])}</ul>
<h2 class="sec">{html.escape(v['trust_h'])}</h2>
<ul class="why">{"".join("<li>%s</li>"%w for w in v['trust'])}</ul>
<h2 class="sec">{html.escape(v['pay_h'])}</h2>
<ul class="why">{"".join("<li>%s</li>"%w for w in v['pay'])}</ul>
<ul class="cats">{cats}</ul>
<ul class="cats">{areas}</ul>
<ul class="cats">{guides}</ul>
<ul class="cats"><li><a href="{SITE}/{shoplang(lang)}/shops/"><b>{html.escape(v['shop_cta'])}</b><small>{html.escape(v['shop_h'])}</small></a></li></ul>"""
    body=body.replace('<h2 class="sec"></h2>','')
    t = "ヨヨイ Yoyoi — %s" % (v["tagline"].replace("<br>"," ").strip())
    return shell(lang, t, v["sub"], v["kw"], "%s/%s/"%(SITE,v["dir"]), body, "")

def catpage(lang, c):
    v=LANGS[lang]
    body=f"""<h1>{html.escape(c['t'][lang])}</h1>
<p class="sub">{html.escape(c['d'][lang])}</p>
<ul class="chips">{"".join("<li>%s</li>"%html.escape(p) for p in v['promise'])}</ul>
{formbox(v,lang)}
<h2 class="sec">{html.escape(v['why_h'])}</h2>
<ul class="why">{"".join("<li>%s</li>"%w for w in v['why'])}</ul>
<a class="back" href="{SITE}/{v['dir']}/">← ヨヨイ</a>"""
    return shell(lang, "%s | ヨヨイ"%c["t"][lang], c["d"][lang], v["kw"], "%s/%s/%s/"%(SITE,v["dir"],c["slug"]), body, c["slug"]+"/")


SHOP = dict(
 ja=dict(title="名古屋のお店の方へ | ヨヨイ",
   h1="外国人のご予約を、<br>安心して受けられるように。",
   sub="ヨヨイ（Yoyoi）は、訪日のお客様に代わって日本語でご予約をお取りするサービスです。お店側のご登録・掲載料・システム導入は一切不要です。",
   lead_h="お店にとって何が変わるか",
   lead=["<b>条件は事前にすべて合意済みです。</b>人数・時間・予算・アレルギー・宗教上の制限まで確認してからお電話します。席についてから話が変わることがありません。",
         "<b>無連絡キャンセルを減らします。</b>お客様とは予約前にやり取りをしています。連絡先が取れる状態です。",
         "<b>問題のあったお客様は、二度お取り次ぎしません。</b>お店では「一度きりの外国人のお客様」でも、私たちには記録が残ります。お店が覚えられないことを、私たちが覚えます。",
         "<b>言語の負担がありません。</b>やり取りはすべて私たちが日本語で行います。"],
   ask_h="お願いしたいこと",
   ask=["お電話でご予約をお受けいただくこと。それだけです。",
        "ご登録・契約・掲載料はありません。断っていただいても構いません。"],
   pay_h="料金について",
   pay=["<b>価値があったと思われた額を、お店の方からお支払いいただけます。</b>お支払いがなくてもお取り次ぎは変わりません。",
        "<b>多くお支払いいただいても、優先的にご紹介することはありません。</b>お金で順番を売りません。売った時点で、このサービスを信頼していただく理由がなくなります。"],
   fair_h="私たちが守ること",
   fair=["お店を評価し、お客様も評価します。片方だけを守ることはしません。",
         "国籍・人種・信条でお客様を選別しません。判断するのは行いだけです。",
         "お客様の個人情報をお店にお渡しすることはありません。"],
   cta="ご質問やご相談は、こちらからお送りください。",
   ph="例：予約の受け方、対応できる時間帯、断りたい条件などがあればお書きください。"),
 en=dict(title="For shops in Nagoya | ヨヨイ",
   h1="Take foreign bookings<br>without the risk.",
   sub="Yoyoi books on behalf of visitors, in Japanese. No sign-up, no listing fee, no system to install.",
   lead_h="What changes for you",
   lead=["<b>Everything is agreed before we call.</b> Headcount, time, budget, allergies, religious restrictions — all confirmed first. Nothing changes at the table.",
         "<b>Fewer no-shows.</b> We have talked with the guest before booking, and we can reach them.",
         "<b>We do not send the same problem twice.</b> To you they are a one-time foreign guest. To us they are on record. We remember what you cannot.",
         "<b>No language burden.</b> Every exchange with us is in Japanese."],
   ask_h="What we ask",
   ask=["That you take the reservation by phone. That is all.",
        "No registration, no contract, no listing fee. You may decline any booking."],
   pay_h="Paying",
   pay=["<b>Pay what you think it was worth.</b> If you pay nothing, nothing changes on our side.",
        "<b>Paying more does not buy priority.</b> We do not sell the order. If we did, there would be no reason to trust us."],
   fair_h="What we keep",
   fair=["We check the shops, and we check the guests. We do not protect only one side.",
         "We never screen guests by nationality, race, or belief. Only by what they do.",
         "We never hand a guest's personal information to a shop."],
   cta="Questions? Send them here.",
   ph="e.g. how you prefer to take reservations, which hours work, anything you would rather decline."),
 ko=dict(title="나고야 가게 여러분께 | 요요이",
   h1="외국인 예약을,<br>안심하고 받으실 수 있도록.",
   sub="요요이(Yoyoi)는 방일 손님을 대신해 일본어로 예약을 잡아드리는 서비스입니다. 가게 쪽의 등록·게재료·시스템 도입은 일절 필요 없습니다.",
   lead_h="가게에 무엇이 달라지는가",
   lead=["<b>조건은 사전에 전부 합의돼 있습니다.</b> 인원·시간·예산·알레르기·종교상 제한까지 확인한 뒤에 전화드립니다. 자리에 앉고 나서 말이 바뀌는 일이 없습니다.",
         "<b>무연락 취소를 줄입니다.</b> 손님과는 예약 전에 대화를 나눕니다. 연락이 닿는 상태입니다.",
         "<b>문제가 있었던 손님은 두 번 연결하지 않습니다.</b> 가게에서는 「한 번뿐인 외국인 손님」이어도, 우리에게는 기록이 남습니다. 가게가 기억할 수 없는 것을 우리가 기억합니다.",
         "<b>언어 부담이 없습니다.</b> 주고받는 것은 전부 우리가 일본어로 합니다."],
   ask_h="부탁드리고 싶은 것",
   ask=["전화로 예약을 받아주시는 것. 그것뿐입니다.",
        "등록·계약·게재료는 없습니다. 거절하셔도 괜찮습니다."],
   pay_h="요금에 대하여",
   pay=["<b>가치가 있었다고 생각되는 금액을, 가게 쪽에서 지불해주시면 됩니다.</b> 지불이 없어도 연결은 달라지지 않습니다.",
        "<b>많이 지불하셔도 우선적으로 소개하지 않습니다.</b> 돈으로 순서를 팔지 않습니다. 파는 순간 이 서비스를 신뢰하실 이유가 없어집니다."],
   fair_h="우리가 지키는 것",
   fair=["가게를 평가하고, 손님도 평가합니다. 한쪽만 지키지 않습니다.",
         "국적·인종·신조로 손님을 선별하지 않습니다. 판단하는 것은 행동뿐입니다.",
         "손님의 개인정보를 가게에 넘기지 않습니다."],
   cta="질문이나 상담은 여기서 보내주세요.",
   ph="예: 예약 받는 방식, 가능한 시간대, 거절하고 싶은 조건 등이 있으면 적어주세요."),
 **{"zh-hant": dict(title="給名古屋店家 | ヨヨイ",
   h1="外國人的預約，<br>安心地接下來。",
   sub="ヨヨイ（Yoyoi）代替訪日客人以日語進行預約。店家不需登記、不收刊登費、不必導入任何系統。",
   lead_h="對店家而言，會有什麼改變",
   lead=["<b>條件在事前已全部談妥。</b>人數、時間、預算、過敏、宗教上的限制，都確認過才打電話。不會坐下之後話又變了。",
         "<b>減少不告而別的取消。</b>我們在預約前已與客人往來過，聯絡得上。",
         "<b>出過問題的客人，不會再介紹第二次。</b>對店家來說是「只來一次的外國客人」，對我們來說有紀錄。店家記不住的，我們替您記住。",
         "<b>沒有語言負擔。</b>所有往來都由我們以日語進行。"],
   ask_h="想拜託您的事",
   ask=["以電話接受預約。就只有這樣。",
        "沒有登記、沒有合約、沒有刊登費。您也可以拒絕。"],
   pay_h="關於費用",
   pay=["<b>覺得值多少，由店家您來支付。</b>不付款，我們的介紹也不會改變。",
        "<b>付得多也不會優先介紹。</b>我們不賣順序。一旦賣了，就沒有理由再信任這項服務。"],
   fair_h="我們會守住的事",
   fair=["我們評估店家，也評估客人。不會只保護單邊。",
         "不以國籍、種族、信仰篩選客人。我們只看行為。",
         "絕不把客人的個人資料交給店家。"],
   cta="有任何問題或想商量的，請從這裡寄給我們。",
   ph="例如：您偏好的預約方式、可以配合的時段、希望婉拒的條件等。"),
 "zh-hans": dict(title="给名古屋店家 | ヨヨイ",
   h1="外国人的预约，<br>安心地接下来。",
   sub="ヨヨイ（Yoyoi）代替访日客人以日语进行预约。店家不需登记、不收刊登费、不必导入任何系统。",
   lead_h="对店家而言，会有什么改变",
   lead=["<b>条件在事前已全部谈妥。</b>人数、时间、预算、过敏、宗教上的限制，都确认过才打电话。不会坐下之后话又变了。",
         "<b>减少不告而别的取消。</b>我们在预约前已与客人往来过，联络得上。",
         "<b>出过问题的客人，不会再介绍第二次。</b>对店家来说是「只来一次的外国客人」，对我们来说有记录。店家记不住的，我们替您记住。",
         "<b>没有语言负担。</b>所有往来都由我们以日语进行。"],
   ask_h="想拜托您的事",
   ask=["以电话接受预约。就只有这样。",
        "没有登记、没有合约、没有刊登费。您也可以拒绝。"],
   pay_h="关于费用",
   pay=["<b>觉得值多少，由店家您来支付。</b>不付款，我们的介绍也不会改变。",
        "<b>付得多也不会优先介绍。</b>我们不卖顺序。一旦卖了，就没有理由再信任这项服务。"],
   fair_h="我们会守住的事",
   fair=["我们评估店家，也评估客人。不会只保护单边。",
         "不以国籍、种族、信仰筛选客人。我们只看行为。",
         "绝不把客人的个人资料交给店家。"],
   cta="有任何问题或想商量的，请从这里寄给我们。",
   ph="例如：您偏好的预约方式、可以配合的时段、希望婉拒的条件等。"),
 "th": dict(title="ถึงร้านค้าในนาโกย่า | Yoyoi",
   h1="รับการจองจากชาวต่างชาติ<br>ได้อย่างสบายใจ",
   sub="Yoyoi จองแทนนักท่องเที่ยวเป็นภาษาญี่ปุ่น ร้านไม่ต้องลงทะเบียน ไม่มีค่าลงประกาศ ไม่ต้องติดตั้งระบบใดๆ",
   lead_h="อะไรจะเปลี่ยนไปสำหรับร้าน",
   lead=["<b>ตกลงเงื่อนไขครบก่อนโทร</b> จำนวนคน เวลา งบประมาณ ภูมิแพ้ ข้อจำกัดทางศาสนา ยืนยันหมดแล้วจึงโทรหาร้าน จะไม่มีการเปลี่ยนเรื่องหลังนั่งโต๊ะแล้ว",
         "<b>ลดการยกเลิกแบบไม่แจ้ง</b> เราคุยกับลูกค้าก่อนจอง และติดต่อกลับได้",
         "<b>ลูกค้าที่เคยมีปัญหา จะไม่ถูกส่งไปอีกเป็นครั้งที่สอง</b> สำหรับร้านคือ “ลูกค้าต่างชาติที่มาครั้งเดียว” แต่สำหรับเรามีบันทึกไว้ สิ่งที่ร้านจำไม่ได้ เราจำแทน",
         "<b>ไม่มีภาระเรื่องภาษา</b> การติดต่อทั้งหมด เราทำเป็นภาษาญี่ปุ่น"],
   ask_h="สิ่งที่อยากขอ",
   ask=["รับการจองทางโทรศัพท์ เท่านั้นเอง",
        "ไม่มีการลงทะเบียน ไม่มีสัญญา ไม่มีค่าลงประกาศ จะปฏิเสธก็ได้"],
   pay_h="เรื่องค่าบริการ",
   pay=["<b>คิดว่ามีค่าเท่าไร ทางร้านจ่ายเท่านั้น</b> ถ้าไม่จ่าย การส่งลูกค้าก็ไม่เปลี่ยนไป",
        "<b>จ่ายมากก็ไม่ได้ถูกแนะนำก่อน</b> เราไม่ขายลำดับ ถ้าขายเมื่อไร ก็ไม่เหลือเหตุผลให้เชื่อใจบริการนี้"],
   fair_h="สิ่งที่เรายึดถือ",
   fair=["เราประเมินร้าน และประเมินลูกค้าด้วย จะไม่ปกป้องเพียงฝ่ายเดียว",
         "เราไม่คัดกรองลูกค้าด้วยสัญชาติ เชื้อชาติ หรือความเชื่อ เราดูที่การกระทำเท่านั้น",
         "เราจะไม่ส่งข้อมูลส่วนบุคคลของลูกค้าให้ร้านเด็ดขาด"],
   cta="มีคำถามหรืออยากปรึกษา ส่งมาทางนี้ได้เลย",
   ph="เช่น วิธีรับจองที่สะดวก ช่วงเวลาที่รับได้ เงื่อนไขที่อยากปฏิเสธ")},
)

def shoppage(lang):
    v=LANGS[lang]; c=SHOP[lang]
    def ul(items): return "".join("<li>%s</li>"%i for i in items)
    body=f"""<h1>{c['h1']}</h1>
<p class="sub">{html.escape(c['sub'])}</p>
<h2 class="sec">{html.escape(c['lead_h'])}</h2>
<ul class="why">{ul(c['lead'])}</ul>
<h2 class="sec">{html.escape(c['ask_h'])}</h2>
<ul class="why">{ul(c['ask'])}</ul>
<h2 class="sec">{html.escape(c['pay_h'])}</h2>
<ul class="why">{ul(c['pay'])}</ul>
<h2 class="sec">{html.escape(c['fair_h'])}</h2>
<ul class="why">{ul(c['fair'])}</ul>
<div class="box">
<h2>{html.escape(c['cta'])}</h2>
<textarea id="q" placeholder="{html.escape(c['ph'])}"></textarea>
<div class="btns">
<button class="p" id="m" type="button">{v['btn_mail']}</button>
<button class="s" id="c" type="button" data-done="{v['copied']}">{v['btn_copy']}</button>
</div>
</div>
<a class="back" href="{SITE}/{v['dir']}/">← ヨヨイ</a>"""
    return shell(lang, c['title'], c['sub'], v['kw'], "%s/%s/shops/"%(SITE,v['dir']), body, "shops/", only=list(SHOP.keys()))


# ── 지역 페이지 ──────────────────────────────────────────
AREAS = [
 dict(slug="sakae", t=dict(en="Sakae & Yabacho", ja="栄・矢場町", ko="사카에·야바초",
      **{"zh-hant":"榮・矢場町","zh-hans":"荣・矢场町","th":"ซาคาเอะ・ยาบาโจ"}),
   d=dict(en="Nagoya's densest block for salons, izakaya and late dinner. Also where the smallest places answer the phone and nothing else.",
          ja="サロン・居酒屋・遅い夕食が最も密集する一帯。電話しか受けていない小さな店も一番多い場所です。",
          ko="살롱·이자카야·늦은 저녁이 가장 빽빽한 곳. 전화만 받는 작은 가게도 여기 제일 많습니다.",
          **{"zh-hant":"美容院、居酒屋、深夜晚餐最密集的一帶。只接電話的小店也最多。",
             "zh-hans":"美容院、居酒屋、深夜晚餐最密集的一带。只接电话的小店也最多。",
             "th":"ย่านที่ร้านเสริมสวย อิซากายะ และร้านอาหารดึกหนาแน่นที่สุด และมีร้านเล็กที่รับแต่โทรศัพท์มากที่สุด"})),
 dict(slug="nagoya-station", t=dict(en="Nagoya Station", ja="名古屋駅", ko="나고야역",
      **{"zh-hant":"名古屋車站","zh-hans":"名古屋车站","th":"สถานีนาโกยา"}),
   d=dict(en="First and last stop of most trips. Good for a meal with luggage, or a salon slot before the Shinkansen.",
          ja="多くの旅の最初と最後。荷物を持ったままの食事、新幹線前のサロン枠に向いています。",
          ko="여행의 처음과 마지막. 짐 들고 먹는 식사, 신칸센 전 살롱 예약에 좋습니다.",
          **{"zh-hant":"多數旅程的起點與終點。適合帶著行李用餐，或搭新幹線前的沙龍時段。",
             "zh-hans":"多数旅程的起点与终点。适合带着行李用餐，或搭新干线前的沙龙时段。",
             "th":"จุดเริ่มและจุดจบของทริปส่วนใหญ่ เหมาะกับมื้ออาหารพร้อมกระเป๋า หรือคิวร้านเสริมสวยก่อนขึ้นชินคันเซ็น"})),
 dict(slug="osu", t=dict(en="Osu", ja="大須", ko="오스",
      **{"zh-hant":"大須","zh-hans":"大须","th":"โอสุ"}),
   d=dict(en="Old shopping arcade, small independent shops, cheap and alive. Many owners run the place alone and take bookings by phone.",
          ja="古い商店街と個人店。安くて活気があります。店主が一人で回していて、予約は電話だけという店が多い場所です。",
          ko="오래된 상점가와 개인 가게들. 싸고 활기 있습니다. 사장님 혼자 운영하고 예약은 전화만 받는 곳이 많습니다.",
          **{"zh-hant":"老商店街與個人小店，便宜又有活力。很多是老闆一人經營，只用電話接受預約。",
             "zh-hans":"老商店街与个人小店，便宜又有活力。很多是老板一人经营，只用电话接受预约。",
             "th":"ย่านการค้าเก่าและร้านเล็กอิสระ ราคาถูกและคึกคัก หลายร้านเจ้าของดูแลคนเดียวและรับจองทางโทรศัพท์เท่านั้น"})),
 dict(slug="kanayama", t=dict(en="Kanayama", ja="金山", ko="가나야마",
      **{"zh-hant":"金山","zh-hans":"金山","th":"คานายามะ"}),
   d=dict(en="Transfer hub. Locals eat here rather than tourists, which is exactly why it is worth booking ahead.",
          ja="乗換の要所。観光客より地元の人が食べる場所です。だからこそ予約しておく価値があります。",
          ko="환승 요지. 관광객보다 현지 사람이 먹는 곳입니다. 그래서 미리 잡아둘 값이 있습니다.",
          **{"zh-hant":"轉乘要地。比起觀光客，這裡是在地人吃飯的地方，所以更值得先訂位。",
             "zh-hans":"转乘要地。比起观光客，这里是本地人吃饭的地方，所以更值得先订位。",
             "th":"จุดเปลี่ยนรถสำคัญ คนท้องถิ่นมากินมากกว่านักท่องเที่ยว จึงยิ่งควรจองล่วงหน้า"})),
 dict(slug="imaike", t=dict(en="Imaike", ja="今池", ko="이마이케",
      **{"zh-hant":"今池","zh-hans":"今池","th":"อิมาอิเกะ"}),
   d=dict(en="Night town with small counters and music bars. Almost nothing here is on an English booking site.",
          ja="小さなカウンターと音楽の店が並ぶ夜の街。英語の予約サイトにはほとんど載っていません。",
          ko="작은 카운터와 음악 가게가 있는 밤의 동네. 영어 예약 사이트에는 거의 없습니다.",
          **{"zh-hant":"小吧檯與音樂酒吧的夜之街。這裡幾乎沒有店家出現在英文訂位網站上。",
             "zh-hans":"小吧台与音乐酒吧的夜之街。这里几乎没有店家出现在英文订位网站上。",
             "th":"ย่านกลางคืนที่มีเคาน์เตอร์เล็กและบาร์ดนตรี แทบไม่มีร้านไหนอยู่บนเว็บจองภาษาอังกฤษ"})),
]

# ── 실용 가이드 ─────────────────────────────────────────
GUIDES = [
 dict(slug="allergies", t=dict(en="Telling a Japanese restaurant about allergies", ja="アレルギーの伝え方",
      ko="일본 음식점에 알레르기 알리는 법", **{"zh-hant":"如何告知日本餐廳過敏","zh-hans":"如何告知日本餐厅过敏","th":"วิธีแจ้งภูมิแพ้กับร้านอาหารญี่ปุ่น"}),
   d=dict(en="Say it when you book, not when you sit down. Small kitchens buy for the day.",
          ja="席に着いてからではなく、予約のときに伝えます。小さな厨房はその日の分だけ仕入れます。",
          ko="앉아서가 아니라 예약할 때 말합니다. 작은 주방은 그날 것만 사둡니다。",
          **{"zh-hant":"訂位時就要說，不是坐下才說。小廚房只採購當天的份量。",
             "zh-hans":"订位时就要说，不是坐下才说。小厨房只采购当天的份量。",
             "th":"บอกตอนจอง ไม่ใช่ตอนนั่งลง ครัวเล็กซื้อวัตถุดิบแค่พอวันนั้น"}),
   b=dict(en=["<b>Book-time, not table-time.</b> A small kitchen has already bought the fish for tonight. If you say it at the table, the honest answer is often \"we cannot serve you\".",
              "<b>Name the ingredient, not the diet.</b> \"No pork, including broth and lard\" travels better than \"halal\". \"No dashi made from fish\" travels better than \"vegetarian\" — dashi is in almost everything.",
              "<b>Say how serious it is.</b> Japanese kitchens treat a medical allergy and a preference very differently, and they will ask.",
              "<b>Some places will say no.</b> That is not rudeness. A counter with one chef cannot guarantee separation. We will find one that can."],
       ja=["<b>席ではなく予約のときに。</b>小さな厨房は今夜の分をもう仕入れています。席で言われると「お出しできません」が正直な答えになります。",
           "<b>食べられない「食材」で伝えます。</b>「ハラル」より「豚肉不可。だしやラードも含む」。「ベジタリアン」より「魚のだし不可」。だしはほとんどの料理に入っています。",
           "<b>重さを伝えます。</b>医学的なアレルギーと好みでは扱いがまったく違います。必ず聞かれます。",
           "<b>断られることもあります。</b>失礼ではありません。一人で回すカウンターでは分離を保証できないからです。できるお店を探します。"],
       ko=["<b>앉아서가 아니라 예약할 때.</b> 작은 주방은 오늘 저녁 분을 이미 사뒀습니다. 자리에서 말하면 「못 드립니다」가 정직한 답이 됩니다.",
           "<b>못 먹는 「재료」로 말합니다.</b> 「할랄」보다 「돼지고기 불가, 육수·라드 포함」. 「채식」보다 「생선 다시 불가」 — 다시는 거의 모든 요리에 들어갑니다.",
           "<b>얼마나 심한지 말합니다.</b> 일본 주방은 의학적 알레르기와 취향을 완전히 다르게 다룹니다. 반드시 물어봅니다.",
           "<b>거절당할 수도 있습니다.</b> 무례한 게 아닙니다. 혼자 하는 카운터는 분리를 보장할 수 없으니까요. 되는 가게를 찾아 드립니다."],
       **{"zh-hant":["<b>訂位時說，不是入座才說。</b>小廚房今晚的食材已經買好了。坐下才說，得到的誠實答案往往是「無法為您準備」。",
                     "<b>用「食材」表達，不要用「飲食法」。</b>「不吃豬肉，含高湯與豬油」比「清真」好用。「不能有魚高湯」比「素食」好用——高湯幾乎在每道菜裡。",
                     "<b>說明嚴重程度。</b>日本廚房對醫療過敏與個人偏好處理完全不同，而且一定會問。",
                     "<b>有些店會拒絕。</b>那不是無禮。一位師傅的吧檯無法保證分離作業。我們幫您找做得到的店。"],
          "zh-hans":["<b>订位时说，不是入座才说。</b>小厨房今晚的食材已经买好了。坐下才说，得到的诚实答案往往是「无法为您准备」。",
                     "<b>用「食材」表达，不要用「饮食法」。</b>「不吃猪肉，含高汤与猪油」比「清真」好用。「不能有鱼高汤」比「素食」好用——高汤几乎在每道菜里。",
                     "<b>说明严重程度。</b>日本厨房对医疗过敏与个人偏好处理完全不同，而且一定会问。",
                     "<b>有些店会拒绝。</b>那不是无礼。一位师傅的吧台无法保证分离作业。我们帮您找做得到的店。"],
          "th":["<b>บอกตอนจอง ไม่ใช่ตอนนั่ง</b> ครัวเล็กซื้อวัตถุดิบของคืนนี้ไว้แล้ว ถ้าบอกตอนนั่งโต๊ะ คำตอบที่ตรงไปตรงมามักคือ ‘เสิร์ฟให้ไม่ได้’",
                "<b>บอกเป็น ‘วัตถุดิบ’ ไม่ใช่ ‘ประเภทอาหาร’</b> ‘ไม่กินหมู รวมน้ำซุปและน้ำมันหมู’ สื่อสารได้ดีกว่า ‘ฮาลาล’ และ ‘ไม่ใส่ดาชิปลา’ ดีกว่า ‘มังสวิรัติ’ เพราะดาชิอยู่ในเกือบทุกจาน",
                "<b>บอกว่ารุนแรงแค่ไหน</b> ครัวญี่ปุ่นแยกชัดระหว่างภูมิแพ้ทางการแพทย์กับความชอบส่วนตัว และเขาจะถาม",
                "<b>บางร้านจะปฏิเสธ</b> ไม่ใช่ความหยาบคาย เคาน์เตอร์ที่มีเชฟคนเดียวรับประกันการแยกวัตถุดิบไม่ได้ เราจะหาร้านที่ทำได้ให้"]})),
 dict(slug="no-show", t=dict(en="If your plans change", ja="予定が変わったら", ko="계획이 바뀌면",
      **{"zh-hant":"如果計畫有變","zh-hans":"如果计划有变","th":"ถ้าแผนเปลี่ยน"}),
   d=dict(en="Tell us. One message saves a small restaurant a real loss — and keeps the door open for the next traveller.",
          ja="ひと言だけください。小さなお店の実損が消え、次の旅行者のために扉が開いたままになります。",
          ko="한 마디만 주세요. 작은 가게의 실제 손실이 사라지고, 다음 여행자를 위해 문이 열린 채로 남습니다.",
          **{"zh-hant":"跟我們說一聲。一則訊息就能免除小店的實際損失，也讓門為下一位旅客留著。",
             "zh-hans":"跟我们说一声。一条消息就能免除小店的实际损失，也让门为下一位旅客留着。",
             "th":"บอกเราสักคำ ข้อความเดียวช่วยร้านเล็กไม่ให้ขาดทุนจริง และทำให้ประตูยังเปิดไว้ให้นักเดินทางคนต่อไป"}),
   b=dict(en=["<b>A no-show is not an empty chair. It is food already bought and staff already scheduled.</b> Many places in Nagoya seat eight people. One missing table is a whole evening.",
              "<b>This is why shops stop taking foreign bookings.</b> Not language — risk. Every time it happens, a door closes for everyone who comes after you.",
              "<b>Just message us.</b> Any time, any language, no explanation needed. We will call and cancel properly in Japanese.",
              "<b>We keep a record.</b> If someone does not show and does not tell us, we stop booking for them. That is how we can promise shops that our guests are safe to accept."],
       ja=["<b>無連絡キャンセルは空席ではありません。</b>仕入れ済みの食材と、組んでしまった人の時間です。名古屋には八席のお店がたくさんあります。一卓は一晩に相当します。",
           "<b>だからお店は外国人の予約をやめます。</b>言葉ではなくリスクです。一度起きるたび、あとから来る人のために扉が一つ閉まります。",
           "<b>ひと言くだされば十分です。</b>いつでも、どの言語でも、理由も要りません。こちらから日本語できちんとお断りします。",
           "<b>記録は残します。</b>連絡なくお越しにならなかった方には、以後お取り次ぎしません。だからこそお店に「うちのお客様は大丈夫です」と言えます。"],
       ko=["<b>노쇼는 빈자리가 아닙니다.</b> 이미 사둔 재료이고, 이미 짜둔 사람의 시간입니다. 나고야에는 여덟 자리짜리 가게가 많습니다. 한 테이블이 하룻밤입니다.",
           "<b>그래서 가게가 외국인 예약을 그만둡니다.</b> 언어가 아니라 위험 때문입니다. 한 번 일어날 때마다 뒤에 오는 사람들을 위한 문이 하나 닫힙니다.",
           "<b>한 마디만 주시면 됩니다.</b> 언제든, 어떤 말로든, 이유도 필요 없습니다. 저희가 일본어로 제대로 취소해 드립니다.",
           "<b>기록은 남깁니다.</b> 연락 없이 안 오신 분은 이후 중개하지 않습니다. 그래야 가게에 「우리 손님은 괜찮습니다」라고 말할 수 있습니다."],
       **{"zh-hant":["<b>訂了不到不是一個空位。</b>那是已經買好的食材與已經排好的人力。名古屋很多店只有八個座位，少一桌就是一整晚。",
                     "<b>所以店家才不再接外國人訂位。</b>不是語言，是風險。每發生一次，就為後面來的人關上一道門。",
                     "<b>跟我們說一聲就好。</b>任何時間、任何語言，不需要理由。我們會用日語替您好好取消。",
                     "<b>我們會留紀錄。</b>沒到又沒通知的客人，之後我們不再代訂。這樣我們才能對店家說「我們的客人可以放心接」。"],
          "zh-hans":["<b>订了不到不是一个空位。</b>那是已经买好的食材与已经排好的人力。名古屋很多店只有八个座位，少一桌就是一整晚。",
                     "<b>所以店家才不再接外国人订位。</b>不是语言，是风险。每发生一次，就为后面来的人关上一道门。",
                     "<b>跟我们说一声就好。</b>任何时间、任何语言，不需要理由。我们会用日语替您好好取消。",
                     "<b>我们会留记录。</b>没到又没通知的客人，之后我们不再代订。这样我们才能对店家说「我们的客人可以放心接」。"],
          "th":["<b>การจองแล้วไม่มา ไม่ใช่แค่เก้าอี้ว่าง</b> แต่คือวัตถุดิบที่ซื้อไว้แล้วและคนที่จัดเวรไว้แล้ว ร้านในนาโกยาหลายแห่งมีแค่แปดที่นั่ง หายไปหนึ่งโต๊ะคือทั้งคืน",
                "<b>นี่คือเหตุผลที่ร้านเลิกรับจองจากชาวต่างชาติ</b> ไม่ใช่เรื่องภาษา แต่เป็นความเสี่ยง ทุกครั้งที่เกิดขึ้น ประตูจะปิดลงหนึ่งบานสำหรับคนที่มาทีหลัง",
                "<b>บอกเราสักคำก็พอ</b> เวลาไหนก็ได้ ภาษาอะไรก็ได้ ไม่ต้องอธิบาย เราจะโทรยกเลิกเป็นภาษาญี่ปุ่นให้เรียบร้อย",
                "<b>เราเก็บบันทึกไว้</b> ผู้ที่ไม่มาและไม่แจ้ง เราจะไม่จองให้อีก นั่นคือเหตุผลที่เราบอกร้านได้ว่าลูกค้าของเราปลอดภัยที่จะรับ"]})),
 dict(slug="counter-seats", t=dict(en="Counter seats and why they are hard to book", ja="カウンター席が取りにくい理由",
      ko="카운터석이 잡기 어려운 이유", **{"zh-hant":"為什麼吧檯座位難訂","zh-hans":"为什么吧台座位难订","th":"ทำไมที่นั่งเคาน์เตอร์จองยาก"}),
   d=dict(en="Eight seats, one chef, one phone. That is the whole system — and it is why these are the best meals in the city.",
          ja="八席、料理人一人、電話一台。それが仕組みのすべてで、だからこそ街で一番いい食事になります。",
          ko="여덟 자리, 요리사 한 명, 전화 한 대. 그게 시스템 전부이고, 그래서 도시에서 제일 좋은 식사가 됩니다.",
          **{"zh-hant":"八個座位、一位師傅、一支電話。整套系統就是這樣——也正因如此，那是城裡最好的一餐。",
             "zh-hans":"八个座位、一位师傅、一支电话。整套系统就是这样——也正因如此，那是城里最好的一餐。",
             "th":"แปดที่นั่ง เชฟหนึ่งคน โทรศัพท์หนึ่งเครื่อง นั่นคือทั้งระบบ และนั่นคือเหตุผลที่มันคืออาหารมื้อที่ดีที่สุดในเมือง"}),
   b=dict(en=["<b>There is no system to put online.</b> The chef is cooking. The phone rings between orders. Adding a booking site would mean hiring someone.",
              "<b>Ask early.</b> Two to four weeks ahead for the good ones. Same-day is possible but it is luck.",
              "<b>Be exact about the number.</b> One extra person is 12% of the room. Changing it later is not a small change.",
              "<b>Arrive on time, not early.</b> There is usually nowhere to wait."],
       ja=["<b>オンラインにする仕組みがそもそもありません。</b>料理人は調理しています。電話は注文の合間に鳴ります。予約サイトを入れるとは、人を雇うということです。",
           "<b>早めに。</b>良いお店は二〜四週間前。当日も不可能ではありませんが運です。",
           "<b>人数は正確に。</b>一人増えると席の12%です。あとからの変更は小さな変更ではありません。",
           "<b>早すぎず、時間ちょうどに。</b>待つ場所がないことがほとんどです。"],
       ko=["<b>온라인으로 올릴 시스템이 애초에 없습니다.</b> 요리사는 요리 중입니다. 전화는 주문 사이에 울립니다. 예약 사이트를 넣는다는 건 사람을 뽑는다는 뜻입니다.",
           "<b>일찍 물어보세요.</b> 좋은 곳은 2~4주 전. 당일도 가능하지만 운입니다.",
           "<b>인원은 정확히.</b> 한 명이 늘면 좌석의 12%입니다. 나중에 바꾸는 건 작은 변경이 아닙니다.",
           "<b>일찍 말고 정시에.</b> 대개 기다릴 곳이 없습니다."],
       **{"zh-hant":["<b>根本沒有可以上線的系統。</b>師傅在做菜，電話在點單的空檔響。要導入訂位網站，等於要多請一個人。",
                     "<b>早點問。</b>好店要提前兩到四週。當天也不是不可能，但看運氣。",
                     "<b>人數要準確。</b>多一個人就是全場的12%。事後更動不是小事。",
                     "<b>準時，不要太早。</b>多數店沒有可以等的地方。"],
          "zh-hans":["<b>根本没有可以上线的系统。</b>师傅在做菜，电话在点单的空档响。要导入订位网站，等于要多请一个人。",
                     "<b>早点问。</b>好店要提前两到四周。当天也不是不可能，但看运气。",
                     "<b>人数要准确。</b>多一个人就是全场的12%。事后更动不是小事。",
                     "<b>准时，不要太早。</b>多数店没有可以等的地方。"],
          "th":["<b>ไม่มีระบบให้ขึ้นออนไลน์ตั้งแต่แรก</b> เชฟกำลังทำอาหาร โทรศัพท์ดังในช่วงว่างระหว่างออเดอร์ การเพิ่มเว็บจองหมายถึงต้องจ้างคนเพิ่ม",
                "<b>ถามแต่เนิ่นๆ</b> ร้านดีควรล่วงหน้าสองถึงสี่สัปดาห์ วันต่อวันก็เป็นไปได้แต่ต้องอาศัยดวง",
                "<b>จำนวนคนต้องแม่น</b> เพิ่มหนึ่งคนคือ 12% ของทั้งร้าน การเปลี่ยนทีหลังไม่ใช่เรื่องเล็ก",
                "<b>มาตรงเวลา อย่ามาเร็วเกิน</b> ส่วนใหญ่ไม่มีที่ให้รอ"]})),
 dict(slug="salon-photos", t=dict(en="Bring a photo to the salon", ja="サロンには写真を", ko="살롱에는 사진을",
      **{"zh-hant":"到沙龍請帶照片","zh-hans":"到沙龙请带照片","th":"พกรูปไปร้านเสริมสวย"}),
   d=dict(en="Words for hair and nails do not survive translation. A picture does.",
          ja="髪とネイルの言葉は翻訳を越えられません。写真は越えます。",
          ko="머리와 네일의 말은 번역을 넘지 못합니다. 사진은 넘습니다.",
          **{"zh-hant":"頭髮和美甲的用語翻譯不過去，照片可以。",
             "zh-hans":"头发和美甲的用语翻译不过去，照片可以。",
             "th":"คำศัพท์เรื่องผมและเล็บข้ามภาษาไม่ได้ แต่รูปข้ามได้"}),
   b=dict(en=["<b>Send us the photo when you book.</b> We ask the salon whether they can do it, and how long it takes, before you go.",
              "<b>Length matters more than you think.</b> Gel, extensions and colour corrections can take three hours. We confirm the time so you do not lose an afternoon.",
              "<b>Ask about your hair type.</b> Not every salon works with every texture. Better to know before the chair than in it.",
              "<b>Prices are usually per-item.</b> Cut, wash, colour, treatment are often separate. We ask for the total in advance."],
       ja=["<b>予約のときに写真をお送りください。</b>できるかどうか、どれくらいかかるかを、行く前にサロンに確認します。",
           "<b>所要時間は思ったより長いです。</b>ジェル、エクステ、カラーの補正は三時間かかることもあります。午後を失わないよう先に確認します。",
           "<b>髪質のことも聞いておきます。</b>どのサロンもすべての髪質を扱えるわけではありません。座る前に分かるほうがいいです。",
           "<b>料金は多くが単品計算です。</b>カット・シャンプー・カラー・トリートメントが別々のことがよくあります。総額を先に聞いておきます。"],
       ko=["<b>예약할 때 사진을 보내주세요.</b> 가능한지, 얼마나 걸리는지 가시기 전에 살롱에 확인합니다.",
           "<b>시간이 생각보다 깁니다.</b> 젤·연장·컬러 보정은 세 시간이 걸리기도 합니다. 오후를 잃지 않도록 미리 확인합니다.",
           "<b>모발 타입도 물어봅니다.</b> 모든 살롱이 모든 모질을 다루지는 않습니다. 앉기 전에 아는 편이 낫습니다.",
           "<b>요금은 대개 항목별입니다.</b> 컷·샴푸·컬러·트리트먼트가 따로인 경우가 많습니다. 총액을 미리 물어봅니다."],
       **{"zh-hant":["<b>訂位時把照片傳給我們。</b>我們會在您出發前，先問沙龍做不做得到、要多久。",
                     "<b>時間比想像中長。</b>光療、接髮、染髮矯色可能要三小時。我們先確認，免得您損失一個下午。",
                     "<b>髮質也會先問。</b>不是每家沙龍都處理得了所有髮質。坐下前知道比較好。",
                     "<b>價格多半是分項計算。</b>剪、洗、染、護常常分開算。我們會先問總價。"],
          "zh-hans":["<b>订位时把照片发给我们。</b>我们会在您出发前，先问沙龙做不做得到、要多久。",
                     "<b>时间比想象中长。</b>光疗、接发、染发矫色可能要三小时。我们先确认，免得您损失一个下午。",
                     "<b>发质也会先问。</b>不是每家沙龙都处理得了所有发质。坐下前知道比较好。",
                     "<b>价格多半是分项计算。</b>剪、洗、染、护常常分开算。我们会先问总价。"],
          "th":["<b>ส่งรูปมาตอนจอง</b> เราจะถามร้านให้ก่อนคุณไป ว่าทำได้ไหมและใช้เวลานานแค่ไหน",
                "<b>เวลานานกว่าที่คิด</b> เจล ต่อผม และแก้สีอาจใช้เวลาสามชั่วโมง เรายืนยันเวลาให้ก่อน คุณจะได้ไม่เสียทั้งบ่าย",
                "<b>เราถามเรื่องสภาพเส้นผมด้วย</b> ไม่ใช่ทุกร้านจะทำได้ทุกสภาพผม รู้ก่อนนั่งดีกว่ารู้ตอนนั่งแล้ว",
                "<b>ราคามักคิดแยกรายการ</b> ตัด สระ ทำสี ทรีตเมนต์ มักแยกกัน เราถามยอดรวมให้ล่วงหน้า"]})),
]

def listpage(lang, item, kind):
    v=LANGS[lang]
    body_items = item.get("b", {}).get(lang)
    inner = ""
    if body_items:
        inner = '<h2 class="sec">%s</h2><ul class="why">%s</ul>' % (
            html.escape(v["why_h"]), "".join("<li>%s</li>"%x for x in body_items))
    else:
        inner = '<h2 class="sec">%s</h2><ul class="why">%s</ul>' % (
            html.escape(v["why_h"]), "".join("<li>%s</li>"%w for w in v["why"]))
    body=f"""<h1>{html.escape(item['t'][lang])}</h1>
<p class="sub">{html.escape(item['d'][lang])}</p>
<ul class="chips">{"".join("<li>%s</li>"%html.escape(p) for p in v['promise'])}</ul>
{formbox(v,lang)}
{inner}
<a class="back" href="{SITE}/{v['dir']}/">← ヨヨイ</a>"""
    sub = "%s/%s/" % (kind, item["slug"])
    return shell(lang, "%s | ヨヨイ"%item["t"][lang], item["d"][lang], v["kw"],
                 "%s/%s/%s"%(SITE,v["dir"],sub), body, sub)

CITYNAMES = dict(ja=("名古屋","京都","大阪"), en=("Nagoya","Kyoto","Osaka"), ko=("나고야","교토","오사카"),
  **{"zh-hant":("名古屋","京都","大阪"), "zh-hans":("名古屋","京都","大阪"), "th":("นาโกยา","เกียวโต","โอซาก้า")})
CITYPATH = (("nagoya",""), ("kyoto","kyoto/"), ("osaka","osaka/"))

def citybar(lang, here):
    d=LANGS[lang]["dir"]; names=CITYNAMES[lang]
    out=[]
    for (key,p),nm in zip(CITYPATH,names):
        cur=' aria-current="page"' if key==here else ''
        out.append('<a href="%s/%s/%s"%s>%s</a>' % (SITE,d,p,cur,html.escape(nm)))
    return '<nav class="langs" style="margin:.2rem 0 1rem">%s</nav>' % "".join(out)

if os.path.isdir(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)
urls=[]
for lang,v in LANGS.items():
    d=os.path.join(OUT,v["dir"]); os.makedirs(d,exist_ok=True)
    open(os.path.join(d,"index.html"),"w",encoding="utf-8").write(home(lang))
    urls.append("%s/%s/"%(SITE,v["dir"]))
    for c in CATS:
        dd=os.path.join(d,c["slug"]); os.makedirs(dd,exist_ok=True)
        open(os.path.join(dd,"index.html"),"w",encoding="utf-8").write(catpage(lang,c))
        urls.append("%s/%s/%s/"%(SITE,v["dir"],c["slug"]))
    for a in AREAS:
        ad=os.path.join(d,"area",a["slug"]); os.makedirs(ad,exist_ok=True)
        open(os.path.join(ad,"index.html"),"w",encoding="utf-8").write(listpage(lang,a,"area"))
        urls.append("%s/%s/area/%s/"%(SITE,v["dir"],a["slug"]))
    for g in GUIDES:
        gd=os.path.join(d,"guide",g["slug"]); os.makedirs(gd,exist_ok=True)
        open(os.path.join(gd,"index.html"),"w",encoding="utf-8").write(listpage(lang,g,"guide"))
        urls.append("%s/%s/guide/%s/"%(SITE,v["dir"],g["slug"]))
    if lang in ABOUT:
        bd=os.path.join(d,"about"); os.makedirs(bd,exist_ok=True)
        open(os.path.join(bd,"index.html"),"w",encoding="utf-8").write(aboutpage(lang))
        urls.append("%s/%s/about/"%(SITE,v["dir"]))
    if lang in RECRUIT:
        rd=os.path.join(d,"recruit"); os.makedirs(rd,exist_ok=True)
        open(os.path.join(rd,"index.html"),"w",encoding="utf-8").write(recruitpage(lang))
        urls.append("%s/%s/recruit/"%(SITE,v["dir"]))
    if lang in SHOP:
        sd=os.path.join(d,"shops"); os.makedirs(sd,exist_ok=True)
        open(os.path.join(sd,"index.html"),"w",encoding="utf-8").write(shoppage(lang))
        urls.append("%s/%s/shops/"%(SITE,v["dir"]))

# 루트: 언어 자동 감지 후 이동
open(os.path.join(OUT,"index.html"),"w",encoding="utf-8").write(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ヨヨイ Yoyoi — Nagoya bookings, in your language</title>
<meta name="description" content="Just write what you want. We book restaurants, hair salons and nail salons in Nagoya — even the ones that only take phone reservations in Japanese.">
<link rel="canonical" href="{SITE}/en/">
{alts("")}
<style>{CSS}</style>
<script>
(function(){{var l=(navigator.language||'en').toLowerCase(),m={{'ja':'ja','ko':'ko','th':'th'}},d='en';
if(l.indexOf('zh')===0){{d=(l.indexOf('cn')>-1||l.indexOf('hans')>-1||l.indexOf('sg')>-1)?'zh-hans':'zh-hant';}}
else{{for(var k in m){{if(l.indexOf(k)===0)d=m[k];}}}}
location.replace('{SITE}/'+d+'/');}})();
</script></head>
<body><main class="wrap"><h1>ヨヨイ<span style="color:var(--acc)">.</span></h1>
<p style="color:var(--mut);margin:-.6rem 0 1rem">Yoyoi</p>
<p class="sub">Nagoya bookings, in your language.</p>
<ul class="cats">{"".join('<li><a href="%s/%s/"><b>%s</b></a></li>'%(SITE,v["dir"],html.escape(v["name"])) for v in LANGS.values())}</ul>
</main></body></html>""")

# ══════════════════════════════════════════════════════════
#  京都 — 도시 2호 (2026-09-18)
#  나고야 카피를 도시 이름만 갈아서 쓰고, 나고야 전용 업종
#  (ひつまぶし)은 京料理・おばんざい로 바꿔 끼운다.
#  URL: /{lang}/kyoto/ · /{lang}/kyoto/{업종}/ · /{lang}/kyoto/area/{지역}/ · /{lang}/kyoto/shops/
#  나고야 페이지는 건드리지 않는다.
# ══════════════════════════════════════════════════════════

CITY_SWAP = {
 "ja":[("名古屋めし","京料理"),("名古屋","京都"),("栄","河原町"),("大須","祇園"),("矢場町","四条")],
 "en":[("Nagoya","Kyoto"),("Sakae","Kawaramachi"),("Osu","Gion")],
 "ko":[("나고야","교토"),("사카에","가와라마치"),("오스","기온")],
 "zh-hant":[("名古屋","京都"),("榮","河原町"),("大須","祇園")],
 "zh-hans":[("名古屋","京都"),("荣","河原町"),("大须","祇园")],
 "th":[("นาโกย่า","เกียวโต"),("นาโกยา","เกียวโต"),("ซาคาเอะ","คาวารามาจิ"),("โอสุ","กิอง")],
}

def ky(x, lang):
    if isinstance(x,str):
        for a,b in CITY_SWAP.get(lang,[]): x=x.replace(a,b)
        return x
    if isinstance(x,list): return [ky(i,lang) for i in x]
    if isinstance(x,tuple): return tuple(ky(i,lang) for i in x)
    if isinstance(x,dict): return {k:ky(vv,lang) for k,vv in x.items()}
    return x

KEEP = ("dir","hreflang","name")
KY_LANGS = {l:{k:(v if k in KEEP else ky(v,l)) for k,v in LANGS[l].items()} for l in LANGS}

def kyitem(it):
    o={}
    for k,v in it.items():
        o[k] = v if k=="slug" else ({l:ky(v[l],l) for l in v} if isinstance(v,dict) else v)
    return o

KY_CATS = [kyitem(c) for c in CATS if c["slug"]!="hitsumabushi"] + [
 dict(slug="kyoryori",
   t=dict(en="Kyo-ryori & obanzai reservations", ja="京料理・おばんざいの予約", ko="교토 요리·오반자이 예약",
      **{"zh-hant":"京料理與家常菜訂位","zh-hans":"京料理与家常菜订位","th":"จองร้านเกียวโตเรียวริและโอบันไซ"}),
   d=dict(en="Counter seats, very few of them, and most take reservations only by phone — in Japanese.",
      ja="カウンター中心で席数が少なく、電話でしか予約を受けていない店が多い分野です。",
      ko="카운터 중심이라 자리가 적고, 전화로만 예약을 받는 가게가 많은 분야입니다.",
      **{"zh-hant":"以吧檯為主、座位很少，多半只接受電話預約。",
         "zh-hans":"以吧台为主、座位很少，多半只接受电话预约。",
         "th":"ที่นั่งเคาน์เตอร์ มีไม่กี่ที่ และส่วนใหญ่รับจองทางโทรศัพท์เท่านั้น"})),
]

KY_AREAS = [
 dict(slug="gion", t=dict(en="Gion & Higashiyama", ja="祇園・東山", ko="기온·히가시야마",
      **{"zh-hant":"祇園・東山","zh-hans":"祇园・东山","th":"กิอง・ฮิงาชิยามะ"}),
   d=dict(en="The blocks where the smallest places answer the phone and nothing else. Many do not take first-time visitors without an introduction.",
          ja="電話しか受けていない小さな店が最も多い一帯です。紹介がないと初めての方を受けない店もあります。",
          ko="전화만 받는 작은 가게가 가장 많은 곳입니다. 소개 없이는 첫 손님을 받지 않는 가게도 있습니다.",
          **{"zh-hant":"只接電話的小店最多的一帶。也有不接受初次客人的店。",
             "zh-hans":"只接电话的小店最多的一带。也有不接受初次客人的店。",
             "th":"ย่านที่ร้านเล็กรับแต่โทรศัพท์มากที่สุด บางร้านไม่รับลูกค้าครั้งแรกหากไม่มีคนแนะนำ"})),
 dict(slug="kawaramachi", t=dict(en="Kawaramachi & Shijo", ja="河原町・四条", ko="가와라마치·시조",
      **{"zh-hant":"河原町・四條","zh-hans":"河原町・四条","th":"คาวารามาจิ・ชิโจ"}),
   d=dict(en="Salons, izakaya and late dinner, all within walking distance. The densest block in the city.",
          ja="サロン・居酒屋・遅い夕食が歩いて回れる範囲に集まる、市内で最も密集した一帯です。",
          ko="살롱·이자카야·늦은 저녁이 걸어서 닿는 거리에 몰려 있는, 시내에서 가장 빽빽한 곳입니다.",
          **{"zh-hant":"美容院、居酒屋、深夜晚餐都在步行範圍內，市內最密集的一帶。",
             "zh-hans":"美容院、居酒屋、深夜晚餐都在步行范围内，市内最密集的一带。",
             "th":"ร้านเสริมสวย อิซากายะ และมื้อดึก อยู่ในระยะเดินถึง เป็นย่านที่หนาแน่นที่สุดในเมือง"})),
 dict(slug="kyoto-station", t=dict(en="Kyoto Station", ja="京都駅", ko="교토역",
      **{"zh-hant":"京都車站","zh-hans":"京都车站","th":"สถานีเกียวโต"}),
   d=dict(en="First and last stop of most trips. Good for a meal with luggage, or a salon slot before the Shinkansen.",
          ja="多くの旅の最初と最後。荷物を持ったままの食事、新幹線前のサロン枠に向いています。",
          ko="여행의 처음과 마지막. 짐을 든 채 하는 식사, 신칸센 전 살롱 예약에 좋습니다.",
          **{"zh-hant":"多數旅程的起點與終點。適合帶著行李用餐，或搭新幹線前的沙龍時段。",
             "zh-hans":"多数旅程的起点与终点。适合带着行李用餐，或搭新干线前的沙龙时段。",
             "th":"จุดเริ่มและจุดจบของทริปส่วนใหญ่ เหมาะกับมื้ออาหารพร้อมกระเป๋า หรือคิวร้านเสริมสวยก่อนขึ้นชินคันเซ็น"})),
 dict(slug="arashiyama", t=dict(en="Arashiyama", ja="嵐山", ko="아라시야마",
      **{"zh-hant":"嵐山","zh-hans":"岚山","th":"อาราชิยามะ"}),
   d=dict(en="Lunch fills up early and last orders come early too. Booking ahead decides whether the day works.",
          ja="昼が早く埋まり、ラストオーダーも早い場所です。予約を先に取れるかで一日が決まります。",
          ko="점심이 일찍 차고 라스트오더도 이릅니다. 예약을 먼저 잡느냐로 하루가 갈립니다.",
          **{"zh-hant":"午餐很早就滿，最後點餐也早。能不能先訂到，決定這一天。",
             "zh-hans":"午餐很早就满，最后点餐也早。能不能先订到，决定这一天。",
             "th":"มื้อกลางวันเต็มเร็ว และปิดรับออร์เดอร์เร็ว จองล่วงหน้าได้หรือไม่ ตัดสินทั้งวัน"})),
]

def sw(x, lang, swap):
    if isinstance(x,str):
        for p,q in swap.get(lang,[]): x=x.replace(p,q)
        return x
    if isinstance(x,list): return [sw(i,lang,swap) for i in x]
    if isinstance(x,tuple): return tuple(sw(i,lang,swap) for i in x)
    if isinstance(x,dict): return {k:sw(vv,lang,swap) for k,vv in x.items()}
    return x

def switem(it, swap):
    return {k:(v if k=="slug" else ({l:sw(v[l],l,swap) for l in v} if isinstance(v,dict) else v)) for k,v in it.items()}

# ══════════════════════════════════════════════════════════
#  大阪 — 도시 3호 (2026-09-18). 교토와 같은 틀.
# ══════════════════════════════════════════════════════════
OS_SWAP = {
 "ja":[("名古屋めし","大阪の味"),("名古屋","大阪"),("栄","難波"),("大須","心斎橋"),("矢場町","本町")],
 "en":[("Nagoya","Osaka"),("Sakae","Namba"),("Osu","Shinsaibashi")],
 "ko":[("나고야","오사카"),("사카에","난바"),("오스","신사이바시")],
 "zh-hant":[("名古屋","大阪"),("榮","難波"),("大須","心齋橋")],
 "zh-hans":[("名古屋","大阪"),("荣","难波"),("大须","心斋桥")],
 "th":[("นาโกย่า","โอซาก้า"),("นาโกยา","โอซาก้า"),("ซาคาเอะ","นัมบะ"),("โอสุ","ชินไซบาชิ")],
}
OS_CATS = [switem(c,OS_SWAP) for c in CATS if c["slug"]!="hitsumabushi"] + [
 dict(slug="okonomiyaki",
   t=dict(en="Okonomiyaki & kushikatsu reservations", ja="お好み焼き・串カツの予約", ko="오코노미야키·쿠시카츠 예약",
      **{"zh-hant":"大阪燒與炸串訂位","zh-hans":"大阪烧与炸串订位","th":"จองร้านโอโคโนมิยากิและคุชิคัตสึ"}),
   d=dict(en="The famous ones have lines out the door. The good local ones take a few bookings — in Japanese.",
      ja="有名店は行列。地元の良い店は、少ない予約枠を日本語で受けています。",
      ko="유명한 곳은 줄이 깁니다. 동네 맛집은 적은 예약을 일본어로만 받습니다.",
      **{"zh-hant":"名店大排長龍。好的在地小店只以日語接受少量預約。",
         "zh-hans":"名店大排长龙。好的在地小店只以日语接受少量预约。",
         "th":"ร้านดังต่อคิวยาว ร้านท้องถิ่นดีๆ รับจองไม่กี่ที่ และเป็นภาษาญี่ปุ่นเท่านั้น"})),
]
OS_AREAS = [
 dict(slug="namba", t=dict(en="Namba & Shinsaibashi", ja="難波・心斎橋", ko="난바·신사이바시",
      **{"zh-hant":"難波・心齋橋","zh-hans":"难波・心斋桥","th":"นัมบะ・ชินไซบาชิ"}),
   d=dict(en="Where most visitors stay and shop. Salons and late dinners everywhere, and the busiest places fill first.",
          ja="多くの旅行者が泊まり、買い物をする一帯。サロンも遅い夕食も多く、人気店から埋まります。",
          ko="여행자 대부분이 묵고 쇼핑하는 곳. 살롱도 늦은 저녁도 많고, 인기 있는 곳부터 찹니다.",
          **{"zh-hant":"多數旅客住宿、購物的一帶。沙龍和深夜晚餐很多，熱門店先滿。",
             "zh-hans":"多数旅客住宿、购物的一带。沙龙和深夜晚餐很多，热门店先满。",
             "th":"ย่านที่นักท่องเที่ยวส่วนใหญ่พักและช้อปปิ้ง ร้านเสริมสวยและมื้อดึกเยอะ ร้านดังเต็มก่อน"})),
 dict(slug="umeda", t=dict(en="Umeda & Kitashinchi", ja="梅田・北新地", ko="우메다·키타신치",
      **{"zh-hant":"梅田・北新地","zh-hans":"梅田・北新地","th":"อุเมดะ・คิตะชินจิ"}),
   d=dict(en="The north side. Kitashinchi's small counters take few guests and mostly by introduction or phone.",
          ja="キタ。北新地の小さなカウンターは席が少なく、紹介か電話での予約が中心です。",
          ko="북쪽 번화가. 키타신치의 작은 카운터는 자리가 적고, 소개나 전화 예약이 중심입니다.",
          **{"zh-hant":"北區。北新地的小吧檯座位少，多半靠介紹或電話預約。",
             "zh-hans":"北区。北新地的小吧台座位少，多半靠介绍或电话预约。",
             "th":"ฝั่งเหนือ เคาน์เตอร์เล็กในคิตะชินจิมีที่นั่งน้อย ส่วนใหญ่ต้องมีคนแนะนำหรือจองทางโทรศัพท์"})),
 dict(slug="tenma", t=dict(en="Tenma & Minamimorimachi", ja="天満・南森町", ko="텐마·미나미모리마치",
      **{"zh-hant":"天滿・南森町","zh-hans":"天满・南森町","th":"เทนมะ・มินามิโมริมาจิ"}),
   d=dict(en="Japan's longest shopping street and a dense block of small izakaya. Very local, very Japanese-only.",
          ja="日本一長い商店街と、小さな居酒屋が密集する一帯。地元色が強く、日本語だけの店がほとんどです。",
          ko="일본에서 가장 긴 상점가와 작은 이자카야가 빽빽한 곳. 동네 색이 강하고 거의 일본어만 됩니다.",
          **{"zh-hant":"日本最長的商店街，小居酒屋密集。在地色彩濃，幾乎只通日語。",
             "zh-hans":"日本最长的商店街，小居酒屋密集。在地色彩浓，几乎只通日语。",
             "th":"ถนนช้อปปิ้งที่ยาวที่สุดในญี่ปุ่น และอิซากายะเล็กๆ หนาแน่น บรรยากาศท้องถิ่น ส่วนใหญ่ใช้ภาษาญี่ปุ่นเท่านั้น"})),
 dict(slug="honmachi", t=dict(en="Honmachi & Kitahama", ja="本町・北浜", ko="혼마치·키타하마",
      **{"zh-hant":"本町・北濱","zh-hans":"本町・北滨","th":"ฮมมาจิ・คิตะฮามะ"}),
   d=dict(en="Between the two centers. Quieter, business hotels, and good salons that locals book ahead.",
          ja="キタとミナミの間。落ち着いた街で、ビジネスホテルと、地元の人が先に予約する良いサロンがあります。",
          ko="북쪽과 남쪽 번화가 사이. 조용하고 비즈니스호텔이 많으며, 현지인이 미리 예약하는 좋은 살롱이 있습니다.",
          **{"zh-hant":"南北兩大鬧區之間。較安靜，商務旅館多，也有在地人提前預約的好沙龍。",
             "zh-hans":"南北两大闹区之间。较安静，商务酒店多，也有在地人提前预约的好沙龙。",
             "th":"ระหว่างสองย่านใหญ่ เงียบกว่า มีโรงแรมธุรกิจ และร้านเสริมสวยดีๆ ที่คนท้องถิ่นจองล่วงหน้า"})),
]

def mkcity(key, swap, cats, areas, recsw):
    return dict(key=key, cats=cats, areas=areas, recsw=recsw,
                L={l:{k:(v if k in KEEP else sw(v,l,swap)) for k,v in LANGS[l].items()} for l in LANGS})

CITIES = [
  mkcity("kyoto", CITY_SWAP, KY_CATS, KY_AREAS, {}),
  mkcity("osaka", OS_SWAP, OS_CATS, OS_AREAS, {"ja":[("京都","大阪")],"ko":[("교토","오사카")]}),
]

def c_home(lang, C):
    v=C["L"][lang]; d=LANGS[lang]["dir"]; k=C["key"]
    cats="".join('<li><a href="%s/%s/%s/%s/"><b>%s</b><small>%s</small></a></li>'%(
        SITE,d,k,c["slug"],html.escape(c["t"][lang]),html.escape(c["d"][lang])) for c in C["cats"])
    areas="".join('<li><a href="%s/%s/%s/area/%s/"><b>%s</b><small>%s</small></a></li>'%(
        SITE,d,k,a["slug"],html.escape(a["t"][lang]),html.escape(a["d"][lang])) for a in C["areas"])
    steps="".join("<li><b>%s</b><span>%s</span></li>"%(html.escape(a),html.escape(b)) for a,b in v["steps"])
    w=WHY[lang]
    rec=""
    if lang in KYREC:
        rt = "お電話をかけてくださる方を探しています" if lang=="ja" else "전화를 걸어주실 분을 찾습니다"
        rs = sw("京都・在宅・スマートフォンだけで" if lang=="ja" else "교토·재택·스마트폰만으로", lang, C["recsw"])
        rec='<li><a href="%s/%s/%s/recruit/"><b>%s</b><small>%s</small></a></li>'%(SITE,d,k,rt,rs)
    body=f"""{citybar(lang,k)}
<div class="why-hero"><b>{html.escape(w[0])}</b><span>{html.escape(w[1])}</span></div>
<h1>{v['tagline']}</h1>
<p class="sub">{html.escape(v['sub'])}</p>
<ul class="chips">{"".join("<li>%s</li>"%html.escape(p) for p in v['promise'])}</ul>
{formbox(v,lang)}
<ol class="steps">{steps}</ol>
<h2 class="sec">{html.escape(v['why_h'])}</h2>
<ul class="why">{"".join("<li>%s</li>"%x for x in v['why'])}</ul>
<h2 class="sec">{html.escape(v['trust_h'])}</h2>
<ul class="why">{"".join("<li>%s</li>"%x for x in v['trust'])}</ul>
<h2 class="sec">{html.escape(v['pay_h'])}</h2>
<ul class="why">{"".join("<li>%s</li>"%x for x in v['pay'])}</ul>
<ul class="cats">{cats}</ul>
<ul class="cats">{areas}</ul>
<ul class="cats"><li><a href="{SITE}/{d}/{k}/shops/"><b>{html.escape(v['shop_cta'])}</b><small>{html.escape(v['shop_h'])}</small></a></li>
{rec}</ul>"""
    t = "ヨヨイ Yoyoi — %s" % (v["tagline"].replace("<br>"," ").strip())
    return shell(lang, t, v["sub"], v["kw"], "%s/%s/%s/"%(SITE,d,k), body, k+"/", foot=v["foot"])

def c_list(lang, C, it, sub):
    v=C["L"][lang]; d=LANGS[lang]["dir"]; k=C["key"]
    body=f"""{citybar(lang,k)}
<h1>{html.escape(it['t'][lang])}</h1>
<p class="sub">{html.escape(it['d'][lang])}</p>
<ul class="chips">{"".join("<li>%s</li>"%html.escape(p) for p in v['promise'])}</ul>
{formbox(v,lang)}
<h2 class="sec">{html.escape(v['why_h'])}</h2>
<ul class="why">{"".join("<li>%s</li>"%x for x in v['why'])}</ul>
<a class="back" href="{SITE}/{d}/{k}/">← ヨヨイ</a>"""
    return shell(lang, "%s | ヨヨイ"%it["t"][lang], it["d"][lang], v["kw"],
                 "%s/%s/%s/%s"%(SITE,d,k,sub), body, "%s/%s"%(k,sub), foot=v["foot"])

def c_shop(lang, C):
    v=C["L"][lang]; d=LANGS[lang]["dir"]; k=C["key"]
    c={kk:(vv if kk in KEEP else sw(vv,lang,{})) for kk,vv in SHOP[lang].items()}
    # SHOP 원문은 나고야 기준이므로 그 도시 이름으로 바꾼다
    c=sw(SHOP[lang], lang, {l:[(CITYNAMES[l][0],CITYNAMES[l][[p[0] for p in CITYPATH].index(k)])] + ([("นาโกย่า",CITYNAMES[l][[p[0] for p in CITYPATH].index(k)])] if l=="th" else []) for l in LANGS})
    def ul(items): return "".join("<li>%s</li>"%i for i in items)
    body=f"""{citybar(lang,k)}
<h1>{c['h1']}</h1>
<p class="sub">{c['sub']}</p>
<h2 class="sec">{html.escape(c['lead_h'])}</h2>
<ul class="why">{ul(c['lead'])}</ul>
<h2 class="sec">{html.escape(c['ask_h'])}</h2>
<ul class="why">{ul(c['ask'])}</ul>
<h2 class="sec">{html.escape(c['pay_h'])}</h2>
<ul class="why">{ul(c['pay'])}</ul>
<h2 class="sec">{html.escape(c['fair_h'])}</h2>
<ul class="why">{ul(c['fair'])}</ul>
<div class="box"><h2>{html.escape(c['cta'])}</h2>
<textarea id="q" placeholder="{html.escape(c['ph'])}"></textarea>
<div class="btns"><button class="p" id="m" type="button">{v['btn_mail']}</button>
<button class="s" id="c" type="button" data-done="{v['copied']}">{v['btn_copy']}</button></div>
<p class="note">{v['note']}</p></div>
<a class="back" href="{SITE}/{d}/{k}/">← ヨヨイ</a>"""
    return shell(lang, c["title"], c["sub"].replace("<br>"," "), v["kw"],
                 "%s/%s/%s/shops/"%(SITE,d,k), body, k+"/shops/", only=list(SHOP.keys()), foot=v["foot"])

# ── 京都: お電話をかけてくださる方の募集 (어르신 모집) ──────────────
KYREC = {
 "ja": dict(
  title="お電話をかけてくださる方を探しています（京都） | ヨヨイ",
  desc="京都のお店に日本語でお電話していただくお仕事です。ご自宅から、スマートフォンだけで。読む文はこちらで用意します。",
  h1="お電話を、<br>かけていただけませんか。",
  sub="京都のお店に、日本語でご予約のお電話をしていただくお仕事です。ご自宅から、スマートフォンだけでできます。",
  secs=[("お願いしたいこと",
         ["画面に<b>そのまま読む文</b>が出ます。お店にお電話して、読んでいただくだけです。",
          "お店のお返事を、画面の<b>三つのボタン</b>（取れた・だめ・あとで）から選んでいただきます。",
          "1日に<b>数件</b>です。夕方前が中心になります。"]),
        ("こんな方に",
         ["日本語でお電話ができる方。それだけです。",
          "パソコンは要りません。<b>スマートフォンが使えれば大丈夫</b>です。",
          "外国語は<b>一切必要ありません</b>。お客様とのやり取りはこちらでいたします。"]),
        ("条件",
         ["ご自宅から（在宅）。週3日ほど、1日1〜2時間。",
          "お電話1件ごとのお支払いです。金額は決まり次第、このページに掲載します。",
          "年齢は問いません。長くお勤めいただける方を探しています。"]),
        ("なぜ人にお願いするのか",
         ["お店との最初のやり取りは、<b>人の声でなければ通らない</b>と考えています。",
          "AIが調べて文を用意し、<b>人が話す</b>。その分担でやっています。"])],
  cta="ご興味があれば、こちらからお送りください。",
  ph="例：お名前、お住まいの地域、お電話できる時間帯。"),
 "ko": dict(
  title="전화를 걸어주실 분을 찾습니다 (교토) | 요요이",
  desc="교토 가게에 일본어로 전화해 예약을 잡는 일입니다. 집에서, 스마트폰만으로. 읽을 문장은 이쪽에서 준비합니다.",
  h1="전화를,<br>걸어주시지 않겠습니까.",
  sub="교토 가게에 일본어로 예약 전화를 넣는 일입니다. 집에서 스마트폰만으로 됩니다.",
  secs=[("부탁드리는 것",
         ["화면에 <b>그대로 읽을 문장</b>이 뜹니다. 가게에 전화해서 읽어주시면 됩니다.",
          "가게 대답을 화면의 <b>버튼 세 개</b>(됐음·안 됨·나중에)에서 고르시면 됩니다.",
          "하루 <b>몇 건</b>입니다. 저녁 전이 중심입니다."]),
        ("이런 분께",
         ["일본어로 전화할 수 있는 분. 그것뿐입니다.",
          "컴퓨터는 필요 없습니다. <b>스마트폰만 쓰실 수 있으면</b> 됩니다.",
          "외국어는 <b>전혀 필요 없습니다</b>. 손님과의 대화는 이쪽에서 합니다."]),
        ("조건",
         ["집에서(재택). 주 3일 정도, 하루 1~2시간.",
          "전화 한 건마다 지급합니다. 금액은 정해지는 대로 이 페이지에 올립니다.",
          "나이는 묻지 않습니다. 오래 함께하실 분을 찾습니다."]),
        ("왜 사람에게 부탁하는가",
         ["가게와의 첫 대화는 <b>사람 목소리가 아니면 통하지 않는다</b>고 봅니다.",
          "AI가 알아보고 문장을 준비하고, <b>사람이 말한다</b>. 그 분담으로 합니다."])],
  cta="관심 있으시면 여기서 보내주세요.",
  ph="예: 성함, 사시는 지역, 전화 가능한 시간대."),
}

def c_recruit(lang, C):
    v=C["L"][lang]; d=LANGS[lang]["dir"]; k=C["key"]
    r=sw(KYREC[lang], lang, C["recsw"])
    secs="".join('<h2 class="sec">%s</h2><ul class="why">%s</ul>'%(
        html.escape(t), "".join("<li>%s</li>"%x for x in items)) for t,items in r["secs"])
    body=f"""{citybar(lang,k)}
<h1>{r['h1']}</h1>
<p class="sub">{html.escape(r['sub'])}</p>
{secs}
<div class="box"><h2>{html.escape(r['cta'])}</h2>
<textarea id="q" placeholder="{html.escape(r['ph'])}"></textarea>
<div class="btns"><button class="p" id="m" type="button">{v['btn_mail']}</button>
<button class="s" id="c" type="button" data-done="{v['copied']}">{v['btn_copy']}</button></div>
<p class="note">{v['note']}</p></div>
<a class="back" href="{SITE}/{d}/{k}/">← ヨヨイ</a>"""
    return shell(lang, r["title"], r["desc"], v["kw"], "%s/%s/%s/recruit/"%(SITE,d,k),
                 body, k+"/recruit/", only=list(KYREC.keys()), foot=v["foot"])

def wr(path, html_):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path,"w",encoding="utf-8").write(html_)

for C in CITIES:
    k=C["key"]
    for lang,v in LANGS.items():
        base=os.path.join(OUT,v["dir"],k); u="%s/%s/%s/"%(SITE,v["dir"],k)
        wr(os.path.join(base,"index.html"), c_home(lang,C)); urls.append(u)
        for c in C["cats"]:
            wr(os.path.join(base,c["slug"],"index.html"), c_list(lang,C,c,c["slug"]+"/")); urls.append(u+c["slug"]+"/")
        for a in C["areas"]:
            wr(os.path.join(base,"area",a["slug"],"index.html"), c_list(lang,C,a,"area/%s/"%a["slug"])); urls.append(u+"area/%s/"%a["slug"])
        if lang in SHOP:
            wr(os.path.join(base,"shops","index.html"), c_shop(lang,C)); urls.append(u+"shops/")
        if lang in KYREC:
            wr(os.path.join(base,"recruit","index.html"), c_recruit(lang,C)); urls.append(u+"recruit/")

open(os.path.join(OUT,"sitemap.xml"),"w",encoding="utf-8").write(
 '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
 + "".join("<url><loc>%s</loc></url>\n"%u for u in urls) + "</urlset>\n")
open(os.path.join(OUT,"robots.txt"),"w",encoding="utf-8").write("User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n"%SITE)
open(os.path.join(OUT,".nojekyll"),"w").write("")
open(os.path.join(OUT,"CNAME"),"w").write("yoyoi.jp\n")
print("생성 완료: %d 페이지 (언어 %d × 업종 %d + 홈)" % (len(urls)+1, len(LANGS), len(CATS)))
