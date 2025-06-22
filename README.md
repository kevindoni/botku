# YouTube Live Streaming Bot Application

Aplikasi lengkap untuk live streaming YouTube dengan bot komentar otomatis untuk meningkatkan jam tayang dan engagement.

## ⚠️ DISCLAIMER
Aplikasi ini dibuat untuk tujuan edukasi dan penelitian. Pengguna bertanggung jawab penuh atas penggunaan aplikasi ini dan harus mematuhi Terms of Service YouTube serta peraturan yang berlaku.

## Fitur Utama

- 🎥 **Live Streaming Otomatis** - Streaming langsung ke YouTube tanpa OBS Studio
- 🤖 **Bot Komentar Cerdas** - Komentar otomatis yang natural dan anti-deteksi
- 📊 **Dashboard Monitoring** - Web interface real-time untuk kontrol lengkap
- ⏰ **Scheduler Streaming** - Jadwal streaming otomatis dengan timezone support
- 👥 **Viewer Bot** - Simulasi viewer untuk meningkatkan watch time
- 🔧 **Production Ready** - Optimized untuk Ubuntu Server 24 dengan Docker support
- 🚀 **Real-time Updates** - WebSocket untuk monitoring live
- 🛡️ **Anti-Detection** - User agent rotation, random delays, proxy support

## Persyaratan Sistem

- Ubuntu Server 24.04 LTS
- Python 3.10+
- Chrome/Chromium browser
- FFmpeg
- Minimum 4GB RAM
- GPU untuk encoding (opsional)

## Instalasi

### 1. Clone Repository
```bash
git clone <your-repo>
cd digindo
```

### 2. Install Dependencies
```bash
# Install sistem dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv
sudo apt install chromium-browser ffmpeg
sudo apt install xvfb # untuk headless display

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

### 3. Konfigurasi
```bash
# Copy konfigurasi template
cp config/config.example.yaml config/config.yaml

# Edit konfigurasi sesuai kebutuhan
nano config/config.yaml
```

### 4. Setup YouTube API
1. Buat project di Google Cloud Console
2. Enable YouTube Data API v3
3. Buat credentials (OAuth 2.0)
4. Download client_secret.json ke folder config/

## Penggunaan

### 1. Jalankan Dashboard
```bash
python src/app.py
```

### 2. Akses Dashboard
Buka browser: `http://localhost:5000`

### 3. Setup Streaming
1. Konfigurasi streaming settings (lihat config.yaml)
2. Setup YouTube stream key
3. Konfigurasi bot settings
4. Mulai streaming

## Struktur Project

```
digindo/
├── src/
│   ├── streaming/          # Modul streaming
│   ├── bot/               # Bot komentar & viewer
│   ├── api/               # API endpoints
│   ├── dashboard/         # Web dashboard
│   └── app.py            # Main application
├── config/               # Konfigurasi
├── templates/           # HTML templates
├── static/             # CSS, JS, assets
└── logs/              # Log files
```

## Konfigurasi Bot

Bot dapat dikonfigurasi untuk:
- Komentar otomatis dengan delay random
- Simulasi viewer dengan IP rotation
- Engagement natural (like, subscribe)
- Multiple account management

## Keamanan & Legal

⚠️ **PENTING**: 
- Gunakan dengan bijak dan sesuai ToS YouTube
- Bot dirancang untuk engagement natural
- Jangan spam atau melanggar guidelines
- Untuk tujuan edukasi dan pengembangan

## Troubleshooting

Lihat file `docs/troubleshooting.md` untuk solusi masalah umum.

## License

MIT License - Lihat file LICENSE untuk detail.
