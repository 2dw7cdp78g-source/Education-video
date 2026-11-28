"""Builds episode.json for Episode 03 (kept as code so the long script stays readable)."""
import json
from pathlib import Path

HERE = Path(__file__).parent
C = json.loads((HERE / "images" / "credits.json").read_text())


def bg(k, dim=.55):
    c = C[k]
    return {"src": f"images/{k}.jpg", "credit": c["short"] + " (Wikimedia Commons)", "credit_full": c["full"], "dim": dim}


def L(en, my, say=None):
    d = {"en": en, "my": my}
    if say:
        d["say"] = say
    return d


scenes = [
    # 0 cold open
    {"type": "shot", "src": "images/shot_grab.jpg", "kicker": "2022 · Myanmar", "heading": "\"Click to grab an order\"",
     "caption": "A real screenshot from a task-scam app", "scroll": 8, "brand": False,
     "lines": [
         L("Click a button. Grab an order. Earn a commission.", "ခလုတ်တစ်ချက်နှိပ်။ အော်ဒါယူ။ ကော်မရှင်ရ။"),
         L("In 2022, apps like this spread across Myanmar's Facebook groups, promising easy money from home.",
           "၂၀၂၂ ခုနှစ်တွင် ဤကဲ့သို့ အက်ပ်များသည် အိမ်မှနေ၍ ငွေလွယ်လွယ်ရှာနိုင်မည်ဟု ကတိပေးကာ မြန်မာ Facebook အုပ်စုများတွင် ပျံ့နှံ့ခဲ့သည်။"),
         L("Thousands of people deposited their savings. Most of them never got it back.",
           "လူထောင်ပေါင်းများစွာ ၎င်းတို့၏ စုငွေများကို ထည့်ခဲ့ကြသည်။ အများစုမှာ ပြန်မရခဲ့ကြပါ။"),
     ]},
    # 1 title
    {"type": "title", "kicker": "Myanmar Explained · Investigation", "title": "Myanmar's Scam Economy",
     "subtitle": "Fake jobs, scam compounds, rigged gambling, and the armed groups that protect them",
     "byline": "Maung Yel Hkawng · Myanmar Community Researcher", "brand": False, "bg": bg("16", .6),
     "lines": [
         L("This is the story of Myanmar's scam economy: how it traps ordinary people, who runs it, and who protects it.",
           "ဤသည်မှာ မြန်မာ့လိမ်လည်မှုစီးပွားရေး၏ ဇာတ်လမ်းဖြစ်သည်။ ၎င်းက သာမန်ပြည်သူများကို မည်သို့ ထောင်ချောက်ဆင်သနည်း၊ မည်သူက လည်ပတ်သနည်း၊ မည်သူက ကာကွယ်ပေးသနည်း။"),
         L("It starts with a true story from 2022.", "၂၀၂၂ ခုနှစ်မှ ဖြစ်ရပ်မှန်တစ်ခုဖြင့် စတင်ပါမည်။"),
     ]},
    # 2 chapter
    {"type": "chapter", "number": 1, "title": "The Joom trap", "bg": bg("13", .6), "art": {"name": "pyramid", "mode": "top"},
     "lines": [L("Part one: the Joom trap.", "အပိုင်း ၁ - Joom ထောင်ချောက်။")]},
    # 3 groups screenshot
    {"type": "shot", "src": "images/shot_groups.jpg", "kicker": "Facebook, 2022", "heading": "It spread through Facebook groups",
     "caption": "Groups promising \"earn money from home\" gathered thousands of members", "scroll": 0,
     "lines": [
         L("In 2022, a website calling itself Joom spread quickly through Myanmar's online communities.",
           "၂၀၂၂ ခုနှစ်တွင် Joom ဟု အမည်ခံထားသော ဝဘ်ဆိုက်တစ်ခု မြန်မာ့အွန်လိုင်းအသိုင်းအဝိုင်းများတွင် လျင်မြန်စွာ ပျံ့နှံ့ခဲ့သည်။"),
         L("Facebook groups with names like \"earn money at home\" gathered thousands of members.",
           "\"အိမ်မှာနေရင်း ငွေရှာမယ်\" ကဲ့သို့ အမည်ရှိသော Facebook အုပ်စုများတွင် အဖွဲ့ဝင် ထောင်နှင့်ချီ စုဝေးခဲ့ကြသည်။"),
         L("But the real Joom is a legitimate online shop based in Europe. The scammers simply copied its name.",
           "သို့သော် တကယ့် Joom သည် ဥရောပအခြေစိုက် တရားဝင် အွန်လိုင်းဈေးဆိုင်ဖြစ်သည်။ လိမ်လည်သူများက ၎င်း၏အမည်ကိုသာ ခိုးယူအသုံးပြုခဲ့ခြင်း ဖြစ်သည်။"),
     ]},
    # 4 orders screenshot
    {"type": "shot", "src": "images/shot_orders.jpg", "kicker": "How it worked", "heading": "\"Boost product ratings\"",
     "caption": "Users clicked on products. Nothing was ever bought or sold.", "scroll": 30,
     "lines": [
         L("The promise was simple: click on products to \"boost their ratings\", and earn a daily commission.",
           "ကတိက ရိုးရှင်းသည်။ ပစ္စည်းများကို နှိပ်၍ \"အဆင့်သတ်မှတ်ချက် မြှင့်တင်ပေးရုံ\" ဖြင့် နေ့စဉ်ကော်မရှင် ရမည်ဟုဆိုသည်။"),
         L("No real product was ever bought or sold.", "တကယ့်ပစ္စည်း တစ်ခုမျှ ဝယ်ယူရောင်းချခြင်း မရှိခဲ့ပါ။"),
         L("To join, people handed over their phone number, an ID document, and a KPay, WavePay or crypto account.",
           "ပါဝင်ရန် လူများက ဖုန်းနံပါတ်၊ မှတ်ပုံတင်နှင့် KPay၊ WavePay သို့မဟုတ် crypto အကောင့်ကို ပေးအပ်ခဲ့ရသည်။",
           say="To join, people handed over their phone number, an ID document, and a K Pay, Wave Pay or crypto account."),
     ]},
    # 5 levels table
    {"type": "shot", "src": "images/shot_levels.jpg", "wide": True, "stamp": "Recruitment table", "kicker": "Pay more, earn more",
     "heading": "Five levels, five deposits", "caption": "Higher levels promised bigger daily income",
     "lines": [
         L("The platform had five levels, named after famous shopping brands.",
           "ပလက်ဖောင်းတွင် နာမည်ကြီး ဈေးဝယ်တံဆိပ်များ၏ အမည်ပေးထားသော အဆင့်ငါးဆင့် ရှိသည်။"),
         L("Entry cost about fifteen dollars. The top level asked for six hundred, and promised almost nine hundred dollars a month.",
           "ဝင်ကြေးမှာ ဒေါ်လာ ၁၅ ခန့်ဖြစ်သည်။ အမြင့်ဆုံးအဆင့်က ဒေါ်လာ ၆၀၀ တောင်းပြီး တစ်လလျှင် ဒေါ်လာ ၉၀၀ နီးပါး ရမည်ဟု ကတိပေးခဲ့သည်။"),
         L("Over the summer, the entry deposit kept rising, from fifteen dollars, to thirty, then seventy.",
           "နွေရာသီတစ်လျှောက် ဝင်ကြေးက ဒေါ်လာ ၁၅ မှ ၃၀၊ ထို့နောက် ၇၀ အထိ တက်လာခဲ့သည်။"),
     ]},
    # 6 team screenshot
    {"type": "shot", "src": "images/shot_team.jpg", "kicker": "Recruit your friends", "heading": "Paid to bring in others",
     "caption": "Members earned rebates from three levels of recruits", "scroll": 10,
     "lines": [
         L("To move up, members had to recruit others. They earned a cut from three levels of their team.",
           "အဆင့်တက်ရန် အဖွဲ့ဝင်များက အခြားသူများကို စည်းရုံးရသည်။ ၎င်းတို့၏ အဖွဲ့အဆင့်သုံးဆင့်မှ ကော်မရှင် ရရှိကြသည်။"),
         L("Recruiters showed withdrawal receipts as proof. Many of them were victims too.",
           "စည်းရုံးသူများက ငွေထုတ်ပြေစာများကို သက်သေအဖြစ် ပြသခဲ့ကြသည်။ ၎င်းတို့အများစုမှာလည်း သားကောင်များပင် ဖြစ်ကြသည်။"),
     ]},
    # 7 flow pyramid
    {"type": "flow", "kicker": "The math", "heading": "Where the \"income\" really came from", "art": {"name": "pyramid"},
     "reveal": True, "reveal_at": [0, 1, 2],
     "items": [{"title": "New deposits", "text": "From late joiners"}, {"title": "Daily \"income\"", "text": "Paid to early members"},
               {"title": "Collapse", "text": "When new money stops", "color": "red"}],
     "lines": [
         L("There was no business behind it. The daily income was simply other people's deposits.",
           "နောက်ကွယ်တွင် လုပ်ငန်းတစ်ခုမျှ မရှိခဲ့ပါ။ နေ့စဉ်ဝင်ငွေဆိုသည်မှာ အခြားသူများ၏ အပ်ငွေများသာ ဖြစ်သည်။"),
         L("Early members were paid with money from late joiners. That is a pyramid scheme.",
           "စောစောဝင်သူများကို နောက်မှဝင်သူများ၏ ငွေဖြင့် ပေးခဲ့သည်။ ၎င်းမှာ ပိရမစ်လိမ်လည်မှု ဖြစ်သည်။"),
         L("And pyramids always collapse when new money stops coming in.",
           "ငွေသစ်ဝင်လာမှု ရပ်သွားသည်နှင့် ပိရမစ်များသည် အမြဲပြိုလဲကြသည်။"),
     ]},
    # 8 account screenshot
    {"type": "shot", "src": "images/shot_account.jpg", "kicker": "One participant's account", "heading": "A balance you could not take out",
     "caption": "Name and personal details blurred", "scroll": 0,
     "lines": [
         L("One participant, living abroad without legal documents, joined in June 2022 hoping to earn from home.",
           "တရားဝင်စာရွက်စာတမ်းမရှိဘဲ ပြည်ပတွင်နေထိုင်သော ပါဝင်သူတစ်ဦးက အိမ်မှငွေရှာရန် မျှော်လင့်ကာ ၂၀၂၂ ဇွန်လတွင် ဝင်ရောက်ခဲ့သည်။"),
         L("The site limited withdrawals and threatened to close accounts, to keep the money inside.",
           "ဆိုက်က ငွေထုတ်ခြင်းကို ကန့်သတ်ပြီး အကောင့်ပိတ်မည်ဟု ခြိမ်းခြောက်ကာ ငွေများကို အတွင်း၌သာ ထိန်းထားခဲ့သည်။"),
         L("When the participant realised it was a scam, they warned their team to stop depositing. But they later lost about five hundred dollars in similar schemes.",
           "လိမ်လည်မှုမှန်း သိသောအခါ ပါဝင်သူက ၎င်း၏အဖွဲ့ကို ငွေထပ်မထည့်ရန် သတိပေးခဲ့သည်။ သို့သော် နောက်ပိုင်းတွင် အလားတူ အစီအစဉ်များ၌ ဒေါ်လာ ၅၀၀ ခန့် ဆုံးရှုံးခဲ့သည်။"),
     ]},
    # 9 collapse stat
    {"type": "stat", "kicker": "The end", "value": "18 Oct 2022", "color": "red", "label": "All withdrawals stopped",
     "detail": "\"Pending\" · \"Rejected\" · \"Technical issues\"", "art": {"name": "alert", "mode": "back", "opacity": .18},
     "lines": [
         L("On the eighteenth of October 2022, all withdrawals stopped.", "၂၀၂၂ အောက်တိုဘာ ၁၈ ရက်တွင် ငွေထုတ်ခြင်းအားလုံး ရပ်သွားခဲ့သည်။"),
         L("Users saw only messages like \"pending\", \"rejected\" or \"technical issues\".",
           "အသုံးပြုသူများမှာ \"ဆိုင်းငံ့ထားသည်\"၊ \"ငြင်းပယ်သည်\" သို့မဟုတ် \"နည်းပညာပြဿနာ\" ကဲ့သို့ စာသားများကိုသာ မြင်ခဲ့ရသည်။"),
         L("A similar scheme called Koala, using kyat and KBZPay, collapsed at the same time. Some people had deposited more than a million kyat.",
           "ကျပ်ငွေနှင့် KBZPay ကို အသုံးပြုသော Koala ဟုခေါ်သည့် အလားတူအစီအစဉ်လည်း တစ်ချိန်တည်းတွင် ပြိုလဲခဲ့သည်။ အချို့က ကျပ်တစ်သန်းကျော် ထည့်ခဲ့ကြသည်။",
           say="A similar scheme called Koala, using kyat and K B Z Pay, collapsed at the same time. Some people had deposited more than a million kyat."),
     ]},
    # 10 losses stat
    {"type": "stat", "kicker": "Estimated losses, 2022", "value": "$1 million+", "label": "lost by Myanmar people to Joom and Koala",
     "detail": "Victims' estimate of many thousands of lakh kyat · not independently verified", "bg": bg("16", .88),
     "lines": [
         L("Victims estimate that Myanmar people lost many thousands of lakh kyat, more than a million US dollars.",
           "သားကောင်များ၏ ခန့်မှန်းချက်အရ မြန်မာပြည်သူများ ကျပ်သိန်းထောင်ပေါင်းများစွာ၊ အမေရိကန်ဒေါ်လာ တစ်သန်းကျော် ဆုံးရှုံးခဲ့ကြသည်။"),
         L("The hardest hit were late joiners, low-income families, and migrants abroad with few other options.",
           "အထိခိုက်ဆုံးမှာ နောက်ကျမှဝင်သူများ၊ ဝင်ငွေနည်းမိသားစုများနှင့် အခြားရွေးချယ်စရာနည်းသော ပြည်ပရွှေ့ပြောင်းလုပ်သားများ ဖြစ်သည်။"),
     ]},
    # 11 chapter 2
    {"type": "chapter", "number": 2, "title": "The scam compounds", "bg": bg("15", .55), "art": {"name": "eye", "mode": "top"},
     "lines": [L("But Joom was small compared with what was being built on Myanmar's borders.",
                 "သို့သော် Joom သည် မြန်မာ့နယ်စပ်တွင် တည်ဆောက်နေသည့်အရာနှင့် နှိုင်းယှဉ်လျှင် သေးငယ်ပါသည်။")]},
    # 12 map
    {"type": "map", "kicker": "Myawaddy · Karen State", "heading": "Scam cities on the border",
     "caption": "Dozens of compounds line the Moei River, facing Thailand.",
     "focus": [96.6, 15.6, 100.2, 18.2], "highlight": {"Kayin": "red"}, "labels": ["Kayin", "Mon"],
     "markers": [{"name": "Shwe Kokko", "lon": 98.52, "lat": 16.86, "color": "gold", "dx": -1},
                 {"name": "Myawaddy", "lon": 98.51, "lat": 16.69, "dx": -1},
                 {"name": "KK Park", "lon": 98.56, "lat": 16.55, "color": "gold"},
                 {"name": "Mae Sot (Thailand)", "lon": 98.6, "lat": 16.72}],
     "lines": [
         L("Along the Moei River near Myawaddy, dozens of guarded compounds grew up after the 2021 coup.",
           "၂၀၂၁ အာဏာသိမ်းပြီးနောက် မြဝတီအနီး သောင်ရင်းမြစ်တစ်လျှောက်တွင် အစောင့်အကြပ်ထားသော ခြံဝင်းဒါဇင်နှင့်ချီ ပေါ်ပေါက်လာခဲ့သည်။",
           say="Along the Moei River near Myawaddy, dozens of guarded compounds grew up after the 2021 coup."),
         L("The best known are Shwe Kokko and KK Park.", "အထင်ရှားဆုံးမှာ ရွှေကုက္ကိုနှင့် KK Park ဖြစ်သည်။",
           say="The best known are Shway Kokko and K K Park."),
     ]},
    # 13 trafficking
    {"type": "points", "kicker": "Inside", "heading": "How workers are trapped", "bg": bg("15", .6),
     "reveal": True, "reveal_at": [0, 1, 2, 3],
     "items": ["Fake job adverts promise high salaries", "Passports taken on arrival", "Daily targets to scam strangers online",
               "Punishment for those who fail or try to leave"],
     "lines": [
         L("Many workers are lured by fake job adverts promising high salaries in Thailand.",
           "အလုပ်သမားများစွာကို ထိုင်းတွင် လစာကောင်းမည်ဟု ကတိပေးသည့် အလုပ်ကြော်ငြာအတုများဖြင့် ဆွဲဆောင်ကြသည်။"),
         L("On arrival, their passports are taken.", "ရောက်ရှိသည်နှင့် ၎င်းတို့၏ နိုင်ငံကူးလက်မှတ်များကို သိမ်းယူကြသည်။"),
         L("They are given daily targets to scam strangers online, through fake romance, investments and crypto.",
           "အချစ်အတု၊ ရင်းနှီးမြှုပ်နှံမှုအတုနှင့် crypto တို့မှတစ်ဆင့် အွန်လိုင်းပေါ်ရှိ မသိသူများကို လိမ်ရန် နေ့စဉ်ပစ်မှတ်များ သတ်မှတ်ပေးကြသည်။"),
         L("Survivors describe being punished when they fail, or when they try to leave.",
           "အောင်မြင်မှုမရလျှင် သို့မဟုတ် ထွက်ခွာရန် ကြိုးစားလျှင် အပြစ်ပေးခံရကြောင်း လွတ်မြောက်လာသူများက ပြောပြကြသည်။"),
     ]},
    # 14 120,000 stat
    {"type": "stat", "kicker": "UN Human Rights, 2023", "value": "120,000", "label": "people in Myanmar may be held in forced scam work",
     "detail": "\"They are victims. They are not criminals.\" — Volker Türk, UN High Commissioner for Human Rights",
     "source": "OHCHR, August 2023",
     "lines": [
         L("In 2023, the UN human rights office estimated that at least 120,000 people in Myanmar may be held in forced scam work.",
           "၂၀၂၃ ခုနှစ်တွင် ကုလသမဂ္ဂ လူ့အခွင့်အရေးရုံးက မြန်မာနိုင်ငံတွင် အနည်းဆုံး လူ ၁၂၀,၀၀၀ ကို လိမ်လည်ရေးလုပ်ငန်းတွင် အတင်းအကြပ် ခိုင်းစေထားနိုင်သည်ဟု ခန့်မှန်းခဲ့သည်။"),
         L("The UN human rights chief, Volker Türk, said: \"They are victims. They are not criminals.\"",
           "ကုလသမဂ္ဂ လူ့အခွင့်အရေးမဟာမင်းကြီး Volker Türk က \"သူတို့သည် သားကောင်များဖြစ်သည်။ ရာဇဝတ်သားများ မဟုတ်ကြပါ\" ဟု ပြောကြားခဲ့သည်။",
           say="The UN human rights chief, Volker Turk, said: They are victims. They are not criminals."),
     ]},
    # 15 losses stat
    {"type": "stat", "kicker": "UN Office on Drugs and Crime", "value": "$114 billion", "label": "lost to scams in Asia-Pacific in 2025",
     "detail": "Estimated $88–114 billion, at least triple the 2023 estimate", "source": "UNODC, July 2026",
     "lines": [
         L("In July 2026, the UN Office on Drugs and Crime estimated that scams cost victims in the Asia-Pacific region up to 114 billion dollars in 2025.",
           "၂၀၂၆ ဇူလိုင်လတွင် ကုလသမဂ္ဂ မူးယစ်ဆေးဝါးနှင့် ရာဇဝတ်မှုဆိုင်ရာရုံးက ၂၀၂၅ ခုနှစ်တွင် အာရှ-ပစိဖိတ်ဒေသ၌ လိမ်လည်မှုကြောင့် ဒေါ်လာ ဘီလီယံ ၁၁၄ အထိ ဆုံးရှုံးခဲ့သည်ဟု ခန့်မှန်းခဲ့သည်။"),
         L("Myanmar and Cambodia are named as two of the main hubs.", "မြန်မာနှင့် ကမ္ဘောဒီးယားကို အဓိက ဗဟိုချက်နှစ်ခုအဖြစ် ဖော်ပြထားသည်။"),
     ]},
    # 16 chapter 3
    {"type": "chapter", "number": 3, "title": "Who protects them", "bg": bg("16", .55), "art": {"name": "documents", "mode": "top"},
     "lines": [L("So how can compounds this large operate in the open?", "ဤမျှကြီးမားသော ခြံဝင်းများ ပေါ်တင် မည်သို့ လည်ပတ်နိုင်သနည်း။")]},
    # 17 BGF
    {"type": "flow", "kicker": "Protection", "heading": "Who profits from the compounds", "reveal": True, "reveal_at": [0, 1, 2],
     "items": [{"title": "Scam bosses", "text": "Build and run the compounds"},
               {"title": "Karen BGF / KNA", "text": "Controls the land, takes a share"},
               {"title": "The junta", "text": "Allied with the BGF since 2010", "color": "red"}],
     "lines": [
         L("Much of the land is controlled by the Karen Border Guard Force, an armed group led by Saw Chit Thu and allied with the military.",
           "မြေအများစုကို စစ်တပ်နှင့် မဟာမိတ်ဖွဲ့ထားပြီး စောချစ်သူ ဦးဆောင်သော ကရင်နယ်ခြားစောင့်တပ် (BGF) က ထိန်းချုပ်ထားသည်။",
           say="Much of the land is controlled by the Karen Border Guard Force, an armed group led by Saw Chit Thu and allied with the military."),
         L("Shwe Kokko was built with a Chinese tycoon, She Zhijiang, on land controlled by the group.",
           "ရွှေကုက္ကိုကို အဆိုပါအဖွဲ့ ထိန်းချုပ်သောမြေပေါ်တွင် တရုတ်စီးပွားရေးသမား She Zhijiang နှင့်အတူ တည်ဆောက်ခဲ့သည်။",
           say="Shway Kokko was built with a Chinese tycoon, Sheh Jir-jyang, on land controlled by the group."),
         L("In 2024 the group renamed itself the Karen National Army, but the US Treasury says it kept cooperating with the junta.",
           "၂၀၂၄ ခုနှစ်တွင် အဆိုပါအဖွဲ့က ကရင်အမျိုးသားတပ် (KNA) ဟု အမည်ပြောင်းခဲ့သော်လည်း စစ်ကောင်စီနှင့် ဆက်လက်ပူးပေါင်းဆောင်ရွက်ခဲ့ကြောင်း အမေရိကန် ဘဏ္ဍာရေးဌာနက ဆိုသည်။"),
     ]},
    # 18 sanctions timeline
    {"type": "timeline", "kicker": "International action", "heading": "Sanctions and pressure", "reveal": True,
     "items": [{"date": "2023", "text": "UK sanctions Saw Chit Thu"}, {"date": "2024", "text": "EU follows"},
               {"date": "May 2025", "text": "US sanctions KNA as a criminal group"},
               {"date": "Sep 2025", "text": "US sanctions Shwe Kokko network"}],
     "lines": [
         L("The United Kingdom sanctioned Saw Chit Thu in 2023, and the European Union followed in 2024.",
           "ယူကေက စောချစ်သူကို ၂၀၂၃ တွင် ပိတ်ဆို့အရေးယူခဲ့ပြီး ဥရောပသမဂ္ဂက ၂၀၂၄ တွင် လိုက်လံဆောင်ရွက်ခဲ့သည်။"),
         L("In May 2025, the United States named the Karen National Army a transnational criminal organisation.",
           "၂၀၂၅ မေလတွင် အမေရိကန်က ကရင်အမျိုးသားတပ်ကို နိုင်ငံဖြတ်ကျော် ရာဇဝတ်အဖွဲ့အစည်းအဖြစ် သတ်မှတ်ခဲ့သည်။"),
         L("A spokesperson for the group replied that the sanctions \"will not affect us in any way\".",
           "အဖွဲ့၏ ပြောရေးဆိုခွင့်ရှိသူက ပိတ်ဆို့မှုများက \"ကျွန်ုပ်တို့ကို မည်သို့မျှ မထိခိုက်ပါ\" ဟု တုံ့ပြန်ခဲ့သည်။"),
         L("In September 2025, Washington also sanctioned people and companies behind Shwe Kokko, including She Zhijiang.",
           "၂၀၂၅ စက်တင်ဘာလတွင် ဝါရှင်တန်က She Zhijiang အပါအဝင် ရွှေကုက္ကို၏ နောက်ကွယ်ရှိ ပုဂ္ဂိုလ်နှင့် ကုမ္ပဏီများကိုလည်း ပိတ်ဆို့ခဲ့သည်။",
           say="In September 2025, Washington also sanctioned people and companies behind Shway Kokko, including Sheh Jir-jyang."),
     ]},
    # 19 crackdown timeline
    {"type": "timeline", "kicker": "The \"crackdown\"", "heading": "Raids, power cuts and demolitions", "reveal": True,
     "items": [{"date": "Jan 2025", "text": "Chinese actor rescued from Shwe Kokko"}, {"date": "Feb 2025", "text": "Thailand cuts power and internet"},
               {"date": "Oct 2025", "text": "Junta raids KK Park"}, {"date": "Oct 2025–Jan 2026", "text": "600+ buildings demolished"}],
     "lines": [
         L("In January 2025, a Chinese actor, Wang Xing, was rescued from a scam centre in Shwe Kokko, and public anger in China grew.",
           "၂၀၂၅ ဇန်နဝါရီလတွင် တရုတ်သရုပ်ဆောင် Wang Xing ကို ရွှေကုက္ကိုရှိ လိမ်လည်ရေးစခန်းမှ ကယ်ဆယ်ခဲ့ပြီး တရုတ်ပြည်သူများ၏ ဒေါသ ကြီးထွားလာခဲ့သည်။",
           say="In January 2025, a Chinese actor, Wahng Shing, was rescued from a scam centre in Shway Kokko, and public anger in China grew."),
         L("In February, Thailand cut electricity, fuel and internet to border areas including Myawaddy.",
           "ဖေဖော်ဝါရီလတွင် ထိုင်းက မြဝတီအပါအဝင် နယ်စပ်ဒေသများသို့ လျှပ်စစ်၊ လောင်စာနှင့် အင်တာနက် ဖြတ်တောက်ခဲ့သည်။"),
         L("In October, the junta announced a raid on KK Park, detaining more than two thousand people and seizing Starlink receivers.",
           "အောက်တိုဘာလတွင် စစ်ကောင်စီက KK Park ကို စီးနင်းကြောင်း ကြေညာပြီး လူ နှစ်ထောင်ကျော် ဖမ်းဆီးကာ Starlink စက်များ သိမ်းဆည်းခဲ့သည်။",
           say="In October, the junta announced a raid on K K Park, detaining more than two thousand people and seizing Starlink receivers."),
         L("By January 2026, more than six hundred buildings had reportedly been demolished.",
           "၂၀၂၆ ဇန်နဝါရီလအထိ အဆောက်အဦ ခြောက်ရာကျော် ဖြိုဖျက်ခဲ့သည်ဟု သတင်းရရှိသည်။"),
     ]},
    # 20 skepticism quote
    {"type": "quote", "text": "The compounds are gone, but the networks remain.", "who": "Prachatai English, 2026", "bg": bg("15", .7),
     "lines": [
         L("But local people and experts called the raid a staged show, coordinated with the Border Guard Force.",
           "သို့သော် ဒေသခံများနှင့် ကျွမ်းကျင်သူများက အဆိုပါ စီးနင်းမှုကို နယ်ခြားစောင့်တပ်နှင့် ပူးပေါင်း၍ ဇာတ်ခင်းထားသော ပြသမှုတစ်ခုဟု ဆိုကြသည်။"),
         L("No senior Border Guard Force leader has been arrested.", "နယ်ခြားစောင့်တပ် အကြီးတန်းခေါင်းဆောင် တစ်ဦးမျှ ဖမ်းဆီးခံရခြင်း မရှိသေးပါ။"),
         L("And in July 2026, reporters found the industry growing again, moving into homes, jungle camps and other militia areas.",
           "၂၀၂၆ ဇူလိုင်လတွင် သတင်းထောက်များက ဤလုပ်ငန်း နေအိမ်များ၊ တောတွင်းစခန်းများနှင့် အခြားပြည်သူ့စစ်နယ်မြေများသို့ ရွှေ့ပြောင်းကာ ပြန်လည်ကြီးထွားနေကြောင်း တွေ့ရှိခဲ့သည်။"),
     ]},
    # 21 chapter 4
    {"type": "chapter", "number": 4, "title": "The rigged casino", "art": {"name": "slot", "mode": "top"},
     "lines": [L("The same networks also run illegal online gambling, aimed at people inside Myanmar.",
                 "အလားတူ ကွန်ရက်များက မြန်မာပြည်တွင်းရှိ လူများကို ပစ်မှတ်ထားသော တရားမဝင် အွန်လိုင်းလောင်းကစားကိုလည်း လုပ်ကိုင်ကြသည်။")]},
    # 22 RTP
    {"type": "stat", "kicker": "The house always wins", "value": "95%", "label": "of every bet returned in the long run, at best",
     "detail": "The platform keeps the rest. Rigged copies of famous games keep far more.", "art": {"name": "slot", "mode": "back", "opacity": .15},
     "lines": [
         L("Every slot, fish-shooting or card game is controlled by a server, not by luck.",
           "စလော့၊ ငါးပစ် သို့မဟုတ် ဖဲဂိမ်းတိုင်းကို ကံက မဟုတ်ဘဲ ဆာဗာက ထိန်းချုပ်ထားသည်။"),
         L("Even an honest game returns only around ninety-five percent of bets over time. The rest is the platform's profit.",
           "ရိုးသားသောဂိမ်းပင်လျှင် အချိန်ကြာလာသည်နှင့်အမျှ လောင်းကြေး၏ ၉၅ ရာခိုင်နှုန်းခန့်သာ ပြန်ပေးသည်။ ကျန်ငွေမှာ ပလက်ဖောင်း၏ အမြတ်ဖြစ်သည်။"),
         L("Many Myanmar sites use rigged copies of famous game brands, set to pay back far less.",
           "မြန်မာဆိုက်များစွာက နာမည်ကြီးဂိမ်းတံဆိပ်များ၏ ဂျင်ထည့်ထားသော မိတ္တူများကို အသုံးပြုကြပြီး ပြန်ပေးငွေကို အလွန်နည်းအောင် ချိန်ညှိထားသည်။"),
     ]},
    # 23 tricks
    {"type": "points", "kicker": "How they cheat winners", "heading": "Five dirty tricks", "art": {"name": "documents"},
     "reveal": True, "reveal_at": [0, 1, 2, 3, 4],
     "items": ["Ban the account with fake excuses", "Stall and limit withdrawals", "Rigged \"clone\" game servers",
               "\"Network error\" right before a big win", "Seize the deposit and threaten the player"],
     "lines": [
         L("Win big, and your account may be banned, blamed on a shared Wi-Fi, a \"system bug\", or a bot.",
           "ငွေအများကြီးနိုင်လျှင် Wi-Fi တူသုံးခြင်း၊ \"စနစ်ချို့ယွင်းချက်\" သို့မဟုတ် bot သုံးခြင်းဟု အကြောင်းပြကာ အကောင့်ပိတ်ခံရနိုင်သည်။"),
         L("Or your withdrawal is \"under investigation\" for days, with a tiny daily limit, until you lose it back.",
           "သို့မဟုတ် ငွေထုတ်ခြင်းကို ရက်ပေါင်းများစွာ \"စစ်ဆေးဆဲ\" ဟုဆိုကာ နေ့စဉ်ကန့်သတ်ချက် အလွန်နည်းအောင်ထားပြီး ပြန်ရှုံးသွားသည်အထိ ဆွဲထားသည်။"),
         L("Some sites run fake copies of famous game servers, tuned so players almost never win.",
           "အချို့ဆိုက်များက ကစားသူ မနိုင်သလောက်ဖြစ်အောင် ချိန်ညှိထားသော နာမည်ကြီးဂိမ်းဆာဗာ အတုများကို အသုံးပြုကြသည်။"),
         L("Players report a sudden \"network error\" just before a jackpot, and the win disappears.",
           "Jackpot ပေါက်ခါနီးတွင် ရုတ်တရက် \"Network Error\" ဖြစ်ပြီး နိုင်ငွေ ပျောက်သွားကြောင်း ကစားသူများက ပြောကြသည်။"),
         L("Some agents even seize the player's own deposit, knowing that illegal gamblers cannot go to the police.",
           "တရားမဝင်လောင်းကစားသူများ ရဲထံ မတိုင်နိုင်မှန်း သိသဖြင့် အချို့အေးဂျင့်များက ကစားသူ၏ အရင်းငွေကိုပင် သိမ်းယူကြသည်။"),
     ]},
    # 24 psychology
    {"type": "points", "kicker": "Built to be addictive", "heading": "How slot games trick the brain", "art": {"name": "slot"},
     "reveal": True, "reveal_at": [0, 1, 2, 3],
     "items": ["Random rewards keep you pressing", "\"Near misses\" are designed on purpose",
               "Lights and sounds release dopamine", "Losses shown as \"WIN!\""],
     "lines": [
         L("Rewards come at random, the same trick psychologists use to train animals to keep pressing a lever.",
           "ဆုလာဘ်များကို ကျပန်းပေးခြင်းသည် တိရစ္ဆာန်များ လီဗာကို ဆက်တိုက်နှိပ်စေရန် စိတ်ပညာရှင်များ အသုံးပြုသည့် လှည့်ကွက်နှင့် တူသည်။"),
         L("Two jackpot symbols land, and the third just misses. That \"near miss\" is designed to make you try again.",
           "Jackpot သင်္ကေတ နှစ်ခုကျပြီး တတိယတစ်ခု ချော်သွားသည်။ ထို \"တစ်ကွက်အလို\" ကို နောက်တစ်ကြိမ် ထပ်ကြိုးစားစေရန် ရည်ရွယ်ချက်ရှိရှိ ဖန်တီးထားသည်။"),
         L("Flashing lights and coin sounds flood the brain with dopamine, even for tiny wins.",
           "မီးရောင်များနှင့် ဒင်္ဂါးသံများက အနိုင်အနည်းငယ်အတွက်ပင် ဦးနှောက်ကို ဒိုပါမင်းများ ပြည့်လျှံစေသည်။"),
         L("Bet one thousand kyat, get five hundred back, and the screen still shouts \"WIN!\". That is a loss, disguised as a win.",
           "ကျပ်တစ်ထောင်လောင်းပြီး ငါးရာပြန်ရလျှင်ပင် ဖန်သားပြင်က \"WIN!\" ဟု အော်ပြသည်။ ၎င်းမှာ နိုင်သလို ဟန်ဆောင်ထားသော အရှုံး ဖြစ်သည်။"),
     ]},
    # 25 money flow
    {"type": "flow", "kicker": "Follow the money", "heading": "Who gets players' losses", "reveal": True, "reveal_at": [0, 1, 2],
     "items": [{"title": "Players lose", "text": "Total bets minus total wins"},
               {"title": "Master agent", "text": "Takes up to 40%", "color": "red"},
               {"title": "Sub-agents", "text": "Split the rest, level by level"}],
     "lines": [
         L("Every kyat that players lose is shared out through a chain of agents.",
           "ကစားသူများ ရှုံးသမျှ ကျပ်ငွေတိုင်းကို အေးဂျင့်ကွင်းဆက်တစ်ခုမှတစ်ဆင့် ခွဲဝေကြသည်။"),
         L("A master agent can take up to forty percent of the losses, and pass the rest down to sub-agents.",
           "Master Agent တစ်ဦးက အရှုံးငွေ၏ ၄၀ ရာခိုင်နှုန်းအထိ ယူနိုင်ပြီး ကျန်ငွေကို Sub-agent များထံ ခွဲပေးသည်။"),
         L("So the agents who invite you to play earn money only when you lose.",
           "ထို့ကြောင့် သင့်ကို ကစားရန် ဖိတ်ခေါ်သော အေးဂျင့်များသည် သင်ရှုံးမှသာ ငွေရကြသည်။"),
     ]},
    # 26 protect yourself
    {"type": "points", "kicker": "Protect yourself", "heading": "Warning signs of a scam", "bg": bg("13", .65),
     "reveal": True, "reveal_at": [0, 1, 2, 3, 4],
     "items": ["Returns no real business could pay", "\"Work\" that is only clicking", "Income depends on recruiting or new deposits",
               "Limits or excuses when you withdraw", "Asks for ID plus your payment account"],
     "lines": [
         L("So how do you spot a scam? First: returns that no real business could pay.",
           "ဒါဆို လိမ်လည်မှုကို ဘယ်လိုသိနိုင်မလဲ။ ပထမ - မည်သည့်တကယ့်လုပ်ငန်းကမျှ မပေးနိုင်သော အမြတ်နှုန်း။"),
         L("Second: \"work\" that is only clicking, with no real product.", "ဒုတိယ - တကယ့်ပစ္စည်းမရှိဘဲ နှိပ်ရုံသာဖြစ်သော \"အလုပ်\"။"),
         L("Third: income that depends on recruiting people or on new deposits.", "တတိယ - လူစည်းရုံးခြင်း သို့မဟုတ် အပ်ငွေသစ်အပေါ် မူတည်သော ဝင်ငွေ။"),
         L("Fourth: limits, delays or excuses when you try to withdraw.", "စတုတ္ထ - ငွေထုတ်ရန် ကြိုးစားသောအခါ ကန့်သတ်ချက်၊ နှောင့်နှေးမှု သို့မဟုတ် အကြောင်းပြချက်များ။"),
         L("And fifth: a request for your ID together with your payment account.", "ပဉ္စမ - မှတ်ပုံတင်နှင့် ငွေပေးချေမှုအကောင့်ကို အတူတကွ တောင်းခြင်း။"),
     ]},
    # 27 conclusion
    {"type": "text", "kicker": "Conclusion", "heading": "A business built on desperation", "bg": bg("16", .7),
     "body": "Scams in Myanmar are not small frauds. They are an industry, protected by armed groups and tolerated by those in power.",
     "lines": [
         L("Myanmar's scams are not small frauds. They are an industry, built on war, poverty and desperation.",
           "မြန်မာ့လိမ်လည်မှုများသည် သေးငယ်သော လိမ်လည်မှုများ မဟုတ်ပါ။ စစ်ပွဲ၊ ဆင်းရဲမှုနှင့် အခက်အခဲများပေါ်တွင် တည်ဆောက်ထားသော လုပ်ငန်းတစ်ခု ဖြစ်သည်။"),
         L("And they survive because armed groups protect them, and those in power have looked away.",
           "လက်နက်ကိုင်အဖွဲ့များက ကာကွယ်ပေးပြီး အာဏာရှိသူများက မျက်ကွယ်ပြုထားသောကြောင့် ဆက်လက်ရှင်သန်နေခြင်း ဖြစ်သည်။"),
         L("If you see a deal that sounds too good to be true, share this video with the person who sent it.",
           "ယုံရခက်လောက်အောင် ကောင်းလွန်းသော ကမ်းလှမ်းချက်ကို တွေ့ပါက ပို့လာသူထံ ဤဗီဒီယိုကို မျှဝေပေးပါ။"),
     ]},
]

