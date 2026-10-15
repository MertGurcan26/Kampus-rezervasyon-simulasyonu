import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from models import Kullanici, Kaynak, BakimPenceresi, Rezervasyon, Rol, KaynakTuru, BeklemeKaydi
from pricing import UcretHesaplayici
from rules import KuralMotoru

class SimulasyonMotoru:
    def __init__(self):
        self.sistem_saati: datetime = datetime.now()
        self.kullanicilar: Dict[str, Kullanici] = {}
        self.kaynaklar: Dict[str, Kaynak] = {}
        self.roller: Dict[str, Rol] = {}
        self.kaynak_turleri: Dict[str, KaynakTuru] = {}
        self.bakim_pencereleri: List[BakimPenceresi] = []
        self.rezervasyonlar: List[Rezervasyon] = []
        self.bekleme_listesi: List[BeklemeKaydi] = []
        self.rez_sayac = 1
        self.bekleme_sayac = 1

    def baslangic_yukle(self, dosya_yolu: str):
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            veri = json.load(f)
            
        self.sistem_saati = datetime.fromisoformat(veri['saat'])
        
        for k, v in veri['roller'].items():
            self.roller[k] = Rol(k, v['azami_sure_dk'], v['ileri_gun'], v['haftalik_kota'])
            
        for k, v in veri['kaynak_turleri'].items():
            ucret_degeri = v.get('saatlik_ucret', v.get('temel_ucret', 0))
            self.kaynak_turleri[k] = KaynakTuru(k, ucret_degeri, v['hazirlik_dk'], v['enerji_yogun'], v.get('sertifika'))
            
        for k_data in veri['kullanicilar']:
            rol_kota = self.roller[k_data['rol']].haftalik_kota
            bakiye = k_data.get('bakiye', rol_kota)
            kul_nesnesi = Kullanici(
                k_data['id'], k_data['ad'], k_data['rol'], bakiye, k_data.get('sertifikalar', [])
            )
            kul_nesnesi.guvenilirlik = k_data.get('guvenilirlik', 100)
            self.kullanicilar[k_data['id']] = kul_nesnesi
            
        for k_data in veri['kaynaklar']:
            self.kaynaklar[k_data['id']] = Kaynak(k_data['id'], k_data['ad'], k_data['tur'], k_data['izinli_roller'])
            
        for b in veri.get('bakim_pencereleri', []):
            self.bakim_pencereleri.append(BakimPenceresi(b['kaynak'], datetime.fromisoformat(b['baslangic']), datetime.fromisoformat(b['bitis'])))

    def komut_isle(self, komut_dict: dict) -> dict:
        islem_turu = komut_dict.get('komut')
        
        if islem_turu == "rezervasyon": return self._rezervasyon_yap(komut_dict)
        elif islem_turu == "saat": return self._saat_ilerlet(komut_dict)
        elif islem_turu == "kullanici_ekle": return self._kullanici_ekle(komut_dict)
        elif islem_turu == "kaynak_ekle": return self._kaynak_ekle(komut_dict)
        elif islem_turu == "iptal": return self._iptal_et(komut_dict)
        elif islem_turu == "giris": return self._giris_yap(komut_dict)
        elif islem_turu == "cikis": return self._cikis_yap(komut_dict)
        else: return {"komut": islem_turu, "durum": "HATA", "kod": "BILINMEYEN_KOMUT"}

    def _rezervasyon_yap(self, komut: dict) -> dict:
        kullanici = self.kullanicilar.get(komut['kullanici'])
        kaynak = self.kaynaklar.get(komut['kaynak'])
        
        if not kullanici or not kaynak:
            return {"komut": "rezervasyon", "durum": "RED", "kod": "GECERSIZ_VERI"}

        baslangic = datetime.fromisoformat(komut['baslangic'])
        bitis = datetime.fromisoformat(komut['bitis'])
        
        kaynak_turu = self.kaynak_turleri[kaynak.tur]
        rol = self.roller[kullanici.rol]
        
        ucret = UcretHesaplayici.ucret_hesapla(kaynak_turu, baslangic, bitis)
        
        onay, sebep = KuralMotoru.rezervasyon_dogrula(
            kullanici, kaynak, kaynak_turu, rol, baslangic, bitis,
            self.rezervasyonlar, self.bakim_pencereleri, self.sistem_saati, ucret
        )
        
        if onay:
            rez_id = f"r{self.rez_sayac}"
            self.rez_sayac += 1
            yeni_rez = Rezervasyon(rez_id, kullanici.id, kaynak.id, baslangic, bitis, ucret, "ONAYLI")
            self.rezervasyonlar.append(yeni_rez)
            kullanici.bakiye -= ucret
            return {"komut": "rezervasyon", "durum": "TAMAM", "rezervasyon_id": rez_id, "ucret": ucret, "bakiye": kullanici.bakiye}
        
        if sebep in ["CAKISMA", "HAZIRLIK_IHLALI"]:
            for b in self.bekleme_listesi:
                if b.kullanici_id == kullanici.id and b.kaynak_id == kaynak.id:
                    if baslangic < b.bitis and bitis > b.baslangic:
                        return {"komut": "rezervasyon", "durum": "RED", "kod": "ZATEN_BEKLEMEDE"}

            bekleme_id = f"b{self.bekleme_sayac}"
            self.bekleme_sayac += 1
            self.bekleme_listesi.append(BeklemeKaydi(bekleme_id, kullanici.id, kaynak.id, baslangic, bitis, self.sistem_saati))
            return {
                "komut": "bekleme",
                "durum": "TAMAM",
                "bekleme_id": bekleme_id,
                "kullanici": kullanici.id,
                "kaynak": kaynak.id,
                "sira": len(self.bekleme_listesi)
            }

        return {"komut": "rezervasyon", "durum": "RED", "kod": sebep}

    def _kuyruktan_ata(self, kaynak_id: str) -> Optional[dict]:
        for b in list(self.bekleme_listesi):
            if b.kaynak_id == kaynak_id:
                kaynak = self.kaynaklar.get(b.kaynak_id)
                kul = self.kullanicilar.get(b.kullanici_id)
                
                if not kul or not kaynak:
                    continue
                    
                kt = self.kaynak_turleri[kaynak.tur]
                rol = self.roller[kul.rol]
                ucret = UcretHesaplayici.ucret_hesapla(kt, b.baslangic, b.bitis)
                
                onay, _ = KuralMotoru.rezervasyon_dogrula(
                    kul, kaynak, kt, rol, b.baslangic, b.bitis,
                    self.rezervasyonlar, self.bakim_pencereleri, self.sistem_saati, ucret
                )
                if onay:
                    yeni_rez_id = f"r{self.rez_sayac}"
                    self.rez_sayac += 1
                    kul.bakiye -= ucret
                    self.rezervasyonlar.append(Rezervasyon(yeni_rez_id, b.kullanici_id, b.kaynak_id, b.baslangic, b.bitis, ucret, "ONAYLI"))
                    self.bekleme_listesi.remove(b)
                    return {
                        "bekleme_id": b.id,
                        "yeni_rez_id": yeni_rez_id,
                        "kullanici_id": kul.id,
                        "kullanici_ad": kul.ad
                    }
        return None

    def _iptal_et(self, komut: dict) -> dict:
        rez_id = komut.get('rezervasyon')
        hedef = next((r for r in self.rezervasyonlar if r.id == rez_id), None)
        
        if not hedef or hedef.durum in ["IPTAL", "TAMAMLANDI", "GELMEDI"]:
            return {"komut": "iptal", "durum": "RED", "kod": "GECERSIZ_REZERVASYON"}
            
        hedef.durum = "IPTAL"
        kullanici = self.kullanicilar.get(hedef.kullanici_id)
        if kullanici:
            kullanici.bakiye += hedef.ucret 
            
        atanan_kuyruk = self._kuyruktan_ata(hedef.kaynak_id)
        return {"komut": "iptal", "durum": "TAMAM", "iade": hedef.ucret, "atanan_kuyruk": atanan_kuyruk}

    def _giris_yap(self, komut: dict) -> dict:
        rez_id = komut.get('rezervasyon')
        hedef = next((r for r in self.rezervasyonlar if r.id == rez_id), None)
        if not hedef:
            return {"komut": "giris", "durum": "RED", "kod": "KAYIT_BULUNAMADI"}
        if hedef.durum != "ONAYLI":
            return {"komut": "giris", "durum": "RED", "kod": f"DURUM_UYGUN_DEGIL ({hedef.durum})"}
        if self.sistem_saati < hedef.baslangic:
            return {"komut": "giris", "durum": "RED", "kod": "REZERVASYON_SAATI_GELMEDI"}
            
        hedef.durum = "KULLANIMDA"
        return {"komut": "giris", "durum": "TAMAM"}

    def _cikis_yap(self, komut: dict) -> dict:
        rez_id = komut.get('rezervasyon')
        hedef = next((r for r in self.rezervasyonlar if r.id == rez_id), None)
        if not hedef or hedef.durum != "KULLANIMDA":
            return {"komut": "cikis", "durum": "RED", "kod": "CIHAZ_KULLANIMDA_DEGIL"}
            
        if self.sistem_saati < hedef.bitis and self.sistem_saati > hedef.baslangic:
            hedef.bitis = self.sistem_saati
        hedef.durum = "TAMAMLANDI"
        return {"komut": "cikis", "durum": "TAMAM"}

    def _saat_ilerlet(self, komut: dict) -> dict:
        yeni_saat = datetime.fromisoformat(komut['zaman'])
        self.sistem_saati = yeni_saat
        olaylar = []
        
        for r in list(self.rezervasyonlar):
            if r.durum == "ONAYLI" and yeni_saat >= r.baslangic + timedelta(minutes=15):
                r.durum = "GELMEDI"
                kul = self.kullanicilar.get(r.kullanici_id)
                yeni_puan = 100
                if kul:
                    mevcut_puan = getattr(kul, "guvenilirlik", 100)
                    yeni_puan = max(0, mevcut_puan - 15)
                    setattr(kul, "guvenilirlik", yeni_puan)
                
                olaylar.append(
                    f"⚠️ GELMEDİ (NO-SHOW): '{r.id}' ({r.kullanici_id}) 15 dk içinde teslim alınmadı! "
                    f"Rezervasyon iptal edildi ve Güvenilirlik Puanı 15 puan düşürüldü (Yeni Puan: {yeni_puan})"
                )
                
                atanan = self._kuyruktan_ata(r.kaynak_id)
                if atanan:
                    olaylar.append(
                        f"🔄 OTOMATİK ATAMA: Sırada bekleyen '{atanan['kullanici_id']}' ({atanan['kullanici_ad']}), "
                        f"boşalan cihaza '{atanan['yeni_rez_id']}' rezervasyon numarasıyla yerleştirildi!"
                    )
            elif r.durum == "KULLANIMDA" and yeni_saat >= r.bitis:
                r.durum = "TAMAMLANDI"
                olaylar.append(f"🏁 {r.id} süresi doldu ve TAMAMLANDI.")
                
        return {"komut": "saat", "durum": "TAMAM", "olaylar": olaylar}

    def _kullanici_ekle(self, komut: dict) -> dict:
        yeni_kul = Kullanici(komut['id'], komut['ad'], komut['rol'], komut['bakiye'], komut.get('sertifikalar', []))
        yeni_kul.guvenilirlik = 100
        self.kullanicilar[komut['id']] = yeni_kul
        return {"komut": "kullanici_ekle", "durum": "TAMAM"}

    def _kaynak_ekle(self, komut: dict) -> dict:
        self.kaynaklar[komut['id']] = Kaynak(komut['id'], komut['ad'], komut['tur'], komut['izinli_roller'])
        return {"komut": "kaynak_ekle", "durum": "TAMAM"}