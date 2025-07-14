#!/usr/bin/env python3
"""
Manual Product Insertion Script
Run this to add your 216 products with URLs to the database.
"""

import psycopg2
import json

def add_products_manually():
    """Add products manually to the database"""
    
    # Database connection
    conn = psycopg2.connect(
        user="postgres",
        password="post",
        host="localhost",
        port="5432",
        database="autostore"
    )
    cursor = conn.cursor()
    
    print("🔄 Adding products to database...")
    
    # Sample product data - REPLACE WITH YOUR 216 PRODUCTS
    products_data = [
        # Format: (name, price, quantity, bin_id, image_url, category)
    ('Rexona Aloe Vera Deodorant Roll on (50 ml)', 9, 105, 'Personal Care', 'http://localhost:8000/static/Roll on 105.png'), 
	('Denver Pride Hamilton Mens Deodorant' , 10 ,214, 'Personal Care' , 'http://localhost:8000/static/deodarnt214.png'),
	('Stayfree Sanitary Pads' , 11 , 84 , 'Personal Care' , 'http://localhost:8000/static/Sanitary pads 84.png'),
	('Indica Easy Shampoo Hair Color' , 12 , 34 , 'Personal Care' , 'http://localhost:8000/static/Hair color 34.png'),
	('Gillette Venus Hair Removal (418 g)' , 13 , 256 ,'Personal Care' , 'http://localhost:8000/static/Hair Removal 99.png'),
	('Bombay Shaving Company After Shave Lotion' , 14 , 225 ,'Personal Care' , 'http://localhost:8000/static/aftershave 256.png'),
	('Gillette Sensitive Shaving Foam (418 g)' , 15 , 256 ,'Personal Care' , 'http://localhost:8000/static/Shaving Cream 256.png'),
	('Pears Pure And Gentle Body Wash (750 ml)' , 16 , 283 ,'Personal Care' , 'http://localhost:8000/static/Body wash 283.png'),
	('Equate Blue Mint Antiseptic Mouthwash' , 17 , 294 ,'Personal Care' , 'http://localhost:8000/static/Mouthwash.png'),
	('Colgate Cavity Protection Toothpaste' , 18 , 105 ,'Personal Care' , 'http://localhost:8000/static/Tooth paste 1.png'),
	('Oral-B Advanced Clean Toothbrushes' , 19 , 135 ,'Personal Care' , 'http://localhost:8000/static/Tooth Brush 10.png'),
	('Tree Hut Moroccan Rose Shea Sugar Body Scrub' , 20 , 382 ,'Personal Care' , 'http://localhost:8000/static/Body Scrub8.png'),
	('Neutrogena Ultra Sheer Sunscreen Spray (80 ml)' , 21 , 476 ,'Personal Care' , 'http://localhost:8000/static/Sunscreen8.png'),
	('CeraVe PM Lotion Face Moisturizer' , 22 , 350 ,'Personal Care' , 'http://localhost:8000/static/Moisturize.png'),
	('Duke Cannon Daily Face Wash (100 ml)' , 23 , 276 ,'Personal Care' , 'http://localhost:8000/static/Face wash.png'),
	('LOreal Paris Extraordinary Oil Hair Serum (100 ml)' , 24 , 395 ,'Personal Care' , 'http://localhost:8000/static/Hair Serum.png'),
	('Parachute Advansed Aloe Vera Hair Oil (250 ml)' , 25 , 115,'Personal Care' , 'http://localhost:8000/static/Hairoil.png'),
	('Pantene Advanced Hair Fall Solution Conditioner (80 ml)' , 26 , 98 ,'Personal Care' , 'http://localhost:8000/static/Conditioner.png'),
	('Ponds Talcum Powder (400 gm)' , 27 ,  374 ,'Personal Care' , 'http://localhost:8000/static/ponds.png');
    ('Comfort After Wash Fabric Conditioner (Lily Fresh) - 860 ml', 57, 205, 'Household Essentials', 'http://localhost:8000/static/comfort.png'), 
	('Lizol Disinfectant Surface & Floor Cleaner 1 l' , 58 ,234, 'Household Essentials' , 'http://localhost:8000/static/surface.png'),
	('Harpic Disinfectant Liquid Bathroom Cleaner (Lemon - 500 ml)' , 59 , 115 , 'Household Essentials' , 'http://localhost:8000/harpic.png'),
	('Ultra Wrap Bio-Degradable Cling Wrap' , 60 , 89 , 'Household Essentials' , 'http://localhost:8000/static/wrap.png'),
	('Premier Silky Tissue Paper Napkins (1 Ply)' , 61 , 59 , 'Household Essentials' , 'http://localhost:8000/static/tissues.png'),
	('Corepac Doodle Print Disposable Glass (250 ml) 1 pack (25 pieces)' , 62 , 89 , 'Household Essentials' , 'http://localhost:8000/static/glass.png'),
	('Matchbox by Homelites 5 pcs (Small Box), 5 units' , 63 , 10 , 'Household Essentials' , 'http://localhost:8000/static/matchbox.png'),
	('Camphor & Sesame Pooja Oil by Shubhkart - 900 ml' , 64 , 183 , 'Household Essentials' , 'http://localhost:8000/static/poojaoil.png'),
	('Mangaldeep Sambrani Dhoop 15 units' , 65 , 15 , 'Household Essentials' , 'http://localhost:8000/static/dhup.png'),
	('Mangaldeep Chandan 3in1 Incense Sticks / Agarbatti 244 g' , 66 , 118, 'Household Essentials' , 'http://localhost:8000/static/sticks.png'),
	('Hit Spray Flies & Mosquito Repellent Spray 400 ml' , 67 , 180 , 'Household Essentials' , 'http://localhost:8000/static/hit.png'),
	('Good Knight Flash Mosquito Killer Machine with 2 Refills - Combo Pack' , 68 , 171 , 'Household Essentials' , 'http://localhost:8000/static/goodnight.png'),
	('Dettol Original Hand Wash - 200 ml' , 69 , 76 , 'Household Essentials' , 'http://localhost:8000/static/handwash.png'),
	('Cosco Aero 500 Nylon Shuttlecock (Yellow) 1 pack (6 pieces)' , 70 , 349 , 'Household Essentials' , 'http://localhost:8000/static/cock.png'),
	('Lifelong Adjustable Hand Gripper Strengthener (Black)' , 71 , 269 , 'Household Essentials' , 'http://localhost:8000/static/gripper.png'),
	('Homestrap Non-Woven 24 Compartments Wardrobe Storage Organiser for Socks (Grey)' , 72 , 201 , 'Household Essentials' , 'http://localhost:8000/static/box.png'),
	('Boldfit Spider Gym Shaker Bottle - 500 ml (Black)' , 73 , 349 , 'Household Essentials' , 'http://localhost:8000/static/bottle.png'),
	('Boldfit Skipping Rope (Black)' , 74 , 120 , 'Household Essentials' , 'http://localhost:8000/static/rope.png'),
	('Hide & Seek Chocolate Chip Cookies (200 g)' , 75 , 50 , 'Snacks & Beverages' , 'http://localhost:8000/static/hideandseek.png'),
	('Karachi Bakery Osmania Bakery Cookies (400 g)' , 76 , 180 , 'Snacks & Beverages' , 'http://localhost:8000/static/osmania.png'),
	('RiteBite Max Protein No Maida 7 Grains Choco Almond 12 g Protein Cookies' , 77 , 59 , 'Snacks & Beverages' , 'http://localhost:8000/static/choco.png'),
	('Lays American Style Cream & Onion Potato Chips' , 78 , 30 , 'Snacks & Beverages' , 'http://localhost:8000/static/lays.png'),
	('Modern White Bread (400 g)' , 79 , 55 , 'Grocery' , 'http://localhost:8000/static/bread.png'),
	('Bingo Mad Angles Achaari Masti Crisps - Pack of 3' , 80 , 58 , 'Snacks & Beverages' , 'http://localhost:8000/static/mad.png'),
	('Haldirams Nagpur Aloo Bhujia - 200 g' , 81 , 55 , 'Snacks & Beverages' , 'http://localhost:8000/static/sev.png'),
	('Cornitos Crisps Peri Peri Nachos & Salsa Dip' , 82 , 78 , 'Snacks & Beverages' , 'http://localhost:8000/static/nacho.png'),
	('Cadbury Dairy Milk Silk Ganache Small Chocolate Bar' , 83 , 100 , 'Snacks & Beverages' , 'http://localhost:8000/static/chocobar.png'),
	('Ferrero Rocher Chocolate Gift Pack (4 pieces)' , 84 , 169 , 'Snacks & Beverages' , 'http://localhost:8000/static/chocoferro.png'),
	('Chupa Chups Sour Bites Mixed Fruit Candy' , 85 , 35 , 'Snacks & Beverages' , 'http://localhost:8000/static/cupa.png'),
	('Amul Taaza Homogenised Toned Milk 1 ltr' , 86 , 74 , 'Snacks & Beverages' , 'http://localhost:8000/static/milk.png'),
	('Brooke Bond Taj Mahal Rich & Flavourful Tea (250 g)' , 87 , 200 , 'Snacks & Beverages' , 'http://localhost:8000/static/tajma.png'),
	('Nescafe Sunrise Instant Coffee Powder - Rich Aroma, Coffee-Chicory Mix (45 g)' , 88 , 180 , 'Snacks & Beverages' , 'http://localhost:8000/static/coffe.png'),
	('Cadbury Hot Chocolate Drink Powder Mix (200 g)' , 89 , 220 , 'Snacks & Beverages' , 'http://localhost:8000/static/hotchoco.png'),
	('Lipton Honey Lemon Green Tea Bags - 25 pieces' , 90 , 153 , 'Snacks & Beverages' , 'http://localhost:8000/static/lemontea.png'),
	('Red Bull Energy Drink (250 ml)' , 91 , 125 , 'Snacks & Beverages' , 'http://localhost:8000/static/eng.png'),
	('Sprite Lemon-Lime Zero Sugar Soft Drink (330 ml)' , 92 , 189 , 'Snacks & Beverages' , 'http://localhost:8000/static/sprite.png'),
	('Dettol Original Alcohol Based Hand Sanitizer - 200 ml' , 93 , 125 , 'Pharma & Wellness' , 'http://localhost:8000/static/sanitizer.png'),
	('QUARANT Disposable Face Mask (Blue) 1 pack - 50 pieces' , 94 , 279 , 'Pharma & Wellness' , 'http://localhost:8000/static/mask.png'),
	('Eno Lemon Antacid 30 g' , 95 , 63 , 'Pharma & Wellness' , 'http://localhost:8000/static/eno.png'),
	('ORSL Apple Drink with Electrolyte - Pack of 6' , 96 , 214 , 'Pharma & Wellness' , 'http://localhost:8000/static/ors.png'),
	('Vicks VapoRub Chest Rub & Balm (Relieve Cold, Cough & Blocked Nose) - 25 ml' , 97 , 109 , 'Pharma & Wellness' , 'http://localhost:8000/static/vicks.png'),
	('Volini Activ Pain Relief Spray (60 g)' , 98 , 208 , 'Pharma & Wellness' , 'http://localhost:8000/static/volini.png'),
	('Wellness Surgicals Crepe Bandage (6 cm X 4 m)' , 99 , 140 , 'Pharma & Wellness' , 'http://localhost:8000/static/bandage.png'),
	('Dettol Antiseptic Liquid - 250 ml' , 100 , 170 , 'Pharma & Wellness' , 'http://localhost:8000/static/dettol.png'),
	('Plush Preg-Oh Basic Pregnancy Test Kit - 1 pieces' , 101 , 67 , 'Pharma & Wellness' , 'http://localhost:8000/static/preg.png'),
	('Kelloggs Corn Flakes with Immuno Nutrients (250 g)' , 102 , 125 , 'Packaged Foods' , 'http://localhost:8000/static/cornflaks.png'),
	('McCain Aloo Tikki (Frozen) - 400 g' , 103 , 102 , 'Packaged Foods' , 'http://localhost:8000/static/tikki.png'),
	('Switz Puff Dough Paratha (Frozen) 400 g (5 pieces)' , 104 , 105 , 'Packaged Foods' , 'http://localhost:8000/static/paratha.png'),
	('Wow! Momo Veg Darjeeling Momos (Frozen) 1 pack (10 pieces)' , 105 , 99 , 'Packaged Foods' , 'http://localhost:8000/static/momo.png'),
	('Prasuma Chicken Tikka Pizza Minis 180 g (2 pieces)' , 106 , 150 , 'Packaged Foods' , 'http://localhost:8000/static/pizza.png'),
	('Maggi Pazzta Cheese Macaroni Instant Pasta (75 g)' , 107 , 35 , 'Packaged Foods' , 'http://localhost:8000/static/pasta.png'),
	('MTR Dosa Breakfast Mix (500 g)' , 108 , 140 , 'Packaged Foods' , 'http://localhost:8000/static/dosa.png'),
	('Aashirvaad Instant Khatta Meetha Poha Ready to Eat (60 g)' , 109 , 26 , 'Packaged Foods' , 'http://localhost:8000/static/poha.png'),
	('Snapin Red Chilli Flakes Seasoning (35 g)' , 110 , 84 , 'Packaged Foods' , 'http://localhost:8000/static/cflaskes.png'),
	('Snapin Oregano (20 g)' , 111 , 93 , 'Packaged Foods' , 'http://localhost:8000/static/oflakes.png'),
	('ITC Master Chef Chicken Popcorn (500 g)' , 112 , 311 , 'Packaged Foods' , 'http://localhost:8000/static/chicken.png'),
	('The Little Farm Co. Mango Pickle (250 g)' , 113 , 215 , 'Packaged Foods' , 'http://localhost:8000/static/mp.png'),
	('Priya Tomato with Garlic Pickle (300 g)' , 114 , 110 , 'Packaged Foods' , 'http://localhost:8000/static/tp.png'),
	('Act II Butter Popcorn - Ready to Eat - 40 g' , 115 , 25 , 'Packaged Foods' , 'http://localhost:8000/static/ipopcorn.png'),
	('4700BC Lemon Pepper Sweet Corn (80 g)' , 116 , 80 , 'Packaged Foods' , 'http://localhost:8000/static/sweetcorn.png'),
	('MamyPoko Pants Standard Diaper (L, 9-14 kg),1 pack (44 pieces)' , 117 , 413 , 'Baby Care' , 'http://localhost:8000/static/bc1.png'),
	('Johnsons Blossoms Baby Soap (75 g)' , 118 , 80 , 'Baby Care' , 'http://localhost:8000/static/bc2.png'),
	('Himalaya Gentle Baby Shampoo (200 ml)' , 119 , 183 , 'Baby Care' , 'http://localhost:8000/static/bc3.png'),
	('Pampers Baby Wipes with Aloe 1 pack (72 wipes)' , 120 , 171 , 'Baby Care' , 'http://localhost:8000/static/bc4.png'),
	('Nestle NAN PRO Stage 1 Infant Formula' , 121 , 93 , 'Baby Care' , 'http://localhost:8000/static/bc5.png'),
	('Himalaya Baby Powder (400 g)' , 122 , 239 , 'Baby Care' , 'http://localhost:8000/static/bc6.png'),
	('Himalaya Baby Lotion (200 ml)' , 123 , 174 , 'Baby Care' , 'http://localhost:8000/static/bc8.png'),
	('LuvLap Baby Feeding Bottle (250 ml, Blue)' , 124 , 170 , 'Baby Care' , 'http://localhost:8000/static/bc7.png'),
	('Eggoz Nutrition Protein Rich White Eggs (6 pieces)' , 124 , 71 , 'Grocery' , 'http://localhost:8000/static/egg.png');
    ('Drools Absolute Calcium Bone Dog Supplement - 40 Pcs', 127, 423, 'Pet Supplies', 'http://localhost:8000/static/p1.png'), 
	('Pedigree Adult Dog Dry Food - Vegetable & Chicken (1.2 kg)', 128, 313, 'Pet Supplies', 'http://localhost:8000/static/p2.png'), 
	('Pedigree Adult Dog Wet Food -Grilled Liver Chunks Flavour in Gravy with Vegetables (70 g)', 129, 49, 'Pet Supplies', 'http://localhost:8000/static/p3.png'), 
	('PurePet Chew Bone (260 g)', 130, 205, 'Pet Supplies', 'http://localhost:8000/static/p4.png'), 
	('Purina Friskies Surfin Favourites Adult Dry Cat Food - 1 kg', 131, 346, 'Pet Supplies', 'http://localhost:8000/static/p5.png'), 
	('PurePet Lickable Real Chicken Creamy Cat Treat - 1 pack (5 x 15 g)', 132, 80, 'Pet Supplies', 'http://localhost:8000/static/p6.png'), 
	('PurePet Lickable Tuna & Bonito Creamy Cat Treat - 1 pack (5 x 15 g)', 133, 80, 'Pet Supplies', 'http://localhost:8000/static/p7.png'), 
	('MoePuppy Anti-Tick Pet Spray (100 ml)', 134, 339, 'Pet Supplies', 'http://localhost:8000/static/p8.png'), 
	('Nootie Pet Wipes (Large) - 1 pack (100 pieces)', 135, 109, 'Pet Supplies', 'http://localhost:8000/static/p9.png'), 
	('Himalaya Erina Puppy Pet Shampoo & Conditioner (200 ml)', 136, 294, 'Pet Supplies', 'http://localhost:8000/static/p10.png'), 
	('Zoivane Pets Bathing Pet Brush (Blue)', 137, 198, 'Pet Supplies', 'http://localhost:8000/static/p11.png'), 
	('Mutt of Course Scooby Dooby Doo Printed Dog Collar (Small)', 138, 599, 'Pet Supplies', 'http://localhost:8000/static/p12.png'), 
	('Mutt of Course I Only Like Hoomans Dog Leash (L)', 139, 699, 'Pet Supplies', 'http://localhost:8000/static/p13.png'), 
	('Pet Food Water Bowls Cat Bowls,Small Dogs', 140, 499, 'Pet Supplies', 'http://localhost:8000/static/p14.png'), 
	('Vibrant Life Gravity Pet Feeder, Blue, Large, 10 Pound Capacity', 141, 1599, 'Pet Supplies', 'http://localhost:8000/static/p15.png'), 
	('Mutt of Course Jungle Vest Large Dog Harness (Dark Blue)', 142, 1799, 'Pet Supplies', 'http://localhost:8000/static/p16.png'); 


        # Add your 216 products here...
    ]
    
    # Insert products
    for i, (name, price, quantity, bin_id, image_url, category) in enumerate(products_data, 1):
        try:
            cursor.execute("""
                INSERT INTO products (name, price, quantity, bin_id, image_url, category, sale_count)
                VALUES (%s, %s, %s, %s, %s, %s, 0)
            """, (name, price, quantity, bin_id, image_url, category))
            
            # Update bin to have this product
            cursor.execute("""
                UPDATE bins SET product_id = %s WHERE id = %s
            """, (i, bin_id))
            
            print(f"   ✅ Added product {i}: {name}")
            
        except Exception as e:
            print(f"   ❌ Error adding product {i} ({name}): {e}")
    
    # Commit and close
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✅ Added {len(products_data)} products to database")
    print("\n📝 Instructions:")
    print("   1. Edit this script to add your 216 products")
    print("   2. Replace the products_data list with your actual products")
    print("   3. Run: python add_products_manual.py")

if __name__ == "__main__":
    add_products_manually() 