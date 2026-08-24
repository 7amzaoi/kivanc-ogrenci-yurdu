# -*- coding: utf-8 -*-
"""Write the SEO landing-page copy into i18n/en.json and i18n/tr.json.

Every factual claim here is taken from data already on the site: the six
universities and their travel times from `uni.*`, the four room types and
rates from `rooms.*`, the twelve facilities from `amen.*`, the address from
`contact.*`. Nothing is invented -- no gym, no study lounge, no meal plan,
no student counts, no review quotes.
"""
import io
import json
import collections

# ---------------------------------------------------------------------------
# Per page: which shared factual blocks it renders, and its own prose.
# BLOCKS are rendered by the generator from the existing JSON data, so they
# cannot drift from what the rest of the site says.
# ---------------------------------------------------------------------------
PAGES = collections.OrderedDict([
    ("istanbul-kiz-yurdu", {
        "blocks": ["location", "transport", "rooms", "facilities"],
        "faq": ["1", "2", "4"],
        "related": ["istanbul-kiz-ogrenci-yurdu", "guvenli-kiz-yurdu-istanbul", "kiz-yurdu-fiyatlari"],
    }),
    ("istanbul-ogrenci-yurdu", {
        "blocks": ["rooms", "included", "facilities"],
        "faq": ["2", "3", "5"],
        "related": ["istanbul-kiz-yurdu", "kiz-yurdu-fiyatlari", "universitelere-yakin-kiz-yurdu"],
    }),
    ("istanbul-kiz-ogrenci-yurdu", {
        "blocks": ["security", "facilities", "rooms"],
        "faq": ["4", "6", "1"],
        "related": ["guvenli-kiz-yurdu-istanbul", "istanbul-kiz-yurdu", "universitelere-yakin-kiz-yurdu"],
    }),
    ("guvenli-kiz-yurdu-istanbul", {
        "blocks": ["security", "location"],
        "faq": ["4", "6", "5"],
        "related": ["istanbul-kiz-ogrenci-yurdu", "istanbul-kiz-yurdu", "kiz-yurdu-fiyatlari"],
    }),
    ("universitelere-yakin-kiz-yurdu", {
        "blocks": ["universities", "transport", "location"],
        "faq": ["1", "2"],
        "related": ["istanbul-ogrenci-yurdu", "istanbul-kiz-yurdu", "kiz-yurdu-fiyatlari"],
    }),
    ("kiz-yurdu-fiyatlari", {
        "blocks": ["rates", "included"],
        "faq": ["3", "5", "2"],
        "related": ["istanbul-ogrenci-yurdu", "istanbul-kiz-yurdu", "guvenli-kiz-yurdu-istanbul"],
    }),
])

