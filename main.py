import csv
import matplotlib.pyplot as plt
from database import connect
import tkinter as tk
from tkinter import ttk, messagebox
from database import connect
import csv


def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def vypis_kody_okresu():
    clear_frame(content_frame)

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT id_okres
        FROM obce_pob
        ORDER BY id_okres
    """)

    data = cur.fetchall()
    conn.close()

    lb = tk.Listbox(content_frame)
    lb.pack(fill="both", expand=True)

    for okres in data:
        lb.insert("end", okres[0])


def get_okres():
    return entry_okres.get().strip().upper()


def zobraz_obce():
    clear_frame(content_frame)

    kod = get_okres()
    if not kod:
        messagebox.showwarning("Chyba", "Zadej kód okresu")
        return

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT nazev, pocet_obyvatel, prumerny_vek
        FROM obce_pob
        WHERE id_okres = %s
        ORDER BY nazev
    """, (kod,))

    data = cur.fetchall()
    conn.close()

    tree = ttk.Treeview(content_frame, columns=("a", "b", "c"), show="headings")
    tree.heading("a", text="Obec")
    tree.heading("b", text="Počet obyvatel")
    tree.heading("c", text="Průměrný věk")

    tree.pack(fill="both", expand=True)

    if not data:
        messagebox.showinfo("Info", "Žádná data")
        return

    for row in data:
        tree.insert("", "end", values=row)


def hledat_obec():
    clear_frame(content_frame)

    tk.Label(content_frame, text="Zadej část názvu:").pack()

    search_entry = tk.Entry(content_frame)
    search_entry.pack()


    def search():
        conn = connect()
        cur = conn.cursor()

        cur.execute("""
            SELECT nazev, pocet_obyvatel
            FROM obce_pob
            WHERE LOWER(nazev) LIKE LOWER(%s)
        """, (f"%{search_entry.get()}%",))

        data = cur.fetchall()
        conn.close()

        result = tk.Listbox(content_frame)
        result.pack(fill="both", expand=True)

        for d in data:
            result.insert("end", f"{d[0]} ({d[1]} obyvatel)")

    tk.Button(content_frame, text="Hledat", command=search).pack()


def statistika():
    clear_frame(content_frame)

    kod = get_okres()
    if not kod:
        messagebox.showwarning("Chyba", "Zadej kód okresu")
        return

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
    conn.close()

    if not data[0]:
        messagebox.showinfo("Info", "Okres nenalezen")
        return

    text = f"""
Počet obyvatel: {int(data[0])}
Průměrný věk: {round(data[1],2)}
Muži: {int(data[2])}
Ženy: {int(data[3])}
"""

    tk.Label(content_frame, text=text, font=("Arial", 12)).pack()


def top10():
    clear_frame(content_frame)

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT nazev, pocet_obyvatel
        FROM obce_pob
        ORDER BY pocet_obyvatel DESC
        LIMIT 10
    """)

    data = cur.fetchall()
    conn.close()

    lb = tk.Listbox(content_frame)
    lb.pack(fill="both", expand=True)

    for i, d in enumerate(data, 1):
        lb.insert("end", f"{i}. {d[0]} - {d[1]} obyvatel")


def export_csv():
    kod = get_okres()
    if not kod:
        return

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT nazev, pocet_obyvatel, prumerny_vek
        FROM obce_pob
        WHERE id_okres = %s
    """, (kod,))

    data = cur.fetchall()
    conn.close()

    with open(f"{kod}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Obec", "Obyvatel", "Věk"])
        writer.writerows(data)

    messagebox.showinfo("Hotovo", f"Export {kod}.csv dokončen")

root = tk.Tk()
root.title("Demografie ČR")
root.geometry("1000x600")

top_frame = tk.Frame(root)
top_frame.pack(fill="x")

tk.Label(top_frame, text="Kód okresu:").pack(side="left")

entry_okres = tk.Entry(top_frame)
entry_okres.pack(side="left", padx=5)

menu_frame = tk.Frame(root)
menu_frame.pack(side="left", fill="y")

content_frame = tk.Frame(root)
content_frame.pack(side="right", fill="both", expand=True)

tk.Button(menu_frame, text="Výpis kódů okresů", command=vypis_kody_okresu).pack(fill="x")
tk.Button(menu_frame, text="Obce", command=zobraz_obce).pack(fill="x")
tk.Button(menu_frame, text="Hledat obec", command=hledat_obec).pack(fill="x")
tk.Button(menu_frame, text="Statistika", command=statistika).pack(fill="x")
tk.Button(menu_frame, text="TOP 10", command=top10).pack(fill="x")
tk.Button(menu_frame, text="Export CSV", command=export_csv).pack(fill="x")


