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
