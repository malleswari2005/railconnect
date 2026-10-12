"""
Andhra Pradesh Railway Network Data
Contains station master records, route corridors, fictional train timetables,
and coach tariff specifications.
"""
from datetime import time

STATIONS_DATA = [
    # 27 Andhra Pradesh Core Stations
    ('BZA', 'Vijayawada Jn', 'Vijayawada', 'Andhra Pradesh', 'SCR'),
    ('TPTY', 'Tirupati', 'Tirupati', 'Andhra Pradesh', 'SCR'),
    ('RU', 'Renigunta Jn', 'Renigunta', 'Andhra Pradesh', 'SCR'),
    ('VSKP', 'Visakhapatnam', 'Visakhapatnam', 'Andhra Pradesh', 'ECoR'),
    ('GNT', 'Guntur Jn', 'Guntur', 'Andhra Pradesh', 'SCR'),
    ('NLR', 'Nellore', 'Nellore', 'Andhra Pradesh', 'SCR'),
    ('RJY', 'Rajahmundry', 'Rajahmundry', 'Andhra Pradesh', 'SCR'),
    ('KRNT', 'Kurnool City', 'Kurnool', 'Andhra Pradesh', 'SCR'),
    ('HX', 'Kadapa', 'Kadapa', 'Andhra Pradesh', 'SCR'),
    ('ATP', 'Anantapur', 'Anantapur', 'Andhra Pradesh', 'SCR'),
    ('OGL', 'Ongole', 'Ongole', 'Andhra Pradesh', 'SCR'),
    ('EE', 'Eluru', 'Eluru', 'Andhra Pradesh', 'SCR'),
    ('TEL', 'Tenali Jn', 'Tenali', 'Andhra Pradesh', 'SCR'),
    ('TDD', 'Tadepalligudem', 'Tadepalligudem', 'Andhra Pradesh', 'SCR'),
    ('SLO', 'Samalkot Jn', 'Samalkot', 'Andhra Pradesh', 'SCR'),
    ('AKP', 'Anakapalle', 'Anakapalle', 'Andhra Pradesh', 'SCR'),
    ('VZM', 'Vizianagaram Jn', 'Vizianagaram', 'Andhra Pradesh', 'ECoR'),
    ('CHE', 'Srikakulam Road', 'Amadalavalasa', 'Andhra Pradesh', 'ECoR'),
    ('NDL', 'Nandyal', 'Nandyal', 'Andhra Pradesh', 'SCR'),
    ('GDR', 'Gudur Jn', 'Gudur', 'Andhra Pradesh', 'SCR'),
    ('CLX', 'Chirala', 'Chirala', 'Andhra Pradesh', 'SCR'),
    ('NRT', 'Narasaraopet', 'Narasaraopet', 'Andhra Pradesh', 'SCR'),
    ('MTM', 'Machilipatnam', 'Machilipatnam', 'Andhra Pradesh', 'SCR'),
    ('CCT', 'Kakinada Town', 'Kakinada', 'Andhra Pradesh', 'SCR'),
    ('GTL', 'Guntakal Jn', 'Guntakal', 'Andhra Pradesh', 'SCR'),
    ('DMM', 'Dharmavaram Jn', 'Dharmavaram', 'Andhra Pradesh', 'SCR'),
    ('DHNE', 'Dhone Jn', 'Dhone', 'Andhra Pradesh', 'SCR'),

    # 3 Outside-AP Core Anchor Stations
    ('SC', 'Secunderabad Jn', 'Hyderabad', 'Telangana', 'SCR'),
    ('MAS', 'Chennai Central', 'Chennai', 'Tamil Nadu', 'SR'),
    ('SBC', 'KSR Bengaluru', 'Bengaluru', 'Karnataka', 'SWR'),

    # Preserved Existing National Stations
    ('NDLS', 'New Delhi', 'New Delhi', 'Delhi', 'NR'),
    ('MMCT', 'Mumbai Central', 'Mumbai', 'Maharashtra', 'WR'),
    ('HWH', 'Howrah Junction', 'Kolkata', 'West Bengal', 'ER'),
    ('ADI', 'Ahmedabad Junction', 'Ahmedabad', 'Gujarat', 'WR'),
    ('CNB', 'Kanpur Central', 'Kanpur', 'Uttar Pradesh', 'NCR'),
    ('PNBE', 'Patna Junction', 'Patna', 'Bihar', 'ECR'),
    ('PUNE', 'Pune Junction', 'Pune', 'Maharashtra', 'CR'),
    ('HYB', 'Hyderabad Deccan', 'Hyderabad', 'Telangana', 'SCR'),
    ('JAT', 'Jammu Tawi', 'Jammu', 'Jammu & Kashmir', 'NR'),
    ('BSB', 'Varanasi Junction', 'Varanasi', 'Uttar Pradesh', 'NR'),
    ('BPL', 'Bhopal Junction', 'Bhopal', 'Madhya Pradesh', 'WCR'),
    ('GKP', 'Gorakhpur Junction', 'Gorakhpur', 'Uttar Pradesh', 'NER'),
    ('CDG', 'Chandigarh Junction', 'Chandigarh', 'Chandigarh', 'NR'),
]

# Standard coach tariff structures
STANDARD_SF_CLASSES = [
    ('1A', 'AC First Class (1A)', 1000.00, 2.60, 1, 24),
    ('2A', 'AC 2-Tier (2A)', 600.00, 1.85, 2, 48),
    ('3A', 'AC 3-Tier (3A)', 380.00, 1.25, 4, 64),
    ('SL', 'Sleeper Class (SL)', 120.00, 0.42, 6, 72),
]

STANDARD_EXPRESS_CLASSES = [
    ('2A', 'AC 2-Tier (2A)', 550.00, 1.80, 2, 48),
    ('3A', 'AC 3-Tier (3A)', 350.00, 1.20, 3, 64),
    ('SL', 'Sleeper Class (SL)', 110.00, 0.40, 6, 72),
    ('2S', 'Second Sitting (2S)', 45.00, 0.22, 4, 108),
]

