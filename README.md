# 🕸️ DefHunter - Omni-Scan Vulnerability Engine

<p align="center">
  <img src="https://img.shields.io/badge/Version-2.1-green?style=for-the-badge">
  <img src="https://img.shields.io/badge/OS-Kali%20Linux-blue?style=for-the-badge">
  <img src="https://img.shields.io/badge/Python-3.x-yellow?style=for-the-badge">
  <img src="https://img.shields.io/badge/Author-DerdliAsiq-red?style=for-the-badge">
</p>

**DefHunter**, sızma testlerinde (pentest) hedef sistem üzerindeki varsayılan (default) kimlik bilgilerini, hatalı yapılandırmaları ve şifresiz bırakılmış kritik servisleri otonom olarak avlayan, multi-thread mimariye sahip agresif bir keşif motorudur.

Gelişmiş ağlarda sıkça unutulan "TassakliSabri" tarzı zayıf profilleri saniyeler içinde tespit edip sisteme ilk gediği açmak için tasarlanmıştır.

## ⚡ Desteklenen Zafiyet Avı Modülleri

- **[Port 21] FTP Anonymous:** Kimlik doğrulamasız dosya okuma/yazma kontrolü.
- **[Port 22] SSH Default Creds:** Sabitlenmiş zayıf şifrelerin (örn: root:root, sabri:123456) denenmesi.
- **[Port 80/8080] Web Directory Listing:** Açık bırakılmış dizin listelemelerinin tespiti.
- **[Port 139/445] SMB Null Session:** Şifresiz paylaşımların ve "TassakliSabrininSirlari" gibi özel alanların keşfi.
- **[Port 389] LDAP Anonymous Bind:** Dizin üzerinde şifresiz okuma yetkisi kontrolü.
- **[Port 873] Rsync Anonymous:** Kimlik sormayan Rsync modüllerinin tespiti.
- **[Port 3306] MySQL Blank Password:** `root` kullanıcısının şifresiz bırakılıp bırakılmadığının kontrolü.
- **[Port 6379] Redis Unauthenticated:** Şifresiz bırakılmış, RCE'ye açık Redis veritabanı kontrolü.
- **[Port 8080] Tomcat Manager:** Varsayılan Tomcat admin paneli parolalarının tespiti.

## 🛠️ Kurulum (Installation)

Aracın çalışması için sisteminizde Python 3.x ve çeşitli kütüphaneler gerekmektedir.

```bash
# Repoyu klonlayın
git clone https://github.com/DerdliAsiq/DefHunter.git
cd DefHunter

# Gerekli bağımlılıklarla birlikte aracı sisteme gömün
sudo pip3 install . --break-system-packages
```

🚀 Kullanım (Usage)

Kurulum tamamlandıktan sonra terminalin herhangi bir yerinden aracı hedef IP adresi ile çağırabilirsiniz. DefHunter önce hızlı bir Pre-Check (Ön Tarama) yapar, sadece açık bulduğu portlara uygun modülleri eşzamanlı (multi-thread) olarak ateşler.

```
# Temel Kullanım:
defhunter -t <HEDEF_IP>

# Örnek:
defhunter -t 192.168.1.50
```

⚠️ Yasal Uyarı

Bu araç, DerdliAsiq tarafından tamamen eğitim ve yasal sızma testi (penetration testing) laboratuvarlarında kullanılmak üzere geliştirilmiştir. Yetkiniz olmayan (izinsiz) sistemler üzerinde kullanmak yasadışıdır ve tüm sorumluluk kullanıcıya aittir.