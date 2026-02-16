import cv2


class Kamera:
    def __init__(self, cislo_kamery=0, sirka=640, vyska=400):
        self.cislo_kamery = int(cislo_kamery)
        self.sirka = int(sirka)
        self.vyska = int(vyska)

        self.zarizeni = cv2.VideoCapture(self.cislo_kamery)
        if self.zarizeni.isOpened():
            self.zarizeni.set(cv2.CAP_PROP_FRAME_WIDTH, self.sirka)
            self.zarizeni.set(cv2.CAP_PROP_FRAME_HEIGHT, self.vyska)

    def nacti_snimek(self):
        if self.zarizeni is None:
            return None

        if not self.zarizeni.isOpened():
            return None

        ok, frame = self.zarizeni.read()
        if not ok:
            return None

        return frame

    def zavri(self):
        if self.zarizeni is None:
            return

        if self.zarizeni.isOpened():
            self.zarizeni.release()
