from typing import List, Dict, Any

INDIAN_FOOD_DATASET: List[Dict[str, Any]] = [
    # =========================================================================
    # NORTH INDIA (उत्तर भारत)
    # =========================================================================
    {
        "name": "Dal Makhani (Black Lentil Curry)",
        "calories": 280.0,
        "protein": 8.5,
        "carbs": 30.0,
        "fat": 14.0,
        "fiber": 5.5,
        "sugar": 2.0,
        "sodium": 390.0,
        "category": "North Indian",
        "region": "North India"
    },
    {
        "name": "Dal Tadka (Yellow Lentil Curry)",
        "calories": 160.0,
        "protein": 8.5,
        "carbs": 24.0,
        "fat": 4.0,
        "fiber": 6.0,
        "sugar": 1.5,
        "sodium": 320.0,
        "category": "North Indian",
        "region": "North India"
    },
    {
        "name": "Paneer Butter Masala (Cottage Cheese Curry)",
        "calories": 360.0,
        "protein": 14.0,
        "carbs": 18.0,
        "fat": 26.0,
        "fiber": 2.5,
        "sugar": 4.0,
        "sodium": 440.0,
        "category": "North Indian",
        "region": "North India"
    },
    {
        "name": "Palak Paneer (Spinach Cottage Cheese)",
        "calories": 220.0,
        "protein": 11.5,
        "carbs": 9.0,
        "fat": 16.0,
        "fiber": 4.2,
        "sugar": 2.2,
        "sodium": 380.0,
        "category": "North Indian",
        "region": "North India"
    },
    {
        "name": "Shahi Paneer (Cashew Nut Gravy)",
        "calories": 340.0,
        "protein": 13.0,
        "carbs": 16.0,
        "fat": 25.0,
        "fiber": 2.0,
        "sugar": 4.5,
        "sodium": 410.0,
        "category": "North Indian",
        "region": "North India"
    },
    {
        "name": "Kadai Paneer (Bell Pepper Cottage Cheese)",
        "calories": 260.0,
        "protein": 13.5,
        "carbs": 12.0,
        "fat": 18.0,
        "fiber": 3.0,
        "sugar": 2.5,
        "sodium": 390.0,
        "category": "North Indian",
        "region": "North India"
    },
    {
        "name": "Matar Paneer (Peas & Cottage Cheese)",
        "calories": 240.0,
        "protein": 11.0,
        "carbs": 16.0,
        "fat": 15.0,
        "fiber": 3.5,
        "sugar": 3.0,
        "sodium": 370.0,
        "category": "North Indian",
        "region": "North India"
    },
    {
        "name": "Chole Bhature (Spiced Chickpeas with Fried Bread)",
        "calories": 480.0,
        "protein": 12.5,
        "carbs": 62.0,
        "fat": 21.0,
        "fiber": 7.0,
        "sugar": 3.2,
        "sodium": 590.0,
        "category": "North Indian",
        "region": "North India"
    },
    {
        "name": "Chole Masala (Chickpea Curry)",
        "calories": 240.0,
        "protein": 10.0,
        "carbs": 36.0,
        "fat": 7.0,
        "fiber": 9.0,
        "sugar": 3.0,
        "sodium": 420.0,
        "category": "North Indian",
        "region": "North India"
    },
    {
        "name": "Rajma Masala (Red Kidney Beans Curry)",
        "calories": 210.0,
        "protein": 9.0,
        "carbs": 32.0,
        "fat": 5.5,
        "fiber": 8.0,
        "sugar": 2.5,
        "sodium": 390.0,
        "category": "North Indian",
        "region": "North India"
    },
    {
        "name": "Sarson Ka Saag & Makki Roti (Mustard Greens & Corn Flatbread)",
        "calories": 310.0,
        "protein": 7.5,
        "carbs": 38.0,
        "fat": 14.5,
        "fiber": 6.5,
        "sugar": 2.0,
        "sodium": 340.0,
        "category": "North Indian",
        "region": "North India"
    },
    {
        "name": "Aloo Paratha (Stuffed Spiced Potato Flatbread - 1 pc)",
        "calories": 290.0,
        "protein": 5.5,
        "carbs": 44.0,
        "fat": 10.5,
        "fiber": 4.2,
        "sugar": 1.5,
        "sodium": 360.0,
        "category": "North Indian",
        "region": "North India"
    },
    {
        "name": "Paneer Paratha (Stuffed Cottage Cheese Flatbread - 1 pc)",
        "calories": 330.0,
        "protein": 12.0,
        "carbs": 36.0,
        "fat": 15.0,
        "fiber": 3.8,
        "sugar": 1.2,
        "sodium": 380.0,
        "category": "North Indian",
        "region": "North India"
    },
    {
        "name": "Gobi Paratha (Stuffed Cauliflower Flatbread - 1 pc)",
        "calories": 250.0,
        "protein": 5.0,
        "carbs": 40.0,
        "fat": 8.0,
        "fiber": 4.5,
        "sugar": 1.8,
        "sodium": 320.0,
        "category": "North Indian",
        "region": "North India"
    },
    {
        "name": "Baingan Bharta (Roasted Spiced Eggplant Mash)",
        "calories": 140.0,
        "protein": 3.0,
        "carbs": 16.0,
        "fat": 7.5,
        "fiber": 5.0,
        "sugar": 4.0,
        "sodium": 290.0,
        "category": "North Indian",
        "region": "North India"
    },
    {
        "name": "Dum Aloo Kashmiri (Spiced Baby Potato Curry)",
        "calories": 230.0,
        "protein": 4.0,
        "carbs": 32.0,
        "fat": 10.0,
        "fiber": 3.8,
        "sugar": 2.5,
        "sodium": 380.0,
        "category": "North Indian",
        "region": "North India"
    },
    {
        "name": "Kadhi Pakora (Yogurt & Gram Flour Curry with Fritters)",
        "calories": 210.0,
        "protein": 7.0,
        "carbs": 24.0,
        "fat": 9.5,
        "fiber": 3.2,
        "sugar": 3.5,
        "sodium": 410.0,
        "category": "North Indian",
        "region": "North India"
    },
    {
        "name": "Malai Kofta (Cottage Cheese & Potato Dumplings in Cream Gravy)",
        "calories": 390.0,
        "protein": 9.0,
        "carbs": 28.0,
        "fat": 28.0,
        "fiber": 2.5,
        "sugar": 5.0,
        "sodium": 460.0,
        "category": "North Indian",
        "region": "North India"
    },
    {
        "name": "Bhindi Masala (Spiced Okra Stir Fry)",
        "calories": 130.0,
        "protein": 3.5,
        "carbs": 14.0,
        "fat": 7.0,
        "fiber": 4.5,
        "sugar": 3.0,
        "sodium": 280.0,
        "category": "North Indian",
        "region": "North India"
    },
    {
        "name": "Jeera Aloo (Cumin Spiced Potatoes)",
        "calories": 160.0,
        "protein": 2.8,
        "carbs": 26.0,
        "fat": 5.5,
        "fiber": 3.0,
        "sugar": 1.2,
        "sodium": 310.0,
        "category": "North Indian",
        "region": "North India"
    },
    {
        "name": "Butter Chicken / Murgh Makhani",
        "calories": 380.0,
        "protein": 26.0,
        "carbs": 12.0,
        "fat": 25.0,
        "fiber": 1.8,
        "sugar": 4.0,
        "sodium": 480.0,
        "category": "North Indian",
        "region": "North India"
    },
    {
        "name": "Tandoori Chicken (Spiced Roasted Chicken Breast)",
        "calories": 240.0,
        "protein": 32.0,
        "carbs": 4.0,
        "fat": 10.0,
        "fiber": 1.0,
        "sugar": 1.0,
        "sodium": 420.0,
        "category": "North Indian",
        "region": "North India"
    },
    {
        "name": "Rogan Josh (Kashmiri Mutton Curry)",
        "calories": 340.0,
        "protein": 24.0,
        "carbs": 8.0,
        "fat": 24.0,
        "fiber": 2.0,
        "sugar": 2.0,
        "sodium": 450.0,
        "category": "North Indian",
        "region": "North India"
    },
    {
        "name": "Amritsari Kulcha (Crispy Stuffed Potato & Onion Bread)",
        "calories": 310.0,
        "protein": 6.0,
        "carbs": 48.0,
        "fat": 11.0,
        "fiber": 3.5,
        "sugar": 1.8,
        "sodium": 390.0,
        "category": "North Indian",
        "region": "North India"
    },
    {
        "name": "Paneer Tikka (Grilled Cottage Cheese Skewers - 4 pcs)",
        "calories": 240.0,
        "protein": 16.0,
        "carbs": 7.0,
        "fat": 17.0,
        "fiber": 2.0,
        "sugar": 2.0,
        "sodium": 350.0,
        "category": "North Indian",
        "region": "North India"
    },

    # =========================================================================
    # SOUTH INDIA (दक्षिण भारत)
    # =========================================================================
    {
        "name": "Plain Dosa (Crispy Fermented Crepe)",
        "calories": 168.0,
        "protein": 3.9,
        "carbs": 29.0,
        "fat": 3.7,
        "fiber": 1.8,
        "sugar": 0.6,
        "sodium": 240.0,
        "category": "South Indian",
        "region": "South India"
    },
    {
        "name": "Masala Dosa with Potato Filling",
        "calories": 280.0,
        "protein": 6.0,
        "carbs": 42.0,
        "fat": 10.0,
        "fiber": 3.5,
        "sugar": 1.8,
        "sodium": 420.0,
        "category": "South Indian",
        "region": "South India"
    },
    {
        "name": "Mysore Masala Dosa (Spicy Red Chutney Dosa)",
        "calories": 320.0,
        "protein": 6.5,
        "carbs": 44.0,
        "fat": 13.0,
        "fiber": 3.8,
        "sugar": 2.0,
        "sodium": 450.0,
        "category": "South Indian",
        "region": "South India"
    },
    {
        "name": "Rava Dosa (Semolina Crispy Crepe)",
        "calories": 210.0,
        "protein": 4.5,
        "carbs": 33.0,
        "fat": 7.0,
        "fiber": 2.0,
        "sugar": 0.8,
        "sodium": 310.0,
        "category": "South Indian",
        "region": "South India"
    },
    {
        "name": "Idli with Sambar (Steamed Rice Cakes - 2 pcs)",
        "calories": 160.0,
        "protein": 6.0,
        "carbs": 30.0,
        "fat": 1.5,
        "fiber": 3.0,
        "sugar": 1.2,
        "sodium": 310.0,
        "category": "South Indian",
        "region": "South India"
    },
    {
        "name": "Medu Vada (Savory Urad Dal Fritter - 2 pcs)",
        "calories": 240.0,
        "protein": 7.5,
        "carbs": 25.0,
        "fat": 12.5,
        "fiber": 3.2,
        "sugar": 0.5,
        "sodium": 330.0,
        "category": "South Indian",
        "region": "South India"
    },
    {
        "name": "Sambar (Lentil & Mixed Vegetable Stew - 1 bowl)",
        "calories": 115.0,
        "protein": 5.0,
        "carbs": 18.0,
        "fat": 2.5,
        "fiber": 4.2,
        "sugar": 2.5,
        "sodium": 390.0,
        "category": "South Indian",
        "region": "South India"
    },
    {
        "name": "Coconut Chutney (Fresh Ground Coconut Dip - 2 tbsp)",
        "calories": 95.0,
        "protein": 1.2,
        "carbs": 3.5,
        "fat": 8.5,
        "fiber": 1.8,
        "sugar": 0.8,
        "sodium": 160.0,
        "category": "South Indian",
        "region": "South India"
    },
    {
        "name": "Ven Pongal (Ghee Moong Dal & Rice Porridge)",
        "calories": 260.0,
        "protein": 6.5,
        "carbs": 38.0,
        "fat": 9.5,
        "fiber": 2.5,
        "sugar": 0.5,
        "sodium": 280.0,
        "category": "South Indian",
        "region": "South India"
    },
    {
        "name": "Upma (Semolina Savory Porridge)",
        "calories": 195.0,
        "protein": 4.8,
        "carbs": 34.0,
        "fat": 4.5,
        "fiber": 2.8,
        "sugar": 1.0,
        "sodium": 310.0,
        "category": "South Indian",
        "region": "South India"
    },
    {
        "name": "Onion Tomato Uttapam (Thick Savory Rice Pancake)",
        "calories": 220.0,
        "protein": 5.2,
        "carbs": 36.0,
        "fat": 6.0,
        "fiber": 3.0,
        "sugar": 2.0,
        "sodium": 340.0,
        "category": "South Indian",
        "region": "South India"
    },
    {
        "name": "Curd Rice / Thayir Sadam (Yogurt Tempered Rice)",
        "calories": 190.0,
        "protein": 5.5,
        "carbs": 30.0,
        "fat": 5.5,
        "fiber": 1.2,
        "sugar": 2.8,
        "sodium": 260.0,
        "category": "South Indian",
        "region": "South India"
    },
    {
        "name": "Lemon Rice / Chitranna (Tangy Turmeric Rice)",
        "calories": 230.0,
        "protein": 4.2,
        "carbs": 38.0,
        "fat": 7.0,
        "fiber": 1.8,
        "sugar": 0.8,
        "sodium": 290.0,
        "category": "South Indian",
        "region": "South India"
    },
    {
        "name": "Bisi Bele Bath (Karnataka Spiced Lentil & Rice)",
        "calories": 280.0,
        "protein": 8.0,
        "carbs": 44.0,
        "fat": 8.0,
        "fiber": 4.5,
        "sugar": 2.0,
        "sodium": 380.0,
        "category": "South Indian",
        "region": "South India"
    },
    {
        "name": "Tamarind Rice / Puliyodharai",
        "calories": 260.0,
        "protein": 4.5,
        "carbs": 42.0,
        "fat": 8.5,
        "fiber": 2.5,
        "sugar": 2.2,
        "sodium": 340.0,
        "category": "South Indian",
        "region": "South India"
    },
    {
        "name": "Tomato Rasam (Spiced Broth - 1 cup)",
        "calories": 45.0,
        "protein": 1.5,
        "carbs": 8.0,
        "fat": 1.0,
        "fiber": 1.2,
        "sugar": 2.0,
        "sodium": 280.0,
        "category": "South Indian",
        "region": "South India"
    },
    {
        "name": "Appam with Vegetable Coconut Stew",
        "calories": 240.0,
        "protein": 4.0,
        "carbs": 36.0,
        "fat": 9.0,
        "fiber": 3.2,
        "sugar": 2.5,
        "sodium": 290.0,
        "category": "South Indian",
        "region": "South India"
    },
    {
        "name": "Kerala Fish Curry (Kudampuli & Coconut Fish)",
        "calories": 250.0,
        "protein": 22.0,
        "carbs": 6.0,
        "fat": 15.0,
        "fiber": 1.5,
        "sugar": 1.2,
        "sodium": 410.0,
        "category": "South Indian",
        "region": "South India"
    },
    {
        "name": "Chettinad Chicken Curry (Spicy Pepper Gravy)",
        "calories": 310.0,
        "protein": 25.0,
        "carbs": 7.0,
        "fat": 20.0,
        "fiber": 2.2,
        "sugar": 1.5,
        "sodium": 460.0,
        "category": "South Indian",
        "region": "South India"
    },
    {
        "name": "Malabar Parotta (Flaky Layered Bread - 1 pc)",
        "calories": 260.0,
        "protein": 4.5,
        "carbs": 36.0,
        "fat": 11.0,
        "fiber": 1.5,
        "sugar": 0.8,
        "sodium": 280.0,
        "category": "South Indian",
        "region": "South India"
    },
    {
        "name": "Avial (Kerala Mixed Vegetables with Coconut & Curd)",
        "calories": 170.0,
        "protein": 3.8,
        "carbs": 16.0,
        "fat": 10.0,
        "fiber": 4.5,
        "sugar": 3.0,
        "sodium": 270.0,
        "category": "South Indian",
        "region": "South India"
    },
    {
        "name": "Hyderabadi Veg Dum Biryani",
        "calories": 290.0,
        "protein": 6.5,
        "carbs": 48.0,
        "fat": 9.0,
        "fiber": 4.0,
        "sugar": 2.8,
        "sodium": 460.0,
        "category": "South Indian",
        "region": "South India"
    },
    {
        "name": "Hyderabadi Chicken Dum Biryani",
        "calories": 390.0,
        "protein": 24.0,
        "carbs": 46.0,
        "fat": 13.0,
        "fiber": 3.0,
        "sugar": 2.0,
        "sodium": 520.0,
        "category": "South Indian",
        "region": "South India"
    },

    # =========================================================================
    # WEST INDIA (पश्चिम भारत - Maharashtra, Gujarat, Rajasthan, Goa)
    # =========================================================================
    {
        "name": "Khaman Dhokla (Steamed Gram Flour Cakes - 2 pcs)",
        "calories": 150.0,
        "protein": 6.0,
        "carbs": 23.0,
        "fat": 3.5,
        "fiber": 2.5,
        "sugar": 3.0,
        "sodium": 340.0,
        "category": "West Indian",
        "region": "West India"
    },
    {
        "name": "Khandvi (Spiced Gram Flour Rolls - 4 pcs)",
        "calories": 160.0,
        "protein": 5.5,
        "carbs": 20.0,
        "fat": 6.5,
        "fiber": 2.2,
        "sugar": 2.0,
        "sodium": 310.0,
        "category": "West Indian",
        "region": "West India"
    },
    {
        "name": "Thepla (Fenugreek Methi Flatbread - 2 pcs)",
        "calories": 210.0,
        "protein": 5.8,
        "carbs": 32.0,
        "fat": 7.0,
        "fiber": 3.5,
        "sugar": 1.0,
        "sodium": 290.0,
        "category": "West Indian",
        "region": "West India"
    },
    {
        "name": "Pav Bhaji (Spiced Vegetable Mash with 2 Butter Pav)",
        "calories": 420.0,
        "protein": 9.0,
        "carbs": 58.0,
        "fat": 18.0,
        "fiber": 6.0,
        "sugar": 4.5,
        "sodium": 580.0,
        "category": "West Indian",
        "region": "West India"
    },
    {
        "name": "Vada Pav (Mumbai Potato Fritter Burger - 1 pc)",
        "calories": 290.0,
        "protein": 6.0,
        "carbs": 42.0,
        "fat": 11.0,
        "fiber": 3.0,
        "sugar": 2.0,
        "sodium": 440.0,
        "category": "West Indian",
        "region": "West India"
    },
    {
        "name": "Misal Pav (Sprouted Moth Curry with Farsan & Pav)",
        "calories": 380.0,
        "protein": 12.0,
        "carbs": 52.0,
        "fat": 14.0,
        "fiber": 7.5,
        "sugar": 3.0,
        "sodium": 520.0,
        "category": "West Indian",
        "region": "West India"
    },
    {
        "name": "Poha (Flattened Rice with Veggies & Peanuts)",
        "calories": 180.0,
        "protein": 4.0,
        "carbs": 33.0,
        "fat": 3.8,
        "fiber": 2.5,
        "sugar": 1.2,
        "sodium": 280.0,
        "category": "West Indian",
        "region": "West India"
    },
    {
        "name": "Sabudana Khichdi (Tapioca Pearls with Roasted Peanuts)",
        "calories": 270.0,
        "protein": 4.0,
        "carbs": 44.0,
        "fat": 9.0,
        "fiber": 1.5,
        "sugar": 1.5,
        "sodium": 240.0,
        "category": "West Indian",
        "region": "West India"
    },
    {
        "name": "Puran Poli (Sweet Chana Dal Stuffed Flatbread - 1 pc)",
        "calories": 260.0,
        "protein": 6.5,
        "carbs": 46.0,
        "fat": 6.0,
        "fiber": 3.5,
        "sugar": 16.0,
        "sodium": 140.0,
        "category": "West Indian",
        "region": "West India"
    },
    {
        "name": "Dal Baati Churma (Baked Wheat Balls with Lentils & Churma)",
        "calories": 520.0,
        "protein": 14.0,
        "carbs": 68.0,
        "fat": 22.0,
        "fiber": 7.5,
        "sugar": 12.0,
        "sodium": 480.0,
        "category": "West Indian",
        "region": "West India"
    },
    {
        "name": "Gatte Ki Sabzi (Gram Flour Dumplings in Curd Gravy)",
        "calories": 240.0,
        "protein": 8.0,
        "carbs": 22.0,
        "fat": 13.0,
        "fiber": 3.5,
        "sugar": 2.8,
        "sodium": 390.0,
        "category": "West Indian",
        "region": "West India"
    },
    {
        "name": "Ker Sangri (Rajasthani Desert Bean Stir Fry)",
        "calories": 160.0,
        "protein": 5.0,
        "carbs": 18.0,
        "fat": 8.0,
        "fiber": 5.5,
        "sugar": 2.0,
        "sodium": 310.0,
        "category": "West Indian",
        "region": "West India"
    },
    {
        "name": "Pitla Bhakri (Besan Curry with Jowar Millet Roti)",
        "calories": 290.0,
        "protein": 9.0,
        "carbs": 45.0,
        "fat": 8.0,
        "fiber": 6.0,
        "sugar": 1.5,
        "sodium": 360.0,
        "category": "West Indian",
        "region": "West India"
    },
    {
        "name": "Thalipeeth (Multi-grain Savory Spiced Pancake - 1 pc)",
        "calories": 210.0,
        "protein": 6.5,
        "carbs": 32.0,
        "fat": 7.0,
        "fiber": 4.5,
        "sugar": 1.0,
        "sodium": 290.0,
        "category": "West Indian",
        "region": "West India"
    },
    {
        "name": "Goan Fish Curry (Kokum & Coconut Fish)",
        "calories": 260.0,
        "protein": 21.0,
        "carbs": 5.5,
        "fat": 17.0,
        "fiber": 1.8,
        "sugar": 1.5,
        "sodium": 420.0,
        "category": "West Indian",
        "region": "West India"
    },
    {
        "name": "Sev Tamatar Ki Sabzi (Tangy Tomato Gravy with Sev)",
        "calories": 220.0,
        "protein": 5.0,
        "carbs": 24.0,
        "fat": 12.0,
        "fiber": 3.0,
        "sugar": 4.5,
        "sodium": 430.0,
        "category": "West Indian",
        "region": "West India"
    },
    {
        "name": "Ragda Pattice (White Peas Gravy with Potato Patties)",
        "calories": 310.0,
        "protein": 9.5,
        "carbs": 48.0,
        "fat": 9.0,
        "fiber": 6.5,
        "sugar": 3.2,
        "sodium": 460.0,
        "category": "West Indian",
        "region": "West India"
    },

    # =========================================================================
    # EAST & NORTH-EAST INDIA (पूर्व एवं उत्तर-पूर्व भारत)
    # =========================================================================
    {
        "name": "Litti Chokha (Roasted Sattu Wheat Balls with Chokha - 2 pcs)",
        "calories": 340.0,
        "protein": 12.5,
        "carbs": 54.0,
        "fat": 8.5,
        "fiber": 8.0,
        "sugar": 2.2,
        "sodium": 380.0,
        "category": "East Indian",
        "region": "East India"
    },
    {
        "name": "Macher Jhol (Traditional Bengali Fish Curry)",
        "calories": 220.0,
        "protein": 22.0,
        "carbs": 6.5,
        "fat": 12.0,
        "fiber": 1.5,
        "sugar": 1.0,
        "sodium": 390.0,
        "category": "East Indian",
        "region": "East India"
    },
    {
        "name": "Kosha Mangsho (Bengali Slow Cooked Spiced Mutton)",
        "calories": 380.0,
        "protein": 26.0,
        "carbs": 9.0,
        "fat": 27.0,
        "fiber": 2.0,
        "sugar": 2.5,
        "sodium": 460.0,
        "category": "East Indian",
        "region": "East India"
    },
    {
        "name": "Luchi with Aloo Dum (Deep Fried Flatbread with Spiced Potatoes)",
        "calories": 360.0,
        "protein": 5.5,
        "carbs": 48.0,
        "fat": 17.0,
        "fiber": 3.5,
        "sugar": 2.0,
        "sodium": 410.0,
        "category": "East Indian",
        "region": "East India"
    },
    {
        "name": "Shukto (Bengali Bitter-Sweet Vegetable Medley)",
        "calories": 140.0,
        "protein": 3.5,
        "carbs": 18.0,
        "fat": 6.0,
        "fiber": 4.0,
        "sugar": 3.0,
        "sodium": 260.0,
        "category": "East Indian",
        "region": "East India"
    },
    {
        "name": "Cholar Dal (Bengali Chana Dal with Coconut & Spices)",
        "calories": 230.0,
        "protein": 9.5,
        "carbs": 32.0,
        "fat": 7.5,
        "fiber": 6.5,
        "sugar": 3.5,
        "sodium": 310.0,
        "category": "East Indian",
        "region": "East India"
    },
    {
        "name": "Dalma (Odisha Lentil Stew with Raw Papaya & Pumpkin)",
        "calories": 170.0,
        "protein": 7.5,
        "carbs": 26.0,
        "fat": 4.5,
        "fiber": 5.5,
        "sugar": 2.5,
        "sodium": 290.0,
        "category": "East Indian",
        "region": "East India"
    },
    {
        "name": "Pakhala Bhata (Fermented Water Rice with Curd & Tempering)",
        "calories": 180.0,
        "protein": 4.2,
        "carbs": 34.0,
        "fat": 3.0,
        "fiber": 1.5,
        "sugar": 1.5,
        "sodium": 220.0,
        "category": "East Indian",
        "region": "East India"
    },
    {
        "name": "Masor Tenga (Assamese Tangy Fish Curry with Tomato & Lemon)",
        "calories": 190.0,
        "protein": 21.0,
        "carbs": 5.0,
        "fat": 9.5,
        "fiber": 1.2,
        "sugar": 1.8,
        "sodium": 340.0,
        "category": "East Indian",
        "region": "East India"
    },
    {
        "name": "Steamed Veg Momos (6 pcs with Chili Dip)",
        "calories": 210.0,
        "protein": 5.5,
        "carbs": 38.0,
        "fat": 4.0,
        "fiber": 3.0,
        "sugar": 1.5,
        "sodium": 360.0,
        "category": "East Indian",
        "region": "East India"
    },
    {
        "name": "Steamed Chicken Momos (6 pcs with Chili Dip)",
        "calories": 260.0,
        "protein": 16.0,
        "carbs": 34.0,
        "fat": 6.5,
        "fiber": 2.0,
        "sugar": 1.0,
        "sodium": 390.0,
        "category": "East Indian",
        "region": "East India"
    },
    {
        "name": "Thukpa (Tibetan / Himalayan Noodle Soup with Veggies)",
        "calories": 240.0,
        "protein": 7.0,
        "carbs": 42.0,
        "fat": 5.0,
        "fiber": 3.5,
        "sugar": 2.0,
        "sodium": 440.0,
        "category": "East Indian",
        "region": "East India"
    },

    # =========================================================================
    # INDIAN BREADS, RICE & STAPLES (रोटी, चावल एवं दाल)
    # =========================================================================
    {
        "name": "Roti / Phulka (Whole Wheat Chapati - 1 pc)",
        "calories": 104.0,
        "protein": 3.4,
        "carbs": 22.0,
        "fat": 0.5,
        "fiber": 3.2,
        "sugar": 0.2,
        "sodium": 120.0,
        "category": "Breads & Rice",
        "region": "All-India"
    },
    {
        "name": "Tandoori Roti (Clay Oven Whole Wheat Flatbread - 1 pc)",
        "calories": 115.0,
        "protein": 3.8,
        "carbs": 24.0,
        "fat": 0.6,
        "fiber": 3.4,
        "sugar": 0.2,
        "sodium": 130.0,
        "category": "Breads & Rice",
        "region": "All-India"
    },
    {
        "name": "Plain Naan (Leavened Oven Bread - 1 pc)",
        "calories": 260.0,
        "protein": 7.0,
        "carbs": 45.0,
        "fat": 5.0,
        "fiber": 2.0,
        "sugar": 2.5,
        "sodium": 340.0,
        "category": "Breads & Rice",
        "region": "All-India"
    },
    {
        "name": "Butter Naan (Layered Leavened Bread with Butter - 1 pc)",
        "calories": 310.0,
        "protein": 7.2,
        "carbs": 45.0,
        "fat": 11.5,
        "fiber": 2.0,
        "sugar": 2.5,
        "sodium": 360.0,
        "category": "Breads & Rice",
        "region": "All-India"
    },
    {
        "name": "Garlic Naan (Leavened Bread with Roasted Garlic - 1 pc)",
        "calories": 280.0,
        "protein": 7.5,
        "carbs": 46.0,
        "fat": 7.0,
        "fiber": 2.2,
        "sugar": 2.6,
        "sodium": 370.0,
        "category": "Breads & Rice",
        "region": "All-India"
    },
    {
        "name": "Missi Roti (Spiced Gram Flour & Wheat Flatbread - 1 pc)",
        "calories": 145.0,
        "protein": 5.2,
        "carbs": 24.0,
        "fat": 3.5,
        "fiber": 3.8,
        "sugar": 0.5,
        "sodium": 210.0,
        "category": "Breads & Rice",
        "region": "All-India"
    },
    {
        "name": "Steamed Basmati Rice (1 cup cooked)",
        "calories": 205.0,
        "protein": 4.2,
        "carbs": 45.0,
        "fat": 0.5,
        "fiber": 0.8,
        "sugar": 0.1,
        "sodium": 5.0,
        "category": "Breads & Rice",
        "region": "All-India"
    },
    {
        "name": "Jeera Rice (Cumin Scented Basmati Rice - 1 cup)",
        "calories": 235.0,
        "protein": 4.4,
        "carbs": 45.0,
        "fat": 4.5,
        "fiber": 1.2,
        "sugar": 0.2,
        "sodium": 180.0,
        "category": "Breads & Rice",
        "region": "All-India"
    },
    {
        "name": "Brown Rice (1 cup cooked)",
        "calories": 218.0,
        "protein": 4.5,
        "carbs": 45.8,
        "fat": 1.6,
        "fiber": 3.5,
        "sugar": 0.3,
        "sodium": 2.0,
        "category": "Breads & Rice",
        "region": "All-India"
    },
    {
        "name": "Moong Dal Khichdi (Comforting Lentil & Rice Porridge)",
        "calories": 175.0,
        "protein": 7.0,
        "carbs": 30.0,
        "fat": 3.0,
        "fiber": 4.0,
        "sugar": 1.0,
        "sodium": 260.0,
        "category": "Breads & Rice",
        "region": "All-India"
    },
    {
        "name": "Boondi Raita (Spiced Yogurt with Gram Crisps - 1 bowl)",
        "calories": 140.0,
        "protein": 5.0,
        "carbs": 12.0,
        "fat": 8.0,
        "fiber": 0.8,
        "sugar": 3.5,
        "sodium": 260.0,
        "category": "Breads & Rice",
        "region": "All-India"
    },
    {
        "name": "Cucumber Raita (Cooling Spiced Yogurt - 1 bowl)",
        "calories": 85.0,
        "protein": 4.5,
        "carbs": 7.0,
        "fat": 4.0,
        "fiber": 1.0,
        "sugar": 3.8,
        "sodium": 190.0,
        "category": "Breads & Rice",
        "region": "All-India"
    },
    {
        "name": "Plain Fresh Curd / Dahi (1 cup)",
        "calories": 100.0,
        "protein": 6.0,
        "carbs": 7.5,
        "fat": 4.5,
        "fiber": 0.0,
        "sugar": 6.0,
        "sodium": 75.0,
        "category": "Breads & Rice",
        "region": "All-India"
    },

    # =========================================================================
    # HEALTHY DESI SNACKS & STREET FOOD (नाश्ता एवं चाट)
    # =========================================================================
    {
        "name": "Roasted Phool Makhana (Roasted Fox Nuts - 1 bowl)",
        "calories": 105.0,
        "protein": 3.0,
        "carbs": 20.0,
        "fat": 1.5,
        "fiber": 2.5,
        "sugar": 0.2,
        "sodium": 140.0,
        "category": "Snacks & Chaat",
        "region": "All-India"
    },
    {
        "name": "Roasted Chana / Bhuna Chana (Roasted Bengal Gram - 50g)",
        "calories": 185.0,
        "protein": 11.0,
        "carbs": 29.0,
        "fat": 3.0,
        "fiber": 7.5,
        "sugar": 1.0,
        "sodium": 110.0,
        "category": "Snacks & Chaat",
        "region": "All-India"
    },
    {
        "name": "Sprouted Moong Salad (Sprouted Beans with Lemon - 1 bowl)",
        "calories": 120.0,
        "protein": 8.0,
        "carbs": 19.0,
        "fat": 1.2,
        "fiber": 6.0,
        "sugar": 2.5,
        "sodium": 95.0,
        "category": "Snacks & Chaat",
        "region": "All-India"
    },
    {
        "name": "Moong Dal Chilla (High Protein Lentil Crepe - 1 pc)",
        "calories": 135.0,
        "protein": 7.5,
        "carbs": 18.0,
        "fat": 4.0,
        "fiber": 4.0,
        "sugar": 1.0,
        "sodium": 220.0,
        "category": "Snacks & Chaat",
        "region": "All-India"
    },
    {
        "name": "Besan Chilla (Savory Gram Flour Veggie Pancake - 1 pc)",
        "calories": 145.0,
        "protein": 6.5,
        "carbs": 20.0,
        "fat": 4.5,
        "fiber": 3.5,
        "sugar": 1.2,
        "sodium": 240.0,
        "category": "Snacks & Chaat",
        "region": "All-India"
    },
    {
        "name": "Bhel Puri (Puffed Rice with Tangy Chutneys - 1 plate)",
        "calories": 210.0,
        "protein": 4.0,
        "carbs": 38.0,
        "fat": 5.0,
        "fiber": 3.0,
        "sugar": 6.5,
        "sodium": 390.0,
        "category": "Snacks & Chaat",
        "region": "All-India"
    },
    {
        "name": "Sev Puri (Flat Puris with Potatoes, Chutneys & Sev - 6 pcs)",
        "calories": 280.0,
        "protein": 5.0,
        "carbs": 40.0,
        "fat": 11.5,
        "fiber": 3.2,
        "sugar": 7.0,
        "sodium": 420.0,
        "category": "Snacks & Chaat",
        "region": "All-India"
    },
    {
        "name": "Pani Puri / Golgappa (Crispy Puris with Mint Water - 6 pcs)",
        "calories": 190.0,
        "protein": 3.5,
        "carbs": 32.0,
        "fat": 5.5,
        "fiber": 2.5,
        "sugar": 3.0,
        "sodium": 460.0,
        "category": "Snacks & Chaat",
        "region": "All-India"
    },
    {
        "name": "Vegetable Samosa (Crispy Potato & Pea Pastry - 1 pc)",
        "calories": 262.0,
        "protein": 3.5,
        "carbs": 32.0,
        "fat": 14.0,
        "fiber": 2.0,
        "sugar": 1.5,
        "sodium": 410.0,
        "category": "Snacks & Chaat",
        "region": "All-India"
    },
    {
        "name": "Aloo Tikki (Crispy Spiced Potato Cutlet - 2 pcs)",
        "calories": 240.0,
        "protein": 3.8,
        "carbs": 34.0,
        "fat": 10.5,
        "fiber": 3.0,
        "sugar": 2.0,
        "sodium": 380.0,
        "category": "Snacks & Chaat",
        "region": "All-India"
    },
    {
        "name": "Paneer Kathi Roll (Whole Wheat Roll with Grilled Paneer)",
        "calories": 320.0,
        "protein": 14.0,
        "carbs": 36.0,
        "fat": 14.0,
        "fiber": 3.8,
        "sugar": 2.5,
        "sodium": 430.0,
        "category": "Snacks & Chaat",
        "region": "All-India"
    },
    {
        "name": "Masala Sweet Corn (Steamed Corn with Spices & Butter)",
        "calories": 140.0,
        "protein": 3.5,
        "carbs": 26.0,
        "fat": 3.0,
        "fiber": 3.2,
        "sugar": 4.5,
        "sodium": 220.0,
        "category": "Snacks & Chaat",
        "region": "All-India"
    },
    {
        "name": "Roasted Masala Papad (Roasted Lentil Crisp with Veggies - 1 pc)",
        "calories": 65.0,
        "protein": 3.2,
        "carbs": 11.0,
        "fat": 0.8,
        "fiber": 2.0,
        "sugar": 1.0,
        "sodium": 240.0,
        "category": "Snacks & Chaat",
        "region": "All-India"
    },

    # =========================================================================
    # BEVERAGES & TRADITIONAL DRINKS (पारंपरिक पेय)
    # =========================================================================
    {
        "name": "Spiced Buttermilk (Chaas / Mattha - 1 glass)",
        "calories": 45.0,
        "protein": 3.0,
        "carbs": 4.5,
        "fat": 1.5,
        "fiber": 0.2,
        "sugar": 3.5,
        "sodium": 180.0,
        "category": "Drinks & Sweets",
        "region": "All-India"
    },
    {
        "name": "Sweet Punjabi Lassi (Creamy Yogurt Drink - 1 glass)",
        "calories": 210.0,
        "protein": 6.5,
        "carbs": 32.0,
        "fat": 7.0,
        "fiber": 0.0,
        "sugar": 26.0,
        "sodium": 95.0,
        "category": "Drinks & Sweets",
        "region": "All-India"
    },
    {
        "name": "Mango Lassi (Chilled Yogurt Mango Shake - 1 glass)",
        "calories": 240.0,
        "protein": 5.8,
        "carbs": 38.0,
        "fat": 7.5,
        "fiber": 1.0,
        "sugar": 32.0,
        "sodium": 85.0,
        "category": "Drinks & Sweets",
        "region": "All-India"
    },
    {
        "name": "Masala Chai (Ginger Cardamom Spiced Tea - 1 cup)",
        "calories": 85.0,
        "protein": 2.5,
        "carbs": 12.0,
        "fat": 3.0,
        "fiber": 0.0,
        "sugar": 9.0,
        "sodium": 35.0,
        "category": "Drinks & Sweets",
        "region": "All-India"
    },
    {
        "name": "Tender Coconut Water (Fresh Natural Drink - 1 coconut)",
        "calories": 45.0,
        "protein": 1.5,
        "carbs": 9.0,
        "fat": 0.5,
        "fiber": 2.5,
        "sugar": 6.0,
        "sodium": 105.0,
        "category": "Drinks & Sweets",
        "region": "All-India"
    },
    {
        "name": "Sattu Sharbat (High-Protein Roasted Gram Drink - 1 glass)",
        "calories": 140.0,
        "protein": 7.5,
        "carbs": 22.0,
        "fat": 2.5,
        "fiber": 5.0,
        "sugar": 1.5,
        "sodium": 190.0,
        "category": "Drinks & Sweets",
        "region": "All-India"
    },
    {
        "name": "Badam Milk (Saffron Almond Warm Milk - 1 cup)",
        "calories": 180.0,
        "protein": 6.5,
        "carbs": 20.0,
        "fat": 8.5,
        "fiber": 1.2,
        "sugar": 16.0,
        "sodium": 65.0,
        "category": "Drinks & Sweets",
        "region": "All-India"
    },
    {
        "name": "Nimbu Shikanji / Fresh Lime Water (1 glass)",
        "calories": 40.0,
        "protein": 0.4,
        "carbs": 10.0,
        "fat": 0.1,
        "fiber": 0.5,
        "sugar": 8.0,
        "sodium": 140.0,
        "category": "Drinks & Sweets",
        "region": "All-India"
    },

    # =========================================================================
    # TRADITIONAL DESI SWEETS & DESSERTS (पारंपरिक मिठाइयां)
    # =========================================================================
    {
        "name": "Rice Kheer (Cardamom Fragrant Rice Pudding - 1 bowl)",
        "calories": 220.0,
        "protein": 5.5,
        "carbs": 34.0,
        "fat": 7.5,
        "fiber": 0.5,
        "sugar": 22.0,
        "sodium": 70.0,
        "category": "Drinks & Sweets",
        "region": "All-India"
    },
    {
        "name": "Gajar Ka Halwa (Slow Cooked Carrot & Milk Pudding - 1 bowl)",
        "calories": 260.0,
        "protein": 4.5,
        "carbs": 36.0,
        "fat": 11.5,
        "fiber": 2.5,
        "sugar": 25.0,
        "sodium": 65.0,
        "category": "Drinks & Sweets",
        "region": "All-India"
    },
    {
        "name": "Gulab Jamun (Soft Khoya Balls in Rose Syrup - 2 pcs)",
        "calories": 300.0,
        "protein": 4.0,
        "carbs": 48.0,
        "fat": 11.0,
        "fiber": 0.5,
        "sugar": 38.0,
        "sodium": 55.0,
        "category": "Drinks & Sweets",
        "region": "All-India"
    },
    {
        "name": "Jalebi (Crispy Saffron Sugar Pretzels - 2 pcs)",
        "calories": 280.0,
        "protein": 2.5,
        "carbs": 52.0,
        "fat": 7.5,
        "fiber": 0.3,
        "sugar": 40.0,
        "sodium": 45.0,
        "category": "Drinks & Sweets",
        "region": "All-India"
    },
    {
        "name": "Besan Ladoo (Roasted Gram Flour & Ghee Sweet - 1 pc)",
        "calories": 180.0,
        "protein": 3.8,
        "carbs": 22.0,
        "fat": 9.0,
        "fiber": 1.8,
        "sugar": 14.0,
        "sodium": 35.0,
        "category": "Drinks & Sweets",
        "region": "All-India"
    },
    {
        "name": "Kaju Katli (Cashew Nut Silver Diamond - 2 pcs)",
        "calories": 170.0,
        "protein": 3.5,
        "carbs": 19.0,
        "fat": 9.0,
        "fiber": 0.8,
        "sugar": 13.0,
        "sodium": 15.0,
        "category": "Drinks & Sweets",
        "region": "All-India"
    },
    {
        "name": "Rasgulla (Spongy Cottage Cheese Sweet in Syrup - 2 pcs)",
        "calories": 190.0,
        "protein": 4.0,
        "carbs": 38.0,
        "fat": 2.5,
        "fiber": 0.2,
        "sugar": 34.0,
        "sodium": 30.0,
        "category": "Drinks & Sweets",
        "region": "East India"
    },
    {
        "name": "Sandesh (Delicate Bengali Chhena Sweet - 2 pcs)",
        "calories": 150.0,
        "protein": 4.5,
        "carbs": 21.0,
        "fat": 5.5,
        "fiber": 0.2,
        "sugar": 16.0,
        "sodium": 25.0,
        "category": "Drinks & Sweets",
        "region": "East India"
    }
]

