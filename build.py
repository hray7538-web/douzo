#!/usr/bin/env python3
"""Douzo Nagoya — 정적 사이트 생성기.
언어 × 업종 조합으로 SEO 페이지를 찍어낸다. 의존성 없음.
  python3 build.py
"""
import os, json, shutil, html

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
SITE = "https://hray7538-web.github.io/douzo"
CONTACT = "hray7538@gmail.com"   # ← 접수받을 주소. 이 한 줄만 바꾸면 됩니다.

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
   foot="Douzo — Nagoya, Japan",
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
   foot="Douzo — 名古屋",
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
   foot="Douzo — 나고야",
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
   foot="Douzo — 名古屋",
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
   foot="Douzo — 名古屋",
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
   foot="Douzo — นาโกยา",
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

CSS = """*{box-sizing:border-box}
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
  location.href='mailto:%s?subject='+encodeURIComponent('Douzo — booking request')+'&body='+body();});
if(c)c.addEventListener('click',function(){
  var d=c.getAttribute('data-done')||'Copied';
  navigator.clipboard.writeText(t.value||'').then(function(){var o=c.textContent;c.textContent=d;setTimeout(function(){c.textContent=o},1600)});});
})();""" % CONTACT

def langbar(cur, sub=""):
    out=[]
    for k,v in LANGS.items():
        href = "%s/%s/%s" % (SITE, v["dir"], sub)
        a = ' aria-current="page"' if k==cur else ''
        out.append('<a href="%s"%s>%s</a>' % (href, a, html.escape(v["name"])))
    return '<nav class="langs">%s</nav>' % "".join(out)

def alts(sub=""):
    r=['<link rel="alternate" hreflang="%s" href="%s/%s/%s">' % (v["hreflang"],SITE,v["dir"],sub) for v in LANGS.values()]
    r.append('<link rel="alternate" hreflang="x-default" href="%s/en/%s">' % (SITE,sub))
    return "\n".join(r)

def shell(lang, title, desc, kw, canon, body, sub=""):
    v=LANGS[lang]
    return f"""<!doctype html>
<html lang="{v['hreflang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="keywords" content="{html.escape(kw)}">
<link rel="canonical" href="{canon}">
{alts(sub)}
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canon}">
<style>{CSS}</style>
</head>
<body>
<header><div class="wrap"><div class="hrow">
<a class="logo" href="{SITE}/{v['dir']}/">Douzo<span>.</span></a>
{langbar(lang, sub)}
</div></div></header>
<main class="wrap">
{body}
</main>
<footer><div class="wrap">{html.escape(v['foot'])} · <a href="{SITE}/en/">English</a></div></footer>
<script>{JS}</script>
</body>
</html>
"""

def formbox(v):
    return f"""<div class="box">
<h2>{v['form_h']}</h2>
<textarea id="q" placeholder="{html.escape(v['form_ph'])}"></textarea>
<div class="btns">
<button class="p" id="m" type="button">{v['btn_mail']}</button>
<button class="s" id="c" type="button" data-done="{v['copied']}">{v['btn_copy']}</button>
</div>
<p class="note">{v['note']}</p>
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
    body=f"""<h1>{v['tagline']}</h1>
<p class="sub">{v['sub']}</p>
<ul class="chips">{"".join("<li>%s</li>"%html.escape(p) for p in v['promise'])}</ul>
{formbox(v)}
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
    t = "Douzo — %s" % (v["tagline"].replace("<br>"," ").strip())
    return shell(lang, t, v["sub"], v["kw"], "%s/%s/"%(SITE,v["dir"]), body, "")

def catpage(lang, c):
    v=LANGS[lang]
    body=f"""<h1>{html.escape(c['t'][lang])}</h1>
<p class="sub">{html.escape(c['d'][lang])}</p>
<ul class="chips">{"".join("<li>%s</li>"%html.escape(p) for p in v['promise'])}</ul>
{formbox(v)}
<h2 class="sec">{html.escape(v['why_h'])}</h2>
<ul class="why">{"".join("<li>%s</li>"%w for w in v['why'])}</ul>
<a class="back" href="{SITE}/{v['dir']}/">← Douzo</a>"""
    return shell(lang, "%s | Douzo"%c["t"][lang], c["d"][lang], v["kw"], "%s/%s/%s/"%(SITE,v["dir"],c["slug"]), body, c["slug"]+"/")


SHOP = dict(
 ja=dict(title="名古屋のお店の方へ | Douzo",
   h1="外国人のご予約を、<br>安心して受けられるように。",
   sub="Douzo は、訪日のお客様に代わって日本語でご予約をお取りするサービスです。お店側のご登録・掲載料・システム導入は一切不要です。",
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
 en=dict(title="For shops in Nagoya | Douzo",
   h1="Take foreign bookings<br>without the risk.",
   sub="Douzo books on behalf of visitors, in Japanese. No sign-up, no listing fee, no system to install.",
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
<a class="back" href="{SITE}/{v['dir']}/">← Douzo</a>"""
    return shell(lang, c['title'], c['sub'], v['kw'], "%s/%s/shops/"%(SITE,v['dir']), body, "shops/")


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
{formbox(v)}
{inner}
<a class="back" href="{SITE}/{v['dir']}/">← Douzo</a>"""
    sub = "%s/%s/" % (kind, item["slug"])
    return shell(lang, "%s | Douzo"%item["t"][lang], item["d"][lang], v["kw"],
                 "%s/%s/%s"%(SITE,v["dir"],sub), body, sub)

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
    if lang in SHOP:
        sd=os.path.join(d,"shops"); os.makedirs(sd,exist_ok=True)
        open(os.path.join(sd,"index.html"),"w",encoding="utf-8").write(shoppage(lang))
        urls.append("%s/%s/shops/"%(SITE,v["dir"]))

# 루트: 언어 자동 감지 후 이동
open(os.path.join(OUT,"index.html"),"w",encoding="utf-8").write(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Douzo — Nagoya bookings, in your language</title>
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
<body><main class="wrap"><h1>Douzo<span style="color:var(--acc)">.</span></h1>
<p class="sub">Nagoya bookings, in your language.</p>
<ul class="cats">{"".join('<li><a href="%s/%s/"><b>%s</b></a></li>'%(SITE,v["dir"],html.escape(v["name"])) for v in LANGS.values())}</ul>
</main></body></html>""")

open(os.path.join(OUT,"sitemap.xml"),"w",encoding="utf-8").write(
 '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
 + "".join("<url><loc>%s</loc></url>\n"%u for u in urls) + "</urlset>\n")
open(os.path.join(OUT,"robots.txt"),"w",encoding="utf-8").write("User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n"%SITE)
open(os.path.join(OUT,".nojekyll"),"w").write("")
print("생성 완료: %d 페이지 (언어 %d × 업종 %d + 홈)" % (len(urls)+1, len(LANGS), len(CATS)))
