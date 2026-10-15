from datetime import datetime, timedelta
from typing import List, Tuple
from models import Kullanici, Kaynak, KaynakTuru, Rol, BakimPenceresi, Rezervasyon

class KuralMotoru:
    """Tüm rezervasyon kısıtlarının (K1-K13) denetlendiği kural motoru."""
    
    @staticmethod
    def rezervasyon_dogrula(
        kullanici: Kullanici,
        kaynak: Kaynak,
        kaynak_turu: KaynakTuru,
        rol: Rol,
        baslangic: datetime,
        bitis: datetime,
        mevcut_rezervasyonlar: List[Rezervasyon],
        bakimlar: List[BakimPenceresi],
        sistem_saati: datetime,
        gereken_ucret: float
    ) -> Tuple[bool, str]:
        
        # K11: Güvenilirlik Puanı Denetimi (getattr ile güvenli okuma - Kırmızı çizgiyi önler)
        guvenilirlik_puani = getattr(kullanici, "guvenilirlik", 100)
        if guvenilirlik_puani < 70:
            return False, f"GUVENILIRLIK_YETERSIZ (Puan: {guvenilirlik_puani})"

        # K1: Zaman adımı 15 dakikanın katı olmalı
        if baslangic.minute % 15 != 0 or bitis.minute % 15 != 0:
            return False, "ZAMAN_ADIMI_HATASI"
            
        if baslangic >= bitis or baslangic < sistem_saati:
            return False, "GECERSIZ_ZAMAN"

        # K2: Rol ve Sertifika Denetimi
        if kullanici.rol not in kaynak.izinli_roller:
            return False, "ROL_IZNI_YOK"

        if kaynak_turu.sertifika and kaynak_turu.sertifika not in kullanici.sertifikalar:
            return False, "SERTIFIKA_YOK"

        # K3: İleri Tarih Sınırı (Gün farkı)
        gun_farki = (baslangic - sistem_saati).days
        if gun_farki > rol.ileri_gun:
            return False, "ILERI_TARIH_SINIRI"

        # K6: Azami Kullanım Süresi
        talep_suresi_dk = (bitis - baslangic).total_seconds() / 60
        if talep_suresi_dk > rol.azami_sure_dk:
            return False, "AZAMI_SURE_ASIMI"

        # Bakiye Yeterliliği
        if kullanici.bakiye < gereken_ucret:
            return False, "BAKIYE_YETERSIZ"

        # Çakışma, Soğuma ve Ardışık Kullanım Denetimi
        for r in mevcut_rezervasyonlar:
            if r.durum in ["ONAYLI", "KULLANIMDA"]:
                # Kullanıcının kendi rezervasyonuyla çakışması
                if r.kullanici_id == kullanici.id:
                    if baslangic < r.bitis and bitis > r.baslangic:
                        return False, "KENDI_CAKISMASI"

                if r.kaynak_id == kaynak.id:
                    if baslangic < r.bitis and bitis > r.baslangic:
                        return False, "CAKISMA"
                    
                    hazirlik_farki = timedelta(minutes=kaynak_turu.hazirlik_dk)
                    if r.baslangic <= bitis < r.baslangic + hazirlik_farki:
                        return False, "HAZIRLIK_IHLALI"
                    if r.bitis <= baslangic < r.bitis + hazirlik_farki:
                        return False, "HAZIRLIK_IHLALI"

                if r.kullanici_id == kullanici.id and r.kaynak_id == kaynak.id:
                    if r.bitis <= baslangic < r.bitis + timedelta(minutes=60):
                        return False, "ARDISIK_KULLANIM"

        # Bakım Penceresi Çakışması
        for bakim in bakimlar:
            if bakim.kaynak_id == kaynak.id:
                if baslangic < bakim.bitis and bitis > bakim.baslangic:
                    return False, "BAKIM_CAKISMASI"

        return True, "TAMAM"