HINDI_PHONETIC_MAP = {
    "दाल": ["dal", "lentil"],
    "daal": ["dal"],
    "dhal": ["dal"],
    "पनीर": ["paneer"],
    "panir": ["paneer"],
    "रोटी": ["roti", "chapati", "naan", "kulcha"],
    "fulka": ["roti", "chapati"],
    "phulka": ["roti", "chapati"],
    "चावल": ["rice", "biryani", "khichdi"],
    "briyani": ["biryani"],
    "समोसा": ["samosa"],
    "samose": ["samosa"],
    "इडली": ["idli"],
    "डोसा": ["dosa"],
    "dhosa": ["dosa"],
    "छोले": ["chole", "chana", "bhature"],
    "chhole": ["chole"],
    "राजमा": ["rajma"],
    "चिकन": ["chicken", "murgh"],
    "लस्सी": ["lassi"],
    "छाछ": ["buttermilk", "chaas"],
    "chaas": ["buttermilk"],
    "पोहा": ["poha"],
    "ढोकला": ["dhokla"],
    "जलेबी": ["jalebi"]
}

def get_dish_image_url(name: str, category: str = "") -> str:
    lower = name.lower()
    if "chole bhature" in lower or "bhature" in lower or "bhatura" in lower:
        return "https://images.pexels.com/photos/11818239/pexels-photo-11818239.jpeg?auto=compress&cs=tinysrgb&w=600"
    if "chole" in lower or "chana masala" in lower:
        return "https://images.pexels.com/photos/8996219/pexels-photo-8996219.jpeg?auto=compress&cs=tinysrgb&w=600"
    if "rajma" in lower:
        return "https://images.pexels.com/photos/12737912/pexels-photo-12737912.jpeg?auto=compress&cs=tinysrgb&w=600"
    if "dal makhani" in lower:
        return "https://images.pexels.com/photos/37182513/pexels-photo-37182513/free-photo-of-dal-makhani-with-butter-on-yellow-tablecloth.jpeg?auto=compress&cs=tinysrgb&w=600"
    if "dal tadka" in lower or "yellow dal" in lower or "dal" in lower:
        return "https://images.pexels.com/photos/33379362/pexels-photo-33379362/free-photo-of-delicious-indian-tadka-dal-with-fresh-ingredients.jpeg?auto=compress&cs=tinysrgb&w=600"
    if "palak paneer" in lower:
        return "https://images.pexels.com/photos/31249589/pexels-photo-31249589/free-photo-of-delicious-indian-palak-paneer-dish-top-view.jpeg?auto=compress&cs=tinysrgb&w=600"
    if "paneer tikka" in lower:
        return "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?auto=format&fit=crop&w=600&q=80"
    if "paneer" in lower:
        return "https://images.pexels.com/photos/9609838/pexels-photo-9609838.jpeg?auto=compress&cs=tinysrgb&w=600"
    if "dosa" in lower or "uttapam" in lower or "chilla" in lower:
        return "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?auto=format&fit=crop&w=600&q=80"
    if "idli" in lower:
        return "https://images.pexels.com/photos/4331491/pexels-photo-4331491.jpeg?auto=compress&cs=tinysrgb&w=600"
    if "vada" in lower and "vada pav" not in lower:
        return "https://images.pexels.com/photos/9619560/pexels-photo-9619560.jpeg?auto=compress&cs=tinysrgb&w=600"
    if "sambar" in lower or "rasam" in lower:
        return "https://images.pexels.com/photos/35041668/pexels-photo-35041668/free-photo-of-south-indian-sambar-in-stainless-steel-saucepan.jpeg?auto=compress&cs=tinysrgb&w=600"
    if "biryani" in lower:
        return "https://images.pexels.com/photos/9738983/pexels-photo-9738983.jpeg?auto=compress&cs=tinysrgb&w=600"
    if "pulao" in lower or "rice" in lower or "khichdi" in lower or "pongal" in lower:
        return "https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=600&q=80"
    if "paratha" in lower or "thepla" in lower or "kulcha" in lower:
        return "https://images.pexels.com/photos/33428723/pexels-photo-33428723.jpeg?auto=compress&cs=tinysrgb&w=600"
    if "roti" in lower or "chapati" in lower or "phulka" in lower:
        return "https://images.pexels.com/photos/13084520/pexels-photo-13084520.jpeg?auto=compress&cs=tinysrgb&w=600"
    if "naan" in lower:
        return "https://images.pexels.com/photos/5835339/pexels-photo-5835339.jpeg?auto=compress&cs=tinysrgb&w=600"
    if "butter chicken" in lower or "chicken curry" in lower or "chettinad" in lower:
        return "https://images.pexels.com/photos/37295815/pexels-photo-37295815/free-photo-of-delicious-butter-chicken-in-creamy-sauce.jpeg?auto=compress&cs=tinysrgb&w=600"
    if "tandoori chicken" in lower:
        return "https://images.pexels.com/photos/36895285/pexels-photo-36895285/free-photo-of-spicy-tandoori-chicken-with-lime-on-wooden-board.jpeg?auto=compress&cs=tinysrgb&w=600"
    if "fish" in lower or "macher" in lower:
        return "https://images.pexels.com/photos/13243817/pexels-photo-13243817.jpeg?auto=compress&cs=tinysrgb&w=600"
    if "mutton" in lower or "rogan josh" in lower:
        return "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=600&q=80"
    if "samosa" in lower:
        return "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=600&q=80"
    if "pav bhaji" in lower or "misal" in lower:
        return "https://images.pexels.com/photos/7625089/pexels-photo-7625089.jpeg?auto=compress&cs=tinysrgb&w=600"
    if "vada pav" in lower:
        return "https://images.pexels.com/photos/34682732/pexels-photo-34682732/free-photo-of-delicious-indian-snack-vada-pav-with-spicy-chili.jpeg?auto=compress&cs=tinysrgb&w=600"
    if "poha" in lower:
        return "https://images.unsplash.com/photo-1645177628172-a94c1f96e6db?auto=format&fit=crop&w=600&q=80"
    if "dhokla" in lower or "khandvi" in lower:
        return "https://images.unsplash.com/photo-1714799263291-272975db795a?auto=format&fit=crop&w=600&q=80"
    if "momo" in lower:
        return "https://images.pexels.com/photos/28445593/pexels-photo-28445593/free-photo-of-nepalese-momos-with-spicy-dipping-sauce-on-marble.jpeg?auto=compress&cs=tinysrgb&w=600"
    if "pani puri" in lower or "golgappa" in lower or "chaat" in lower or "bhel" in lower or "sev puri" in lower:
        return "https://images.pexels.com/photos/13063312/pexels-photo-13063312.jpeg?auto=compress&cs=tinysrgb&w=600"
    if "chai" in lower or "tea" in lower:
        return "https://images.pexels.com/photos/10377676/pexels-photo-10377676.jpeg?auto=compress&cs=tinysrgb&w=600"
    if "lassi" in lower or "chaas" in lower or "buttermilk" in lower:
        return "https://images.pexels.com/photos/14509267/pexels-photo-14509267.jpeg?auto=compress&cs=tinysrgb&w=600"
    if "coconut water" in lower:
        return "https://images.unsplash.com/photo-1525385133512-2f3bdd039054?auto=format&fit=crop&w=600&q=80"
    if "gulab jamun" in lower:
        return "https://images.pexels.com/photos/7406887/pexels-photo-7406887.jpeg?auto=compress&cs=tinysrgb&w=600"
    if "jalebi" in lower:
        return "https://images.pexels.com/photos/39852669/pexels-photo-39852669.jpeg?auto=compress&cs=tinysrgb&w=600"
    if "kheer" in lower or "payasam" in lower:
        return "https://images.pexels.com/photos/31109623/pexels-photo-31109623.jpeg?auto=compress&cs=tinysrgb&w=600"
    if "halwa" in lower:
        return "https://images.pexels.com/photos/20689161/pexels-photo-20689161.jpeg?auto=compress&cs=tinysrgb&w=600"
    if "sweet" in lower or "ladoo" in lower or "kaju" in lower or "rasgulla" in lower:
        return "https://images.unsplash.com/photo-1599488615731-7e5c2823ff28?auto=format&fit=crop&w=600&q=80"
    if "makhana" in lower or "sprout" in lower or "chana" in lower:
        return "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=600&q=80"
    return "https://images.pexels.com/photos/8996219/pexels-photo-8996219.jpeg?auto=compress&cs=tinysrgb&w=600"

# Enrich dataset with authentic image URLs
for dish in INDIAN_FOOD_DATASET:
    if "image_url" not in dish or not dish["image_url"]:
        dish["image_url"] = get_dish_image_url(dish["name"], dish.get("category", ""))

def search_indian_food(query: str) -> List[Dict[str, Any]]:
    """Filters dishes by name, category, or region containing the query string (supports English & Hindi)."""
    q = query.strip().lower()
    if not q:
        return INDIAN_FOOD_DATASET

    aliases = [q]
    if q in HINDI_PHONETIC_MAP:
        aliases.extend(HINDI_PHONETIC_MAP[q])

    results = []
    for dish in INDIAN_FOOD_DATASET:
        name_lower = dish["name"].lower()
        cat_lower = (dish.get("category") or "").lower()
        reg_lower = (dish.get("region") or "").lower()
        if any(a in name_lower or a in cat_lower or a in reg_lower for a in aliases):
            results.append(dish)
    return results

