from ultralytics import YOLO


class DetektorObjektu:
    def __init__(self, cesta_k_modelu: str = "yolov8n.pt", minimalni_jistota: float = 0.50):
        self.minimalni_jistota = float(minimalni_jistota)
        self.model = YOLO(cesta_k_modelu)

    def analyzuj(self, snimek, sledovana_trida_id: int):
        vysledky = self.model(snimek, verbose=False)

        je_na_snimku = False
        pocet = 0

        if not vysledky:
            return False, 0

        vysledek = vysledky[0]
        boxy = getattr(vysledek, "boxes", None)
        if boxy is None:
            return False, 0

        tridy = boxy.cls
        jistoty = boxy.conf

        if tridy is None or jistoty is None:
            return False, 0

        for i in range(len(tridy)):
            trida = int(tridy[i])
            jistota = float(jistoty[i])

            if trida != int(sledovana_trida_id):
                continue

            if jistota < self.minimalni_jistota:
                continue

            pocet += 1
            je_na_snimku = True

        return je_na_snimku, pocet