ep = {
    "id": "03-scam-economy",
    "title": "Myanmar's Scam Economy: Fake Jobs, Scam Compounds and Rigged Gambling",
    "channel_html": "Maung Yel Hkawng <b>· Myanmar Community Researcher</b>",
    "short_endcard_title": "Myanmar's Scam Economy",
    "theme": "cinema",
    "music": {"level_lufs": -28},
    "subtitle_scale": 1.15,
    "subtitle_my_scale": 1.33,
    "ai_voice": {"voice": "george", "speed": 1.15, "gap_scale": 0.75},
    "people": {},
    "scenes": scenes,
    "shorts": [
        {"id": "short-01-joom-trap", "hook": "The *Joom scam* that emptied Myanmar wallets", "scenes": [4, 5, 7, 9],
         "caption": "A fake \"click to earn\" app took Myanmar people's savings in 2022. Here's how it worked.",
         "hashtags": ["#Myanmar", "#ScamAlert", "#Joom", "#OnlineScam", "#Burma"]},
        {"id": "short-02-rigged-casino", "hook": "How online casinos *cheat* you", "scenes": [23, 25],
         "caption": "Five dirty tricks illegal gambling sites use, and who profits when you lose.",
         "hashtags": ["#Myanmar", "#OnlineGambling", "#ScamAlert", "#Explained"]},
        {"id": "short-03-who-protects", "hook": "Who *protects* Myanmar's scam cities?", "scenes": [17, 19, 20],
         "caption": "Scam compounds on the Thai border, the armed group that hosts them, and the \"crackdown\".",
         "hashtags": ["#Myanmar", "#ScamCompounds", "#Myawaddy", "#HumanTrafficking"]},
    ],
    "thumbnail": {"kicker": "Myanmar investigation", "text": "Myanmar's|scam|economy", "size": 140,
                  "bg": dict(bg("16"), pos="60% 40%")},
    "sources": [
        "First-hand account: \"The Joom Online Task Scam in Myanmar (2022)\", one participant, June–October 2022 (figures unverified)",
        "OHCHR (Aug 2023): Online scam operations and trafficking into forced criminality in Southeast Asia",
        "UNODC (Jul 2026): scam losses in East/Southeast Asia, Australia and NZ estimated at $88–114bn for 2025",
        "US Treasury OFAC (5 May 2025): sanctions on the Karen National Army, Saw Chit Thu and sons",
        "US Treasury OFAC (Sep 2025): sanctions on Shwe Kokko network incl. She Zhijiang",
        "Reuters / AP / Bangkok Post (Feb 2025): Thailand cuts power, fuel and internet to Myawaddy area",
        "Al Jazeera / RFA / The Irrawaddy (Oct 2025): KK Park raid, 2,000+ detained, 30 Starlink receivers",
        "Myanmar Now (2026): 600+ buildings razed Oct 2025–Jan 2026; operations relocating",
        "ABC News (Jul 2026): scam centres growing 'exponentially' despite crackdown",
        "Prachatai English (2026): 'The compounds are gone, but the networks remain'",
        "Online gambling mechanics: Maung Yel Hkawng, Burmese-language research article",
    ],
    "upload": {
        "titles": ["Myanmar's Scam Economy: Fake Jobs, Scam Compounds and Rigged Gambling",
                   "The Joom Scam, KK Park and the Rigged Casino: Inside Myanmar's Scam Economy",
                   "How Myanmar Became the World's Scam Capital"],
        "description": ("In 2022, a fake \"click to earn\" app using the name Joom took the savings of thousands of Myanmar people. "
                        "It was only a small part of a much bigger industry: scam compounds on the Thai border, illegal online gambling, "
                        "and the armed groups that protect them.\n\nThis video combines a first-hand account, UN reports and international reporting. "
                        "Personal details in screenshots are blurred.\n\nNote: Joom is a real, legitimate online shop. The scam only copied its name.\n\n"
                        "English narration · မြန်မာစာတန်းထိုး (Burmese subtitles)"),
        "footer": ("Research and script: Maung Yel Hkawng, Myanmar Community Researcher.\nNarration: AI voice. Music: original. "
                   "Visuals: real screenshots (personal details blurred), original animations, openly licensed photos.\n"
                   "Spotted a mistake? Tell me in the comments and I'll correct it here."),
        "tags": ["Myanmar", "Burma", "scam", "online scam", "Joom scam", "Koala scam", "scam compounds", "KK Park", "Shwe Kokko",
                 "Myawaddy", "online gambling", "BGF", "Saw Chit Thu", "human trafficking", "pig butchering", "explained"],
        "hashtags": ["#Myanmar", "#ScamAlert", "#Explained"],
    },
}
(HERE / "episode.json").write_text(json.dumps(ep, ensure_ascii=False, indent=1), encoding="utf-8")
words = sum(len(l["en"].split()) for s in scenes for l in s["lines"])
print("scenes", len(scenes), "words", words)
