# -*- coding: utf-8 -*-
"""
Generates SQL for all 64 Districts and Upazilas of Bangladesh.
Division IDs:
  Dhaka: 2
  Chattogram: 5
  Rajshahi: 6
  Khulna: 7
  Barishal: 8
  Sylhet: 9
  Rangpur: 10
  Mymensingh: 11
"""

districts_data = [
    # Dhaka Division (Parent 2)
    (3, 2, "DHAKA_DIST", "ঢাকা জেলা", "Dhaka District"),
    (102, 2, "GAZIPUR_DIST", "গাজীপুর জেলা", "Gazipur District"),
    (103, 2, "NARAYANGANJ_DIST", "নারায়ণগঞ্জ জেলা", "Narayanganj District"),
    (104, 2, "TANGAIL_DIST", "টাঙ্গাইল জেলা", "Tangail District"),
    (105, 2, "KISHOREGANJ_DIST", "কিশোরগঞ্জ জেলা", "Kishoreganj District"),
    (106, 2, "MANIKGANJ_DIST", "মানিকগঞ্জ জেলা", "Manikganj District"),
    (107, 2, "MUNSHIGANJ_DIST", "মুন্সীগঞ্জ জেলা", "Munshiganj District"),
    (108, 2, "NARSINGDI_DIST", "নরসিংদী জেলা", "Narsingdi District"),
    (109, 2, "FARIDPUR_DIST", "ফরিদপুর জেলা", "Faridpur District"),
    (110, 2, "GOPALGANJ_DIST", "গোপালগঞ্জ জেলা", "Gopalganj District"),
    (111, 2, "MADARIPUR_DIST", "মাদারীপুর জেলা", "Madaripur District"),
    (112, 2, "RAJBARI_DIST", "রাজবাড়ী জেলা", "Rajbari District"),
    (113, 2, "SHARIATPUR_DIST", "শরীয়তপুর জেলা", "Shariatpur District"),

    # Chattogram Division (Parent 5)
    (114, 5, "CHATTOGRAM_DIST", "চট্টগ্রাম জেলা", "Chattogram District"),
    (115, 5, "COXS_BAZAR_DIST", "কক্সবাজার জেলা", "Cox's Bazar District"),
    (116, 5, "CUMILLA_DIST", "কুমিল্লা জেলা", "Cumilla District"),
    (117, 5, "FENI_DIST", "ফেনী জেলা", "Feni District"),
    (118, 5, "BRAHMANBARIA_DIST", "ব্রাহ্মণবাড়িয়া জেলা", "Brahmanbaria District"),
    (119, 5, "RANGAMATI_DIST", "রাঙ্গামাটি জেলা", "Rangamati District"),
    (120, 5, "NOAKHALI_DIST", "নোয়াখালী জেলা", "Noakhali District"),
    (121, 5, "CHANDPUR_DIST", "চাঁদপুর জেলা", "Chandpur District"),
    (122, 5, "LAKSHMIPUR_DIST", "লক্ষ্মীপুর জেলা", "Lakshmipur District"),
    (123, 5, "KHAGRACHHARI_DIST", "খাগড়াছড়ি জেলা", "Khagrachhari District"),
    (124, 5, "BANDARBAN_DIST", "বান্দরবান জেলা", "Bandarban District"),

    # Rajshahi Division (Parent 6)
    (125, 6, "RAJSHAHI_DIST", "রাজশাহী জেলা", "Rajshahi District"),
    (126, 6, "BOGURA_DIST", "বগুড়া জেলা", "Bogura District"),
    (127, 6, "PABNA_DIST", "পাবনা জেলা", "Pabna District"),
    (128, 6, "SIRAJGANJ_DIST", "সিরাজগঞ্জ জেলা", "Sirajganj District"),
    (129, 6, "NAOGAON_DIST", "নওগাঁ জেলা", "Naogaon District"),
    (130, 6, "NATORE_DIST", "নাটোর জেলা", "Natore District"),
    (131, 6, "CHAPAINAWABGANJ_DIST", "চাঁপাইনবাবগঞ্জ জেলা", "Chapainawabganj District"),
    (132, 6, "JOYPURHAT_DIST", "জয়পুরহাট জেলা", "Joypurhat District"),

    # Khulna Division (Parent 7)
    (133, 7, "KHULNA_DIST", "খুলনা জেলা", "Khulna District"),
    (134, 7, "JASHORE_DIST", "যশোর জেলা", "Jashore District"),
    (135, 7, "SATKHIRA_DIST", "সাতক্ষীরা জেলা", "Satkhira District"),
    (136, 7, "BAGERHAT_DIST", "বাগেরহাট জেলা", "Bagerhat District"),
    (137, 7, "KUSHTIA_DIST", "কুষ্টিয়া জেলা", "Kushtia District"),
    (138, 7, "JHENAIDAH_DIST", "ঝিনাইদহ জেলা", "Jhenaidah District"),
    (139, 7, "CHUADANGA_DIST", "চুয়াডাঙ্গা জেলা", "Chuadanga District"),
    (140, 7, "MAGURA_DIST", "মাগুরা জেলা", "Magura District"),
    (141, 7, "MEHERPUR_DIST", "মেহেরপুর জেলা", "Meherpur District"),
    (142, 7, "NARAIL_DIST", "নড়াইল জেলা", "Narail District"),

    # Barishal Division (Parent 8)
    (143, 8, "BARISHAL_DIST", "বরিশাল জেলা", "Barishal District"),
    (144, 8, "BHOLA_DIST", "ভোলা জেলা", "Bhola District"),
    (145, 8, "PATUAKHALI_DIST", "পটুয়াখালী জেলা", "Patuakhali District"),
    (146, 8, "PIROJPUR_DIST", "পিরোজপুর জেলা", "Pirojpur District"),
    (147, 8, "BARGUNA_DIST", "বরগুনা জেলা", "Barguna District"),
    (148, 8, "JHALOKATI_DIST", "ঝালকাঠি জেলা", "Jhalokati District"),

    # Sylhet Division (Parent 9)
    (149, 9, "SYLHET_DIST", "সিলেট জেলা", "Sylhet District"),
    (150, 9, "MOULVIBAZAR_DIST", "মৌলভীবাজার জেলা", "Moulvibazar District"),
    (151, 9, "HABIGANJ_DIST", "হবিগঞ্জ জেলা", "Habiganj District"),
    (152, 9, "SUNAMGANJ_DIST", "সুনামগঞ্জ জেলা", "Sunamganj District"),

    # Rangpur Division (Parent 10)
    (153, 10, "RANGPUR_DIST", "রংপুর জেলা", "Rangpur District"),
    (154, 10, "DINAJPUR_DIST", "দিনাজপুর জেলা", "Dinajpur District"),
    (155, 10, "KURIGRAM_DIST", "কুড়িগ্রাম জেলা", "Kurigram District"),
    (156, 10, "GAIBANDHA_DIST", "গাইবান্ধা জেলা", "Gaibandha District"),
    (157, 10, "NILPHAMARI_DIST", "নীলফামারী জেলা", "Nilphamari District"),
    (158, 10, "PANCHAGARH_DIST", "পঞ্চগড় জেলা", "Panchagarh District"),
    (159, 10, "THAKURGAON_DIST", "ঠাকুরগাঁও জেলা", "Thakurgaon District"),
    (160, 10, "LALMONIRHAT_DIST", "লালমনিরহাট জেলা", "Lalmonirhat District"),

    # Mymensingh Division (Parent 11)
    (161, 11, "MYMENSINGH_DIST", "ময়মনসিংহ জেলা", "Mymensingh District"),
    (162, 11, "JAMALPUR_DIST", "জামালপুর জেলা", "Jamalpur District"),
    (163, 11, "NETROKONA_DIST", "নেত্রকোণা জেলা", "Netrokona District"),
    (164, 11, "SHERPUR_DIST", "শেরপুর জেলা", "Sherpur District"),
]

