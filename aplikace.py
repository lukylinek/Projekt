import sys
import cv2

from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QCheckBox, QHBoxLayout, QVBoxLayout, QGridLayout, QGroupBox, QInputDialog
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap, QFont

from config import NastaveniPohybu
from kamera import Kamera
from detektor_pohybu import DetektorPohybu
from clovek import DetektorObjektu
from zona import Zona


def cv_obraz_do_pixmap(obraz_bgr):
    obraz_rgb = cv2.cvtColor(obraz_bgr, cv2.COLOR_BGR2RGB)

    vyska = obraz_rgb.shape[0]
    sirka = obraz_rgb.shape[1]
    kanaly = obraz_rgb.shape[2]

    bytes_per_pixel = kanaly
    bytes_per_line = bytes_per_pixel * sirka

    qimg = QImage(obraz_rgb.data, sirka, vyska, bytes_per_line, QImage.Format_RGB888)
    pixmap = QPixmap.fromImage(qimg)
    return pixmap


def cv_seda_do_pixmap(obraz_gray):
    vyska = obraz_gray.shape[0]
    sirka = obraz_gray.shape[1]

    bytes_per_pixel = 1
    bytes_per_line = bytes_per_pixel * sirka

    qimg = QImage(obraz_gray.data, sirka, vyska, bytes_per_line, QImage.Format_Grayscale8)
    pixmap = QPixmap.fromImage(qimg)
    return pixmap


def nacti_coco_tridy(cesta="COCO.txt"):
    tridy = {}

    with open(cesta, "r", encoding="utf-8") as f:
        for radek in f:
            radek = radek.strip()
            if not radek:
                continue
            if "=" not in radek:
                continue

            leva_cast, prava_cast = radek.split("=", 1)

            leva_cast = leva_cast.strip()
            prava_cast = prava_cast.strip()

            if not leva_cast or not prava_cast:
                continue

            try:
                tid = int(leva_cast)
            except ValueError:
                continue

            tridy[tid] = prava_cast

    return tridy


