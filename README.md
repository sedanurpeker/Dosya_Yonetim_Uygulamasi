# Dosya Yönetim Uygulaması (File Management System)

Bu proje, kullanıcı giriş sistemiyle entegre bir **dosya yönetim web uygulamasıdır**.  
Kullanıcılar sisteme kayıt olabilir, giriş yapabilir, dosyalarını yükleyip yönetebilir.  
Yüklenen dosyalar hem sunucuda hem de SQL Server veritabanında saklanır.

---

##  Özellikler
-  **Kullanıcı Kaydı ve Girişi**  
  - Şifre güvenlik kontrolleri (küçük harf, büyük harf, rakam, özel karakter).  
  - Şifreler **hashlenmiş** olarak veritabanında saklanır.  
-  **Dosya Yönetimi**  
  - Dosya yükleme, listeleme ve silme işlemleri.  
  - Her kullanıcıya özel klasör oluşturulur (`uploads/{UserID}`).  
-  **SQL Server Entegrasyonu**  
  - Kullanıcı ve dosya bilgileri `DosyaYonetimDB` veritabanında tutulur.  
-  **Tema Desteği**  
  - Kullanıcılar açık ve karanlık mod arasında geçiş yapabilir.  
-  **Modern Arayüz**  
  - HTML5, CSS3 (Poppins font) ve animasyonlu tasarım.  

---

##  Kullanılan Teknolojiler
- **Python 3.9+**
- **Flask** (web framework)
- **PyODBC** (SQL Server bağlantısı)
- **Werkzeug** (şifre güvenliği ve dosya yönetimi)
- **HTML / CSS (Poppins Font + Modern Tasarım)**

---

## Kurulum ve Çalıştırma

### 1️. Gerekli kütüphaneleri yükle
```bash
pip install flask pyodbc werkzeug
```
### 2️. SQL Server’da veritabanını oluştur
```bash
CREATE DATABASE DosyaYonetimDB;
GO

USE DosyaYonetimDB;

CREATE TABLE Users (
    UserID INT IDENTITY(1,1) PRIMARY KEY,
    Username NVARCHAR(100) UNIQUE NOT NULL,
    Password NVARCHAR(255) NOT NULL
);

CREATE TABLE Files (
    FileID INT IDENTITY(1,1) PRIMARY KEY,
    Filename NVARCHAR(255) NOT NULL,
    UserID INT FOREIGN KEY REFERENCES Users(UserID)
);
```

### 3️. Proje dizin yapısı
```
dosya-yonetim
 ┣  dosya_yonetim.py        # Ana Flask uygulaması
 ┣  templates/
 ┃ ┣  base.html
 ┃ ┣  login.html
 ┃ ┣  register.html
 ┃ ┗  dashboard.html
 ┣  static/
 ┃ ┗  css/style.css
 ┣  uploads/                # Kullanıcı dosyalarının saklandığı klasör
 ┗  README.md
```
### 4️. Uygulamayı çalıştır
```bash
python dosya_yonetim.py
```
Tarayıcıda şu adresi aç: http://127.0.0.1:5000

| Sayfa              | Açıklama                                                      |
| ------------------ | ------------------------------------------------------------- |
| **register.html**  | Kullanıcı kayıt formu (şifre kuralları canlı kontrol edilir). |
| **login.html**     | Kullanıcı giriş ekranı (karanlık mod destekli).               |
| **dashboard.html** | Dosya yükleme, listeleme, silme işlemleri yapılır.            |
| **base.html**      | Ortak şablon dosyası (Flask `block` yapısı ile).              |



👩‍💻 Developer: Sedanur Peker












