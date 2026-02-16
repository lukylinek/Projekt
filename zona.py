import cv2


class Zona:
    def __init__(self, x, y, sirka, vyska):
        self.x = int(x)
        self.y = int(y)
        self.sirka = int(sirka)
        self.vyska = int(vyska)

    def bod_je_v_zone(self, bx, by):
        bx = int(bx)
        by = int(by)

        leva = self.x
        prava = self.x + self.sirka
        horni = self.y
        dolni = self.y + self.vyska

        if bx < leva:
            return False
        if bx > prava:
            return False
        if by < horni:
            return False
        if by > dolni:
            return False
        return True

    def posun(self, dx, dy, max_sirka, max_vyska):
        nove_x = self.x + int(dx)
        nove_y = self.y + int(dy)

        if nove_x < 0:
            nove_x = 0
        if nove_y < 0:
            nove_y = 0

        if nove_x + self.sirka > int(max_sirka):
            nove_x = int(max_sirka) - self.sirka
        if nove_y + self.vyska > int(max_vyska):
            nove_y = int(max_vyska) - self.vyska

        if nove_x < 0:
            nove_x = 0
        if nove_y < 0:
            nove_y = 0

        self.x = nove_x
        self.y = nove_y

    def zmen_velikost(self, ds, max_sirka, max_vyska):
        nova_sirka = self.sirka + int(ds)
        nova_vyska = self.vyska + int(ds)

        minimalni = 40
        if nova_sirka < minimalni:
            nova_sirka = minimalni
        if nova_vyska < minimalni:
            nova_vyska = minimalni

        if self.x + nova_sirka > int(max_sirka):
            nova_sirka = int(max_sirka) - self.x
        if self.y + nova_vyska > int(max_vyska):
            nova_vyska = int(max_vyska) - self.y

        if nova_sirka < minimalni:
            nova_sirka = minimalni
        if nova_vyska < minimalni:
            nova_vyska = minimalni

        self.sirka = int(nova_sirka)
        self.vyska = int(nova_vyska)

    def vykresli(self, obraz, aktivni=False):
        if aktivni:
            barva = (0, 255, 0)
        else:
            barva = (255, 0, 0)

        cv2.rectangle(
            obraz,
            (self.x, self.y),
            (self.x + self.sirka, self.y + self.vyska),
            barva,
            2
        )

        cv2.putText(
            obraz,
            "ZONA",
            (self.x + 5, self.y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            barva,
            2
        )