TR = {
    "istanbul-kiz-yurdu": {
        "title": "İstanbul Kız Yurdu | Kıvanç Kız Yurdu",
        "description": "Avcılar'da özel kız yurdu: 45 oda, oda içi banyo, 7/24 güvenlik ve kamera kaydı, kahvaltı dahil. Metrobüs yürüme mesafesinde.",
        "h1": "İstanbul Kız Yurdu",
        "navLabel": "İstanbul Kız Yurdu",
        "lede": "Kıvanç Kız Yurdu, İstanbul Avcılar'da yalnızca kız öğrencilere hizmet veren özel bir yurttur. Binada dört farklı büyüklükte 45 oda bulunur; hepsinde oda içi banyo ve WC, televizyon, mini buzdolabı ve sıfır çalışma takımı vardır.",
        "intro": [
            {"h": "Yurt hakkında", "p": [
                "Yurt, Cihangir Mahallesi'nde Kirazlı Caddesi üzerinde tek bir binada hizmet verir. Odalar tek, iki, üç ve dört kişilik olarak ayrılır; aradaki fark yalnızca odayı kaç kişinin paylaştığı ve buna bağlı aylık ücrettir. Donanım her oda tipinde aynıdır.",
                "Binada yaşayan bir yurt müdürü vardır. Bir sorun olduğunda başka bir şehirdeki çağrı merkezine değil, öğrenciyi adıyla tanıyan bir kişiye ulaşırsınız."
            ]},
        ],
        "close": {"h": "Neden Kıvanç Kız Yurdu?", "p": [
            "Tek bir aylık rakam ödersiniz: kira, faturalar, fiber internet, haftalık oda temizliği, çamaşırhane, kesintisiz sıcak su ve her sabah kahvaltı bu rakama dahildir. Ay sonunda ayrıca fatura çıkmaz.",
            "Yerinde göremeyecek durumdaysanız odaları görüntülü görüşmeyle canlı olarak gösteriyoruz."
        ]},
    },
    "istanbul-ogrenci-yurdu": {
        "title": "İstanbul Öğrenci Yurdu | Kıvanç Kız Yurdu",
        "description": "Avcılar'da öğrenci yurdu: dört oda tipi, aylık ₺15.000'den başlayan fiyatlar, taksitli ödeme, kahvaltı ve faturalar dahil.",
        "h1": "İstanbul Öğrenci Yurdu",
        "navLabel": "İstanbul Öğrenci Yurdu",
        "lede": "Kıvanç Kız Yurdu, Avcılar'da kız öğrenciler için akademik yıl boyunca konaklama sunar. Standart sözleşme eylül–haziran arasını kapsar ve ödeme taksitlendirilir.",
        "intro": [
            {"h": "Öğrenciler için ne sunuyoruz", "p": [
                "Bir öğrenci yurdu seçerken asıl mesele, aylık rakamın gerçekten ne kadarını kapsadığıdır. Burada tek bir tutar ödenir; faturalar, internet, temizlik, çamaşırhane, sıcak su ve kahvaltı içindedir. Ay sonunda sürpriz bir hesap çıkmaz.",
                "Odaların tamamı otel tipidir: banyo ve WC oda içindedir, koridorda sıra beklenmez. Her odada televizyon, mini buzdolabı ve yeni bir çalışma masası bulunur."
            ]},
        ],
        "close": {"h": "Sözleşme ve ödeme", "p": [
            "Standart sözleşme eylül–haziran akademik yılını kapsar. Yaz dönemi ve daha kısa kalışlar yer durumuna bağlı olarak değerlendirilir.",
            "Ödeme peşinat ve taksitler şeklindedir; her ödeme için makbuz düzenlenir. Belgesiz nakit talep edilmez."
        ]},
    },
    "istanbul-kiz-ogrenci-yurdu": {
        "title": "İstanbul Kız Öğrenci Yurdu | Kıvanç Kız Yurdu",
        "description": "Yalnızca kız öğrencilere özel yurt. Kartlı geçiş, 7/24 kamera kaydı, giriş-çıkış bildirimi ve binada yaşayan yönetim.",
        "h1": "İstanbul Kız Öğrenci Yurdu",
        "navLabel": "İstanbul Kız Öğrenci Yurdu",
        "lede": "Kıvanç Kız Yurdu yalnızca kız öğrencilere hizmet verir. Bina karma değildir; yatakhane katlarına giriş kartlıdır ve ziyaretçiler giriş katındaki salonda ağırlanır.",
        "intro": [
            {"h": "Aileler için", "p": [
                "Şehir dışından bir öğrenciyi İstanbul'a göndermenin en zor tarafı, ne olup bittiğini görememektir. Öğrencinin binaya her girişi ve çıkışı kaydedilir; isteyen aileye bu bildirimler WhatsApp üzerinden iletilir.",
                "Binada yaşayan bir yurt müdürü vardır ve aileler ziyaret saatleri içinde ağırlanır."
            ]},
        ],
        "close": {"h": "Günlük hayat", "p": [
            "Bina hafta içi 23:00'te, hafta sonu 24:00'te kapanır. Daha geç dönmesi gereken bir öğrenci yurt müdürüyle önceden görüşür.",
            "Haftalık oda temizliği ve ortak alanların günlük bakımı aylık ücrete dahildir."
        ]},
    },
    "guvenli-kiz-yurdu-istanbul": {
        "title": "Güvenli Kız Yurdu İstanbul | Kıvanç Kız Yurdu",
        "description": "7/24 personelli resepsiyon, kartlı geçiş, tüm ortak alanlarda kesintisiz kamera kaydı ve aileye giriş-çıkış bildirimi.",
        "h1": "Güvenli Kız Yurdu İstanbul",
        "navLabel": "Güvenli Kız Yurdu İstanbul",
        "lede": "Güvenlik, bir yurt broşüründe en kolay yazılan ve en zor kanıtlanan şeydir. Aşağıda Kıvanç Kız Yurdu'nda fiilen uygulanan düzenlemeler yer alır.",
        "intro": [
            {"h": "Nasıl çalışıyor", "p": [
                "Resepsiyon gece gündüz personellidir ve tüm girişlerde kartlı geçiş sistemi vardır. Yatakhane katlarına kartsız girilmez.",
                "Ortak alanların ve girişlerin tamamı gün boyu kesintisiz kaydedilir. Kayıtlar düzenli olarak saklanır."
            ]},
        ],
        "close": {"h": "Ziyaret kuralları", "p": [
            "Aileler ziyaret saatleri içinde giriş katındaki salonda ağırlanır. Yatakhane katlarına ziyaretçi çıkmaz.",
            "Bina hafta içi 23:00'te, hafta sonu 24:00'te kapanır."
        ]},
    },
    "universitelere-yakin-kiz-yurdu": {
        "title": "Üniversitelere Yakın Kız Yurdu İstanbul | Kıvanç",
        "description": "Avcılar'dan Metrobüs ile Gelişim 5 dk, Beykent 10 dk, Aydın 15 dk, Arel 20 dk, Biruni 30 dk. Durak yürüme mesafesinde.",
        "h1": "Üniversitelere Yakın Kız Yurdu İstanbul",
        "navLabel": "Üniversitelere Yakın Kız Yurdu",
        "lede": "Avcılar'ın avantajı Metrobüs hattıdır. Yurttan durağa yürünür ve İstanbul'un vakıf üniversitelerinin çoğuna aktarmasız ulaşılır.",
        "intro": [
            {"h": "Konum neden önemli", "p": [
                "Bir yurdun aylık ücreti kadar önemli olan, her sabah yolda geçen süredir. Aşağıdaki süreler Metrobüs hattı üzerinden, normal trafik koşullarında yaklaşık değerlerdir.",
                "Sabah ilk derse yetişmek için yarım saatten fazla yol yapmak, bir akademik yıl boyunca ciddi bir farktır."
            ]},
        ],
        "close": {"h": "Kapıda toplu taşıma", "p": [
            "Metrobüs, otobüs ve minibüs hatlarının tamamı binaya kısa bir yürüyüş mesafesindedir.",
            "Süreleri kendiniz de doğrulayabilirsiniz; adres aşağıda ve haritada işaretlidir."
        ]},
    },
    "kiz-yurdu-fiyatlari": {
        "title": "Kız Yurdu Fiyatları İstanbul | Kıvanç Kız Yurdu",
        "description": "2026 kız yurdu fiyatları: tek kişilik ₺30.000, iki kişilik ₺24.000, üç kişilik ₺18.000, dört kişilik ₺15.000. Kahvaltı ve faturalar dahil.",
        "h1": "Kız Yurdu Fiyatları İstanbul",
        "navLabel": "Kız Yurdu Fiyatları",
        "lede": "Aşağıdaki aylık ücretler kişi başıdır ve odayı kaç öğrencinin paylaştığına göre değişir. Donanım her oda tipinde aynıdır.",
        "intro": [
            {"h": "Fiyatlar nasıl belirleniyor", "p": [
                "Odalar arasındaki tek fark kişi sayısıdır. Oda içi banyo, televizyon, mini buzdolabı ve çalışma takımı her oda tipinde vardır; dört kişilik oda ucuz olduğu için eksik donanımlı değildir.",
                "Ödeme peşinat ve taksitler şeklinde yapılır. Her ödeme için makbuz düzenlenir."
            ]},
        ],
        "close": {"h": "Fiyata dahil olmayanlar", "p": [
            "Aylık ücret kirayı, faturaları, interneti, haftalık temizliği, çamaşırhaneyi, sıcak suyu, güvenliği ve kahvaltıyı kapsar.",
            "Öğle ve akşam yemeği aylık ücrete dahil değildir."
        ]},
    },
}