root.mainloop()


root.title("Demografie ČR")
root.geometry("1000x600")

nadpis = tk.Label(
    root,
    text="DEMOGRAFIE ČR",
    font=("Arial", 18, "bold")
)
nadpis.pack(pady=10)

frame = tk.Frame(root)
frame.pack()

tk.Label(
    frame,
    text="Kód okresu:"
).pack(side="left")

entry_okres = tk.Entry(
    frame,
    width=20
)
entry_okres.pack(
    side="left",
    padx=10
)

btn_obce = tk.Button(
    frame,
    text="Načíst obce",
    command=nacti_obce
)
btn_obce.pack(side="left")

btn_stat = tk.Button(
    frame,
    text="Statistika",
    command=statistika
)
btn_stat.pack(
    side="left",
    padx=10
)

tree = ttk.Treeview(
    root,
    columns=(
        "obec",
        "obyvatele",
        "vek"
    ),
    show="headings"
)

tree.heading(
    "obec",
    text="Obec"
)

tree.heading(
    "obyvatele",
    text="Počet obyvatel"
)

tree.heading(
    "vek",
    text="Průměrný věk"
)

tree.column(
    "obec",
    width=400
)

tree.column(
    "obyvatele",
    width=150
)

tree.column(
    "vek",
    width=150
)

tree.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)

root.mainloop()


def obce_v_okrese():
    kod = input("Zadej kód okresu: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT nazev, pocet_obyvatel, prumerny_vek
        FROM obce_pob
        WHERE id_okres = %s
        ORDER BY nazev
    """, (kod,))

    vysledky = cur.fetchall()

    if not vysledky:
        print("Okres nebyl nalezen.")
        cur.close()
        conn.close()
        return

    print("\nNázev obce | Obyvatel | Průměrný věk")
    print("-" * 60)

    for obec in vysledky:
        print(f"{obec[0]:30} {obec[1]:10} {obec[2]}")

    cur.close()
    conn.close()


def hledani_obce():
    hledat = input("Zadej část názvu obce: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT nazev, pocet_obyvatel
        FROM obce_pob
        WHERE LOWER(nazev) LIKE LOWER(%s)
        ORDER BY nazev
    """, (f"%{hledat}%",))

    vysledky = cur.fetchall()

    print("\nNalezené obce")
    print("-" * 40)

    if not vysledky:
        print("Žádná obec nenalezena.")

    for obec in vysledky:
        print(f"{obec[0]} ({obec[1]} obyvatel)")

    cur.close()
    conn.close()


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
        cur.close()
        conn.close()
        return

    print("\nSTATISTIKA OKRESU")
    print("-" * 40)
    print(f"Počet obyvatel: {int(data[0])}")
    print(f"Průměrný věk: {round(data[1], 2)}")
    print(f"Počet mužů: {int(data[2])}")
    print(f"Počet žen: {int(data[3])}")

    if data[3] != 0:
        print(f"Poměr muži/ženy: {round(data[2] / data[3], 2)}")

    cur.close()
    conn.close()


def top10():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT nazev, pocet_obyvatel
        FROM obce_pob
        ORDER BY pocet_obyvatel DESC
        LIMIT 10
    """)

    print("\nTOP 10 NEJVĚTŠÍCH OBCÍ")
    print("-" * 40)

    for poradi, obec in enumerate(cur.fetchall(), start=1):
        print(f"{poradi}. {obec[0]} - {obec[1]} obyvatel")

    cur.close()
    conn.close()


def export_csv():
    kod = input("Zadej kód okresu: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT nazev, pocet_obyvatel, prumerny_vek
        FROM obce_pob
        WHERE id_okres = %s
        ORDER BY nazev
    """, (kod,))

    data = cur.fetchall()

    if not data:
        print("Okres nebyl nalezen.")
        cur.close()
        conn.close()
        return

    with open(f"{kod}.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Obec", "Počet obyvatel", "Průměrný věk"])
        writer.writerows(data)

    print(f"Soubor {kod}.csv byl vytvořen.")

    cur.close()
    conn.close()


def graf_okresu():
    kod = input("Zadej kód okresu: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT nazev, pocet_obyvatel
        FROM obce_pob
        WHERE id_okres = %s
        ORDER BY pocet_obyvatel DESC
        LIMIT 10
    """, (kod,))

    data = cur.fetchall()

    if not data:
        print("Okres nebyl nalezen.")
        cur.close()
        conn.close()
        return

    nazvy = [x[0] for x in data]
    obyvatele = [x[1] for x in data]

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
            vypis_kody_okresu()
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


if __name__ == "__main__":
    menu()
