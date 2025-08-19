# TaskTycoon – Görevlerle Şirket Kur

Bu proje, Flask tabanlı bir şirket simülasyon oyunudur. Her gün yapılan görevlerle şirketinizi büyütün, departmanlar açın ve ekonominizi yönetin.

## Kurulum

1. Sanal ortam oluşturun ve aktif edin:
   ```
   python -m venv venv
   .\venv\Scripts\activate
   ```
2. Bağımlılıkları yükleyin:
   ```
   pip install -r requirements.txt
   ```
3. Uygulamayı başlatın:
   ```
   python app/main.py
   ```

## API Endpointleri
- `GET /api/state` : Şirket state bilgisini döndürür.

## Yol Haritası
- Günlük görevlerle adım adım ilerleme.
- Her gün yapılan değişiklikler GitHub'a yüklenecek.

## Lisans
MIT
