from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class Rol:
    ad: str
    azami_sure_dk: int
    ileri_gun: int
    haftalik_kota: int

@dataclass
class KaynakTuru:
    ad: str
    saatlik_ucret: float
    hazirlik_dk: int
    enerji_yogun: bool
    sertifika: Optional[str] = None

@dataclass
class Kullanici:
    id: str
    ad: str
    rol: str
    bakiye: float
    sertifikalar: List[str] = field(default_factory=list)
    guvenilirlik: int = 100

@dataclass
class Kaynak:
    id: str
    ad: str
    tur: str
    izinli_roller: List[str] = field(default_factory=list)

@dataclass
class BakimPenceresi:
    kaynak_id: str
    baslangic: datetime
    bitis: datetime

@dataclass
class Rezervasyon:
    id: str
    kullanici_id: str
    kaynak_id: str
    baslangic: datetime
    bitis: datetime
    ucret: float
    durum: str  # ONAYLI, KULLANIMDA, TAMAMLANDI, IPTAL, GELMEDI

@dataclass
class BeklemeKaydi:
    id: str
    kullanici_id: str
    kaynak_id: str
    baslangic: datetime
    bitis: datetime
    talep_zamani: datetime