import cv2
import numpy as np
import time
import os


class DetektorPohybu:
    def __init__(self, nastaveni):
        self.nastaveni = nastaveni
        self.pozadi = None
        self.cas_posledniho_ulozeni = 0.0

    def priprav_obraz(self, snimek):
        sedy = cv2.cvtColor(snimek, cv2.COLOR_BGR2GRAY)

        velikost = int(self.nastaveni.rozmazani)
        if velikost < 1:
            velikost = 1
        if velikost % 2 == 0:
            velikost += 1

        rozmazany = cv2.GaussianBlur(sedy, (velikost, velikost), 0)
        return rozmazany

    def detekuj(self, snimek):
        obraz = self.priprav_obraz(snimek)

        if self.pozadi is None:
            self.pozadi = obraz.astype("float")
            maska = np.zeros_like(obraz)
            return maska, [], False

        cv2.accumulateWeighted(obraz, self.pozadi, 0.02)
        pozadi_uint8 = cv2.convertScaleAbs(self.pozadi)

        rozdil = cv2.absdiff(obraz, pozadi_uint8)

        prah = int(self.nastaveni.prah_pohybu)
        _, maska = cv2.threshold(rozdil, prah, 255, cv2.THRESH_BINARY)

        iterace = int(self.nastaveni.dilatace)
        if iterace > 0:
            maska = cv2.dilate(maska, None, iterations=iterace)

        vysledek = cv2.findContours(maska, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        kontury = vysledek[0]

        obdelniky = []
        min_vel = int(self.nastaveni.minimalni_velikost)

        for kontura in kontury:
            plocha = cv2.contourArea(kontura)
            if plocha < min_vel:
                continue

            x, y, sirka, vyska = cv2.boundingRect(kontura)
            obdelniky.append((x, y, sirka, vyska))

        pohyb = len(obdelniky) > 0
        return maska, obdelniky, pohyb

    def resetuj_pozadi(self):
        self.pozadi = None

    def uloz_snimek(self, snimek, obdelniky, slozka="zachyty"):
        aktualni_cas = time.time()
        pauza = float(self.nastaveni.pauza_mezi_ulozenim)

        if aktualni_cas - self.cas_posledniho_ulozeni < pauza:
            return

        if not os.path.exists(slozka):
            os.makedirs(slozka)

        for x, y, s, v in obdelniky:
            cv2.rectangle(snimek, (x, y), (x + s, y + v), (0, 0, 255), 2)

        casovy_text = time.strftime("%Y%m%d_%H%M%S")
        nazev = os.path.join(slozka, "snimek_" + casovy_text + ".jpg")
        cv2.imwrite(nazev, snimek)

        self.cas_posledniho_ulozeni = aktualni_cas
