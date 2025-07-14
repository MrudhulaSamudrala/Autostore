#!/usr/bin/env python3
"""
Add Products to SQLite Database
This script adds your 216 products to the SQLite database.
"""

import sqlite3
import os

def add_products_to_sqlite():
    """Add products to SQLite database"""
    
    # Connect to SQLite database
    conn = sqlite3.connect("autostore.db")
    cursor = conn.cursor()
    
    print("🔄 Adding products to SQLite database...")
    
    # Sample product data - REPLACE WITH YOUR 216 PRODUCTS
    products_data = [
        # Format: (name, price, quantity, category, image_url, bin_id)
        ('Drools Absolute Calcium Bone Dog Supplement - 40 Pcs', 127, 423, 'Pet Supplies', 'http://localhost:8000/static/p1.png', 1), 
        ('Pedigree Adult Dog Dry Food - Vegetable & Chicken (1.2 kg)', 128, 313, 'Pet Supplies', 'http://localhost:8000/static/p2.png', 2), 
        ('Pedigree Adult Dog Wet Food -Grilled Liver Chunks Flavour in Gravy with Vegetables (70 g)', 129, 49, 'Pet Supplies', 'http://localhost:8000/static/p3.png', 3), 
        ('PurePet Chew Bone (260 g)', 130, 205, 'Pet Supplies', 'http://localhost:8000/static/p4.png', 4), 
        ('Purina Friskies Surfin Favourites Adult Dry Cat Food - 1 kg', 131, 346, 'Pet Supplies', 'http://localhost:8000/static/p5.png', 5), 
        ('PurePet Lickable Real Chicken Creamy Cat Treat - 1 pack (5 x 15 g)', 132, 80, 'Pet Supplies', 'http://localhost:8000/static/p6.png', 6), 
        ('PurePet Lickable Tuna & Bonito Creamy Cat Treat - 1 pack (5 x 15 g)', 133, 80, 'Pet Supplies', 'http://localhost:8000/static/p7.png', 7), 
        ('MoePuppy Anti-Tick Pet Spray (100 ml)', 134, 339, 'Pet Supplies', 'http://localhost:8000/static/p8.png', 8), 
        ('Nootie Pet Wipes (Large) - 1 pack (100 pieces)', 135, 109, 'Pet Supplies', 'http://localhost:8000/static/p9.png', 9), 
        ('Himalaya Erina Puppy Pet Shampoo & Conditioner (200 ml)', 136, 294, 'Pet Supplies', 'http://localhost:8000/static/p10.png', 10), 
        ('Zoivane Pets Bathing Pet Brush (Blue)', 137, 198, 'Pet Supplies', 'http://localhost:8000/static/p11.png', 11), 
        ('Mutt of Course Scooby Dooby Doo Printed Dog Collar (Small)', 138, 599, 'Pet Supplies', 'http://localhost:8000/static/p12.png', 12), 
        ('Mutt of Course I Only Like Hoomans Dog Leash (L)', 139, 699, 'Pet Supplies', 'http://localhost:8000/static/p13.png', 13), 
        ('Pet Food Water Bowls Cat Bowls,Small Dogs', 140, 499, 'Pet Supplies', 'http://localhost:8000/static/p14.png', 14), 
        ('Vibrant Life Gravity Pet Feeder, Blue, Large, 10 Pound Capacity', 141, 1599, 'Pet Supplies', 'http://localhost:8000/static/p15.png', 15), 
        ('Mutt of Course Jungle Vest Large Dog Harness (Dark Blue)', 142, 1799, 'Pet Supplies', 'http://localhost:8000/static/p16.png', 16),
        ('Comfort After Wash Fabric Conditioner (Lily Fresh) - 860 ml', 57, 205, 'Household Essentials', 'http://localhost:8000/static/comfort.png', 17), 
        ('Lizol Disinfectant Surface & Floor Cleaner 1 l' , 58 ,234, 'Household Essentials' , 'http://localhost:8000/static/surface.png', 18),
        ('Harpic Disinfectant Liquid Bathroom Cleaner (Lemon - 500 ml)' , 59 , 115 , 'Household Essentials' , 'http://localhost:8000/harpic.png', 19),
        ('Ultra Wrap Bio-Degradable Cling Wrap' , 60 , 89 , 'Household Essentials' , 'http://localhost:8000/static/wrap.png', 20),
        ('Premier Silky Tissue Paper Napkins (1 Ply)' , 61 , 59 , 'Household Essentials' , 'http://localhost:8000/static/tissues.png', 21),
        ('Corepac Doodle Print Disposable Glass (250 ml) 1 pack (25 pieces)' , 62 , 89 , 'Household Essentials' , 'http://localhost:8000/static/glass.png', 22),
        ('Matchbox by Homelites 5 pcs (Small Box), 5 units' , 63 , 10 , 'Household Essentials' , 'http://localhost:8000/static/matchbox.png', 23),
        ('Camphor & Sesame Pooja Oil by Shubhkart - 900 ml' , 64 , 183 , 'Household Essentials' , 'http://localhost:8000/static/poojaoil.png', 24),
        ('Mangaldeep Sambrani Dhoop 15 units' , 65 , 15 , 'Household Essentials' , 'http://localhost:8000/static/dhup.png', 25),
        ('Mangaldeep Chandan 3in1 Incense Sticks / Agarbatti 244 g' , 66 , 118, 'Household Essentials' , 'http://localhost:8000/static/sticks.png', 26),
        ('Hit Spray Flies & Mosquito Repellent Spray 400 ml' , 67 , 180 , 'Household Essentials' , 'http://localhost:8000/static/hit.png', 27),
        ('Good Knight Flash Mosquito Killer Machine with 2 Refills - Combo Pack' , 68 , 171 , 'Household Essentials' , 'http://localhost:8000/static/goodnight.png', 28),
        ('Dettol Original Hand Wash - 200 ml' , 69 , 76 , 'Household Essentials' , 'http://localhost:8000/static/handwash.png', 29),
        ('Cosco Aero 500 Nylon Shuttlecock (Yellow) 1 pack (6 pieces)' , 70 , 349 , 'Household Essentials' , 'http://localhost:8000/static/cock.png', 30),
        ('Lifelong Adjustable Hand Gripper Strengthener (Black)' , 71 , 269 , 'Household Essentials' , 'http://localhost:8000/static/gripper.png', 31),
        ('Homestrap Non-Woven 24 Compartments Wardrobe Storage Organiser for Socks (Grey)' , 72 , 201 , 'Household Essentials' , 'http://localhost:8000/static/box.png', 32),
        ('Boldfit Spider Gym Shaker Bottle - 500 ml (Black)' , 73 , 349 , 'Household Essentials' , 'http://localhost:8000/static/bottle.png', 33),
        ('Boldfit Skipping Rope (Black)' , 74 , 120 , 'Household Essentials' , 'http://localhost:8000/static/rope.png', 34),
        ('Hide & Seek Chocolate Chip Cookies (200 g)' , 75 , 50 , 'Snacks & Beverages' , 'http://localhost:8000/static/hideandseek.png', 35),
        ('Karachi Bakery Osmania Bakery Cookies (400 g)' , 76 , 180 , 'Snacks & Beverages' , 'http://localhost:8000/static/osmania.png', 36),
        ('RiteBite Max Protein No Maida 7 Grains Choco Almond 12 g Protein Cookies' , 77 , 59 , 'Snacks & Beverages' , 'http://localhost:8000/static/choco.png', 37),
        ('Lays American Style Cream & Onion Potato Chips' , 78 , 30 , 'Snacks & Beverages' , 'http://localhost:8000/static/lays.png', 38),
        ('Modern White Bread (400 g)' , 79 , 55 , 'Grocery' , 'http://localhost:8000/static/bread.png', 39),
        ('Bingo Mad Angles Achaari Masti Crisps - Pack of 3' , 80 , 58 , 'Snacks & Beverages' , 'http://localhost:8000/static/mad.png', 40),
        ('Haldirams Nagpur Aloo Bhujia - 200 g' , 81 , 55 , 'Snacks & Beverages' , 'http://localhost:8000/static/sev.png', 41),
        ('Cornitos Crisps Peri Peri Nachos & Salsa Dip' , 82 , 78 , 'Snacks & Beverages' , 'http://localhost:8000/static/nacho.png', 42),
        ('Cadbury Dairy Milk Silk Ganache Small Chocolate Bar' , 83 , 100 , 'Snacks & Beverages' , 'http://localhost:8000/static/chocobar.png', 43),
        ('Ferrero Rocher Chocolate Gift Pack (4 pieces)' , 84 , 169 , 'Snacks & Beverages' , 'http://localhost:8000/static/chocoferro.png', 44),
        ('Chupa Chups Sour Bites Mixed Fruit Candy' , 85 , 35 , 'Snacks & Beverages' , 'http://localhost:8000/static/cupa.png', 45),
        ('Amul Taaza Homogenised Toned Milk 1 ltr' , 86 , 74 , 'Snacks & Beverages' , 'http://localhost:8000/static/milk.png', 46),
        ('Brooke Bond Taj Mahal Rich & Flavourful Tea (250 g)' , 87 , 200 , 'Snacks & Beverages' , 'http://localhost:8000/static/tajma.png', 47),
        ('Nescafe Sunrise Instant Coffee Powder - Rich Aroma, Coffee-Chicory Mix (45 g)' , 88 , 180 , 'Snacks & Beverages' , 'http://localhost:8000/static/coffe.png', 48),
        ('Cadbury Hot Chocolate Drink Powder Mix (200 g)' , 89 , 220 , 'Snacks & Beverages' , 'http://localhost:8000/static/hotchoco.png', 49),
        ('Lipton Honey Lemon Green Tea Bags - 25 pieces' , 90 , 153 , 'Snacks & Beverages' , 'http://localhost:8000/static/lemontea.png', 50),
        ('Red Bull Energy Drink (250 ml)' , 91 , 125 , 'Snacks & Beverages' , 'http://localhost:8000/static/eng.png', 51),
        ('Sprite Lemon-Lime Zero Sugar Soft Drink (330 ml)' , 92 , 189 , 'Snacks & Beverages' , 'http://localhost:8000/static/sprite.png', 52),
        ('Dettol Original Alcohol Based Hand Sanitizer - 200 ml' , 93 , 125 , 'Pharma & Wellness' , 'http://localhost:8000/static/sanitizer.png', 53),
        ('QUARANT Disposable Face Mask (Blue) 1 pack - 50 pieces' , 94 , 279 , 'Pharma & Wellness' , 'http://localhost:8000/static/mask.png', 54),
        ('Eno Lemon Antacid 30 g' , 95 , 63 , 'Pharma & Wellness' , 'http://localhost:8000/static/eno.png', 55),
        ('ORSL Apple Drink with Electrolyte - Pack of 6' , 96 , 214 , 'Pharma & Wellness' , 'http://localhost:8000/static/ors.png', 56),
        ('Vicks VapoRub Chest Rub & Balm (Relieve Cold, Cough & Blocked Nose) - 25 ml' , 97 , 109 , 'Pharma & Wellness' , 'http://localhost:8000/static/vicks.png', 57),
        ('Volini Activ Pain Relief Spray (60 g)' , 98 , 208 , 'Pharma & Wellness' , 'http://localhost:8000/static/volini.png', 58),
        ('Wellness Surgicals Crepe Bandage (6 cm X 4 m)' , 99 , 140 , 'Pharma & Wellness' , 'http://localhost:8000/static/bandage.png', 59),
        ('Dettol Antiseptic Liquid - 250 ml' , 100 , 170 , 'Pharma & Wellness' , 'http://localhost:8000/static/dettol.png', 60),
        ('Plush Preg-Oh Basic Pregnancy Test Kit - 1 pieces' , 101 , 67 , 'Pharma & Wellness' , 'http://localhost:8000/static/preg.png', 61),
        ('Kelloggs Corn Flakes with Immuno Nutrients (250 g)' , 102 , 125 , 'Packaged Foods' , 'http://localhost:8000/static/cornflaks.png', 62),
        ('McCain Aloo Tikki (Frozen) - 400 g' , 103 , 102 , 'Packaged Foods' , 'http://localhost:8000/static/tikki.png', 63),
        ('Switz Puff Dough Paratha (Frozen) 400 g (5 pieces)' , 104 , 105 , 'Packaged Foods' , 'http://localhost:8000/static/paratha.png', 64),
        ('Wow! Momo Veg Darjeeling Momos (Frozen) 1 pack (10 pieces)' , 105 , 99 , 'Packaged Foods' , 'http://localhost:8000/static/momo.png', 65),
        ('Prasuma Chicken Tikka Pizza Minis 180 g (2 pieces)' , 106 , 150 , 'Packaged Foods' , 'http://localhost:8000/static/pizza.png', 66),
        ('Maggi Pazzta Cheese Macaroni Instant Pasta (75 g)' , 107 , 35 , 'Packaged Foods' , 'http://localhost:8000/static/pasta.png', 67),
        ('MTR Dosa Breakfast Mix (500 g)' , 108 , 140 , 'Packaged Foods' , 'http://localhost:8000/static/dosa.png', 68),
        ('Aashirvaad Instant Khatta Meetha Poha Ready to Eat (60 g)' , 109 , 26 , 'Packaged Foods' , 'http://localhost:8000/static/poha.png', 69),
        ('Snapin Red Chilli Flakes Seasoning (35 g)' , 110 , 84 , 'Packaged Foods' , 'http://localhost:8000/static/cflaskes.png', 70),
        ('Snapin Oregano (20 g)' , 111 , 93 , 'Packaged Foods' , 'http://localhost:8000/static/oflakes.png', 71),
        ('ITC Master Chef Chicken Popcorn (500 g)' , 112 , 311 , 'Packaged Foods' , 'http://localhost:8000/static/chicken.png', 72),
        ('The Little Farm Co. Mango Pickle (250 g)' , 113 , 215 , 'Packaged Foods' , 'http://localhost:8000/static/mp.png', 73),
        ('Priya Tomato with Garlic Pickle (300 g)' , 114 , 110 , 'Packaged Foods' , 'http://localhost:8000/static/tp.png', 74),
        ('Act II Butter Popcorn - Ready to Eat - 40 g' , 115 , 25 , 'Packaged Foods' , 'http://localhost:8000/static/ipopcorn.png', 75),
        ('4700BC Lemon Pepper Sweet Corn (80 g)' , 116 , 80 , 'Packaged Foods' , 'http://localhost:8000/static/sweetcorn.png', 76),
        ('MamyPoko Pants Standard Diaper (L, 9-14 kg),1 pack (44 pieces)' , 117 , 413 , 'Baby Care' , 'http://localhost:8000/static/bc1.png', 77),
        ('Johnsons Blossoms Baby Soap (75 g)' , 118 , 80 , 'Baby Care' , 'http://localhost:8000/static/bc2.png', 78),
        ('Himalaya Gentle Baby Shampoo (200 ml)' , 119 , 183 , 'Baby Care' , 'http://localhost:8000/static/bc3.png', 79),
        ('Pampers Baby Wipes with Aloe 1 pack (72 wipes)' , 120 , 171 , 'Baby Care' , 'http://localhost:8000/static/bc4.png', 80),
        ('Nestle NAN PRO Stage 1 Infant Formula' , 121 , 93 , 'Baby Care' , 'http://localhost:8000/static/bc5.png', 81),
        ('Himalaya Baby Powder (400 g)' , 122 , 239 , 'Baby Care' , 'http://localhost:8000/static/bc6.png', 82),
        ('Himalaya Baby Lotion (200 ml)' , 123 , 174 , 'Baby Care' , 'http://localhost:8000/static/bc8.png', 83),
        ('LuvLap Baby Feeding Bottle (250 ml, Blue)' , 124 , 170 , 'Baby Care' , 'http://localhost:8000/static/bc7.png', 84),
        ('Eggoz Nutrition Protein Rich White Eggs (6 pieces)' , 124 , 71 , 'Grocery' , 'http://localhost:8000/static/egg.png', 85),
        ('Rexona Aloe Vera Deodorant Roll on (50 ml)', 9, 105, 'Personal Care', 'http://localhost:8000/static/Roll on 105.png', 86), 
        ('Denver Pride Hamilton Mens Deodorant' , 10 ,214, 'Personal Care' , 'http://localhost:8000/static/deodarnt214.png', 87),
        ('Stayfree Sanitary Pads' , 11 , 84 , 'Personal Care' , 'http://localhost:8000/static/Sanitary pads 84.png', 88),
        ('Indica Easy Shampoo Hair Color' , 12 , 34 , 'Personal Care' , 'http://localhost:8000/static/Hair color 34.png', 89),
        ('Gillette Venus Hair Removal (418 g)' , 13 , 256 ,'Personal Care' , 'http://localhost:8000/static/Hair Removal 99.png', 90),
        ('Bombay Shaving Company After Shave Lotion' , 14 , 225 ,'Personal Care' , 'http://localhost:8000/static/aftershave 256.png', 91),
        ('Gillette Sensitive Shaving Foam (418 g)' , 15 , 256 ,'Personal Care' , 'http://localhost:8000/static/Shaving Cream 256.png', 92),
        ('Pears Pure And Gentle Body Wash (750 ml)' , 16 , 283 ,'Personal Care' , 'http://localhost:8000/static/Body wash 283.png', 93),
        ('Equate Blue Mint Antiseptic Mouthwash' , 17 , 294 ,'Personal Care' , 'http://localhost:8000/static/Mouthwash.png', 94),
        ('Colgate Cavity Protection Toothpaste' , 18 , 105 ,'Personal Care' , 'http://localhost:8000/static/Tooth paste 1.png', 95),
        ('Oral-B Advanced Clean Toothbrushes' , 19 , 135 ,'Personal Care' , 'http://localhost:8000/static/Tooth Brush 10.png', 96),
        ('Tree Hut Moroccan Rose Shea Sugar Body Scrub' , 20 , 382 ,'Personal Care' , 'http://localhost:8000/static/Body Scrub8.png', 97),
        ('Neutrogena Ultra Sheer Sunscreen Spray (80 ml)' , 21 , 476 ,'Personal Care' , 'http://localhost:8000/static/Sunscreen8.png', 98),
        ('CeraVe PM Lotion Face Moisturizer' , 22 , 350 ,'Personal Care' , 'http://localhost:8000/static/Moisturize.png', 99),
        ('Duke Cannon Daily Face Wash (100 ml)' , 23 , 276 ,'Personal Care' , 'http://localhost:8000/static/Face wash.png', 100),
        ('LOreal Paris Extraordinary Oil Hair Serum (100 ml)' , 24 , 395 ,'Personal Care' , 'http://localhost:8000/static/Hair Serum.png', 101),
        ('Parachute Advansed Aloe Vera Hair Oil (250 ml)' , 25 , 115,'Personal Care' , 'http://localhost:8000/static/Hairoil.png', 102),
        ('Pantene Advanced Hair Fall Solution Conditioner (80 ml)' , 26 , 98 ,'Personal Care' , 'http://localhost:8000/static/Conditioner.png', 103),
        ('Ponds Talcum Powder (400 gm)' , 27 ,  374 ,'Personal Care' , 'http://localhost:8000/static/ponds.png', 104),
        # Add more products to reach 216...
    ]
    
    # Insert products
    for i, (name, price, quantity, category, image_url, bin_id) in enumerate(products_data, 1):
        try:
            cursor.execute("""
                INSERT INTO products (name, price, quantity, bin_id, image_url, category, sale_count)
                VALUES (?, ?, ?, ?, ?, ?, 0)
            """, (name, price, quantity, bin_id, image_url, category))
            
            # Update bin to have this product
            cursor.execute("""
                UPDATE bins SET product_id = ? WHERE id = ?
            """, (i, bin_id))
            
            print(f"   ✅ Added product {i}: {name}")
            
        except Exception as e:
            print(f"   ❌ Error adding product {i} ({name}): {e}")
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"✅ Added {len(products_data)} products to SQLite database")
    print(f"📊 Total products added: {len(products_data)}")
    print("\n🚀 Next steps:")
    print("   1. Start backend: uvicorn main:app --reload")
    print("   2. Start dashboard: cd autostore-dashboard && npm start")
    print("   3. Start frontend: cd autostore-frontend && npm start")

if __name__ == "__main__":
    add_products_to_sqlite() 