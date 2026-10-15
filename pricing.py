from datetime import datetime, timedelta
from models import KaynakTuru

class UcretHesaplayici:
    """Kaynak kiralama ücretlerini hesaplayan servis sınıfı."""
    
    @staticmethod
    def ucret_hesapla(kaynak_turu: KaynakTuru, baslangic: datetime, bitis: datetime) -> float:
        toplam_ucret = 0.0
        suanki_zaman = baslangic
        
        dilim_ucreti = kaynak_turu.saatlik_ucret / 4.0
        
        while suanki_zaman < bitis:
            carpan = 1.0
            
            if kaynak_turu.enerji_yogun:
                if 10 <= suanki_zaman.hour < 16:
                    carpan = 1.5
                    
            toplam_ucret += dilim_ucreti * carpan
            suanki_zaman += timedelta(minutes=15)
            
        return toplam_ucret