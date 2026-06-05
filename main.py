import psycopg
import csv
import matplotlib.pyplot as plt


# =========================
# Připojení k databázi
# =========================

def connect():
    return psycopg.connect(
        host="localhost",
        dbname="obce",
        user="student",
        password="student"
    )


# =========================
# Výpis okresů
# =========================

def vypis_okresu():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT id_okres, nazev
        FROM okresy
        ORDER BY nazev
    """)

    print("\nSEZNAM OKRESŮ")
    print("-" * 40)

    for okres in cur.fetchall():
        print(f"{okres[0]} - {okres[1]}")

    cur.close()
    conn.close()


# =========================
# Obce v okrese
# =========================

def obce_v_okrese():
    kod = input("Zadej kód okresu: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            nazev,
            pocet_obyvatel,
            prumerny_vek
        FROM obce_pob
        WHERE id_okres = %s
        ORDER BY nazev
    """, (kod,))

    vysledky = cur.fetchall()

    if not vysledky:
        print("Okres nebyl nalezen.")
        return

    print("\nNázev obce | Obyvatel | Průměrný věk")
    print("-" * 60)

    for obec in vysledky:
        print(
            f"{obec[0]:30} "
            f"{obec[1]:10} "
            f"{obec[2]}"
        )

    cur.close()
    conn.close()


# =========================
# Hledání obce
# =========================

def hledani_obce():
    hledat = input("Zadej část názvu obce: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            nazev,
            pocet_obyvatel
        FROM obce_pob
        WHERE LOWER(nazev)
        LIKE LOWER(%s)
        ORDER BY nazev
    """, (f"%{hledat}%",))

    vysledky = cur.fetchall()

    print("\nNalezené obce")
    print("-" * 40)

    if len(vysledky) == 0:
        print("Žádná obec nenalezena.")

    for obec in vysledky:
        print(f"{obec[0]} ({obec[1]} obyvatel)")

    cur.close()
    conn.close()


# =========================
# Statistiky okresu
# =========================

def statistika_okresu():
    kod = input("Zadej kód okresu: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            SUM(pocet_obyvatel),
            AVG(prumerny_vek),
            SUM(pocet_muzi),
            SUM(pocet_zeny)
        FROM obce_pob
        WHERE id_okres = %s
    """, (kod,))

    data = cur.fetchone()

    if data[0] is None:
        print("Okres nebyl nalezen.")
        return

    print("\nSTATISTIKA OKRESU")
    print("-" * 40)

    print(f"Počet obyvatel: {int(data[0])}")
    print(f"Průměrný věk: {round(data[1],2)}")
    print(f"Počet mužů: {int(data[2])}")
    print(f"Počet žen: {int(data[3])}")

    if data[3] != 0:
        pomer = round(data[2] / data[3], 2)
        print(f"Poměr muži/ženy: {pomer}")

    cur.close()
    conn.close()


# =========================
# TOP 10 obcí
# =========================

def top10():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            nazev,
            pocet_obyvatel
        FROM obce_pob
        ORDER BY pocet_obyvatel DESC
        LIMIT 10
    """)

    print("\nTOP 10 NEJVĚTŠÍCH OBCÍ")
    print("-" * 40)

    poradi = 1

    for obec in cur.fetchall():
        print(
            f"{poradi}. "
            f"{obec[0]} - "
            f"{obec[1]} obyvatel"
        )
        poradi += 1

    cur.close()
    conn.close()


# =========================
# Export do CSV
# =========================

def export_csv():
    kod = input("Zadej kód okresu: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            nazev,
            pocet_obyvatel,
            prumerny_vek
        FROM obce_pob
        WHERE id_okres = %s
        ORDER BY nazev
    """, (kod,))

    data = cur.fetchall()

    if len(data) == 0:
        print("Okres nebyl nalezen.")
        return

    soubor = f"{kod}.csv"

    with open(
        soubor,
        "w",
        newline="",
        encoding="utf-8"
    ) as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow([
            "Obec",
            "Počet obyvatel",
            "Průměrný věk"
        ])

        writer.writerows(data)

    print(f"Soubor {soubor} byl vytvořen.")

    cur.close()
    conn.close()


# =========================
# Graf obyvatel
# =========================

def graf_okresu():
    kod = input("Zadej kód okresu: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            nazev,
            pocet_obyvatel
        FROM obce_pob
        WHERE id_okres = %s
        ORDER BY pocet_obyvatel DESC
        LIMIT 10
    """, (kod,))

    data = cur.fetchall()

    if len(data) == 0:
        print("Okres nebyl nalezen.")
        return

    nazvy = []
    obyvatele = []

    for obec in data:
        nazvy.append(obec[0])
        obyvatele.append(obec[1])

    plt.figure(figsize=(10, 5))
    plt.bar(nazvy, obyvatele)
    plt.title(f"TOP 10 obcí okresu {kod}")
    plt.xlabel("Obec")
    plt.ylabel("Počet obyvatel")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    cur.close()
    conn.close()


# =========================
# MENU
# =========================

def menu():
    while True:

        print("\n=========================")
        print(" DEMOGRAFIE ČR ")
        print("=========================")
        print("1 - Seznam okresů")
        print("2 - Obce v okrese")
        print("3 - Hledat obec")
        print("4 - Statistiky okresu")
        print("5 - TOP 10 obcí")
        print("6 - Export do CSV")
        print("7 - Graf okresu")
        print("0 - Konec")

        volba = input("\nVyber: ")

        if volba == "1":
            vypis_okresu()

        elif volba == "2":
            obce_v_okrese()

        elif volba == "3":
            hledani_obce()

        elif volba == "4":
            statistika_okresu()

        elif volba == "5":
            top10()

        elif volba == "6":
            export_csv()

        elif volba == "7":
            graf_okresu()

        elif volba == "0":
            print("Program ukončen.")
            break

        else:
            print("Neplatná volba.")


# =========================
# START PROGRAMU
# =========================

if __name__ == "__main__":
    menu()