upazilas_by_district = {
    # Dhaka (3)
    3: [
        ("UPZ_SAVAR", "সাভার", "Savar"),
        ("UPZ_DHAMRAI", "ধামরাই", "Dhamrai"),
        ("UPZ_KERANIGANJ", "কেরানীগঞ্জ", "Keraniganj"),
        ("UPZ_NAWABGANJ_DHAKA", "নবাবগঞ্জ", "Nawabganj"),
        ("UPZ_DOHAR", "দোহার", "Dohar"),
        ("UPZ_TEJGAON", "তেজগাঁও", "Tejgaon"),
        ("UPZ_MIRPUR", "মিরপুর", "Mirpur"),
        ("UPZ_DHANMONDI", "ধানমন্ডি", "Dhanmondi"),
        ("UPZ_GULSHAN", "গুলশান", "Gulshan"),
        ("UPZ_UTTARA", "উত্তরা", "Uttara")
    ],
    # Gazipur (102)
    102: [
        ("UPZ_GAZIPUR_SADAR", "গাজীপুর সদর", "Gazipur Sadar"),
        ("UPZ_KALIAKAIR", "কালিয়াকৈর", "Kaliakair"),
        ("UPZ_KALIGANJ_GAZIPUR", "কালীগঞ্জ", "Kaliganj"),
        ("UPZ_KAPASIA", "কাপাসিয়া", "Kapasia"),
        ("UPZ_SREEPUR_GAZIPUR", "শ্রীপুর", "Sreepur")
    ],
    # Narayanganj (103)
    103: [
        ("UPZ_NARAYANGANJ_SADAR", "নারায়ণগঞ্জ সদর", "Narayanganj Sadar"),
        ("UPZ_BANDAR", "বন্দর", "Bandar"),
        ("UPZ_RUPGANJ", "রূপগঞ্জ", "Rupganj"),
        ("UPZ_SONARGAON", "সোনারগাঁও", "Sonargaon"),
        ("UPZ_ARAIHAZAR", "আড়াইহাজার", "Araihazar")
    ],
    # Tangail (104)
    104: [
        ("UPZ_TANGAIL_SADAR", "টাঙ্গাইল সদর", "Tangail Sadar"),
        ("UPZ_MIRZAPUR", "মির্জাপুর", "Mirzapur"),
        ("UPZ_GHATAIL", "ঘাটাইল", "Ghatail"),
        ("UPZ_MADHUPUR", "মধুপুর", "Madhupur"),
        ("UPZ_KALIHATI", "কালিহাতী", "Kalihati"),
        ("UPZ_GOPALPUR_TANGAIL", "গোপালপুর", "Gopalpur"),
        ("UPZ_SAKSHIPUR", "সখিপুর", "Sakhipur"),
        ("UPZ_BASAIL", "বাসাইল", "Basail"),
        ("UPZ_DELDUAR", "দেলদুয়ার", "Delduar"),
        ("UPZ_NAGARPUR", "নাগরপুর", "Nagarpur"),
        ("UPZ_BHUAPUR", "ভূঞাপুর", "Bhuapur"),
        ("UPZ_DHANBARI", "ধনবাড়ী", "Dhanbari")
    ],
    # Kishoreganj (105)
    105: [
        ("UPZ_KISHOREGANJ_SADAR", "কিশোরগঞ্জ সদর", "Kishoreganj Sadar"),
        ("UPZ_BHAIRAB", "ভৈরব", "Bhairab"),
        ("UPZ_BAJITPUR", "বাজিতপুর", "Bajitpur"),
        ("UPZ_KATIADI", "কটিয়াদী", "Katiadi"),
        ("UPZ_KARIMGANJ", "করিমগঞ্জ", "Karimganj"),
        ("UPZ_PAKUNDIA", "পাকুন্দিয়া", "Pakundia"),
        ("UPZ_KULLIARCHAR", "কুলিয়ারচর", "Kuliarchar"),
        ("UPZ_HOSSAINPUR", "হোসেনপুর", "Hossainpur"),
        ("UPZ_TARIAL", "তাড়াইল", "Tarail"),
        ("UPZ_ITNA", "ইটনা", "Itna"),
        ("UPZ_MITHAMOIN", "মিঠামইন", "Mithamoin"),
        ("UPZ_AUSTAGRAM", "অষ্টগ্রাম", "Austagram"),
        ("UPZ_NIKLI", "নিকলী", "Nikli")
    ],
    # Manikganj (106)
    106: [
        ("UPZ_MANIKGANJ_SADAR", "মানিকগঞ্জ সদর", "Manikganj Sadar"),
        ("UPZ_SINGAIR", "সিংগাইর", "Singair"),
        ("UPZ_SHIBALAYA", "শিবালয়", "Shibalaya"),
        ("UPZ_SATURIA", "সাটুরিয়া", "Saturia"),
        ("UPZ_HARIRAMPUR", "হরিরামপুর", "Harirampur"),
        ("UPZ_GHIOR", "ঘিওর", "Ghior"),
        ("UPZ_DAULATPUR_MANIKGANJ", "দৌলতপুর", "Daulatpur")
    ],
    # Munshiganj (107)
    107: [
        ("UPZ_MUNSHIGANJ_SADAR", "মুন্সীগঞ্জ সদর", "Munshiganj Sadar"),
        ("UPZ_SREENAGAR", "শ্রীনগর", "Sreenagar"),
        ("UPZ_SIRAJDIKHAN", "সিরাজদিখান", "Sirajdikhan"),
        ("UPZ_LOUHAJANG", "লৌহজং", "Louhajang"),
        ("UPZ_TONGIBARI", "টংগিবাড়ী", "Tongibari"),
        ("UPZ_GAZARIA", "গজারিয়া", "Gazaria")
    ],
    # Narsingdi (108)
    108: [
        ("UPZ_NARSINGDI_SADAR", "নরসিংদী সদর", "Narsingdi Sadar"),
        ("UPZ_PALASH", "পলাশ", "Palash"),
        ("UPZ_SHIBPUR", "শিবপুর", "Shibpur"),
        ("UPZ_RAIPURA", "রায়পুরা", "Raipura"),
        ("UPZ_BELABO", "বেলাবো", "Belabo"),
        ("UPZ_MONOHARDI", "মনোহরদী", "Monohardi")
    ],
    # Faridpur (109)
    109: [
        ("UPZ_FARIDPUR_SADAR", "ফরিদপুর সদর", "Faridpur Sadar"),
        ("UPZ_BOALMARI", "বোয়ালমারী", "Boalmari"),
        ("UPZ_BHANGA", "ভাঙ্গা", "Bhanga"),
        ("UPZ_ALFADANGA", "আলফাডাঙ্গা", "Alfadanga"),
        ("UPZ_MADHUKHALI", "মধুখালী", "Madhukhali"),
        ("UPZ_NAGARKANDA", "নগরকান্দা", "Nagarkanda"),
        ("UPZ_CHARBHADRASAN", "চরভদ্রাসন", "Charbhadrasan"),
        ("UPZ_SADARPUR", "সদরপুর", "Sadarpur"),
        ("UPZ_SALTHA", "সালথা", "Saltha")
    ],
    # Gopalganj (110)
    110: [
        ("UPZ_GOPALGANJ_SADAR", "গোপালগঞ্জ সদর", "Gopalganj Sadar"),
        ("UPZ_KASHIANI", "কাশিয়ানী", "Kashiani"),
        ("UPZ_KOTALIPARA", "কোটালীপাড়া", "Kotalipara"),
        ("UPZ_MUKSUDPUR", "মুকসুদপুর", "Muksudpur"),
        ("UPZ_TUNGIPARA", "টুঙ্গিপাড়া", "Tungipara")
    ],
    # Madaripur (111)
    111: [
        ("UPZ_MADARIPUR_SADAR", "মাদারীপুর সদর", "Madaripur Sadar"),
        ("UPZ_SHIBCHAR", "শিবচর", "Shibchar"),
        ("UPZ_KALKINI", "কালকিনি", "Kalkini"),
        ("UPZ_RAJOIR", "রাজৈর", "Rajoir"),
        ("UPZ_DASAR", "ডাসার", "Dasar")
    ],
    # Rajbari (112)
    112: [
        ("UPZ_RAJBARI_SADAR", "রাজবাড়ী সদর", "Rajbari Sadar"),
        ("UPZ_GOALANDA", "গোয়ালন্দ", "Goalanda"),
        ("UPZ_PANGSHA", "পাংশা", "Pangsha"),
        ("UPZ_BALIAKANDI", "বালিয়াকান্দি", "Baliakandi"),
        ("UPZ_KALUKHALI", "কালুখালী", "Kalukhali")
    ],
    # Shariatpur (113)
    113: [
        ("UPZ_SHARIATPUR_SADAR", "শরীয়তপুর সদর", "Shariatpur Sadar"),
        ("UPZ_NARIA", "নড়িয়া", "Naria"),
        ("UPZ_ZAJIRA", "জাজিরা", "Zajira"),
        ("UPZ_GOSAIRHAT", "গোসাইরহাট", "Gosairhat"),
        ("UPZ_BHEDARGANJ", "ভেদরগঞ্জ", "Bhedarganj"),
        ("UPZ_DAMUDYA", "ডামুড্যা", "Damudya")
    ],

    # Chattogram (114)
    114: [
        ("UPZ_KOTWALI_CHATTOGRAM", "কোতোয়ালী", "Kotwali"),
        ("UPZ_HATHAZARI", "হাটহাজারী", "Hathazari"),
        ("UPZ_RAOZAN", "রাউজান", "Raozan"),
        ("UPZ_RANGUNIA", "রাঙ্গুনিয়া", "Rangunia"),
        ("UPZ_SITAKUNDA", "সীতাকুণ্ড", "Sitakunda"),
        ("UPZ_MIRSHARAI", "মীরসরাই", "Mirsharai"),
        ("UPZ_PATIYA", "পটিয়া", "Patiya"),
        ("UPZ_BOALKHALI", "বোয়ালখালী", "Boalkhali"),
        ("UPZ_ANWARA", "আনোয়ারা", "Anwara"),
        ("UPZ_CHANDANAISH", "চন্দনাইশ", "Chandanaish"),
        ("UPZ_BANSHKHALI", "বাঁশখালী", "Banshkhali"),
        ("UPZ_LOHAGARA_CHATTOGRAM", "লোহাগাড়া", "Lohagara"),
        ("UPZ_SATKANIA", "সাতকানিয়া", "Satkania"),
        ("UPZ_FATIKCHHARI", "ফটিকছড়ি", "Fatikchhari"),
        ("UPZ_KARNAPHULI", "কর্ণফুলী", "Karnaphuli")
    ],
    # Cox's Bazar (115)
    115: [
        ("UPZ_COXS_BAZAR_SADAR", "কক্সবাজার সদর", "Cox's Bazar Sadar"),
        ("UPZ_CHAKARIA", "চকোরিয়া", "Chakaria"),
        ("UPZ_MAHESHKHALI", "মহেশখালী", "Maheshkhali"),
        ("UPZ_TEKNAF", "টেকনাফ", "Teknaf"),
        ("UPZ_RAMU", "রামু", "Ramu"),
        ("UPZ_UKHIYA", "উখিয়া", "Ukhiya"),
        ("UPZ_PEKUA", "পেকুয়া", "Pekua"),
        ("UPZ_KUTUBDIA", "কুতুবদিয়া", "Kutubdia"),
        ("UPZ_EIDGAON", "ঈদগাঁও", "Eidgaon")
    ],
    # Cumilla (116)
    116: [
        ("UPZ_CUMILLA_ADARSHA_SADAR", "কুমিল্লা আদর্শ সদর", "Cumilla Adarsha Sadar"),
        ("UPZ_CUMILLA_SADAR_DAKSHIN", "কুমিল্লা সদর দক্ষিণ", "Cumilla Sadar Dakshin"),
        ("UPZ_DAUDKANDI", "দাউদকান্দি", "Daudkandi"),
        ("UPZ_CHANDINA", "চান্দিনা", "Chandina"),
        ("UPZ_DEBIDWAR", "দেবিদ্বার", "Debidwar"),
        ("UPZ_HOMNA", "হোমনা", "Homna"),
        ("UPZ_LAKSAM", "লাকসাম", "Laksam"),
        ("UPZ_MURADNAGAR", "মুরাদনগর", "Muradnagar"),
        ("UPZ_BURICHANG", "বুড়িচং", "Burichang"),
        ("UPZ_BRAHMANPARA", "ব্রাহ্মণপাড়া", "Brahmanpara"),
        ("UPZ_CHAUDDAGRAM", "চৌদ্দগ্রাম", "Chauddagram"),
        ("UPZ_BARURA", "বরুড়া", "Barura"),
        ("UPZ_MEGHNA", "মেঘনা", "Meghna"),
        ("UPZ_MONOHARGONJ", "মনোহরগঞ্জ", "Monohargonj"),
        ("UPZ_TITAS", "তিতাস", "Titas"),
        ("UPZ_LALMAI", "লালমাই", "Lalmai")
    ],
    # Feni (117)
    117: [
        ("UPZ_FENI_SADAR", "ফেনী সদর", "Feni Sadar"),
        ("UPZ_DAGANBHUIYAN", "দাগনভূঞা", "Daganbhuiyan"),
        ("UPZ_CHHAGALNAIYA", "ছাগলনাইয়া", "Chhagalnaiya"),
        ("UPZ_SONAGAZI", "সোনাগাজী", "Sonagazi"),
        ("UPZ_PARSHURAM", "পরশুরাম", "Parshuram"),
        ("UPZ_FULGAZI", "ফুলগাজী", "Fulgazi")
    ],
    # Brahmanbaria (118)
    118: [
        ("UPZ_BRAHMANBARIA_SADAR", "ব্রাহ্মণবাড়িয়া সদর", "Brahmanbaria Sadar"),
        ("UPZ_KASBA", "কসবা", "Kasba"),
        ("UPZ_NABINAGAR", "নবীনগর", "Nabinagar"),
        ("UPZ_SARIL", "সরাইল", "Sarail"),
        ("UPZ_ASHUGANJ", "আশুগঞ্জ", "Ashuganj"),
        ("UPZ_AKHAURA", "আখাউড়া", "Akhaura"),
        ("UPZ_BANCHARAMPUR", "বাঞ্ছারামপুর", "Bancharampur"),
        ("UPZ_BIJOYNAGAR", "বিজয়নগর", "Bijoynagar"),
        ("UPZ_NASIRNAGAR", "নাসিরনগর", "Nasirnagar")
    ],
    # Rangamati (119)
    119: [
        ("UPZ_RANGAMATI_SADAR", "রাঙ্গামাটি সদর", "Rangamati Sadar"),
        ("UPZ_KAPTAI", "কাপ্তাই", "Kaptai"),
        ("UPZ_BAGHAICHHARI", "বাঘাইছড়ি", "Baghaichhari"),
        ("UPZ_BARKAL", "বরকল", "Barkal"),
        ("UPZ_KAWKH уз", "কাউখালী", "Kawkhali"),
        ("UPZ_LANGADU", "লংগদু", "Langadu"),
        ("UPZ_NANIARCHAR", "নানিয়ারচর", "Naniarchar"),
        ("UPZ_RAJASTHALI", "রাজস্থলী", "Rajasthali"),
        ("UPZ_BELAICHHARI", "বিলাইছড়ি", "Belaichhari"),
        ("UPZ_JURAICHHARI", "জুরাইছড়ি", "Juraichhari")
    ],
    # Noakhali (120)
    120: [
        ("UPZ_NOAKHALI_SADAR", "নোয়াখালী সদর", "Noakhali Sadar"),
        ("UPZ_BEGUMGANJ", "বেগমগঞ্জ", "Begumganj"),
        ("UPZ_CHATKHIL", "চাটখিল", "Chatkhil"),
        ("UPZ_COMPANIGANJ_NOAKHALI", "কোম্পানীগঞ্জ", "Companiganj"),
        ("UPZ_HATIYA", "হাতিয়া", "Hatiya"),
        ("UPZ_SENBAGH", "সেনবাগ", "Senbagh"),
        ("UPZ_SUBARNACHAR", "সুবর্ণচর", "Subarnachar"),
        ("UPZ_SONAIMURI", "সোনাইমুড়ী", "Sonaimuri"),
        ("UPZ_KABIRHAT", "কবিরহাট", "Kabirhat")
    ],
    # Chandpur (121)
    121: [
        ("UPZ_CHANDPUR_SADAR", "চাঁদপুর সদর", "Chandpur Sadar"),
        ("UPZ_HAJIGANJ", "হাজীগঞ্জ", "Hajiganj"),
        ("UPZ_FARIDGANJ", "ফরিদগঞ্জ", "Faridganj"),
        ("UPZ_KACHUA_CHANDPUR", "কচুয়া", "Kachua"),
        ("UPZ_SHAHRASTI", "শাহরাস্তি", "Shahrasti"),
        ("UPZ_MATLAB_UTTAR", "মতলব উত্তর", "Matlab Uttar"),
        ("UPZ_MATLAB_DAKSHIN", "মতলব দক্ষিণ", "Matlab Dakshin"),
        ("UPZ_HAIMCHAR", "হাইমচর", "Haimchar")
    ],
    # Lakshmipur (122)
    122: [
        ("UPZ_LAKSHMIPUR_SADAR", "লক্ষ্মীপুর সদর", "Lakshmipur Sadar"),
        ("UPZ_RAIPUR", "রায়পুর", "Raipur"),
        ("UPZ_RAMGANJ", "রামগঞ্জ", "Ramganj"),
        ("UPZ_RAMGATI", "রামগতি", "Ramgati"),
        ("UPZ_KAMALNAGAR", "কমলনগর", "Kamalnagar")
    ],
    # Khagrachhari (123)
    123: [
        ("UPZ_KHAGRACHHARI_SADAR", "খাগড়াছড়ি সদর", "Khagrachhari Sadar"),
        ("UPZ_DIGHINALA", "দিঘীনালা", "Dighinala"),
        ("UPZ_PANCHHARI", "পানছড়ি", "Panchhari"),
        ("UPZ_MAHALCHHARI", "মহালছড়ি", "Mahalchhari"),
        ("UPZ_MATIRANGA", "মাটিরাঙ্গা", "Matiranga"),
        ("UPZ_MANIKCHHARI", "মানিকছড়ি", "Manikchhari"),
        ("UPZ_RAMGARH", "রামগড়", "Ramgarh"),
        ("UPZ_LAKSHMICHHARI", "লক্ষ্মীছড়ি", "Lakshmichhari"),
        ("UPZ_GUIMARA", "গুইমারা", "Guimara")
    ],
    # Bandarban (124)
    124: [
        ("UPZ_BANDARBAN_SADAR", "বান্দরবান সদর", "Bandarban Sadar"),
        ("UPZ_ROWANGCHHARI", "রোয়াংছড়ি", "Rowangchhari"),
        ("UPZ_RUMA", "রুমা", "Ruma"),
        ("UPZ_THANCHI", "থানচি", "Thanchi"),
        ("UPZ_LAMA", "লামা", "Lama"),
        ("UPZ_ALIKADAM", "আলীকদম", "Alikadam"),
        ("UPZ_NAIKHONGCHHARI", "নাইক্ষ্যংছড়ি", "Naikhongchhari")
    ],

    # Rajshahi (125)
    125: [
        ("UPZ_PABA", "পবা", "Paba"),
        ("UPZ_GODAGARI", "গোদাগাড়ী", "Godagari"),
        ("UPZ_TANORE", "তানোর", "Tanore"),
        ("UPZ_MOHANPUR", "মোহনপুর", "Mohanpur"),
        ("UPZ_BAGMARA", "বাগমারা", "Bagmara"),
        ("UPZ_DURGAPUR_RAJSHAHI", "দুর্গাপুর", "Durgapur"),
        ("UPZ_PUTHIA", "পুঠিয়া", "Puthia"),
        ("UPZ_CHARGHAT", "চারঘাট", "Charghat"),
        ("UPZ_BAGHA", "বাঘা", "Bagha")
    ],
    # Bogura (126)
    126: [
        ("UPZ_BOGURA_SADAR", "বগুড়া সদর", "Bogura Sadar"),
        ("UPZ_SHIBGANJ_BOGURA", "শিবগঞ্জ", "Shibganj"),
        ("UPZ_SONATALA", "সোনাতলা", "Sonatala"),
        ("UPZ_GABTALI", "গাবতলী", "Gabtali"),
        ("UPZ_SARIAKANDI", "সারিয়াকান্দি", "Sariakandi"),
        ("UPZ_DHUNAT", "ধুনট", "Dhunat"),
        ("UPZ_SHERPUR_BOGURA", "শেরপুর", "Sherpur"),
        ("UPZ_NANDIGRAM", "নন্দীগ্রাম", "Nandigram"),
        ("UPZ_KAHALOO", "কাহালু", "Kahaloo"),
        ("UPZ_ADAMDIGHI", "আদমদীঘি", "Adamdighi"),
        ("UPZ_DUPCHANCHIA", "দুপচাঁচিয়া", "Dupchanchia"),
        ("UPZ_SHAJAHANPUR", "শাহজাহানপুর", "Shajahanpur")
    ],
    # Pabna (127)
    127: [
        ("UPZ_PABNA_SADAR", "পাবনা সদর", "Pabna Sadar"),
        ("UPZ_ISHWARDI", "ঈশ্বরদী", "Ishwardi"),
        ("UPZ_SANTHIA", "সাঁথিয়া", "Santhia"),
        ("UPZ_CHATMOHAR", "চাটমোহর", "Chatmohar"),
        ("UPZ_SUJANAGAR", "সুজানগর", "Sujanagar"),
        ("UPZ_BERA", "বেড়া", "Bera"),
        ("UPZ_ATGHARIA", "আটঘরিয়া", "Atgharia"),
        ("UPZ_BHANGURA", "ভাঙ্গুড়া", "Bhangura"),
        ("UPZ_FARIDPUR_PABNA", "ফরিদপুর", "Faridpur")
    ],
    # Sirajganj (128)
    128: [
        ("UPZ_SIRAJGANJ_SADAR", "সিরাজগঞ্জ সদর", "Sirajganj Sadar"),
        ("UPZ_SHAHJADPUR", "শাহজাদপুর", "Shahjadpur"),
        ("UPZ_ULLAPARA", "উল্লাপাড়া", "Ullapara"),
        ("UPZ_BELKUCHI", "বেলকুচি", "Belkuchi"),
        ("UPZ_KAZIPUR", "কাজীপুর", "Kazipur"),
        ("UPZ_KAMARKHANDA", "কামারখন্দ", "Kamarkhanda"),
        ("UPZ_TARASH", "তাড়াশ", "Tarash"),
        ("UPZ_ROYGANJ", "রায়গঞ্জ", "Royganj"),
        ("UPZ_CHAUHALI", "চৌহালী", "Chauhali")
    ],
    # Naogaon (129)
    129: [
        ("UPZ_NAOGAON_SADAR", "নওগাঁ সদর", "Naogaon Sadar"),
        ("UPZ_MOHADEVPUR", "মহাদেবপুর", "Mohadevpur"),
        ("UPZ_PATNITALA", "পত্নীতলা", "Patnitala"),
        ("UPZ_DHAMOIRHAT", "ধামইরহাট", "Dhamoirhat"),
        ("UPZ_BADALGACHHI", "বদলগাছী", "Badalgachhi"),
        ("UPZ_MANDA", "মান্দা", "Manda"),
        ("UPZ_ATRAI", "আত্রাই", "Atrai"),
        ("UPZ_RANINAGAR", "রাণীনগর", "Raninagar"),
        ("UPZ_NIAMATPUR", "নিয়ামতপুর", "Niamatpur"),
        ("UPZ_SAPAHAR", "সাপাহার", "Sapahar"),
        ("UPZ_PORSHA", "পোরশা", "Porsha")
    ],
    # Natore (130)
    130: [
        ("UPZ_NATORE_SADAR", "নাটোর সদর", "Natore Sadar"),
        ("UPZ_SINGRA", "সিংড়া", "Singra"),
        ("UPZ_BARAIGRAM", "বড়াইগ্রাম", "Baraigram"),
        ("UPZ_GURUDASPUR", "গুরুদাসপুর", "Gurudaspur"),
        ("UPZ_LALPUR", "লালপুর", "Lalpur"),
        ("UPZ_BAGATIPARA", "বাগাতিপাড়া", "Bagatipara"),
        ("UPZ_NALDANGA", "নলডাঙ্গা", "Naldanga")
    ],
    # Chapainawabganj (131)
    131: [
        ("UPZ_CHAPAINAWABGANJ_SADAR", "চাঁপাইনবাবগঞ্জ সদর", "Chapainawabganj Sadar"),
        ("UPZ_SHIBGANJ_CHAPAINAWABGANJ", "শিবগঞ্জ", "Shibganj"),
        ("UPZ_GOMASTAPUR", "গোমস্তাপুর", "Gomastapur"),
        ("UPZ_NACHOLE", "নাচোল", "Nachole"),
        ("UPZ_BHOLAHAT", "ভোলাহাট", "Bholahat")
    ],
    # Joypurhat (132)
    132: [
        ("UPZ_JOYPURHAT_SADAR", "জয়পুরহাট সদর", "Joypurhat Sadar"),
        ("UPZ_PANCHBIBI", "পাঁচবিবি", "Panchbibi"),
        ("UPZ_KALAI", "কালাই", "Kalai"),
        ("UPZ_KHETLAL", "ক্ষেতলাল", "Khetlal"),
        ("UPZ_AKKELPUR", "আক্কেলপুর", "Akkelpur")
    ],

    # Khulna (133)
    133: [
        ("UPZ_RUPSHA", "রূপসা", "Rupsha"),
        ("UPZ_TEROKHADA", "তেরখাদা", "Terokhada"),
        ("UPZ_DIGHALIA", "দিঘলিয়া", "Dighalia"),
        ("UPZ_PHULTALA", "ফুলতলা", "Phultala"),
        ("UPZ_DUMURIA", "ডুমুরিয়া", "Dumuria"),
        ("UPZ_BATIAGHATA", "বটিয়াঘাটা", "Batiaghata"),
        ("UPZ_DACOPE", "দাকোপ", "Dacope"),
        ("UPZ_PAIKGACHHA", "পাইকগাছা", "Paikgachha"),
        ("UPZ_KOYRA", "কয়রা", "Koyra")
    ],
    # Jashore (134)
    134: [
        ("UPZ_JASHORE_SADAR", "যশোর সদর", "Jashore Sadar"),
        ("UPZ_JHIKARGACHHA", "ঝিকরগাছা", "Jhikargachha"),
        ("UPZ_SHARSHA", "শার্শা", "Sharsha"),
        ("UPZ_BAGHERPARA", "বাঘারপাড়া", "Bagherpara"),
        ("UPZ_ABHAYNAGAR", "অভয়নগর", "Abhaynagar"),
        ("UPZ_MANIRAMPUR", "মণিরামপুর", "Manirampur"),
        ("UPZ_KESHABPUR", "কেশবপুর", "Keshabpur"),
        ("UPZ_CHAUGACHHA", "চৌগাছা", "Chaugachha")
    ],
    # Satkhira (135)
    135: [
        ("UPZ_SATKHIRA_SADAR", "সাতক্ষীরা সদর", "Satkhira Sadar"),
        ("UPZ_ASSASUNI", "আশাশুনি", "Assasuni"),
        ("UPZ_DEBHATA", "দেবহাটা", "Debhata"),
        ("UPZ_KALAROA", "কলারোয়া", "Kalaroa"),
        ("UPZ_KALIGANJ_SATKHIRA", "কালীগঞ্জ", "Kaliganj"),
        ("UPZ_SHYAMNAGAR", "শ্যামনগর", "Shyamnagar"),
        ("UPZ_TALA", "তালা", "Tala")
    ],
    # Bagerhat (136)
    136: [
        ("UPZ_BAGERHAT_SADAR", "বাগেরহাট সদর", "Bagerhat Sadar"),
        ("UPZ_CHITALMARI", "চিতলমারী", "Chitalmari"),
        ("UPZ_FAKIRHAT", "ফকিরহাট", "Fakirhat"),
        ("UPZ_KACHUA_BAGERHAT", "কচুয়া", "Kachua"),
        ("UPZ_MOLLAHAT", "মোল্লাহাট", "Mollahat"),
        ("UPZ_MONGLA", "মোংলা", "Mongla"),
        ("UPZ_MORRELGANJ", "মোড়েলগঞ্জ", "Morrelganj"),
        ("UPZ_RAMPAL", "রামপাল", "Rampal"),
        ("UPZ_SARANKHOLA", "শরণখোলা", "Sarankhola")
    ],
    # Kushtia (137)
    137: [
        ("UPZ_KUSHTIA_SADAR", "কুষ্টিয়া সদর", "Kushtia Sadar"),
        ("UPZ_KUMARKHALI", "কুমারখালী", "Kumarkhali"),
        ("UPZ_KHOKSA", "খোকসা", "Khoksa"),
        ("UPZ_MIRPUR_KUSHTIA", "মিরপুর", "Mirpur"),
        ("UPZ_BHERAMARA", "ভেড়ামারা", "Bheramara"),
        ("UPZ_DAULATPUR_KUSHTIA", "দৌলতপুর", "Daulatpur")
    ],
    # Jhenaidah (138)
    138: [
        ("UPZ_JHENAIDAH_SADAR", "ঝিনাইদহ সদর", "Jhenaidah Sadar"),
        ("UPZ_SHAILKUPA", "শৈলকূপা", "Shailkupa"),
        ("UPZ_HARINAKUNDU", "হরিণাকুণ্ডু", "Harinakundu"),
        ("UPZ_KALIGANJ_JHENAIDAH", "কালীগঞ্জ", "Kaliganj"),
        ("UPZ_KOTCHANDPUR", "কোটচাঁদপুর", "Kotchandpur"),
        ("UPZ_MAHESHPUR", "মহেশপুর", "Maheshpur")
    ],
    # Chuadanga (139)
    139: [
        ("UPZ_CHUADANGA_SADAR", "চুয়াডাঙ্গা সদর", "Chuadanga Sadar"),
        ("UPZ_ALAMDANGA", "আলমডাঙ্গা", "Alamdanga"),
        ("UPZ_DAMURHUDA", "দামুড়হুদা", "Damurhuda"),
        ("UPZ_JIBANNAGAR", "জীবননগর", "Jibannagar")
    ],
    # Magura (140)
    140: [
        ("UPZ_MAGURA_SADAR", "মাগুরা সদর", "Magura Sadar"),
        ("UPZ_MOHAMMADPUR_MAGURA", "মহম্মদপুর", "Mohammadpur"),
        ("UPZ_SHALIKHA", "শালিখা", "Shalikha"),
        ("UPZ_SREEPUR_MAGURA", "শ্রীপুর", "Sreepur")
    ],
    # Meherpur (141)
    141: [
        ("UPZ_MEHERPUR_SADAR", "মেহেরপুর সদর", "Meherpur Sadar"),
        ("UPZ_GANGNI", "গাংনী", "Gangni"),
        ("UPZ_MUJIBNAGAR", "মুজিবনগর", "Mujibnagar")
    ],
    # Narail (142)
    142: [
        ("UPZ_NARAIL_SADAR", "নড়াইল সদর", "Narail Sadar"),
        ("UPZ_LOHAGARA_NARAIL", "লোহাগড়া", "Lohagara"),
        ("UPZ_KALIA", "কালিয়া", "Kalia")
    ],

    # Barishal (143)
    143: [
        ("UPZ_BARISHAL_SADAR", "বরিশাল সদর", "Barishal Sadar"),
        ("UPZ_BAKERGANJ", "বাকেরগঞ্জ", "Bakerganj"),
        ("UPZ_BABUGANJ", "বাবুগঞ্জ", "Babuganj"),
        ("UPZ_WAZIRPUR", "উজিরপুর", "Wazirpur"),
        ("UPZ_BANARIPARA", "বানারীপাড়া", "Banaripara"),
        ("UPZ_GOURNADI", "গৌরনদী", "Gournadi"),
        ("UPZ_AGAILJHARA", "আগৈলঝাড়া", "Agailjhara"),
        ("UPZ_MEHENDIGANJ", "মেহেন্দীগঞ্জ", "Mehendiganj"),
        ("UPZ_MULADI", "মুলাদী", "Muladi"),
        ("UPZ_HIZLA", "হিজলা", "Hizla")
    ],
    # Bhola (144)
    144: [
        ("UPZ_BHOLA_SADAR", "ভোলা সদর", "Bhola Sadar"),
        ("UPZ_BURHANUDDIN", "বোরহানউদ্দিন", "Burhanuddin"),
        ("UPZ_CHAR_FASSON", "চরফ্যাশন", "Char Fasson"),
        ("UPZ_DAULATKHAN", "দৌলতখান", "Daulatkhan"),
        ("UPZ_LALMOHAN", "লালমোহন", "Lalmohan"),
        ("UPZ_MANPURA", "মনপুরা", "Manpura"),
        ("UPZ_TAZUMUDDIN", "তজুমদ্দিন", "Tazumuddin")
    ],
    # Patuakhali (145)
    145: [
        ("UPZ_PATUAKHALI_SADAR", "পটুয়াখালী সদর", "Patuakhali Sadar"),
        ("UPZ_BAUPHAL", "বাউফল", "Bauphal"),
        ("UPZ_DASHMINA", "দশমিনা", "Dashmina"),
        ("UPZ_GALACHIPA", "গলাচিপা", "Galachipa"),
        ("UPZ_KALAPARA", "কলাপাড়া", "Kalapara"),
        ("UPZ_MIRZAGANJ", "মির্জাগঞ্জ", "Mirzaganj"),
        ("UPZ_DUMKI", "দুমকি", "Dumki"),
        ("UPZ_RANGABALI", "রাঙ্গাবালী", "Rangabali")
    ],
    # Pirojpur (146)
    146: [
        ("UPZ_PIROJPUR_SADAR", "পিরোজপুর সদর", "Pirojpur Sadar"),
        ("UPZ_BHANDARIA", "ভান্ডারিয়া", "Bhandaria"),
        ("UPZ_MATHBARIA", "মঠবাড়িয়া", "Mathbaria"),
        ("UPZ_NAZIRPUR", "নাজিরপুর", "Nazirpur"),
        ("UPZ_NESARABAD", "নেছারাবাদ", "Nesarabad"),
        ("UPZ_KAWKHALI_PIROJPUR", "কাউখালী", "Kawkhali"),
        ("UPZ_ZIANAGAR", "জিয়ানগর", "Zianagar")
    ],
    # Barguna (147)
    147: [
        ("UPZ_BARGUNA_SADAR", "বরগুনা সদর", "Barguna Sadar"),
        ("UPZ_AMTALI", "আমতলী", "Amtali"),
        ("UPZ_BAMNA", "বামনা", "Bamna"),
        ("UPZ_BETAGI", "বেতাগী", "Betagi"),
        ("UPZ_PATHARGHATA", "পাথরঘাটা", "Patharghata"),
        ("UPZ_TALTALI", "তালতলী", "Taltali")
    ],
    # Jhalokati (148)
    148: [
        ("UPZ_JHALOKATI_SADAR", "ঝালকাঠি সদর", "Jhalokati Sadar"),
        ("UPZ_KATHALIA", "কাঁঠালিয়া", "Kathalia"),
        ("UPZ_NALCHHITY", "নলছিটি", "Nalchhity"),
        ("UPZ_RAJAPUR", "রাজাপুর", "Rajapur")
    ],

    # Sylhet (149)
    149: [
        ("UPZ_SYLHET_SADAR", "সিলেট সদর", "Sylhet Sadar"),
        ("UPZ_BEANIBAZAR", "বিয়ানীবাজার", "Beanibazar"),
        ("UPZ_GOLAPGANJ", "গোলাপগঞ্জ", "Golapganj"),
        ("UPZ_FENCHUGANJ", "ফেঞ্চুগঞ্জ", "Fenchuganj"),
        ("UPZ_BALAGANJ", "বালাগঞ্জ", "Balaganj"),
        ("UPZ_BISWANATH", "বিশ্বনাথ", "Biswanath"),
        ("UPZ_COMPANIGANJ_SYLHET", "কোম্পানীগঞ্জ", "Companiganj"),
        ("UPZ_GOWAINGHAT", "গোয়াইনঘাট", "Gowainghat"),
        ("UPZ_JAINTIAPUR", "জৈন্তাপুর", "Jaintiapur"),
        ("UPZ_KANAIGHAT", "কানাইঘাট", "Kanaighat"),
        ("UPZ_ZAKIGANJ", "জকিগঞ্জ", "Zakiganj"),
        ("UPZ_SOUTH_SURMA", "দক্ষিণ সুরমা", "South Surma"),
        ("UPZ_OSMANI_NAGAR", "ওসমানীনগর", "Osmani Nagar")
    ],
    # Moulvibazar (150)
    150: [
        ("UPZ_MOULVIBAZAR_SADAR", "মৌলভীবাজার সদর", "Moulvibazar Sadar"),
        ("UPZ_BARLEKHA", "বড়লেখা", "Barlekha"),
        ("UPZ_JURI", "জুড়ী", "Juri"),
        ("UPZ_KAMALGANJ", "কমলগঞ্জ", "Kamalganj"),
        ("UPZ_KULAURA", "কুলাউড়া", "Kulaura"),
        ("UPZ_RAJNAGAR", "রাজনগর", "Rajnagar"),
        ("UPZ_SREEMANGAL", "শ্রীমঙ্গল", "Sreemangal")
    ],
    # Habiganj (151)
    151: [
        ("UPZ_HABIGANJ_SADAR", "হবিগঞ্জ সদর", "Habiganj Sadar"),
        ("UPZ_AJMIRIGANJ", "আজমিরীগঞ্জ", "Ajmiriganj"),
        ("UPZ_BAHUBAL", "বাহুবল", "Bahubal"),
        ("UPZ_BANIACHONG", "বানিয়াচং", "Baniachong"),
        ("UPZ_CHUNARUGHAT", "চুনারুঘাট", "Chunarughat"),
        ("UPZ_LAKHAI", "লাখাই", "Lakhai"),
        ("UPZ_MADHABPUR", "মাধবপুর", "Madhabpur"),
        ("UPZ_NABIGANJ", "নবীগঞ্জ", "Nabiganj"),
        ("UPZ_SHAYESTAGANJ", "শায়েস্তাগঞ্জ", "Shayestaganj")
    ],
    # Sunamganj (152)
    152: [
        ("UPZ_SUNAMGANJ_SADAR", "সুনামগঞ্জ সদর", "Sunamganj Sadar"),
        ("UPZ_BISHWAMBARPUR", "বিশ্বম্ভরপুর", "Bishwambarpur"),
        ("UPZ_CHHATAK", "ছাতক", "Chhatak"),
        ("UPZ_DERAI", "দিরাই", "Derai"),
        ("UPZ_DHARAMPASHA", "ধর্মপাশা", "Dharampasha"),
        ("UPZ_DOWARABAZAR", "দোয়ারাবাজার", "Dowarabazar"),
        ("UPZ_JAGANNATHPUR", "জগন্নাথপুর", "Jagannathpur"),
        ("UPZ_JAMALGANJ", "জামালগঞ্জ", "Jamalganj"),
        ("UPZ_SHANTIGANJ", "শান্তিগঞ্জ", "Shantiganj"),
        ("UPZ_SHULLA", "শাল্লা", "Shulla"),
        ("UPZ_TAHIRPUR", "তাহিরপুর", "Tahirpur"),
        ("UPZ_MADHYANAGAR", "মধ্যনগর", "Madhyanagar")
    ],

    # Rangpur (153)
    153: [
        ("UPZ_RANGPUR_SADAR", "রংপুর সদর", "Rangpur Sadar"),
        ("UPZ_BADARGANJ", "বদরগঞ্জ", "Badarganj"),
        ("UPZ_MITHAPUKUR", "মিঠাপুকুর", "Mithapukur"),
        ("UPZ_PIRGACHHA", "পীরগাছা", "Pirgachha"),
        ("UPZ_PIRGANJ_RANGPUR", "পীরগঞ্জ", "Pirganj"),
        ("UPZ_KAUNIA", "কাউনিয়া", "Kaunia"),
        ("UPZ_GANGACHHARA", "গংগাচড়া", "Gangachhara"),
        ("UPZ_TARAGANJ", "তারাগঞ্জ", "Taraganj")
    ],
    # Dinajpur (154)
    154: [
        ("UPZ_DINAJPUR_SADAR", "দিনাজপুর সদর", "Dinajpur Sadar"),
        ("UPZ_BIRGANJ", "বীরগঞ্জ", "Birganj"),
        ("UPZ_BOCHAGANJ", "বোচাগঞ্জ", "Bochaganj"),
        ("UPZ_KAHAROLE", "কাহারোল", "Kaharole"),
        ("UPZ_CHIRIRBANDAR", "চিরিরবন্দর", "Chirirbandar"),
        ("UPZ_FULBARI_DINAJPUR", "ফুলবাড়ী", "Fulbari"),
        ("UPZ_GHORAGHAT", "ঘোড়াঘাট", "Ghoraghat"),
        ("UPZ_HAKIMPUR", "হাকিমপুর", "Hakimpur"),
        ("UPZ_BIRAMPUR", "বিরামপুর", "Birampur"),
        ("UPZ_PARBATIPUR", "পার্বতীপুর", "Parbatipur"),
        ("UPZ_NAWABGANJ_DINAJPUR", "নবাবগঞ্জ", "Nawabganj"),
        ("UPZ_KHANSAMA", "খানসামা", "Khansama"),
        ("UPZ_BIRAL", "বিরল", "Biral")
    ],
    # Kurigram (155)
    155: [
        ("UPZ_KURIGRAM_SADAR", "কুড়িগ্রাম সদর", "Kurigram Sadar"),
        ("UPZ_NAGESHWARI", "নাগেশ্বরী", "Nageshwari"),
        ("UPZ_BHURUNGAMARI", "ভুরুঙ্গামারী", "Bhurungamari"),
        ("UPZ_PHULBARI_KURIGRAM", "ফুলবাড়ী", "Phulbari"),
        ("UPZ_RAJARHAT", "রাজারহাট", "Rajarhat"),
        ("UPZ_ULIPUR", "উলিপুর", "Ulipur"),
        ("UPZ_CHILMARI", "চিলমারী", "Chilmari"),
        ("UPZ_ROWMARI", "রৌমারী", "Rowmari"),
        ("UPZ_CHAR_RAJIBPUR", "চর রাজিবপুর", "Char Rajibpur")
    ],
    # Gaibandha (156)
    156: [
        ("UPZ_GAIBANDHA_SADAR", "গাইবান্ধা সদর", "Gaibandha Sadar"),
        ("UPZ_SADULLAPUR", "সাদুল্লাপুর", "Sadullapur"),
        ("UPZ_SUNDARGANJ", "সুন্দরগঞ্জ", "Sundarganj"),
        ("UPZ_GOBINDAGANJ", "গোবিন্দগঞ্জ", "Gobindaganj"),
        ("UPZ_PALASHBARI", "পলাশবাড়ী", "Palashbari"),
        ("UPZ_PHULCHHARI", "ফুলছড়ি", "Phulchhari"),
        ("UPZ_SAGHATA", "সাঘাটা", "Saghata")
    ],
    # Nilphamari (157)
    157: [
        ("UPZ_NILPHAMARI_SADAR", "নীলফামারী সদর", "Nilphamari Sadar"),
        ("UPZ_SAIDPUR", "সৈয়দপুর", "Saidpur"),
        ("UPZ_JALDHAKA", "জলঢাকা", "Jaldhaka"),
        ("UPZ_KISHOREGANJ_NILPHAMARI", "কিশোরগঞ্জ", "Kishoreganj"),
        ("UPZ_DOMAR", "ডোমার", "Domar"),
        ("UPZ_DIMLA", "ডিমলা", "Dimla")
    ],
    # Panchagarh (158)
    158: [
        ("UPZ_PANCHAGARH_SADAR", "পঞ্চগড় সদর", "Panchagarh Sadar"),
        ("UPZ_BODA", "বোদা", "Boda"),
        ("UPZ_DEBIGANJ", "দেবীগঞ্জ", "Debiganj"),
        ("UPZ_ATWARI", "আটোয়ারী", "Atwari"),
        ("UPZ_TETULIA", "তেঁতুলিয়া", "Tetulia")
    ],
    # Thakurgaon (159)
    159: [
        ("UPZ_THAKURGAON_SADAR", "ঠাকুরগাঁও সদর", "Thakurgaon Sadar"),
        ("UPZ_PIRGANJ_THAKURGAON", "পীরগঞ্জ", "Pirganj"),
        ("UPZ_RANISANKAIL", "রাণীশংকৈল", "Ranisankail"),
        ("UPZ_BALIADANGI", "বালিয়াডাঙ্গী", "Baliadangi"),
        ("UPZ_HARIPUR", "হরিপুর", "Haripur")
    ],
    # Lalmonirhat (160)
    160: [
        ("UPZ_LALMONIRHAT_SADAR", "লালমনিরহাট সদর", "Lalmonirhat Sadar"),
        ("UPZ_PATGRAM", "পাটগ্রাম", "Patgram"),
        ("UPZ_HATIBANDHA", "হাতীবান্ধা", "Hatibandha"),
        ("UPZ_KALIGANJ_LALMONIRHAT", "কালীগঞ্জ", "Kaliganj"),
        ("UPZ_ADITMARI", "আদিতমারী", "Aditmari")
    ],

    # Mymensingh (161)
    161: [
        ("UPZ_MYMENSINGH_SADAR", "ময়মনসিংহ সদর", "Mymensingh Sadar"),
        ("UPZ_MUKTAGACHHA", "মুক্তাগাছা", "Muktagachha"),
        ("UPZ_FULBARIA", "ফুলবাড়ীয়া", "Fulbaria"),
        ("UPZ_TRISHAL", "ত্রিশাল", "Trishal"),
        ("UPZ_BHALUKA", "ভালুকা", "Bhaluka"),
        ("UPZ_GAFARGAON", "গফরগাঁও", "Gafargaon"),
        ("UPZ_NANDAIL", "নান্দাইল", "Nandail"),
        ("UPZ_ISHWARGANJ", "ঈশ্বরগঞ্জ", "Ishwarganj"),
        ("UPZ_HALUAGHAT", "হালুয়াঘাট", "Haluaghat"),
        ("UPZ_DHOBAURA", "ধোবাউড়া", "Dhobaura"),
        ("UPZ_PHULPUR", "ফুলপুর", "Phulpur"),
        ("UPZ_TARAKANDA", "তারাকান্দা", "Tarakanda"),
        ("UPZ_GOURIPUR", "গৌরীপুর", "Gouripur")
    ],
    # Jamalpur (162)
    162: [
        ("UPZ_JAMALPUR_SADAR", "জামালপুর সদর", "Jamalpur Sadar"),
        ("UPZ_MELANDAHA", "মেলান্দহ", "Melandaha"),
        ("UPZ_ISLAMPUR", "ইসলামপুর", "Islampur"),
        ("UPZ_DEWANGANJ", "দেওয়ানগঞ্জ", "Dewanganj"),
        ("UPZ_SARISHABARI", "সরিষাবাড়ী", "Sarishabari"),
        ("UPZ_MADARGANJ", "মাদারগঞ্জ", "Madarganj"),
        ("UPZ_BAKSHIGANJ", "বকশীগঞ্জ", "Bakshiganj")
    ],
    # Netrokona (163)
    163: [
        ("UPZ_NETROKONA_SADAR", "নেত্রকোণা সদর", "Netrokona Sadar"),
        ("UPZ_BARHATTA", "বারহাট্টা", "Barhatta"),
        ("UPZ_DURGAPUR_NETROKONA", "দুর্গাপুর", "Durgapur"),
        ("UPZ_KENDUA", "কেন্দুয়া", "Kendua"),
        ("UPZ_ATPARA", "আটপাড়া", "Atpara"),
        ("UPZ_MOHANGANJ", "মোহনগঞ্জ", "Mohanganj"),
        ("UPZ_KALMAKANDA", "কলমাকান্দা", "Kalmakanda"),
        ("UPZ_PURBADHALA", "পূর্বধলা", "Purbadhala"),
        ("UPZ_KHALIAJURI", "খালিয়াজুড়ী", "Khaliajuri"),
        ("UPZ_MADAN", "মদন", "Madan")
    ],
    # Sherpur (164)
    164: [
        ("UPZ_SHERPUR_SADAR", "শেরপুর সদর", "Sherpur Sadar"),
        ("UPZ_NALITABARI", "নালিতাবাড়ী", "Nalitabari"),
        ("UPZ_SREEBARDI", "শ্রীবরদী", "Sreebardi"),
        ("UPZ_NAKLA", "নকলা", "Nakla"),
        ("UPZ_JHENAIGATI", "ঝিনাইগাতী", "Jhenaigati")
    ]
}