class Aplikace(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Kamera – detekce pohybu a objektu")
        self.resize(1200, 720)

        self.nastaveni = NastaveniPohybu()
        self.kamera = Kamera()
        self.detektor_pohybu = DetektorPohybu(self.nastaveni)
        self.detektor_objektu = DetektorObjektu()
        self.zona = Zona(x=100, y=100, sirka=300, vyska=200)

        self.slovnik_trid = nacti_coco_tridy("COCO.txt")
        self.sledovana_trida_id = 0

        self.sledovany_objekt_byl_ve_snimku = False
        self.pocet_vyskytu_sledovaneho_objektu = 0

        self.ukladat = False
        self.yolo_jen_pri_pohybu = True

        self.posledni_rozmer = None

        self.label_kamera = QLabel()
        self.label_maska = QLabel()
        self.label_kamera.setAlignment(Qt.AlignCenter)
        self.label_maska.setAlignment(Qt.AlignCenter)

        self.stav_sledovano = QLabel()
        self.stav_pohyb = QLabel()
        self.stav_zona = QLabel()
        self.stav_objekt = QLabel()
        self.stav_pocet = QLabel()
        self.stav_vyskyt = QLabel()
        self.stav_ukladani = QLabel()

        font = QFont("Segoe UI", 12)
        self.stav_sledovano.setFont(font)
        self.stav_pohyb.setFont(font)
        self.stav_zona.setFont(font)
        self.stav_objekt.setFont(font)
        self.stav_pocet.setFont(font)
        self.stav_vyskyt.setFont(font)
        self.stav_ukladani.setFont(font)

        self.check_ukladat = QCheckBox("Ukládat při pohybu")
        self.check_ukladat.stateChanged.connect(self.prepni_ukladani)

        self.tlacitko_reset = QPushButton("Reset pozadí")
        self.tlacitko_reset.clicked.connect(self.reset_pozadi)

        self.tl_vyber_objekt = QPushButton("Vybrat objekt")
        self.tl_vyber_objekt.clicked.connect(self.vyber_objekt)

        self.tl_zona_up = QPushButton("↑")
        self.tl_zona_down = QPushButton("↓")
        self.tl_zona_left = QPushButton("←")
        self.tl_zona_right = QPushButton("→")
        self.tl_plus = QPushButton("+")
        self.tl_minus = QPushButton("-")



        self.tl_zona_up.clicked.connect(self.posun_nahoru)
        self.tl_zona_down.clicked.connect(self.posun_dolu)
        self.tl_zona_left.clicked.connect(self.posun_vlevo)
        self.tl_zona_right.clicked.connect(self.posun_vpravo)
        self.tl_plus.clicked.connect(self.zvetsi_zonu)
        self.tl_minus.clicked.connect(self.zmensi_zonu)


        box_stav = QGroupBox("Stav")
        layout_stav = QVBoxLayout()
        layout_stav.addWidget(self.stav_sledovano)
        layout_stav.addWidget(self.stav_pohyb)
        layout_stav.addWidget(self.stav_zona)
        layout_stav.addWidget(self.stav_objekt)
        layout_stav.addWidget(self.stav_pocet)
        layout_stav.addWidget(self.stav_vyskyt)
        layout_stav.addWidget(self.stav_ukladani)
        box_stav.setLayout(layout_stav)

        box_ovladani = QGroupBox("Ovládání")
        grid = QGridLayout()

        grid.addWidget(self.tl_vyber_objekt, 0, 0, 1, 4)
        grid.addWidget(self.check_ukladat, 1, 0, 1, 4)
        grid.addWidget(self.tlacitko_reset, 2, 0, 1, 4)

        grid.addWidget(self.tl_zona_up, 3, 1)
        grid.addWidget(self.tl_zona_left, 4, 0)
        grid.addWidget(self.tl_zona_down, 4, 1)
        grid.addWidget(self.tl_zona_right, 4, 2)

        grid.addWidget(self.tl_plus, 5, 0, 1, 2)
        grid.addWidget(self.tl_minus, 5, 2, 1, 2)

        box_ovladani.setLayout(grid)

        layout_pravy = QVBoxLayout()
        layout_pravy.addWidget(box_stav)
        layout_pravy.addWidget(box_ovladani)
        layout_pravy.addStretch(1)

        layout_videa = QVBoxLayout()
        layout_videa.addWidget(QLabel("Kamera"))
        layout_videa.addWidget(self.label_kamera, 1)
        layout_videa.addWidget(QLabel("Maska pohybu"))
        layout_videa.addWidget(self.label_maska, 1)

        hlavni_layout = QHBoxLayout()
        hlavni_layout.addLayout(layout_videa, 3)
        hlavni_layout.addLayout(layout_pravy, 1)
        self.setLayout(hlavni_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.aktualizuj)
        self.timer.start(30)

        self.obnov_stav(False, False, False, 0)

    def vyber_objekt(self):
        moznosti = []
        for tid in sorted(self.slovnik_trid):
            text = str(tid) + " - " + self.slovnik_trid[tid]
            moznosti.append(text)

        vybrano, ok = QInputDialog.getItem(
            self,
            "Vyber objekt",
            "Zvol tridu:",
            moznosti,
            0,
            False
        )

        if ok:
            casti = vybrano.split("-", 1)
            tid_text = casti[0].strip()
            try:
                tid = int(tid_text)
            except ValueError:
                return

            self.sledovana_trida_id = tid
            self.sledovany_objekt_byl_ve_snimku = False

    def prepni_ukladani(self):
        self.ukladat = self.check_ukladat.isChecked()

    def reset_pozadi(self):
        self.detektor_pohybu.resetuj_pozadi()

    def posun_zony(self, dx, dy):
        if self.posledni_rozmer is None:
            return
        w, h = self.posledni_rozmer
        self.zona.posun(dx, dy, w, h)
    def posun_nahoru(self):
        self.posun_zony(0, -10)

    def posun_dolu(self):
        self.posun_zony(0, 10)

    def posun_vlevo(self):
        self.posun_zony(-10, 0)

    def posun_vpravo(self):
        self.posun_zony(10, 0)

    def zvetsi_zonu(self):
        self.zmena_velikosti(20)

    def zmensi_zonu(self):
        self.zmena_velikosti(-20)

     

    def zmena_velikosti(self, ds):
        if self.posledni_rozmer is None:
            return

        w, h = self.posledni_rozmer
        self.zona.zmen_velikost(ds, w, h)

    def obnov_stav(self, pohyb, pohyb_v_zone, je_objekt, pocet_na_snimku):
        nazev = self.slovnik_trid.get(self.sledovana_trida_id, str(self.sledovana_trida_id))

        self.stav_sledovano.setText("Sledováno: " + nazev)

        if pohyb:
            self.stav_pohyb.setText("Pohyb: ANO")
        else:
            self.stav_pohyb.setText("Pohyb: NE")

        if pohyb_v_zone:
            self.stav_zona.setText("Pohyb v zóně: ANO")
            self.stav_zona.setStyleSheet("color: green;")
        else:
            self.stav_zona.setText("Pohyb v zóně: NE")
            self.stav_zona.setStyleSheet("color: red;")

        if je_objekt:
            self.stav_objekt.setText("Objekt: ANO")
        else:
            self.stav_objekt.setText("Objekt: NE")

        self.stav_pocet.setText("Počet objektů na snímku: " + str(pocet_na_snimku))
        self.stav_vyskyt.setText("Počet výskytů: " + str(self.pocet_vyskytu_sledovaneho_objektu))

        if self.ukladat:
            self.stav_ukladani.setText("Ukládání: ZAP")
        else:
            self.stav_ukladani.setText("Ukládání: VYP")

    def vypocitej_stred(self, x, y, sirka, vyska):
        stred_x = x + int(sirka / 2)
        stred_y = y + int(vyska / 2)
        return stred_x, stred_y

    def aktualizuj(self):
        snimek = self.kamera.nacti_snimek()
        if snimek is None:
            return

        sirka = snimek.shape[1]
        vyska = snimek.shape[0]
        self.posledni_rozmer = (sirka, vyska)

        maska, obdelniky, pohyb = self.detektor_pohybu.detekuj(snimek)

        pohyb_v_zone = False
        for obdelnik in obdelniky:
            x = obdelnik[0]
            y = obdelnik[1]
            s = obdelnik[2]
            v = obdelnik[3]

            cv2.rectangle(snimek, (x, y), (x + s, y + v), (0, 0, 255), 1)

            stred_x, stred_y = self.vypocitej_stred(x, y, s, v)
            if self.zona.bod_je_v_zone(stred_x, stred_y):
                pohyb_v_zone = True

        spustit_yolo = True
        if self.yolo_jen_pri_pohybu:
            if not pohyb:
                spustit_yolo = False

        if spustit_yolo:
            je_sledovany_objekt, pocet_sledovanych = self.detektor_objektu.analyzuj(snimek, self.sledovana_trida_id)
        else:
            je_sledovany_objekt = False
            pocet_sledovanych = 0

        if je_sledovany_objekt:
            if not self.sledovany_objekt_byl_ve_snimku:
                self.pocet_vyskytu_sledovaneho_objektu += 1
            self.sledovany_objekt_byl_ve_snimku = True
        else:
            self.sledovany_objekt_byl_ve_snimku = False

        self.zona.vykresli(snimek, pohyb_v_zone)

        if pohyb and self.ukladat:
            self.detektor_pohybu.uloz_snimek(snimek.copy(), obdelniky)

        self.obnov_stav(pohyb, pohyb_v_zone, je_sledovany_objekt, pocet_sledovanych)

        pixmap_kamera = cv_obraz_do_pixmap(snimek)
        pixmap_kamera = pixmap_kamera.scaled(self.label_kamera.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label_kamera.setPixmap(pixmap_kamera)

        pixmap_maska = cv_seda_do_pixmap(maska)
        pixmap_maska = pixmap_maska.scaled(self.label_maska.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label_maska.setPixmap(pixmap_maska)

    def closeEvent(self, event):
        self.timer.stop()
        self.kamera.zavri()
        event.accept()


app = QApplication(sys.argv)
okno = Aplikace()
okno.show()
sys.exit(app.exec())
