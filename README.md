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
git clone https://github.com/kevindoni/botku.git
cd botku
```

### 2. Install Dependencies

**📋 Opsi Instalasi:**

| Script | Deskripsi | Untuk |
|--------|-----------|-------|
| `quick-install.sh` | ⚡ Instalasi cepat dan sederhana | Root & Non-root |
| `install.sh` | 🔧 Instalasi lengkap dengan konfigurasi | Non-root (auto-handle root) |
| `install-root.sh` | 🛡️ Instalasi khusus root dengan user dedicated | Root VPS |

**Pilihan A: Quick Install (Direkomendasikan untuk VPS)**
```bash
chmod +x quick-install.sh
./quick-install.sh
```

**Pilihan B: Standard Install**
```bash
chmod +x install.sh
./install.sh
```

**Pilihan C: Root Install dengan Dedicated User**
```bash
chmod +x install-root.sh
./install-root.sh
```

**Pilihan D: Manual Install**
```bash
# Install sistem dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv
sudo apt install chromium-browser ffmpeg xvfb

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
cp config/client_secrets.example.json config/client_secrets.json
cp .env.example .env

# Edit konfigurasi sesuai kebutuhan
nano config/config.yaml
nano .env
```

### 4. Setup YouTube API
1. Buat project di Google Cloud Console
2. Enable YouTube Data API v3
3. Buat credentials (OAuth 2.0)
4. Download client_secret.json ke folder config/

## Script Instalasi

### 🚀 quick-install.sh
Script instalasi tercepat yang bekerja di direktori saat ini:
- ✅ Support root dan non-root user
- ✅ Instalasi minimal namun lengkap
- ✅ Otomatis setup ChromeDriver
- ✅ Konfigurasi firewall

### 🔧 install.sh  
Script instalasi standar dengan fitur lengkap:
- ✅ Auto-detect root/non-root
- ✅ Membuat user dedicated jika root
- ✅ Setup systemd service
- ✅ Konfigurasi supervisor

### 🛡️ install-root.sh
Script khusus untuk instalasi sebagai root di VPS:
- ✅ Membuat user 'botuser' dedicated
- ✅ Setup environment lengkap
- ✅ Konfigurasi systemd service
- ✅ Nginx dan firewall setup

## Penggunaan

### 1. Jalankan Dashboard
```bash
# Menggunakan script yang disediakan
./start.sh

# Atau jalankan manual
python src/app.py
```

### 2. Akses Dashboard
Buka browser: `http://localhost:5000`

### 3. Setup Streaming
1. Konfigurasi streaming settings di config/config.yaml
2. Setup YouTube stream key di dashboard
3. Konfigurasi bot settings (komentar & viewer)
4. Mulai streaming melalui dashboard

## Docker Deployment

```bash
# Build dan jalankan dengan Docker Compose
docker-compose up -d

# Atau build manual
docker build -t youtube-streaming-bot .
docker run -p 5000:5000 youtube-streaming-bot
```

## Struktur Project

```
botku/
├── src/
│   ├── streaming/          # Modul streaming FFmpeg
│   ├── bot/               # Bot komentar & viewer 
│   ├── api/               # YouTube API integration
│   ├── dashboard/         # Analytics & monitoring
│   └── app.py            # Main Flask application
├── config/               # File konfigurasi
│   ├── config.example.yaml
│   ├── client_secrets.example.json
│   ├── comments.json
│   └── accounts.json
├── templates/           # HTML templates
├── static/             # CSS, JS, assets
├── docs/              # Dokumentasi
├── nginx/             # Nginx configuration
├── requirements.txt   # Python dependencies
├── Dockerfile        # Docker configuration
├── docker-compose.yml # Docker Compose
├── install.sh        # Standard installation script
├── install-root.sh   # Root installation script
├── quick-install.sh  # Quick installation script
├── start.sh         # Application start script
├── dev.sh           # Development script
└── logs/             # Log files
```

## Konfigurasi Bot

Bot dapat dikonfigurasi untuk:
- **Komentar otomatis** dengan delay random (30-60 detik)
- **Simulasi viewer** dengan session duration realistis
- **IP rotation** menggunakan proxy (opsional)
- **Multiple account** management dari config/accounts.json
- **Anti-detection** dengan user agent rotation dan random delays
- **Natural engagement** pattern yang menyerupai behavior manusia

### File Konfigurasi Penting:
- `config/config.yaml` - Konfigurasi utama aplikasi
- `config/comments.json` - Database komentar untuk bot
- `config/accounts.json` - Akun-akun untuk bot (tidak di-commit)
- `config/client_secrets.json` - YouTube API credentials (tidak di-commit)

## Keamanan & Legal

⚠️ **PENTING**: 
- Gunakan dengan bijak dan sesuai Terms of Service YouTube
- Bot dirancang untuk engagement natural dan anti-detection
- Jangan spam atau melanggar community guidelines
- Untuk tujuan edukasi dan pengembangan skill
- Pengguna bertanggung jawab penuh atas penggunaan aplikasi
- Respek rate limits dan API quotas
- Gunakan proxy dan rotate IP untuk menghindari blocking

## Troubleshooting

### Common Issues

**1. Permission Denied saat menjalankan script:**
```bash
chmod +x *.sh
./quick-install.sh
```

**2. Error setuptools/numpy saat instalasi Python packages:**
```bash
# Install system dependencies first
sudo apt update
sudo apt install python3-dev python3-setuptools build-essential libhdf5-dev

# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# Install setuptools first
pip install --upgrade pip setuptools wheel

# Install packages one by one if needed
pip install --no-cache-dir flask==2.3.3
pip install --no-cache-dir "numpy>=1.21.0"
pip install --no-cache-dir "opencv-python>=4.5.0"
```

**3. ChromeDriver tidak ditemukan:**
```bash
# Install ulang ChromeDriver
sudo apt install chromium-browser
# Script akan otomatis download ChromeDriver yang sesuai
```

**4. FFmpeg tidak ditemukan:**
```bash
sudo apt update
sudo apt install ffmpeg
ffmpeg -version  # Verify installation
```

**5. Virtual environment issues:**
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**6. Port 5000 sudah digunakan:**
```bash
# Edit config/config.yaml dan ubah port
nano config/config.yaml
# Atau jalankan dengan port berbeda
python src/app.py --port 5001
```

**7. Masalah dengan snap packages (Chromium):**
```bash
# Install chromium dari apt instead of snap
sudo snap remove chromium
sudo apt install chromium-browser
```

Lihat file `docs/troubleshooting.md` untuk solusi masalah umum lainnya.

## Contributing

1. Fork repository ini
2. Buat branch untuk fitur baru (`git checkout -b feature/nama-fitur`)
3. Commit perubahan (`git commit -am 'Tambah fitur baru'`)
4. Push ke branch (`git push origin feature/nama-fitur`)
5. Buat Pull Request

## Support

Jika menemukan bug atau memiliki pertanyaan:
- Buat issue di GitHub repository
- Pastikan menyertakan log error dan informasi sistem
- Ikuti template issue yang disediakan

## License

MIT License - Lihat file LICENSE untuk detail.