lines = [
    "SET client_encoding = 'UTF8';",
    "BEGIN;",
    "-- 1. Seed All 64 Districts (AreaTypeId = 3)"
]

def escape_sql(s):
    return s.replace("'", "''") if s else ""

for d_id, parent_id, code, name_bn, name_en in districts_data:
    nbn = escape_sql(name_bn)
    nen = escape_sql(name_en)
    lines.append(
        f"INSERT INTO geo.areas (area_id, parent_area_id, area_type_id, code, name_bn, name_en, is_active) "
        f"VALUES ({d_id}, {parent_id}, 3, '{code}', '{nbn}', '{nen}', TRUE) "
        f"ON CONFLICT (area_id) DO UPDATE SET parent_area_id = EXCLUDED.parent_area_id, name_bn = EXCLUDED.name_bn, name_en = EXCLUDED.name_en;"
    )

lines.append("\n-- 2. Seed Upazilas (AreaTypeId = 5)")
next_upz_id = 1001

for dist_id, upzs in upazilas_by_district.items():
    for code, name_bn, name_en in upzs:
        nbn = escape_sql(name_bn)
        nen = escape_sql(name_en)
        lines.append(
            f"INSERT INTO geo.areas (area_id, parent_area_id, area_type_id, code, name_bn, name_en, is_active) "
            f"VALUES ({next_upz_id}, {dist_id}, 5, '{code}', '{nbn}', '{nen}', TRUE) "
            f"ON CONFLICT (area_id) DO UPDATE SET parent_area_id = EXCLUDED.parent_area_id, name_bn = EXCLUDED.name_bn, name_en = EXCLUDED.name_en;"
        )
        next_upz_id += 1

lines.append("COMMIT;")
lines.append(f"-- Total Upazilas Seeded: {next_upz_id - 1001}")

with open("scripts/seed_all_districts_and_upazilas.sql", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Generated SQL for {len(districts_data)} Districts and {next_upz_id - 1001} Upazilas.")
