import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

class AnaPencere(ctk.CTk):
    def __init__(self, motor):
        super().__init__()
        self.motor = motor
        self.secili_rez_id = "r1"
        
        self.tooltip_win = None
        self.surukleme_aktif = False
        self.surukleme_kaynak: str = ""
        self.surukleme_y_offset = 0
        self.surukleme_bas_x = 0
        self.surukleme_bas_dk = 0
        self.surukleme_bit_dk = 0
        self.satir_koordinatlari = {}

        self.title("Kampüs Kaynak Rezervasyon Sistemi ")
        self.geometry("1420x860")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.arayuz_olustur()
        self.ekrani_guncelle()

    def arayuz_olustur(self):
        # --- ÜST PANEL ---
        self.ust_panel = ctk.CTkFrame(self, height=70, corner_radius=0, fg_color="#1a1a1a")
        self.ust_panel.grid(row=0, column=0, columnspan=2, sticky="new")
        
        self.lbl_saat = ctk.CTkLabel(self.ust_panel, text="Sistem Saati: -", font=("Segoe UI", 22, "bold"), text_color="#00FFCC")
        self.lbl_saat.pack(side="left", padx=30, pady=15)
        
        self.btn_1saat = ctk.CTkButton(self.ust_panel, text="⏩ +1 Saat İleri", command=lambda: self.saat_ilerlet(60), 
                                       font=("Segoe UI", 15, "bold"), fg_color="#6610f2", hover_color="#520dc2", width=140, height=40)
        self.btn_1saat.pack(side="right", padx=(10, 30), pady=15)
        
        self.btn_15dk = ctk.CTkButton(self.ust_panel, text="⏱️ +15 Dk İleri", command=lambda: self.saat_ilerlet(15), 
                                      font=("Segoe UI", 15, "bold"), fg_color="#007bff", hover_color="#0056b3", width=140, height=40)
        self.btn_15dk.pack(side="right", padx=10, pady=15)

        # --- SOL PANEL ---
        self.sol_panel = ctk.CTkFrame(self, width=330, corner_radius=0, fg_color="#212529")
        self.sol_panel.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # 1. KULLANICI EKLEME ALANI
        ctk.CTkLabel(self.sol_panel, text="1. Yeni Kullanıcı Ekle", font=("Segoe UI", 16, "bold"), text_color="#f1c40f").pack(pady=(8, 2))
        
        ctk.CTkLabel(self.sol_panel, text="Kullanıcı ID (Örn: u5):", anchor="w", font=("Segoe UI", 12)).pack(fill="x", padx=15)
        self.yeni_kul_id = ctk.StringVar(value="")
        ctk.CTkEntry(self.sol_panel, textvariable=self.yeni_kul_id, height=26).pack(fill="x", padx=15, pady=(0, 4))
        
        ctk.CTkLabel(self.sol_panel, text="Adınız ve Soyadınız:", anchor="w", font=("Segoe UI", 12)).pack(fill="x", padx=15)
        self.yeni_kul_ad = ctk.StringVar(value="")
        ctk.CTkEntry(self.sol_panel, textvariable=self.yeni_kul_ad, height=26).pack(fill="x", padx=15, pady=(0, 4))
        
        ctk.CTkLabel(self.sol_panel, text="Rolünüz (Meslek):", anchor="w", font=("Segoe UI", 12)).pack(fill="x", padx=15)
        self.yeni_kul_rol = ctk.StringVar(value="OGRENCI")
        ctk.CTkOptionMenu(self.sol_panel, variable=self.yeni_kul_rol, values=["OGRENCI", "ARASTIRMACI", "TEKNISYEN"], height=26).pack(fill="x", padx=15, pady=(0, 4))
        
        ctk.CTkLabel(self.sol_panel, text="Gerekli Sertifikalarınız Var mı?:", anchor="w", font=("Segoe UI", 12)).pack(fill="x", padx=15)
        self.yeni_kul_sertifika = ctk.StringVar(value="Hayır")
        ctk.CTkOptionMenu(self.sol_panel, variable=self.yeni_kul_sertifika, values=["Evet", "Hayır"], height=26).pack(fill="x", padx=15, pady=(0, 8))
        
        ctk.CTkButton(self.sol_panel, text="Sisteme Kaydet", command=self.kullanici_ekle_gonder, font=("Segoe UI", 13, "bold"), fg_color="#17a2b8", hover_color="#138496", height=30).pack(fill="x", padx=15, pady=2)
        
        ctk.CTkFrame(self.sol_panel, height=2, fg_color="#444").pack(fill="x", pady=8, padx=10)

        # 2. YENİ REZERVASYON ALANI
        ctk.CTkLabel(self.sol_panel, text="2. Rezervasyon Oluştur", font=("Segoe UI", 16, "bold"), text_color="#00FFCC").pack(pady=(0, 2))
        
        ctk.CTkLabel(self.sol_panel, text="Kullanıcı ID (Örn: u3):", anchor="w", font=("Segoe UI", 12)).pack(fill="x", padx=15)
        self.kullanici_var = ctk.StringVar(value="u3")
        ctk.CTkEntry(self.sol_panel, textvariable=self.kullanici_var, height=26).pack(fill="x", padx=15, pady=(0, 4))
        
        ctk.CTkLabel(self.sol_panel, text="Kaynak Seçin:", anchor="w", font=("Segoe UI", 12)).pack(fill="x", padx=15)
        kaynak_isimleri = list(self.motor.kaynaklar.keys()) if self.motor.kaynaklar else ["YAZ-2"]
        self.kaynak_var = ctk.StringVar(value=kaynak_isimleri[0])
        self.opt_kaynak = ctk.CTkOptionMenu(self.sol_panel, variable=self.kaynak_var, values=kaynak_isimleri, height=26)
        self.opt_kaynak.pack(fill="x", padx=15, pady=(0, 4))
        
        ctk.CTkLabel(self.sol_panel, text="Başlangıç (YYYY-AA-GG SS:DD):", anchor="w", font=("Segoe UI", 12)).pack(fill="x", padx=15)
        self.baslangic_var = ctk.StringVar(value="2027-03-08 10:00")
        ctk.CTkEntry(self.sol_panel, textvariable=self.baslangic_var, height=26).pack(fill="x", padx=15, pady=(0, 4))
        
        ctk.CTkLabel(self.sol_panel, text="Bitiş (YYYY-AA-GG SS:DD):", anchor="w", font=("Segoe UI", 12)).pack(fill="x", padx=15)
        self.bitis_var = ctk.StringVar(value="2027-03-08 12:00")
        ctk.CTkEntry(self.sol_panel, textvariable=self.bitis_var, height=26).pack(fill="x", padx=15, pady=(0, 8))
        
        ctk.CTkButton(self.sol_panel, text="Hemen Rezerve Et", command=self.rezervasyon_gonder, font=("Segoe UI", 13, "bold"), fg_color="#28a745", hover_color="#218838", height=30).pack(fill="x", padx=15, pady=2)

        ctk.CTkFrame(self.sol_panel, height=2, fg_color="#444").pack(fill="x", pady=8, padx=10)

        # 3. İŞLEM YÖNETİMİ
        ctk.CTkLabel(self.sol_panel, text="3. Cihaz Teslim & İptal", font=("Segoe UI", 16, "bold"), text_color="#ff4c4c").pack(pady=(0, 2))
        
        ctk.CTkLabel(self.sol_panel, text="Rezervasyon ID:", anchor="w", font=("Segoe UI", 12)).pack(fill="x", padx=15)
        self.islem_rez_id = ctk.StringVar(value="r1")
        ctk.CTkEntry(self.sol_panel, textvariable=self.islem_rez_id, height=26).pack(fill="x", padx=15, pady=(0, 8))
        
        islem_btn_frame = ctk.CTkFrame(self.sol_panel, fg_color="transparent")
        islem_btn_frame.pack(fill="x", padx=15, pady=2)
        ctk.CTkButton(islem_btn_frame, text="Teslim Al (Giriş)", command=self.giris_gonder, font=("Segoe UI", 12, "bold"), fg_color="#ffc107", hover_color="#e0a800", text_color="black", width=135, height=30).pack(side="left", padx=(0, 4))
        ctk.CTkButton(islem_btn_frame, text="Bitir (Çıkış)", command=self.cikis_gonder, font=("Segoe UI", 12, "bold"), fg_color="#0dcaf0", hover_color="#0bacbe", text_color="black", width=135, height=30).pack(side="right", padx=(4, 0))
        
        ctk.CTkButton(self.sol_panel, text="Rezervasyonu İptal Et", command=self.iptal_gonder, font=("Segoe UI", 12, "bold"), fg_color="#dc3545", hover_color="#c82333", height=30).pack(fill="x", padx=15, pady=(6, 2))

        # --- SAĞ PANEL (GANTT & LOG) ---
        self.sag_panel = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.sag_panel.grid(row=1, column=1, sticky="nsew", padx=20, pady=10)
        
        self.sag_panel.grid_columnconfigure(0, weight=1) 
        self.sag_panel.grid_rowconfigure(0, weight=3)
        self.sag_panel.grid_rowconfigure(1, weight=1)
        
        self.canvas_frame = ctk.CTkFrame(self.sag_panel, fg_color="#212529", corner_radius=10)
        self.canvas_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 15))
        
        ctk.CTkLabel(self.canvas_frame, text="Kaynak Zaman Çizelgesi", font=("Segoe UI", 18, "bold"), text_color="#ffffff").pack(anchor="w", padx=15, pady=10)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="#1a1a1a", highlightthickness=0, cursor="crosshair")
        self.canvas.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.canvas.bind("<ButtonPress-1>", self.canvas_fare_basildi)
        self.canvas.bind("<B1-Motion>", self.canvas_fare_suruklendi)
        self.canvas.bind("<ButtonRelease-1>", self.canvas_fare_birakildi)
        
        self.log_frame = ctk.CTkFrame(self.sag_panel, fg_color="#212529", corner_radius=10)
        self.log_frame.grid(row=1, column=0, sticky="nsew")
        ctk.CTkLabel(self.log_frame, text="Sistem İşlem Logları", font=("Segoe UI", 15, "bold"), text_color="#ffffff").pack(anchor="w", padx=15, pady=(10,0))
        
        self.log_text = tk.Text(self.log_frame, bg="#1a1a1a", fg="#ffffff", font=("Consolas", 13), state="disabled", relief="flat")
        self.log_text.pack(fill="both", expand=True, padx=15, pady=15)
        self.log_text.tag_config("RED", foreground="#ff4c4c")
        self.log_text.tag_config("ONAYLI", foreground="#00FFCC")
        self.log_text.tag_config("SARI", foreground="#f1c40f")

    # =========================================================================
    # ÖZELLİK 1: HOVER TOOLTIP
    # =========================================================================
    def tooltip_goster(self, event, rez):
        self.tooltip_gizle()
        
        kul = self.motor.kullanicilar.get(rez.kullanici_id)
        kaynak = self.motor.kaynaklar.get(rez.kaynak_id)
        kt = self.motor.kaynak_turleri.get(kaynak.tur) if kaynak else None
        
        kul_ad = kul.ad if kul else "Bilinmiyor"
        kul_rol = kul.rol if kul else "-"
        guvenilirlik = getattr(kul, "guvenilirlik", 100) if kul else 100
        hazirlik_dk = kt.hazirlik_dk if kt else 0
        soguma_bitis = (rez.bitis + timedelta(minutes=hazirlik_dk)).strftime('%H:%M')
        
        bilgi_metni = (
            f"📌 Rezervasyon No : {rez.id} ({rez.durum})\n"
            f"👤 Kullanıcı      : {kul_ad} ({rez.kullanici_id})\n"
            f"🎓 Rolü           : {kul_rol}\n"
            f"🕒 Saat Aralığı   : {rez.baslangic.strftime('%H:%M')} - {rez.bitis.strftime('%H:%M')}\n"
            f"💰 Ödenen Ücret   : {rez.ucret} KP\n"
            f"🟪 Soğuma Bitişi  : {soguma_bitis} (+{hazirlik_dk} dk)\n"
            f"🛡️ Güvenilirlik   : {guvenilirlik} / 100 Puan"
        )
        
        self.tooltip_win = tk.Toplevel(self)
        self.tooltip_win.wm_overrideredirect(True)
        self.tooltip_win.wm_geometry(f"+{event.x_root + 16}+{event.y_root + 16}")
        self.tooltip_win.attributes("-topmost", True)
        
        cerceve = tk.Frame(self.tooltip_win, bg="#00FFCC", padx=1, pady=1)
        cerceve.pack()
        
        lbl = tk.Label(
            cerceve, text=bilgi_metni, justify="left", bg="#111418", fg="#ffffff",
            font=("Consolas", 10, "bold"), padx=12, pady=8
        )
        lbl.pack()

    def tooltip_hareket(self, event):
        if self.tooltip_win:
            self.tooltip_win.wm_geometry(f"+{event.x_root + 16}+{event.y_root + 16}")

    def tooltip_gizle(self, event=None):
        if self.tooltip_win:
            self.tooltip_win.destroy()
            self.tooltip_win = None

    # =========================================================================
    # ÖZELLİK 2: SÜRÜKLE-BIRAK (DRAG & DROP)
    # =========================================================================
    def _x_to_dakika(self, x_coord):
        x_sinirli = max(120, min(120 + 14 * 75, x_coord))
        gecen_saat = (x_sinirli - 120) / 75.0
        toplam_dk = int(round((gecen_saat * 60) / 15.0) * 15)
        return max(0, min(14 * 60, toplam_dk))

    def _dakika_to_saat_str(self, toplam_dk):
        saat = 8 + (toplam_dk // 60)
        dk = toplam_dk % 60
        return f"{saat:02d}:{dk:02d}"

    def canvas_fare_basildi(self, event):
        items = self.canvas.find_withtag("current")
        if items:
            tags = self.canvas.gettags(items[0])
            for t in tags:
                if t.startswith("rez_"):
                    return

        secilen_kaynak = ""
        secilen_y_ust = 0
        for k_id, (y_ust, y_alt) in self.satir_koordinatlari.items():
            if y_ust <= event.y <= y_alt:
                secilen_kaynak = k_id
                secilen_y_ust = y_ust
                break

        if not secilen_kaynak or event.x < 115:
            return

        self.tooltip_gizle()
        self.surukleme_aktif = True
        self.surukleme_kaynak = secilen_kaynak
        self.surukleme_y_offset = secilen_y_ust
        self.surukleme_bas_dk = self._x_to_dakika(event.x)
        self.surukleme_bit_dk = min(14 * 60, self.surukleme_bas_dk + 60)
        self._surukleme_kutusunu_ciz()

    def canvas_fare_suruklendi(self, event):
        if not self.surukleme_aktif:
            return
        anlik_dk = self._x_to_dakika(event.x)
        if anlik_dk == self.surukleme_bas_dk:
            anlik_dk = min(14 * 60, self.surukleme_bas_dk + 15)
        self.surukleme_bit_dk = anlik_dk
        self._surukleme_kutusunu_ciz()

    def canvas_fare_birakildi(self, event):
        if not self.surukleme_aktif:
            return
        self.surukleme_aktif = False
        self.canvas.delete("drag_preview")

        bas_dk = min(self.surukleme_bas_dk, self.surukleme_bit_dk)
        bit_dk = max(self.surukleme_bas_dk, self.surukleme_bit_dk)
        if bit_dk - bas_dk < 15:
            bit_dk = min(14 * 60, bas_dk + 15)

        tarih_str = self.motor.sistem_saati.strftime("%Y-%m-%d") if self.motor.sistem_saati else "2027-03-08"
        bas_saat_str = self._dakika_to_saat_str(bas_dk)
        bit_saat_str = self._dakika_to_saat_str(bit_dk)

        if self.surukleme_kaynak:
            self.kaynak_var.set(self.surukleme_kaynak)
        self.baslangic_var.set(f"{tarih_str} {bas_saat_str}")
        self.bitis_var.set(f"{tarih_str} {bit_saat_str}")

        self.log_yaz(
            f"🖱️ TAKVİMDEN SEÇİLDİ: '{self.surukleme_kaynak}' kaynağı için "
            f"{bas_saat_str} - {bit_saat_str} aralığı forma otomatik dolduruldu!",
            "ONAYLI"
        )

    def _surukleme_kutusunu_ciz(self):
        self.canvas.delete("drag_preview")
        bas_dk = min(self.surukleme_bas_dk, self.surukleme_bit_dk)
        bit_dk = max(self.surukleme_bas_dk, self.surukleme_bit_dk)
        if bit_dk - bas_dk < 15:
            bit_dk = min(14 * 60, bas_dk + 15)

        x1 = 120 + (bas_dk / 60.0) * 75
        x2 = 120 + (bit_dk / 60.0) * 75
        y = self.surukleme_y_offset

        self.canvas.create_rectangle(
            x1, y + 6, x2, y + 38,
            fill="#1d4ed8", outline="#00FFCC", width=2, dash=(4, 2),
            stipple="gray50", tags="drag_preview"
        )
        saat_metni = f"{self._dakika_to_saat_str(bas_dk)} - {self._dakika_to_saat_str(bit_dk)}"
        self.canvas.create_text(
            (x1 + x2) / 2, y + 22,
            text=saat_metni, fill="#ffffff", font=("Segoe UI", 9, "bold"),
            tags="drag_preview"
        )

    # =========================================================================
    # STANDART İŞLEM FONKSİYONLARI
    # =========================================================================
    def kutuya_tiklandi(self, rez_id):
        self.secili_rez_id = rez_id
        self.islem_rez_id.set(rez_id)
        self.log_yaz(f"🎯 SEÇİLDİ: Takvim üzerinden '{rez_id}' seçildi.", "SARI")
        self.ekrani_guncelle()

    def kullanici_ekle_gonder(self):
        kul_id = self.yeni_kul_id.get().strip()
        kul_ad = self.yeni_kul_ad.get().strip()
        if not kul_id or not kul_ad:
            self.log_yaz("❌ HATA: Lütfen Kullanıcı ID ve Ad Soyad alanlarını boş bırakmayın!", "RED")
            messagebox.showwarning("Eksik Bilgi", "Lütfen Kullanıcı ID ve Ad Soyad alanlarını doldurun!")
            return
            
        sertifikalar_listesi = ["CIHAZ_EGITIMI", "LAB_GUVENLIK"] if self.yeni_kul_sertifika.get() == "Evet" else []
        komut = {
            "komut": "kullanici_ekle", "id": kul_id, "ad": kul_ad,
            "rol": self.yeni_kul_rol.get(), "bakiye": 500, "sertifikalar": sertifikalar_listesi
        }
        self.motor.komut_isle(komut)
        durum = "Sertifikalı" if self.yeni_kul_sertifika.get() == "Evet" else "Sertifikasız"
        self.log_yaz(f"👤 YENİ KAYIT: {komut['ad']} ({komut['id']}) - {durum} olarak sisteme eklendi!", "ONAYLI")
        self.kullanici_var.set(komut['id']) 

    def iptal_gonder(self):
        hedef_id = self.islem_rez_id.get().strip()
        sonuc = self.motor.komut_isle({"komut": "iptal", "rezervasyon": hedef_id})
        if sonuc["durum"] == "TAMAM":
            mesaj = f"❌ İPTAL EDİLDİ: '{hedef_id}' numaralı rezervasyon silindi. (İade Edilen: {sonuc['iade']} KP)"
            self.log_yaz(mesaj, "RED")
            atanan = sonuc.get("atanan_kuyruk")
            if atanan:
                self.secili_rez_id = atanan["yeni_rez_id"]
                self.islem_rez_id.set(atanan["yeni_rez_id"])
                self.log_yaz(
                    f"🔄 OTOMATİK ATAMA: Sırada bekleyen '{atanan['kullanici_id']}' ({atanan['kullanici_ad']}), "
                    f"boşalan cihaza '{atanan['yeni_rez_id']}' numaralı rezervasyon ile otomatik yerleştirildi!",
                    "ONAYLI"
                )
            self.ekrani_guncelle()
        else:
            self.log_yaz(f"❌ İPTAL BAŞARISIZ: {sonuc.get('kod')}", "RED")

    def giris_gonder(self):
        sonuc = self.motor.komut_isle({"komut": "giris", "rezervasyon": self.islem_rez_id.get().strip()})
        if sonuc["durum"] == "TAMAM":
            self.log_yaz(f"✅ CİHAZ TESLİM ALINDI (CHECK-İN): {self.islem_rez_id.get()} şu an KULLANIMDA!", "SARI")
            self.ekrani_guncelle()
        else:
            self.log_yaz(f"❌ TESLİM ALMA BAŞARISIZ: {sonuc.get('kod')}", "RED")

    def cikis_gonder(self):
        sonuc = self.motor.komut_isle({"komut": "cikis", "rezervasyon": self.islem_rez_id.get().strip()})
        if sonuc["durum"] == "TAMAM":
            self.log_yaz(f"🏁 CİHAZ TESLİM EDİLDİ (CHECK-OUT): {self.islem_rez_id.get()} kullanımı tamamlandı.", "ONAYLI")
            self.ekrani_guncelle()
        else:
            self.log_yaz(f"❌ ÇIKIŞ BAŞARISIZ: {sonuc.get('kod')}", "RED")

    def rezervasyon_gonder(self):
        bas = self.baslangic_var.get().strip().replace(" ", "T")
        bit = self.bitis_var.get().strip().replace(" ", "T")
        kul_id = self.kullanici_var.get().strip()
        kaynak_id = self.kaynak_var.get().strip()
        
        sonuc = self.motor.komut_isle({
            "komut": "rezervasyon",
            "kullanici": kul_id,
            "kaynak": kaynak_id,
            "baslangic": bas,
            "bitis": bit
        })
        
        if sonuc.get('komut') == "bekleme":
            self.log_yaz(
                f"⏳ SIRAYA ALINDI: '{kaynak_id}' bu saatte başka bir kullanıcıda! '{kul_id}' bekleme kuyruğuna eklendi "
                f"(Kuyruktaki Sırası: {sonuc['sira']}. sırada)",
                "SARI"
            )
        elif sonuc.get('durum') == "TAMAM":
            self.secili_rez_id = sonuc['rezervasyon_id']
            self.islem_rez_id.set(sonuc['rezervasyon_id'])
            self.log_yaz(
                f"✅ ONAY: '{sonuc['rezervasyon_id']}' numaralı rezervasyon '{kul_id}' için oluşturuldu. "
                f"(Ücret: {sonuc['ucret']} KP | Kalan Bakiye: {sonuc['bakiye']} KP)",
                "ONAYLI"
            )
        else:
            hata_kodu = sonuc.get('kod')
            # EĞER KİŞİNİN KENDİ REZERVASYONU VARSA POP-UP WARNING EKRANI AÇ!
            if hata_kodu == "KENDI_CAKISMASI":
                self.log_yaz(
                    f"⚠️ UYARI: '{kul_id}' kullanıcısının seçilen saat aralığında zaten aktif bir rezervasyonu mevcut!",
                    "RED"
                )
                messagebox.showwarning(
                    "Mevcut Rezervasyon Uyarısı",
                    f"'{kul_id}' kullanıcısının bu saat aralığında zaten aktif bir rezervasyonu bulunmaktadır!\n\n"
                    f"Aynı saat için kendinizi bekleme sırasına alamazsınız veya ikinci bir kayıt oluşturamazsınız."
                )
            elif hata_kodu == "ZATEN_BEKLEMEDE":
                self.log_yaz(
                    f"⚠️ UYARI: '{kul_id}' kullanıcısı bu kaynak ve saat için zaten bekleme listesinde!",
                    "RED"
                )
                messagebox.showwarning(
                    "Bekleme Listesi Uyarısı",
                    f"'{kul_id}' kullanıcısı bu cihaz ve saat aralığı için zaten bekleme sırasındadır!"
                )
            else:
                self.log_yaz(f"❌ RED: Hata Kodu -> {hata_kodu}", "RED")
            
        self.ekrani_guncelle()

    def saat_ilerlet(self, dakika):
        yeni_saat = self.motor.sistem_saati + timedelta(minutes=dakika)
        sonuc = self.motor.komut_isle({"komut": "saat", "zaman": yeni_saat.isoformat()})
        
        self.log_yaz(f"⏰ SİSTEM SAATİ İLERLETİLDİ: {yeni_saat.strftime('%H:%M')}", "SARI")
            
        for olay in sonuc.get("olaylar", []):
            self.log_yaz(f"   ↳ {olay}", "ONAYLI" if "OTOMATİK ATAMA" in olay else "RED")
        self.ekrani_guncelle()

    def log_yaz(self, mesaj, tag=None):
        self.log_text.config(state="normal")
        if tag: self.log_text.insert("end", mesaj + "\n", tag)
        else: self.log_text.insert("end", mesaj + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def ekrani_guncelle(self):
        self.tooltip_gizle()
        if self.motor.sistem_saati:
            self.lbl_saat.configure(text=f"Sistem Saati: {self.motor.sistem_saati.strftime('%Y-%m-%d %H:%M')}")
        self.canvas.delete("all")
        self.satir_koordinatlari.clear()
        y_offset = 40
        
        for i in range(15): 
            x = 120 + (i * 75)
            self.canvas.create_text(x, 15, text=f"{8+i:02}:00", fill="#b0b0b0", font=("Segoe UI", 10, "bold"))
            self.canvas.create_line(x, 30, x, 1000, fill="#333333", dash=(4, 4))

        for kaynak_id, kaynak in self.motor.kaynaklar.items():
            self.satir_koordinatlari[kaynak_id] = (y_offset, y_offset + 62)
            
            self.canvas.create_text(15, y_offset + 18, text=kaynak_id, fill="#ffffff", anchor="w", font=("Segoe UI", 12, "bold"))
            self.canvas.create_text(15, y_offset + 35, text=kaynak.tur, fill="#888888", anchor="w", font=("Segoe UI", 9))
            self.canvas.create_line(0, y_offset + 62, 2000, y_offset + 62, fill="#333333")
            
            # 1. Bakım Pencereleri (Turuncu)
            for b in self.motor.bakim_pencereleri:
                if b.kaynak_id == kaynak_id:
                    b_bas = b.baslangic.hour + (b.baslangic.minute / 60.0)
                    b_bit = b.bitis.hour + (b.bitis.minute / 60.0)
                    if 8 <= b_bas <= 22:
                        bx1, bx2 = 120 + ((b_bas - 8) * 75), 120 + ((b_bit - 8) * 75)
                        self.canvas.create_rectangle(bx1, y_offset+6, bx2, y_offset+38, fill="#fd7e14", outline="#1a1a1a", stipple="gray50")
                        self.canvas.create_text(bx1+5, y_offset+22, text="BAKIM", fill="white", anchor="w", font=("Segoe UI", 9, "bold"))

            # 2. Onaylı / Kullanımda Olan Rezervasyonlar
            ilgili = [r for r in self.motor.rezervasyonlar if r.kaynak_id == kaynak_id and r.durum not in ["IPTAL", "GELMEDI"]]
            for r in ilgili:
                bas_saat = r.baslangic.hour + (r.baslangic.minute / 60.0)
                bit_saat = r.bitis.hour + (r.bitis.minute / 60.0)
                if 8 <= bas_saat <= 22:
                    x1, x2 = 120 + ((bas_saat - 8) * 75), 120 + ((bit_saat - 8) * 75)
                    renk = "#20c997" if r.durum == "ONAYLI" else "#ffc107" if r.durum == "KULLANIMDA" else "#0d6efd"
                    
                    cerceve_renk = "#ffffff" if r.id == self.secili_rez_id else "#1a1a1a"
                    cerceve_kalinlik = 3 if r.id == self.secili_rez_id else 1
                    
                    tag_adi = f"rez_{r.id}"
                    self.canvas.create_rectangle(x1, y_offset+6, x2, y_offset+38, fill=renk, outline=cerceve_renk, width=cerceve_kalinlik, tags=(tag_adi,))
                    yazi_rengi = "#000000" if r.durum in ["ONAYLI", "KULLANIMDA"] else "#ffffff"
                    self.canvas.create_text(x1+8, y_offset+22, text=f"{r.id} ({r.kullanici_id})", fill=yazi_rengi, anchor="w", font=("Segoe UI", 10, "bold"), tags=(tag_adi,))
                    
                    self.canvas.tag_bind(tag_adi, "<Button-1>", lambda e, rid=r.id: self.kutuya_tiklandi(rid))
                    self.canvas.tag_bind(tag_adi, "<Enter>", lambda e, rez_obj=r: self.tooltip_goster(e, rez_obj))
                    self.canvas.tag_bind(tag_adi, "<Motion>", self.tooltip_hareket)
                    self.canvas.tag_bind(tag_adi, "<Leave>", self.tooltip_gizle)
                    
                    # Hazırlık / Soğuma Süresi Bloğu (Mor Kuyruk)
                    kt = self.motor.kaynak_turleri.get(kaynak.tur)
                    if kt and kt.hazirlik_dk > 0:
                        soguma_x2 = x2 + ((kt.hazirlik_dk / 60.0) * 75)
                        self.canvas.create_rectangle(x2, y_offset+12, soguma_x2, y_offset+32, fill="#6f42c1", outline="")

            # 3. Sırada Bekleyenler
            bekleyenler = [b for b in self.motor.bekleme_listesi if b.kaynak_id == kaynak_id]
            for idx, b in enumerate(bekleyenler):
                b_bas = b.baslangic.hour + (b.baslangic.minute / 60.0)
                b_bit = b.bitis.hour + (b.bitis.minute / 60.0)
                if 8 <= b_bas <= 22:
                    bx1, bx2 = 120 + ((b_bas - 8) * 75), 120 + ((b_bit - 8) * 75)
                    self.canvas.create_rectangle(bx1, y_offset+41, bx2, y_offset+59, fill="#3b3216", outline="#f1c40f", width=1, dash=(3, 2))
                    self.canvas.create_text(bx1+6, y_offset+50, text=f"Sırada {idx+1}: {b.kullanici_id}", fill="#f1c40f", anchor="w", font=("Segoe UI", 8, "bold"))

            y_offset += 68

        # 4. Canlı Sistem Saati Çizgisi (Kırmızı Lazer Çizgisi)
        if self.motor.sistem_saati:
            anlik = self.motor.sistem_saati.hour + (self.motor.sistem_saati.minute / 60.0)
            if 8 <= anlik <= 22:
                sx = 120 + ((anlik - 8) * 75)
                self.canvas.create_line(sx, 25, sx, y_offset, fill="#ff3366", width=2)
                self.canvas.create_oval(sx-4, 22, sx+4, 30, fill="#ff3366", outline="")