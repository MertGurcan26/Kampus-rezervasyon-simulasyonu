import os
from engine import SimulasyonMotoru
from gui import AnaPencere

def main():
    print("Kampüs Kaynak Rezervasyon Sistemi Başlatılıyor...")
    
    # Motoru ayağa kaldır
    motor = SimulasyonMotoru()
    
    # Başlangıç verilerini yükle (JSON dosyası projenin ana dizininde olmalı)
    baslangic_dosyasi = "baslangic.json"
    
    if os.path.exists(baslangic_dosyasi):
        motor.baslangic_yukle(baslangic_dosyasi)
        print("Başlangıç verileri başarıyla yüklendi!")
    else:
        print(f"UYARI: {baslangic_dosyasi} bulunamadı! Arayüz boş verilerle açılacak.")

    # Modern Arayüzü Başlat
    app = AnaPencere(motor)
    app.mainloop()

if __name__ == "__main__":
    main()