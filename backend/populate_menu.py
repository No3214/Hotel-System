import asyncio
import os
import sys

# Append the current directory to sys.path so we can import from database and helpers
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db
from helpers import new_id, utcnow

MENU_CATEGORIES = [
    {"key": "breakfast", "name_tr": "Kahvaltı", "name_en": "Breakfast", "icon": "coffee", "sort_order": 1},
    {"key": "appetizers", "name_tr": "Mezeler", "name_en": "Appetizers", "icon": "salad", "sort_order": 2},
    {"key": "warm_starters", "name_tr": "Ara Sıcaklar & Başlangıçlar", "name_en": "Warm Starters", "icon": "flame", "sort_order": 3},
    {"key": "pizza_sandwich", "name_tr": "Taş Fırın Pizza & Sandviç", "name_en": "Pizza & Sandwich", "icon": "pizza", "sort_order": 4},
    {"key": "cheese", "name_tr": "Peynir Tabakları", "name_en": "Cheese Plates", "icon": "cheese", "sort_order": 5},
    {"key": "main_courses", "name_tr": "Ana Yemekler", "name_en": "Main Courses", "icon": "utensils", "sort_order": 6},
    {"key": "desserts", "name_tr": "Tatlılar", "name_en": "Desserts", "icon": "cake", "sort_order": 7},
    {"key": "beverages", "name_tr": "İçecekler", "name_en": "Beverages", "icon": "wine", "sort_order": 8},
]