EN = {
    "istanbul-kiz-yurdu": {
        "title": "Girls' Dormitory in Istanbul | Kıvanç Kız Yurdu",
        "description": "A private female-only residence in Avcılar: 45 rooms, private bathrooms, 24/7 security and camera recording, breakfast included.",
        "h1": "Girls' Dormitory in Istanbul",
        "navLabel": "Istanbul Girls' Dormitory",
        "lede": "Kıvanç Kız Yurdu is a private residence in Avcılar, Istanbul, for female students only. The building holds 45 rooms in four sizes; every one has its own bathroom and WC, a television, a mini fridge and a brand-new study set.",
        "intro": [
            {"h": "About the residence", "p": [
                "The residence occupies a single building on Kirazlı Caddesi in Cihangir Mahallesi. Rooms come as singles, doubles, triples and quads; what changes between them is how many people share, and what that does to the monthly rate. The fittings are the same in every room type.",
                "A manager lives in the building. When something goes wrong you reach a person who knows the student by name, not a call centre in another city."
            ]},
        ],
        "close": {"h": "Why Kıvanç Kız Yurdu", "p": [
            "You pay one monthly figure: rent, utilities, fibre internet, weekly room cleaning, the laundry, hot water around the clock and breakfast every morning are all inside it. There is no separate bill at the end of the month.",
            "If you cannot visit in person, we will show you the rooms live over a video call."
        ]},
    },
    "istanbul-ogrenci-yurdu": {
        "title": "Student Residence in Istanbul | Kıvanç Kız Yurdu",
        "description": "A student residence in Avcılar: four room types from ₺15,000 a month, payment by instalments, breakfast and utilities included.",
        "h1": "Student Residence in Istanbul",
        "navLabel": "Istanbul Student Residence",
        "lede": "Kıvanç Kız Yurdu houses female students in Avcılar for the academic year. The standard contract runs September to June, and payment is spread over instalments.",
        "intro": [
            {"h": "What students get", "p": [
                "When you compare student residences, the real question is how much of the monthly figure it actually covers. Here you pay one amount, and utilities, internet, cleaning, laundry, hot water and breakfast are inside it. Nothing arrives separately at the end of the month.",
                "Every room is hotel-style: the bathroom and WC are inside the room, so there is no queue in a corridor. Each room has a television, a mini fridge and a new study desk."
            ]},
        ],
        "close": {"h": "Contract and payment", "p": [
            "The standard contract covers the September to June academic year. Summer stays and shorter stays are considered subject to availability.",
            "Payment is a deposit plus instalments, and a receipt is issued for every payment. Cash is never requested without a document."
        ]},
    },
    "istanbul-kiz-ogrenci-yurdu": {
        "title": "Female Student Residence in Istanbul | Kıvanç Kız Yurdu",
        "description": "A residence for female students only. Card entry, 24/7 camera recording, entry and exit notifications, and management living on site.",
        "h1": "Female Student Residence in Istanbul",
        "navLabel": "Istanbul Female Student Residence",
        "lede": "Kıvanç Kız Yurdu takes female students only. The building is not mixed, entry to the dormitory floors is by card, and visitors are received in the ground-floor lounge.",
        "intro": [
            {"h": "For families", "p": [
                "The hardest part of sending a student to Istanbul from another city is not being able to see what is happening. Every entry and exit is logged, and families who want them receive those notifications over WhatsApp.",
                "A manager lives in the building, and families are welcome during visiting hours."
            ]},
        ],
        "close": {"h": "Daily life", "p": [
            "The building closes at 23:00 on weeknights and 24:00 at weekends. A student who needs to return later arranges it with the manager in advance.",
            "Weekly room cleaning and daily upkeep of the common areas are included in the monthly rate."
        ]},
    },
    "guvenli-kiz-yurdu-istanbul": {
        "title": "Secure Girls' Residence in Istanbul | Kıvanç Kız Yurdu",
        "description": "Staffed reception around the clock, card entry, uninterrupted camera recording in all common areas, and entry and exit notifications to families.",
        "h1": "Secure Girls' Residence in Istanbul",
        "navLabel": "Secure Girls' Residence",
        "lede": "Security is the easiest thing to write in a residence brochure and the hardest to demonstrate. What follows is what is actually in place at Kıvanç Kız Yurdu.",
        "intro": [
            {"h": "How it works", "p": [
                "Reception is staffed day and night, and every entrance has card access. There is no way onto the dormitory floors without a card.",
                "All common areas and entrances are recorded continuously through the day, and the recordings are retained."
            ]},
        ],
        "close": {"h": "Visiting rules", "p": [
            "Families are received in the ground-floor lounge during visiting hours. Visitors do not go up to the dormitory floors.",
            "The building closes at 23:00 on weeknights and 24:00 at weekends."
        ]},
    },
    "universitelere-yakin-kiz-yurdu": {
        "title": "Girls' Residence Near Universities, Istanbul | Kıvanç",
        "description": "From Avcılar by Metrobüs: Gelişim 5 min, Beykent 10 min, Aydın 15 min, Arel 20 min, Biruni 30 min. The stop is a short walk away.",
        "h1": "Girls' Residence Near Universities in Istanbul",
        "navLabel": "Residence Near Universities",
        "lede": "Avcılar's advantage is the Metrobüs line. You walk to the stop from the residence and reach most of Istanbul's private university campuses without changing.",
        "intro": [
            {"h": "Why the location matters", "p": [
                "The time spent on the road every morning matters as much as the monthly rate. The times below are approximate, over the Metrobüs line, in normal traffic.",
                "More than half an hour each way to make a first lecture adds up over an academic year."
            ]},
        ],
        "close": {"h": "Transport at the door", "p": [
            "The Metrobüs, bus and minibus lines are all a short walk from the building.",
            "You can check the times yourself: the address is below and marked on the map."
        ]},
    },
    "kiz-yurdu-fiyatlari": {
        "title": "Girls' Dormitory Prices in Istanbul | Kıvanç Kız Yurdu",
        "description": "2026 rates: single ₺30,000, double ₺24,000, triple ₺18,000, quad ₺15,000 per month. Breakfast and utilities included.",
        "h1": "Girls' Dormitory Prices in Istanbul",
        "navLabel": "Dormitory Prices",
        "lede": "The monthly rates below are per person and vary only by how many students share the room. The fittings are the same in every room type.",
        "intro": [
            {"h": "How the rates are set", "p": [
                "The only difference between the rooms is how many people are in them. The private bathroom, the television, the mini fridge and the study set are in every room type; the quad is not less well equipped because it costs less.",
                "Payment is a deposit plus instalments, and a receipt is issued for every payment."
            ]},
        ],
        "close": {"h": "What the rate does not cover", "p": [
            "The monthly figure covers rent, utilities, internet, weekly cleaning, the laundry, hot water, security and breakfast.",
            "Lunch and dinner are not included in the monthly rate."
        ]},
    },
}

