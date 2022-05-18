EngineUnit1 = f"mysql+mysqlconnector://root:P%40ssw0rd@192.168.1.10/db_bat_tja1"
EngineUnit2 = f"mysql+mysqlconnector://root:P%40ssw0rd@192.168.1.11/db_bat_tja2"

EngineUnit = {
    'tja1': f"mysql+mysqlconnector://smlds:SMLds2021!@35.219.48.62/db_bat_tja1",
    'tja2': f"mysql+mysqlconnector://smlds:SMLds2021!@35.219.48.62/db_bat_tja2",
}

TagsDescription = {
    "COPT Enable": "COMBUSTION ENABLE",
    "SOPT Enable": "SOOT BLOWER OPERATION ON/OFF (Main Start/Stop)",
    "Watchdog": "WatchdogStatus",
    "COPT Safeguard": "SAFEGUARD:COMBUSTION",
    "Efficiency": "Efficiency"
}

UpdateRate = 60 * 10     # seconds