MENU_ITEMS = [
    # Kahvaltı
    {"category": "breakfast", "name": "Gurme Serpme Kahvaltı", "desc": "Sahanda tereyağlı sucuklu yumurta, avokado, Hatay kırma zeytin, çeşitli peynirler, ceviz, mevsim meyveleri, jalapenolu labne, acılı ezme, taze pişi, köy ekmeği, bal, kaymak ve ev yapımı reçeller. (G)(S)(Y)(F)", "price_try": 750, "sort_order": 1},
    {"category": "breakfast", "name": "Pişi Kahvaltı Tabağı", "desc": "2 Adet sıcak pişi, beyaz ve tulum peynir, zeytinler, acılı ezme, reçel, domates ve salatalık. (G)(S)", "price_try": 750, "sort_order": 2},
    {"category": "breakfast", "name": "Mıhlama", "desc": "Karadeniz usulü, mısır unu ve eritme peynir. (G)(S)", "price_try": 450, "sort_order": 3},
    {"category": "breakfast", "name": "Sahanda Sucuklu Yumurta", "desc": "(Y)", "price_try": 400, "sort_order": 4},
    {"category": "breakfast", "name": "Patates Kızartması", "desc": "Baharatlı veya sade.", "price_try": 350, "sort_order": 5},
    {"category": "breakfast", "name": "Fransız Tereyağlı Kruvasan (2 Adet)", "desc": "(G)(S)(F)", "price_try": 400, "sort_order": 6},
    {"category": "breakfast", "name": "Fesleğenli Domatesli Ciabatta (4 adet)", "desc": "(G)(S)", "price_try": 300, "sort_order": 7},
    {"category": "breakfast", "name": "Kare Rustik Ekmek", "desc": "(G)", "price_try": 300, "sort_order": 8},
    {"category": "breakfast", "name": "Omlet", "desc": "(sade / peynirli) (Y)(S)", "price_try": 300, "sort_order": 9},
    {"category": "breakfast", "name": "Sahanda Menemen", "desc": "(Y)", "price_try": 350, "sort_order": 10},
    {"category": "breakfast", "name": "Sahanda Peynirli Yumurta", "desc": "(Y)(S)", "price_try": 300, "sort_order": 11},
    {"category": "breakfast", "name": "Sigara Böreği (4 adet)", "desc": "(G)(S)", "price_try": 300, "sort_order": 12},
    {"category": "breakfast", "name": "Pişi (adet)", "desc": "(G)", "price_try": 100, "sort_order": 13},
    {"category": "breakfast", "name": "Dulce De Leche", "desc": "(S)", "price_try": 100, "sort_order": 14},
    {"category": "breakfast", "name": "Çikolata Kreması", "desc": "(S)(F)", "price_try": 100, "sort_order": 15},

    # Mezeler
    {"category": "appetizers", "name": "Konağın Meze Tabağı (2 kişilik — 5 çeşit)", "desc": "Atom, kuru cacık, deniz börülcesi, yaprak sarma, havuç tarator. Rustik ekmek eşliğinde. 2 kadeh Paşaeli seçkiniz ile taçlandırılır. (G)(S)(SU)", "price_try": 2400, "sort_order": 1},
    {"category": "appetizers", "name": "Tereyağlı Pastırmalı Antakya Humus", "desc": "Nohut-tahin humusu, üzerine tereyağında kızdırılmış pastırma. (SU)", "price_try": 450, "sort_order": 2},
    {"category": "appetizers", "name": "Avokadolu Kapya Biber", "desc": "Közlenmiş kapya biber ve avokado.", "price_try": 350, "sort_order": 3},
    {"category": "appetizers", "name": "Zeytinyağlı Vişneli Yaprak Sarma", "desc": "Asma yaprağında pirinç dolma, vişnenin ekşi-tatlı dengesiyle.", "price_try": 350, "sort_order": 4},
    {"category": "appetizers", "name": "Tek Porsiyon Mezeler", "desc": "Acılı Atom, Deniz Börülcesi, Haydari, Kuru Cacık, La Pena (Acılı), Yoğurtlu Havuç Tarator, Yoğurtlu Patlıcan, Zeytinyağlı Domatesli Humus.", "price_try": 300, "sort_order": 5},

    # Ara Sıcaklar & Başlangıçlar
    {"category": "warm_starters", "name": "Somon Havyarı", "desc": "(B)", "price_try": 3000, "sort_order": 1},
    {"category": "warm_starters", "name": "Kaşarlı Mantar", "desc": "(S)", "price_try": 450, "sort_order": 2},
    {"category": "warm_starters", "name": "Rustik Ekmek Üstü Füme Somon", "desc": "(G)(B)", "price_try": 500, "sort_order": 3},
    {"category": "warm_starters", "name": "Kızarmış Tavuk & Baharatlı Patates", "desc": "(G)", "price_try": 650, "sort_order": 4},
    {"category": "warm_starters", "name": "Roka Salatası", "desc": "Roka, beyaz peynir, kuru incir, ceviz, balsamik glaze. (S)(F)", "price_try": 400, "sort_order": 5},
    {"category": "warm_starters", "name": "Başlangıç Tabağı (2 kişilik)", "desc": "Zeytin, zahter, zeytinyağı, ciabatta. (G)(SU)", "price_try": 350, "sort_order": 6},
    {"category": "warm_starters", "name": "Antakya Usulü İçli Köfte (adet)", "desc": "(G)", "price_try": 200, "sort_order": 7},
    {"category": "warm_starters", "name": "Paçanga Böreği (adet)", "desc": "(G)(S)", "price_try": 200, "sort_order": 8},
    {"category": "warm_starters", "name": "Tereyağlı Jumbo Karides", "desc": "(G)(B)", "price_try": 850, "sort_order": 9},
    {"category": "warm_starters", "name": "Kalamar", "desc": "(G)(B)", "price_try": 850, "sort_order": 10},

    # Taş Fırın Pizza & Sandviç
    {"category": "pizza_sandwich", "name": "Füme Dana Kaburga Pizza", "desc": "(G)(S)", "price_try": 1000, "sort_order": 1},
    {"category": "pizza_sandwich", "name": "Hindi Füme Pizza", "desc": "(G)(S)", "price_try": 900, "sort_order": 2},
    {"category": "pizza_sandwich", "name": "Taş Fırın Karışık Pizza", "desc": "(G)(S)", "price_try": 750, "sort_order": 3},
    {"category": "pizza_sandwich", "name": "Taş Fırın Margarita Pizza", "desc": "(G)(S)", "price_try": 700, "sort_order": 4},
    {"category": "pizza_sandwich", "name": "Dana Kaburga Füme Etli Sandviç", "desc": "(G)", "price_try": 750, "sort_order": 5},
    {"category": "pizza_sandwich", "name": "Füme Somonlu Sandviç", "desc": "(G)(S)(B)", "price_try": 750, "sort_order": 6},
    {"category": "pizza_sandwich", "name": "Sıcak Baget Sandviç", "desc": "(G)(S)", "price_try": 400, "sort_order": 7},
    {"category": "pizza_sandwich", "name": "Gurme Rustik Pesto Sandviç", "desc": "(G)(S)", "price_try": 600, "sort_order": 8},

    # Peynir Tabakları
    {"category": "cheese", "name": "Rakı Eşlikçisi Peynir Tabağı", "desc": "(S)", "price_try": 800, "sort_order": 1},
    {"category": "cheese", "name": "Türk Yerli Peynir & Şarap Tabağı", "desc": "(S)", "price_try": 1000, "sort_order": 2},

    # Ana Yemekler
    {"category": "main_courses", "name": "Dallas Steak", "desc": "Altın rengi patates püresi, ızgara mısır ve havuç eşliğinde.", "price_try": 3500, "sort_order": 1},
    {"category": "main_courses", "name": "Lokum Bonfile", "desc": "Patates püresi tabanında, ızgara mısır ve havuç, kavrulmuş file badem. (F)", "price_try": 1500, "sort_order": 2},
    {"category": "main_courses", "name": "Izgara Pirzola", "desc": "Patates püresi, kavrulmuş file badem. (F)", "price_try": 1200, "sort_order": 3},
    {"category": "main_courses", "name": "Konak Saç Kavurma", "desc": "Patates püresi tabanı ve kavrulmuş file badem. (F)", "price_try": 1000, "sort_order": 4},
    {"category": "main_courses", "name": "Konak Köfte", "desc": "Patates püresi ve kavrulmuş file badem. (F)", "price_try": 800, "sort_order": 5},

    # Tatlılar
    {"category": "desserts", "name": "Antep Fıstıklı Katmer", "desc": "Vanilyalı Maraş dondurma eşliğinde. (G)(S)(F)", "price_try": 400, "sort_order": 1},
    {"category": "desserts", "name": "Künefe", "desc": "Fıstık ve kaymak eşliğinde. (G)(S)(F)", "price_try": 400, "sort_order": 2},
    {"category": "desserts", "name": "Churros", "desc": "Çikolata sosu ve pudra şekeri ile. (G)", "price_try": 400, "sort_order": 3},
    {"category": "desserts", "name": "Çikolatalı Mini Berliner (2 adet)", "desc": "(G)(S)", "price_try": 300, "sort_order": 4},
    {"category": "desserts", "name": "Vanilyalı Maraş Dondurma (2 top)", "desc": "(S)", "price_try": 300, "sort_order": 5},
    {"category": "desserts", "name": "Tatlı & Kahve Keyfi", "desc": "Herhangi bir tatlı + Türk Kahvesi.", "price_try": 500, "sort_order": 6},

    # İçecekler (Simplified due to ranges)
    {"category": "beverages", "name": "Şarap Tadımları (Beyaz/Kırmızı)", "desc": "2 kadeh + mini peynir tabağı", "price_try": 1600, "sort_order": 1},
    {"category": "beverages", "name": "Wines (Paşaeli Seçkisi) - Kadeh", "desc": "600 TL - 800 TL arası. Lütfen garsona danışın.", "price_try": 700, "sort_order": 2},
    {"category": "beverages", "name": "Wines (Paşaeli Seçkisi) - Şişe", "desc": "2.200 TL - 3.000 TL arası. Lütfen garsona danışın.", "price_try": 2500, "sort_order": 3},
    {"category": "beverages", "name": "Rakı (Beylerbeyi Göbek / Efe Gold) - Tek", "desc": "", "price_try": 500, "sort_order": 4},
    {"category": "beverages", "name": "Rakı (Beylerbeyi Göbek / Efe Gold) - 35cl", "desc": "2.150 TL - 2.200 TL arası.", "price_try": 2150, "sort_order": 5},
    {"category": "beverages", "name": "Rakı (Beylerbeyi Göbek / Efe Gold) - 70cl", "desc": "3.400 TL", "price_try": 3400, "sort_order": 6},
    {"category": "beverages", "name": "Rakı (Beylerbeyi Göbek / Efe Gold) - 100cl", "desc": "3.850 TL", "price_try": 3850, "sort_order": 7},
    {"category": "beverages", "name": "Kokteyl (Kuzu Kulağı/Wild Berry)", "desc": "", "price_try": 750, "sort_order": 8},
    {"category": "beverages", "name": "Bira", "desc": "250 TL - 275 TL arası.", "price_try": 250, "sort_order": 9},
    {"category": "beverages", "name": "Viskiler - Tek", "desc": "500 TL - 800 TL arası.", "price_try": 600, "sort_order": 10},
    {"category": "beverages", "name": "Viskiler - 70cl", "desc": "4.300 TL - 6.500 TL arası.", "price_try": 5000, "sort_order": 11},
    {"category": "beverages", "name": "Çay", "desc": "", "price_try": 50, "sort_order": 12},
    {"category": "beverages", "name": "Kahveler", "desc": "Türk Kahvesi, Espresso, vb.", "price_try": 150, "sort_order": 13},
    {"category": "beverages", "name": "Soda/Gazoz", "desc": "", "price_try": 100, "sort_order": 14},
    {"category": "beverages", "name": "Kola/Fanta/Ice Tea", "desc": "", "price_try": 150, "sort_order": 15},
    {"category": "beverages", "name": "Ice Latte/Americano", "desc": "", "price_try": 200, "sort_order": 16},
    {"category": "beverages", "name": "Taze Sıkma Portakal Suyu", "desc": "", "price_try": 250, "sort_order": 17},
]

async def populate():
    print("Clearing old menu data...")
    await db.menu_categories.delete_many({})
    await db.menu_items.delete_many({})

    print("Inserting menu categories...")
    for cat in MENU_CATEGORIES:
        cat_doc = {
            "id": new_id(),
            **cat,
            "is_active": True,
            "created_at": utcnow()
        }
        await db.menu_categories.insert_one(cat_doc)
        print(f"  Inserted category: {cat['name_tr']}")

    print("Inserting menu items...")
    for item in MENU_ITEMS:
        item_doc = {
            "id": new_id(),
            **item,
            "is_available": True,
            "created_at": utcnow(),
            "updated_at": utcnow()
        }
        await db.menu_items.insert_one(item_doc)
        print(f"  Inserted item: {item['name']}")

    print("Verification data:")
    cat_count = await db.menu_categories.count_documents({})
    item_count = await db.menu_items.count_documents({})
    print(f"Total Categories: {cat_count}")
    print(f"Total Menu Items: {item_count}")
    print("DONE!")

if __name__ == "__main__":
    asyncio.run(populate())