COMMON = {
    "tr": {
        "breadcrumbHome": "Ana sayfa",
        "breadcrumbLabel": "Sayfa yolu",
        "footerTitle": "Kız Yurdu Rehberi",
        "locationH": "Konum",
        "locationP": "Yurt, Cihangir Mahallesi, Kirazlı Caddesi No:18, 34310 Avcılar / İstanbul adresindedir. Bina tek girişlidir ve zili No:18'dedir.",
        "transportH": "Ulaşım",
        "transportP": "Metrobüs, otobüs ve minibüs hatları binaya kısa bir yürüyüş mesafesindedir. Aşağıdaki üniversite süreleri Metrobüs hattı üzerinden hesaplanmıştır.",
        "roomsH": "Odalar",
        "roomsP": "Binada dört büyüklükte 45 oda vardır. Her odada oda içi banyo ve WC, televizyon, mini buzdolabı ve sıfır çalışma takımı bulunur.",
        "facilitiesH": "Olanaklar",
        "universitiesH": "Yakındaki üniversiteler",
        "universitiesP": "Süreler Metrobüs hattı üzerinden, normal trafik koşullarında yaklaşık değerlerdir.",
        "securityH": "Güvenlik",
        "includedH": "Aylık ücrete dahil",
        "ratesH": "Oda tipleri ve aylık ücretler",
        "faqH": "Sık sorulan sorular",
        "ctaH": "Yer durumunu sorun",
        "ctaP": "Adınızı, üniversitenizi ve tercih ettiğiniz oda tipini yazın; kısa sürede dönüş yapalım.",
        "ctaWa": "WhatsApp'tan yazın",
        "ctaForm": "İletişim formu",
        "relatedH": "İlgili sayfalar",
        "tblRoom": "Oda tipi",
        "tblCap": "Kapasite",
        "tblPrice": "Aylık (kişi başı)",
        "tblUni": "Üniversite",
        "tblTime": "Süre",
        "seeRooms": "Bütün odalar ve fiyatlar",
    },
    "en": {
        "breadcrumbHome": "Home",
        "breadcrumbLabel": "Breadcrumb",
        "footerTitle": "Residence Guide",
        "locationH": "Location",
        "locationP": "The residence is at Cihangir Mah., Kirazlı Cad. No:18, 34310 Avcılar / İstanbul. There is one entrance, and the bell is at No:18.",
        "transportH": "Transport",
        "transportP": "Metrobüs, bus and minibus lines are a short walk from the building. The university times below are over the Metrobüs line.",
        "roomsH": "Rooms",
        "roomsP": "The building holds 45 rooms in four sizes. Every room has its own bathroom and WC, a television, a mini fridge and a brand-new study set.",
        "facilitiesH": "Facilities",
        "universitiesH": "Nearby universities",
        "universitiesP": "Times are approximate, over the Metrobüs line, in normal traffic.",
        "securityH": "Security",
        "includedH": "Included in the monthly rate",
        "ratesH": "Room types and monthly rates",
        "faqH": "Frequently asked questions",
        "ctaH": "Ask about availability",
        "ctaP": "Send your name, your university and the room type you want, and we will reply shortly.",
        "ctaWa": "Message on WhatsApp",
        "ctaForm": "Contact form",
        "relatedH": "Related pages",
        "tblRoom": "Room type",
        "tblCap": "Capacity",
        "tblPrice": "Monthly (per person)",
        "tblUni": "University",
        "tblTime": "Time",
        "seeRooms": "All rooms and rates",
    },
}


def main():
    for lang, copy in (("tr", TR), ("en", EN)):
        p = "i18n/%s.json" % lang
        d = json.loads(io.open(p, encoding="utf-8").read(),
                       object_pairs_hook=collections.OrderedDict)
        seo = collections.OrderedDict()
        seo["common"] = collections.OrderedDict(sorted(COMMON[lang].items()))
        for slug in PAGES:
            seo[slug] = copy[slug]
        d["seo"] = seo
        io.open(p, "w", encoding="utf-8").write(
            json.dumps(d, ensure_ascii=False, indent=2) + "\n")
        print("%s: seo copy for %d pages written" % (p, len(PAGES)))


if __name__ == "__main__":
    main()
