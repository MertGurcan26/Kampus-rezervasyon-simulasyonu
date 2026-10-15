import sys
import json
from engine import SimulasyonMotoru

def main():
    # Varsayılan dosya isimleri (Komut satırından argüman verilmezse bunları kullanır)
    baslangic_dosyasi = sys.argv[1] if len(sys.argv) > 1 else "baslangic.json"
    komutlar_dosyasi = sys.argv[2] if len(sys.argv) > 2 else "komutlar.jsonl"
    sonuclar_dosyasi = sys.argv[3] if len(sys.argv) > 3 else "sonuclar.jsonl"

    motor = SimulasyonMotoru()
    
    try:
        motor.baslangic_yukle(baslangic_dosyasi)
    except FileNotFoundError:
        print(json.dumps({"hata": f"{baslangic_dosyasi} dosyasi bulunamadi!"}, ensure_ascii=False))
        return

    # Komutları satır satır oku, işle ve hem ekrana hem sonuclar.jsonl dosyasına yaz
    try:
        with open(komutlar_dosyasi, 'r', encoding='utf-8') as f_girdi, \
             open(sonuclar_dosyasi, 'w', encoding='utf-8') as f_cikti:
            
            for satir in f_girdi:
                satir = satir.strip()
                if not satir:
                    continue
                
                komut_dict = json.loads(satir)
                sonuc = motor.komut_isle(komut_dict)
                
                json_satiri = json.dumps(sonuc, ensure_ascii=False)
                print(json_satiri)                # 1. Ekrana (Terminale) bas
                f_cikti.write(json_satiri + "\n") # 2. sonuclar.jsonl dosyasına kaydet
                
    except FileNotFoundError:
        print(json.dumps({"hata": f"{komutlar_dosyasi} dosyasi bulunamadi!"}, ensure_ascii=False))

if __name__ == "__main__":
    main()