INTERCITY_CC_CLASSES = [
    ('CC', 'AC Chair Car (CC)', 220.00, 0.95, 4, 78),
    ('2S', 'Second Sitting (2S)', 45.00, 0.22, 8, 108),
]

PASSENGER_MEMU_CLASSES = [
    ('SL', 'Sleeper Class (SL)', 90.00, 0.35, 2, 72),
    ('2S', 'Second Sitting (2S)', 35.00, 0.18, 10, 108),
]

# Helper function to convert total elapsed minutes from midnight to (time_object, day_offset)
def min_to_time(base_minutes, offset_day=0):
    total_minutes = base_minutes
    days = offset_day + (total_minutes // 1440)
    mins_in_day = total_minutes % 1440
    hr = mins_in_day // 60
    mn = mins_in_day % 60
    return time(hr, mn), days


# 18 Pairs (36 Trains) covering all 7 corridors
TRAINS_DATA = [
    # -------------------------------------------------------------
    # Corridor 1: Coastal Trunk (Visakhapatnam <-> Chennai Central)
    # 780 km. Superfast avg ~63 km/h.
    # -------------------------------------------------------------
    {
        'number': '92801',
        'name': 'Andhra Coastal Superfast',
        'type': 'SUPERFAST',
        'src': 'VSKP', 'dest': 'MAS',
        'dep': time(6, 0), 'arr': time(18, 35),
        'dist': 780,
        'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
        'stops': [
            # code, order, arr, dep, halt, dist, offset
            ('VSKP', 1, None, time(6, 0), 0, 0, 0),
            ('AKP', 2, time(6, 32), time(6, 34), 2, 33, 0),
            ('SLO', 3, time(8, 5), time(8, 7), 2, 151, 0),
            ('RJY', 4, time(8, 50), time(8, 55), 5, 201, 0),
            ('TDD', 5, time(9, 35), time(9, 37), 2, 243, 0),
            ('EE', 6, time(10, 20), time(10, 22), 2, 291, 0),
            ('BZA', 7, time(11, 20), time(11, 30), 10, 350, 0),
            ('TEL', 8, time(12, 0), time(12, 2), 2, 381, 0),
            ('CLX', 9, time(12, 52), time(12, 54), 2, 438, 0),
            ('OGL', 10, time(13, 40), time(13, 42), 2, 488, 0),
            ('NLR', 11, time(15, 25), time(15, 27), 2, 604, 0),
            ('GDR', 12, time(16, 8), time(16, 10), 2, 642, 0),
            ('MAS', 13, time(18, 35), None, 0, 780, 0),
        ],
        'classes': STANDARD_SF_CLASSES,
    },
    {
        'number': '92802',
        'name': 'Andhra Coastal Superfast (Return)',
        'type': 'SUPERFAST',
        'src': 'MAS', 'dest': 'VSKP',
        'dep': time(6, 30), 'arr': time(19, 5),
        'dist': 780,
        'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
        'stops': [
            ('MAS', 1, None, time(6, 30), 0, 0, 0),
            ('GDR', 2, time(8, 55), time(8, 57), 2, 138, 0),
            ('NLR', 3, time(9, 38), time(9, 40), 2, 176, 0),
            ('OGL', 4, time(11, 23), time(11, 25), 2, 292, 0),
            ('CLX', 5, time(12, 11), time(12, 13), 2, 342, 0),
            ('TEL', 6, time(13, 3), time(13, 5), 2, 399, 0),
            ('BZA', 7, time(13, 35), time(13, 45), 10, 430, 0),
            ('EE', 8, time(14, 43), time(14, 45), 2, 489, 0),
            ('TDD', 9, time(15, 28), time(15, 30), 2, 537, 0),
            ('RJY', 10, time(16, 10), time(16, 15), 5, 579, 0),
            ('SLO', 11, time(16, 58), time(17, 0), 2, 629, 0),
            ('AKP', 12, time(18, 31), time(18, 33), 2, 747, 0),
            ('VSKP', 13, time(19, 5), None, 0, 780, 0),
        ],
        'classes': STANDARD_SF_CLASSES,
    },

    # -------------------------------------------------------------
    # Corridor 2: North Coastal Extension (Srikakulam Road <-> Vijayawada)
    # 481 km. Express avg ~52 km/h.
    # -------------------------------------------------------------
    {
        'number': '92803',
        'name': 'Kalinga Corridor Express',
        'type': 'EXPRESS',
        'src': 'CHE', 'dest': 'BZA',
        'dep': time(6, 15), 'arr': time(15, 30),
        'dist': 481,
        'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
        'stops': [
            ('CHE', 1, None, time(6, 15), 0, 0, 0),
            ('VZM', 2, time(7, 30), time(7, 35), 5, 70, 0),
            ('VSKP', 3, time(8, 45), time(9, 5), 20, 131, 0),
            ('AKP', 4, time(9, 45), time(9, 47), 2, 164, 0),
            ('SLO', 5, time(11, 40), time(11, 42), 2, 282, 0),
            ('RJY', 6, time(12, 30), time(12, 35), 5, 332, 0),
            ('TDD', 7, time(13, 20), time(13, 22), 2, 374, 0),
            ('EE', 8, time(14, 15), time(14, 17), 2, 422, 0),
            ('BZA', 9, time(15, 30), None, 0, 481, 0),
        ],
        'classes': STANDARD_EXPRESS_CLASSES,
    },
    {
        'number': '92804',
        'name': 'Kalinga Corridor Express (Return)',
        'type': 'EXPRESS',
        'src': 'BZA', 'dest': 'CHE',
        'dep': time(10, 45), 'arr': time(20, 0),
        'dist': 481,
        'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
        'stops': [
            ('BZA', 1, None, time(10, 45), 0, 0, 0),
            ('EE', 2, time(11, 58), time(12, 0), 2, 59, 0),
            ('TDD', 3, time(12, 53), time(12, 55), 2, 107, 0),
            ('RJY', 4, time(13, 40), time(13, 45), 5, 149, 0),
            ('SLO', 5, time(14, 33), time(14, 35), 2, 199, 0),
            ('AKP', 6, time(16, 28), time(16, 30), 2, 317, 0),
            ('VSKP', 7, time(17, 10), time(17, 30), 20, 350, 0),
            ('VZM', 8, time(18, 40), time(18, 45), 5, 411, 0),
            ('CHE', 9, time(20, 0), None, 0, 481, 0),
        ],
        'classes': STANDARD_EXPRESS_CLASSES,
    },

    # -------------------------------------------------------------
    # Corridor 3: Swarna Andhra Intercity (Visakhapatnam <-> Vijayawada)
    # 350 km. Superfast avg ~64 km/h.
    # -------------------------------------------------------------
    {
        'number': '92805',
        'name': 'Swarna Andhra Intercity',
        'type': 'SUPERFAST',
        'src': 'VSKP', 'dest': 'BZA',
        'dep': time(6, 0), 'arr': time(11, 30),
        'dist': 350,
        'days': 'MON,TUE,WED,THU,FRI,SAT',
        'stops': [
            ('VSKP', 1, None, time(6, 0), 0, 0, 0),
            ('AKP', 2, time(6, 32), time(6, 34), 2, 33, 0),
            ('SLO', 3, time(8, 2), time(8, 4), 2, 151, 0),
            ('RJY', 4, time(8, 48), time(8, 52), 4, 201, 0),
            ('TDD', 5, time(9, 30), time(9, 32), 2, 243, 0),
            ('EE', 6, time(10, 13), time(10, 15), 2, 291, 0),
            ('BZA', 7, time(11, 30), None, 0, 350, 0),
        ],
        'classes': INTERCITY_CC_CLASSES,
    },
    {
        'number': '92806',
        'name': 'Swarna Andhra Intercity (Return)',
        'type': 'SUPERFAST',
        'src': 'BZA', 'dest': 'VSKP',
        'dep': time(17, 15), 'arr': time(22, 45),
        'dist': 350,
        'days': 'MON,TUE,WED,THU,FRI,SAT',
        'stops': [
            ('BZA', 1, None, time(17, 15), 0, 0, 0),
            ('EE', 2, time(18, 30), time(18, 32), 2, 59, 0),
            ('TDD', 3, time(19, 13), time(19, 15), 2, 107, 0),
            ('RJY', 4, time(19, 53), time(19, 57), 4, 149, 0),
            ('SLO', 5, time(20, 41), time(20, 43), 2, 199, 0),
            ('AKP', 6, time(22, 11), time(22, 13), 2, 317, 0),
            ('VSKP', 7, time(22, 45), None, 0, 350, 0),
        ],
        'classes': INTERCITY_CC_CLASSES,
    },

    # -------------------------------------------------------------
    # Corridor 4: Konaseema Link (Kakinada Town <-> Vijayawada)
    # 212 km. Express avg ~53 km/h.
    # -------------------------------------------------------------
    {
        'number': '92807',
        'name': 'Konaseema Link Express',
        'type': 'EXPRESS',
        'src': 'CCT', 'dest': 'BZA',
        'dep': time(6, 30), 'arr': time(10, 30),
        'dist': 212,
        'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
        'stops': [
            ('CCT', 1, None, time(6, 30), 0, 0, 0),
            ('SLO', 2, time(6, 44), time(6, 46), 2, 12, 0),
            ('RJY', 3, time(7, 36), time(7, 40), 4, 63, 0),
            ('TDD', 4, time(8, 26), time(8, 28), 2, 105, 0),
            ('EE', 5, time(9, 18), time(9, 20), 2, 153, 0),
            ('BZA', 6, time(10, 30), None, 0, 212, 0),
        ],
        'classes': [
            ('CC', 'AC Chair Car (CC)', 210.00, 0.90, 2, 78),
            ('SL', 'Sleeper Class (SL)', 100.00, 0.38, 4, 72),
            ('2S', 'Second Sitting (2S)', 40.00, 0.20, 6, 108),
        ],
    },
    {
        'number': '92808',
        'name': 'Konaseema Link Express (Return)',
        'type': 'EXPRESS',
        'src': 'BZA', 'dest': 'CCT',
        'dep': time(16, 30), 'arr': time(20, 30),
        'dist': 212,
        'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
        'stops': [
            ('BZA', 1, None, time(16, 30), 0, 0, 0),
            ('EE', 2, time(17, 40), time(17, 42), 2, 59, 0),
            ('TDD', 3, time(18, 32), time(18, 34), 2, 107, 0),
            ('RJY', 4, time(19, 20), time(19, 24), 4, 149, 0),
            ('SLO', 5, time(20, 14), time(20, 16), 2, 200, 0),
            ('CCT', 6, time(20, 30), None, 0, 212, 0),
        ],
        'classes': [
            ('CC', 'AC Chair Car (CC)', 210.00, 0.90, 2, 78),
            ('SL', 'Sleeper Class (SL)', 100.00, 0.38, 4, 72),
            ('2S', 'Second Sitting (2S)', 40.00, 0.20, 6, 108),
        ],
    },

    # -------------------------------------------------------------
    # Corridor 5: Capital & Telangana Superfast (Vijayawada <-> Secunderabad)
    # 348 km. Superfast avg ~63 km/h.
    # -------------------------------------------------------------
    {
        'number': '92809',
        'name': 'Amaravati Link Superfast',
        'type': 'SUPERFAST',
        'src': 'BZA', 'dest': 'SC',
        'dep': time(6, 10), 'arr': time(11, 40),
        'dist': 348,
        'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
        'stops': [
            ('BZA', 1, None, time(6, 10), 0, 0, 0),
            ('GNT', 2, time(6, 45), time(6, 50), 5, 32, 0),
            ('NRT', 3, time(7, 34), time(7, 36), 2, 77, 0),
            ('SC', 4, time(11, 40), None, 0, 348, 0),
        ],
        'classes': [
            ('2A', 'AC 2-Tier (2A)', 580.00, 1.80, 2, 48),
            ('3A', 'AC 3-Tier (3A)', 370.00, 1.25, 4, 64),
            ('CC', 'AC Chair Car (CC)', 230.00, 0.95, 3, 78),
            ('2S', 'Second Sitting (2S)', 45.00, 0.22, 6, 108),
        ],
    },
    {
        'number': '92810',
        'name': 'Amaravati Link Superfast (Return)',
        'type': 'SUPERFAST',
        'src': 'SC', 'dest': 'BZA',
        'dep': time(16, 45), 'arr': time(22, 15),
        'dist': 348,
        'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
        'stops': [
            ('SC', 1, None, time(16, 45), 0, 0, 0),
            ('NRT', 2, time(20, 49), time(20, 51), 2, 271, 0),
            ('GNT', 3, time(21, 35), time(21, 40), 5, 316, 0),
            ('BZA', 4, time(22, 15), None, 0, 348, 0),
        ],
        'classes': [
            ('2A', 'AC 2-Tier (2A)', 580.00, 1.80, 2, 48),
            ('3A', 'AC 3-Tier (3A)', 370.00, 1.25, 4, 64),
            ('CC', 'AC Chair Car (CC)', 230.00, 0.95, 3, 78),
            ('2S', 'Second Sitting (2S)', 45.00, 0.22, 6, 108),
        ],
    },

    # -------------------------------------------------------------
    # Corridor 6: Coastal to Telangana (Visakhapatnam <-> Secunderabad)
    # 698 km. Overnight Superfast avg ~58 km/h.
    # -------------------------------------------------------------
    {
        'number': '92811',
        'name': 'Telangana Andhra Link Superfast',
        'type': 'SUPERFAST',
        'src': 'VSKP', 'dest': 'SC',
        'dep': time(20, 0), 'arr': time(8, 0),
        'dist': 698,
        'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
        'stops': [
            ('VSKP', 1, None, time(20, 0), 0, 0, 0),
            ('AKP', 2, time(20, 33), time(20, 35), 2, 33, 0),
            ('SLO', 3, time(22, 10), time(22, 12), 2, 151, 0),
            ('RJY', 4, time(23, 0), time(23, 5), 5, 201, 0),
            ('EE', 5, time(0, 20), time(0, 22), 2, 291, 1),
            ('BZA', 6, time(1, 40), time(1, 55), 15, 350, 1),
            ('SC', 7, time(8, 0), None, 0, 698, 1),
        ],
        'classes': STANDARD_SF_CLASSES,
    },
    {
        'number': '92812',
        'name': 'Telangana Andhra Link Superfast (Return)',
        'type': 'SUPERFAST',
        'src': 'SC', 'dest': 'VSKP',
        'dep': time(20, 15), 'arr': time(8, 15),
        'dist': 698,
        'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
        'stops': [
            ('SC', 1, None, time(20, 15), 0, 0, 0),
            ('BZA', 2, time(2, 20), time(2, 35), 15, 348, 1),
            ('EE', 3, time(3, 53), time(3, 55), 2, 407, 1),
            ('RJY', 4, time(5, 10), time(5, 15), 5, 497, 1),
            ('SLO', 5, time(6, 3), time(6, 5), 2, 547, 1),
            ('AKP', 6, time(7, 42), time(7, 44), 2, 665, 1),
            ('VSKP', 7, time(8, 15), None, 0, 698, 1),
        ],
        'classes': STANDARD_SF_CLASSES,
    },

    # -------------------------------------------------------------
    # Corridor 7: South Coast Link (Vijayawada <-> Tirupati)
    # 386 km. Superfast avg ~62 km/h.
    # -------------------------------------------------------------
    {
        'number': '92813',
        'name': 'Tirumala Link Superfast',
        'type': 'SUPERFAST',
        'src': 'BZA', 'dest': 'TPTY',
        'dep': time(6, 0), 'arr': time(12, 15),
        'dist': 386,
        'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
        'stops': [
            ('BZA', 1, None, time(6, 0), 0, 0, 0),
            ('TEL', 2, time(6, 30), time(6, 32), 2, 31, 0),
            ('CLX', 3, time(7, 24), time(7, 26), 2, 89, 0),
            ('OGL', 4, time(8, 12), time(8, 14), 2, 138, 0),
            ('NLR', 5, time(10, 0), time(10, 2), 2, 255, 0),
            ('GDR', 6, time(10, 42), time(10, 44), 2, 293, 0),
            ('RU', 7, time(11, 58), time(12, 0), 2, 376, 0),
            ('TPTY', 8, time(12, 15), None, 0, 386, 0),
        ],
        'classes': STANDARD_EXPRESS_CLASSES,
    },
    {
        'number': '92814',
        'name': 'Tirumala Link Superfast (Return)',
        'type': 'SUPERFAST',
        'src': 'TPTY', 'dest': 'BZA',
        'dep': time(15, 30), 'arr': time(21, 45),
        'dist': 386,
        'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
        'stops': [
            ('TPTY', 1, None, time(15, 30), 0, 0, 0),
            ('RU', 2, time(15, 45), time(15, 47), 2, 10, 0),
            ('GDR', 3, time(17, 1), time(17, 3), 2, 93, 0),
            ('NLR', 4, time(17, 43), time(17, 45), 2, 131, 0),
            ('OGL', 5, time(19, 31), time(19, 33), 2, 248, 0),
            ('CLX', 6, time(20, 19), time(20, 21), 2, 297, 0),
            ('TEL', 7, time(21, 13), time(21, 15), 2, 355, 0),
            ('BZA', 8, time(21, 45), None, 0, 386, 0),
        ],
        'classes': STANDARD_EXPRESS_CLASSES,
    },

    # -------------------------------------------------------------
    # Corridor 8: Guntur to Tirupati (Guntur <-> Tirupati)
    # User specific stops: GNT - TEL - CLX - OGL - NLR - GDR - RU - TPTY
    # 380 km. Express avg ~54 km/h.
    # -------------------------------------------------------------
    {
        'number': '92815',
        'name': 'Seven Hills Link Express',
        'type': 'EXPRESS',
        'src': 'GNT', 'dest': 'TPTY',
        'dep': time(7, 30), 'arr': time(14, 30),
        'dist': 380,
        'days': 'MON,WED,FRI',
        'stops': [
            ('GNT', 1, None, time(7, 30), 0, 0, 0),
            ('TEL', 2, time(7, 59), time(8, 1), 2, 26, 0),
            ('CLX', 3, time(8, 57), time(8, 59), 2, 83, 0),
            ('OGL', 4, time(9, 50), time(9, 52), 2, 133, 0),
            ('NLR', 5, time(11, 48), time(11, 50), 2, 249, 0),
            ('GDR', 6, time(12, 32), time(12, 34), 2, 287, 0),
            ('RU', 7, time(14, 10), time(14, 12), 2, 370, 0),
            ('TPTY', 8, time(14, 30), None, 0, 380, 0),
        ],
        'classes': STANDARD_EXPRESS_CLASSES,
    },
    {
        'number': '92816',
        'name': 'Seven Hills Link Express (Return)',
        'type': 'EXPRESS',
        'src': 'TPTY', 'dest': 'GNT',
        'dep': time(8, 15), 'arr': time(15, 15),
        'dist': 380,
        'days': 'TUE,THU,SAT',
        'stops': [
            ('TPTY', 1, None, time(8, 15), 0, 0, 0),
            ('RU', 2, time(8, 33), time(8, 35), 2, 10, 0),
            ('GDR', 3, time(10, 11), time(10, 13), 2, 93, 0),
            ('NLR', 4, time(10, 55), time(10, 57), 2, 131, 0),
            ('OGL', 5, time(12, 53), time(12, 55), 2, 247, 0),
            ('CLX', 6, time(13, 46), time(13, 48), 2, 297, 0),
            ('TEL', 7, time(14, 46), time(14, 48), 2, 354, 0),
            ('GNT', 8, time(15, 15), None, 0, 380, 0),
        ],
        'classes': STANDARD_EXPRESS_CLASSES,
    },

    # -------------------------------------------------------------
    # Corridor 9: Rayalaseema to Secunderabad (Tirupati <-> Secunderabad)
    # 675 km. Overnight Superfast avg ~58 km/h.
    # -------------------------------------------------------------
    {
        'number': '92817',
        'name': 'Rayalaseema Link Superfast',
        'type': 'SUPERFAST',
        'src': 'TPTY', 'dest': 'SC',
        'dep': time(19, 30), 'arr': time(7, 5),
        'dist': 675,
        'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
        'stops': [
            ('TPTY', 1, None, time(19, 30), 0, 0, 0),
            ('RU', 2, time(19, 43), time(19, 45), 2, 10, 0),
            ('HX', 3, time(21, 48), time(21, 50), 2, 135, 0),
            ('GTL', 4, time(0, 50), time(0, 55), 5, 310, 1),
            ('DHNE', 5, time(2, 5), time(2, 7), 2, 378, 1),
            ('KRNT', 6, time(3, 5), time(3, 10), 5, 432, 1),
            ('SC', 7, time(7, 5), None, 0, 675, 1),
        ],
        'classes': STANDARD_SF_CLASSES,
    },
    {
        'number': '92818',
        'name': 'Rayalaseema Link Superfast (Return)',
        'type': 'SUPERFAST',
        'src': 'SC', 'dest': 'TPTY',
        'dep': time(18, 45), 'arr': time(6, 20),
        'dist': 675,
        'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
        'stops': [
            ('SC', 1, None, time(18, 45), 0, 0, 0),
            ('KRNT', 2, time(22, 40), time(22, 45), 5, 243, 0),
            ('DHNE', 3, time(23, 43), time(23, 45), 2, 297, 0),
            ('GTL', 4, time(0, 55), time(1, 0), 5, 365, 1),
            ('HX', 5, time(4, 0), time(4, 2), 2, 540, 1),
            ('RU', 6, time(6, 5), time(6, 7), 2, 665, 1),
            ('TPTY', 7, time(6, 20), None, 0, 675, 1),
        ],
        'classes': STANDARD_SF_CLASSES,
    },

    # -------------------------------------------------------------
    # Corridor 10: Tungabhadra Link Intercity (Kurnool City <-> Tirupati)
    # 432 km. Express avg ~54 km/h.
    # -------------------------------------------------------------
    {
        'number': '92819',
        'name': 'Tungabhadra Link Intercity',
        'type': 'EXPRESS',
        'src': 'KRNT', 'dest': 'TPTY',
        'dep': time(6, 30), 'arr': time(14, 30),
        'dist': 432,
        'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
        'stops': [
            ('KRNT', 1, None, time(6, 30), 0, 0, 0),
            ('DHNE', 2, time(7, 30), time(7, 32), 2, 54, 0),
            ('GTL', 3, time(8, 45), time(8, 50), 5, 122, 0),
            ('HX', 4, time(11, 50), time(11, 52), 2, 297, 0),
            ('RU', 5, time(14, 8), time(14, 10), 2, 422, 0),
            ('TPTY', 6, time(14, 30), None, 0, 432, 0),
        ],
        'classes': [
            ('CC', 'AC Chair Car (CC)', 220.00, 0.95, 2, 78),
            ('SL', 'Sleeper Class (SL)', 110.00, 0.40, 4, 72),
            ('2S', 'Second Sitting (2S)', 45.00, 0.22, 6, 108),
        ],
    },
    {
        'number': '92820',
        'name': 'Tungabhadra Link Intercity (Return)',
        'type': 'EXPRESS',
        'src': 'TPTY', 'dest': 'KRNT',
        'dep': time(15, 0), 'arr': time(23, 0),
        'dist': 432,
        'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
        'stops': [
            ('TPTY', 1, None, time(15, 0), 0, 0, 0),
            ('RU', 2, time(15, 18), time(15, 20), 2, 10, 0),
            ('HX', 3, time(17, 36), time(17, 38), 2, 135, 0),
            ('GTL', 4, time(20, 38), time(20, 43), 5, 310, 0),
            ('DHNE', 5, time(21, 56), time(21, 58), 2, 378, 0),
            ('KRNT', 6, time(23, 0), None, 0, 432, 0),
        ],
        'classes': [
            ('CC', 'AC Chair Car (CC)', 220.00, 0.95, 2, 78),
            ('SL', 'Sleeper Class (SL)', 110.00, 0.40, 4, 72),
            ('2S', 'Second Sitting (2S)', 45.00, 0.22, 6, 108),
        ],
    },

    # -------------------------------------------------------------
    # Corridor 11: Bengaluru Rayalaseema Link (KSR Bengaluru <-> Tirupati)
    # User specific stops: SBC - DMM - ATP - GTL - HX - RU - TPTY
    # 597 km. Express avg ~52 km/h.
    # -------------------------------------------------------------
    {
        'number': '92821',
        'name': 'Bengaluru Rayalaseema Link',
        'type': 'EXPRESS',
        'src': 'SBC', 'dest': 'TPTY',
        'dep': time(6, 15), 'arr': time(17, 45),
        'dist': 597,
        'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
        'stops': [
            ('SBC', 1, None, time(6, 15), 0, 0, 0),
            ('DMM', 2, time(9, 45), time(9, 50), 5, 186, 0),
            ('ATP', 3, time(10, 26), time(10, 28), 2, 219, 0),
            ('GTL', 4, time(11, 45), time(11, 50), 5, 287, 0),
            ('HX', 5, time(15, 5), time(15, 7), 2, 462, 0),
            ('RU', 6, time(17, 25), time(17, 27), 2, 587, 0),
            ('TPTY', 7, time(17, 45), None, 0, 597, 0),
        ],
        'classes': STANDARD_EXPRESS_CLASSES,
    },
    {
        'number': '92822',
        'name': 'Bengaluru Rayalaseema Link (Return)',
        'type': 'EXPRESS',
        'src': 'TPTY', 'dest': 'SBC',
        'dep': time(7, 30), 'arr': time(19, 0),
        'dist': 597,
        'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
        'stops': [
            ('TPTY', 1, None, time(7, 30), 0, 0, 0),
            ('RU', 2, time(7, 48), time(7, 50), 2, 10, 0),
            ('HX', 3, time(10, 8), time(10, 10), 2, 135, 0),
            ('GTL', 4, time(13, 25), time(13, 30), 5, 310, 0),
            ('ATP', 5, time(14, 47), time(14, 49), 2, 378, 0),
            ('DMM', 6, time(15, 25), time(15, 30), 5, 411, 0),
            ('SBC', 7, time(19, 0), None, 0, 597, 0),
        ],
        'classes': STANDARD_EXPRESS_CLASSES,
    },

    # -------------------------------------------------------------
    # Corridor 12: Karnataka Andhra Corridor Express (KSR Bengaluru <-> Vijayawada)
    # SBC - DMM - ATP - GTL - DHNE - NDL - NRT - GNT - BZA
    # 660 km. Express avg ~53 km/h.
    # -------------------------------------------------------------
    {
        'number': '92823',
        'name': 'Karnataka Andhra Corridor Express',
        'type': 'EXPRESS',
        'src': 'SBC', 'dest': 'BZA',
        'dep': time(18, 0), 'arr': time(6, 30),
        'dist': 660,
        'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
        'stops': [
            ('SBC', 1, None, time(18, 0), 0, 0, 0),
            ('DMM', 2, time(21, 25), time(21, 30), 5, 186, 0),
            ('ATP', 3, time(22, 5), time(22, 7), 2, 219, 0),
            ('GTL', 4, time(23, 20), time(23, 25), 5, 287, 0),
            ('DHNE', 5, time(0, 38), time(0, 40), 2, 355, 1),
            ('NDL', 6, time(1, 58), time(2, 0), 2, 430, 1),
            ('NRT', 7, time(4, 38), time(4, 40), 2, 583, 1),
            ('GNT', 8, time(5, 30), time(5, 35), 5, 628, 1),
            ('BZA', 9, time(6, 30), None, 0, 660, 1),
        ],
        'classes': STANDARD_EXPRESS_CLASSES,
    },
    {
        'number': '92824',
        'name': 'Karnataka Andhra Corridor Express (Return)',
        'type': 'EXPRESS',
        'src': 'BZA', 'dest': 'SBC',
        'dep': time(18, 30), 'arr': time(7, 0),
        'dist': 660,
        'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
        'stops': [
            ('BZA', 1, None, time(18, 30), 0, 0, 0),
            ('GNT', 2, time(19, 10), time(19, 15), 5, 32, 0),
            ('NRT', 3, time(20, 5), time(20, 7), 2, 77, 0),
            ('NDL', 4, time(22, 45), time(22, 47), 2, 230, 0),
            ('DHNE', 5, time(0, 5), time(0, 7), 2, 305, 1),
            ('GTL', 6, time(1, 20), time(1, 25), 5, 373, 1),
            ('ATP', 7, time(2, 38), time(2, 40), 2, 441, 1),
            ('DMM', 8, time(3, 18), time(3, 23), 5, 474, 1),
            ('SBC', 9, time(7, 0), None, 0, 660, 1),
        ],
        'classes': STANDARD_EXPRESS_CLASSES,
    },

    # -------------------------------------------------------------
    # Corridor 13: Southern Coastal Superfast (Chennai Central <-> Visakhapatnam)
    # 780 km. Superfast avg ~64 km/h (Complementary timing).
    # -------------------------------------------------------------
    {
        'number': '92825',
        'name': 'Southern Coastal Superfast',
        'type': 'SUPERFAST',
        'src': 'MAS', 'dest': 'VSKP',
        'dep': time(17, 30), 'arr': time(5, 45),
        'dist': 780,
        'days': 'TUE,THU,SAT',
        'stops': [
            ('MAS', 1, None, time(17, 30), 0, 0, 0),
            ('GDR', 2, time(19, 38), time(19, 40), 2, 138, 0),
            ('NLR', 3, time(20, 18), time(20, 20), 2, 176, 0),
            ('OGL', 4, time(22, 3), time(22, 5), 2, 292, 0),
            ('TEL', 5, time(23, 43), time(23, 45), 2, 399, 0),
            ('BZA', 6, time(0, 20), time(0, 30), 10, 430, 1),
            ('EE', 7, time(1, 28), time(1, 30), 2, 489, 1),
            ('TDD', 8, time(2, 13), time(2, 15), 2, 537, 1),
            ('RJY', 9, time(2, 55), time(3, 0), 5, 579, 1),
            ('SLO', 10, time(3, 43), time(3, 45), 2, 629, 1),
            ('AKP', 11, time(5, 13), time(5, 15), 2, 747, 1),
            ('VSKP', 12, time(5, 45), None, 0, 780, 1),
        ],
        'classes': STANDARD_SF_CLASSES,
    },
    {
        'number': '92826',
        'name': 'Southern Coastal Superfast (Return)',
        'type': 'SUPERFAST',
        'src': 'VSKP', 'dest': 'MAS',
        'dep': time(18, 15), 'arr': time(6, 30),
        'dist': 780,
        'days': 'MON,WED,FRI',
        'stops': [
            ('VSKP', 1, None, time(18, 15), 0, 0, 0),
            ('AKP', 2, time(18, 47), time(18, 49), 2, 33, 0),
            ('SLO', 3, time(20, 17), time(20, 19), 2, 151, 0),
            ('RJY', 4, time(21, 2), time(21, 7), 5, 201, 0),
            ('TDD', 5, time(21, 47), time(21, 49), 2, 243, 0),
            ('EE', 6, time(22, 32), time(22, 34), 2, 291, 0),
            ('BZA', 7, time(23, 30), time(23, 40), 10, 350, 0),
            ('TEL', 8, time(0, 10), time(0, 12), 2, 381, 1),
            ('OGL', 9, time(1, 50), time(1, 52), 2, 488, 1),
            ('NLR', 10, time(3, 35), time(3, 37), 2, 604, 1),
            ('GDR', 11, time(4, 18), time(4, 20), 2, 642, 1),
            ('MAS', 12, time(6, 30), None, 0, 780, 1),
        ],
        'classes': STANDARD_SF_CLASSES,
    },

    # -------------------------------------------------------------
    # Corridor 14: Krishna Passenger (Machilipatnam <-> Guntur)
    # 137 km. Passenger avg ~40 km/h.
    # -------------------------------------------------------------
    {
        'number': '92827',
        'name': 'Krishna Machilipatnam Passenger',
        'type': 'EXPRESS',
        'src': 'MTM', 'dest': 'GNT',
        'dep': time(6, 45), 'arr': time(10, 10),
        'dist': 137,
        'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
        'stops': [
            ('MTM', 1, None, time(6, 45), 0, 0, 0),
            ('BZA', 2, time(8, 45), time(8, 55), 10, 80, 0),
            ('TEL', 3, time(9, 36), time(9, 38), 2, 111, 0),
            ('GNT', 4, time(10, 10), None, 0, 137, 0),
        ],
        'classes': PASSENGER_MEMU_CLASSES,
    },
    {
        'number': '92828',
        'name': 'Krishna Machilipatnam Passenger (Return)',
        'type': 'EXPRESS',
        'src': 'GNT', 'dest': 'MTM',
        'dep': time(16, 0), 'arr': time(19, 25),
        'dist': 137,
        'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
        'stops': [
            ('GNT', 1, None, time(16, 0), 0, 0, 0),
            ('TEL', 2, time(16, 32), time(16, 34), 2, 26, 0),
            ('BZA', 3, time(17, 15), time(17, 25), 10, 57, 0),
            ('MTM', 4, time(19, 25), None, 0, 137, 0),
        ],
        'classes': PASSENGER_MEMU_CLASSES,
    },

    # -------------------------------------------------------------
    # Corridor 15: Southern Link Intercity (Vijayawada <-> Chennai Central)
    # 430 km. Superfast avg ~63 km/h.
    # -------------------------------------------------------------
    {
        'number': '92829',
        'name': 'Southern Link Intercity',
        'type': 'SUPERFAST',
        'src': 'BZA', 'dest': 'MAS',
        'dep': time(6, 15), 'arr': time(13, 5),
        'dist': 430,
        'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
        'stops': [
            ('BZA', 1, None, time(6, 15), 0, 0, 0),
            ('TEL', 2, time(6, 45), time(6, 47), 2, 31, 0),
            ('CLX', 3, time(7, 39), time(7, 41), 2, 89, 0),
            ('OGL', 4, time(8, 27), time(8, 29), 2, 138, 0),
            ('NLR', 5, time(10, 15), time(10, 17), 2, 255, 0),
            ('GDR', 6, time(10, 57), time(10, 59), 2, 293, 0),
            ('MAS', 7, time(13, 5), None, 0, 430, 0),
        ],
        'classes': INTERCITY_CC_CLASSES,
    },
    {
        'number': '92830',
        'name': 'Southern Link Intercity (Return)',
        'type': 'SUPERFAST',
        'src': 'MAS', 'dest': 'BZA',
        'dep': time(14, 15), 'arr': time(21, 5),
        'dist': 430,
        'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
        'stops': [
            ('MAS', 1, None, time(14, 15), 0, 0, 0),
            ('GDR', 2, time(16, 21), time(16, 23), 2, 137, 0),
            ('NLR', 3, time(17, 3), time(17, 5), 2, 175, 0),
            ('OGL', 4, time(18, 51), time(18, 53), 2, 292, 0),
            ('CLX', 5, time(19, 39), time(19, 41), 2, 341, 0),
            ('TEL', 6, time(20, 33), time(20, 35), 2, 399, 0),
            ('BZA', 7, time(21, 5), None, 0, 430, 0),
        ],
        'classes': INTERCITY_CC_CLASSES,
    },

    # -------------------------------------------------------------
    # Corridor 16: North Coast Passenger (Vizianagaram <-> Rajahmundry)
    # 262 km. Passenger avg ~38 km/h.
    # -------------------------------------------------------------
    {
        'number': '92831',
        'name': 'North Coast Passenger',
        'type': 'EXPRESS',
        'src': 'VZM', 'dest': 'RJY',
        'dep': time(5, 45), 'arr': time(12, 40),
        'dist': 262,
        'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
        'stops': [
            ('VZM', 1, None, time(5, 45), 0, 0, 0),
            ('VSKP', 2, time(7, 10), time(7, 25), 15, 61, 0),
            ('AKP', 3, time(8, 17), time(8, 19), 2, 94, 0),
            ('SLO', 4, time(10, 35), time(10, 37), 2, 212, 0),
            ('RJY', 5, time(12, 40), None, 0, 262, 0),
        ],
        'classes': PASSENGER_MEMU_CLASSES,
    },
    {
        'number': '92832',
        'name': 'North Coast Passenger (Return)',
        'type': 'EXPRESS',
        'src': 'RJY', 'dest': 'VZM',
        'dep': time(14, 0), 'arr': time(20, 55),
        'dist': 262,
        'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
        'stops': [
            ('RJY', 1, None, time(14, 0), 0, 0, 0),
            ('SLO', 2, time(16, 3), time(16, 5), 2, 50, 0),
            ('AKP', 3, time(18, 21), time(18, 23), 2, 168, 0),
            ('VSKP', 4, time(19, 15), time(19, 30), 15, 201, 0),
            ('VZM', 5, time(20, 55), None, 0, 262, 0),
        ],
        'classes': PASSENGER_MEMU_CLASSES,
    },

    # -------------------------------------------------------------
    # Corridor 17: Deccan Rayalaseema Superfast (Secunderabad <-> KSR Bengaluru)
    # User specific stops: SC - KRNT - DHNE - GTL - ATP - DMM - SBC
    # 652 km. Superfast avg ~62 km/h.
    # -------------------------------------------------------------
    {
        'number': '92833',
        'name': 'Deccan Rayalaseema Superfast',
        'type': 'SUPERFAST',
        'src': 'SC', 'dest': 'SBC',
        'dep': time(19, 0), 'arr': time(5, 30),
        'dist': 652,
        'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
        'stops': [
            ('SC', 1, None, time(19, 0), 0, 0, 0),
            ('KRNT', 2, time(22, 55), time(23, 0), 5, 243, 0),
            ('DHNE', 3, time(23, 53), time(23, 55), 2, 297, 0),
            ('GTL', 4, time(1, 3), time(1, 8), 5, 365, 1),
            ('ATP', 5, time(2, 16), time(2, 18), 2, 433, 1),
            ('DMM', 6, time(2, 51), time(2, 55), 4, 466, 1),
            ('SBC', 7, time(5, 30), None, 0, 652, 1),
        ],
        'classes': STANDARD_SF_CLASSES,
    },
    {
        'number': '92834',
        'name': 'Deccan Rayalaseema Superfast (Return)',
        'type': 'SUPERFAST',
        'src': 'SBC', 'dest': 'SC',
        'dep': time(20, 15), 'arr': time(6, 45),
        'dist': 652,
        'days': 'MON,TUE,WED,THU,FRI,SAT,SUN',
        'stops': [
            ('SBC', 1, None, time(20, 15), 0, 0, 0),
            ('DMM', 2, time(22, 50), time(22, 54), 4, 186, 0),
            ('ATP', 3, time(23, 27), time(23, 29), 2, 219, 0),
            ('GTL', 4, time(0, 37), time(0, 42), 5, 287, 1),
            ('DHNE', 5, time(1, 50), time(1, 52), 2, 355, 1),
            ('KRNT', 6, time(2, 45), time(2, 50), 5, 409, 1),
            ('SC', 7, time(6, 45), None, 0, 652, 1),
        ],
        'classes': STANDARD_SF_CLASSES,
    },

    # -------------------------------------------------------------
    # Corridor 18: Circar Link Express (Kakinada Town <-> Chennai Central)
    # 642 km. Express avg ~53 km/h.
    # -------------------------------------------------------------
    {
        'number': '92835',
        'name': 'Circar Link Express',
        'type': 'EXPRESS',
        'src': 'CCT', 'dest': 'MAS',
        'dep': time(17, 15), 'arr': time(5, 20),
        'dist': 642,
        'days': 'MON,WED,FRI,SUN',
        'stops': [
            ('CCT', 1, None, time(17, 15), 0, 0, 0),
            ('SLO', 2, time(17, 29), time(17, 31), 2, 12, 0),
            ('RJY', 3, time(18, 23), time(18, 28), 5, 63, 0),
            ('TDD', 4, time(19, 14), time(19, 16), 2, 105, 0),
            ('EE', 5, time(20, 8), time(20, 10), 2, 153, 0),
            ('BZA', 6, time(21, 20), time(21, 30), 10, 212, 0),
            ('TEL', 7, time(22, 5), time(22, 7), 2, 243, 0),
            ('OGL', 8, time(0, 10), time(0, 12), 2, 350, 1),
            ('NLR', 9, time(2, 25), time(2, 27), 2, 466, 1),
            ('GDR', 10, time(3, 10), time(3, 12), 2, 504, 1),
            ('MAS', 11, time(5, 20), None, 0, 642, 1),
        ],
        'classes': STANDARD_EXPRESS_CLASSES,
    },
    {
        'number': '92836',
        'name': 'Circar Link Express (Return)',
        'type': 'EXPRESS',
        'src': 'MAS', 'dest': 'CCT',
        'dep': time(18, 45), 'arr': time(6, 50),
        'dist': 642,
        'days': 'TUE,THU,SAT,SUN',
        'stops': [
            ('MAS', 1, None, time(18, 45), 0, 0, 0),
            ('GDR', 2, time(20, 53), time(20, 55), 2, 138, 0),
            ('NLR', 3, time(21, 38), time(21, 40), 2, 176, 0),
            ('OGL', 4, time(23, 53), time(23, 55), 2, 292, 0),
            ('TEL', 5, time(1, 58), time(2, 0), 2, 399, 1),
            ('BZA', 6, time(2, 35), time(2, 45), 10, 430, 1),
            ('EE', 7, time(3, 55), time(3, 57), 2, 489, 1),
            ('TDD', 8, time(4, 49), time(4, 51), 2, 537, 1),
            ('RJY', 9, time(5, 37), time(5, 42), 5, 579, 1),
            ('SLO', 10, time(6, 34), time(6, 36), 2, 630, 1),
            ('CCT', 11, time(6, 50), None, 0, 642, 1),
        ],
        'classes': STANDARD_EXPRESS_CLASSES,
    },
]
