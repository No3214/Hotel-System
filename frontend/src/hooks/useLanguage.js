import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getTranslations, getLanguages } from '../api';

const LanguageContext = createContext();

const FALLBACK_TR = {
  dashboard: "Dashboard", rooms: "Odalar", guests: "Misafirler",
  chatbot: "AI Asistan", messages: "Mesajlar", tasks: "Gorevler",
  events: "Etkinlikler", housekeeping: "Kat Hizmetleri",
  knowledge: "Bilgi Bankasi", menu: "QR Menu",
  reservations: "Rezervasyonlar", staff: "Personel",
  campaigns: "Kampanyalar", settings: "Ayarlar",
  welcome: "Hos Geldiniz", occupancy: "Doluluk Orani",
  add: "Ekle", save: "Kaydet", delete: "Sil", cancel: "Iptal",
  search: "Ara", total: "Toplam", available: "Musait",
  occupied: "Dolu", pending: "Bekleyen", completed: "Tamamlanan",
  whatsapp: "WhatsApp", pricing: "Fiyatlama", reviews: "Google Yorumlari",
  lifecycle: "Misafir Dongusu", social: "Sosyal Medya",
  table_reservations: "Masa Rez.", organization: "Organizasyon", proposals: "Teklifler",
  guide: "Foca Rehberi", automation: "Otomasyon",
  general: "Genel", communication: "Iletisim", operations: "Operasyon",
  information: "Bilgi", system: "Sistem",
  hotel_management: "Otel Yonetim Paneli",
  occupancy_rate: "Doluluk Orani", total_rooms: "Toplam Oda",
  occupied_rooms: "Dolu Oda", available_rooms: "Bos Oda",
  todays_checkins: "Bugunun Girisleri", todays_checkouts: "Bugunun Cikislari",
  revenue: "Gelir", monthly_revenue: "Aylik Gelir",
  weekly_trend: "Haftalik Doluluk Trendi",
  recent_activity: "Son Aktiviteler", recent_tasks: "Son Gorevler",
  platform_ratings: "Platform Puanlari",
  room_status: "Oda Durumu", live: "Canli",
  logout: "Cikis Yap", admin: "Admin", reception: "Resepsiyon",
  language: "Dil", no_data: "Henuz veri yok",
  confirmed: "Onaylandi", checked_in: "Giris Yapti", checked_out: "Cikis Yapti",
  cancelled: "Iptal Edildi", cleaning: "Temizlik",
  today: "Bugun", this_month: "Bu Ay",
  revenue: "Gelir Yonetimi", analytics: "Analitik", audit: "Guvenlik",
  hotelrunner: "HotelRunner", integrations: "Entegrasyonlar",
  marketing_hub: "Pazarlama", event_leads: "Etkinlik Leadleri",
  presence_monitor: "Online Varlik", seo: "SEO Yonetimi", competitor: "Rakip Analizi",
  financials: "Gelir/Gider", kitchen: "Mutfak", pricing: "Fiyatlandirma",
  revenue: "Gelir Yonetimi", finance: "Finans",
};

export function LanguageProvider({ children }) {
  const [lang, setLang] = useState(() => localStorage.getItem('kozbeyli_lang') || 'tr');
  const [translations, setTranslations] = useState(FALLBACK_TR);
  const [languages, setLanguages] = useState([]);

  useEffect(() => {
    getLanguages().then(r => setLanguages(r.data.languages)).catch(() => {});
  }, []);

  useEffect(() => {
    localStorage.setItem('kozbeyli_lang', lang);
    getTranslations(lang)
      .then(r => setTranslations(r.data.translations))
      .catch(() => setTranslations(FALLBACK_TR));
  }, [lang]);

  const t = useCallback((key) => translations[key] || FALLBACK_TR[key] || key, [translations]);

  return (
    <LanguageContext.Provider value={{ lang, setLang, t, languages }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error('useLanguage must be used within LanguageProvider');
  return ctx;
}
