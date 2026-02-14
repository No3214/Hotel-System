import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { MessageSquare, Upload, CheckCircle, Users, FileText } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const WhatsAppPage = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // Check if it's a text file
      if (selectedFile.type === 'text/plain' || selectedFile.name.endsWith('.txt')) {
        setFile(selectedFile);
        setError(null);
      } else {
        setError('Lütfen sadece .txt uzantılı WhatsApp export dosyası yükleyin');
      }
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(
        `${BACKEND_URL}/api/whatsapp/parse`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-6 max-w-5xl mx-auto" data-testid="whatsapp-page">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-4xl font-heading font-bold mb-2 flex items-center">
          <MessageSquare className="w-10 h-10 mr-3 text-green-400" />
          WhatsApp Entegrasyonu
        </h1>
        <p className="text-gray-400">
          WhatsApp görüşme export dosyanızı yükleyin, AI otomatik görevlere dönüştürsün
        </p>
      </motion.div>

      {/* Upload Section */}
      <div className="grid md:grid-cols-2 gap-8 mb-8">
        {/* Left: Upload */}
        <div className="bg-bg-surface border border-white/5 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">1. WhatsApp Export Yükle</h3>
          
          <div className="mb-6">
            <label className="block text-sm text-gray-400 mb-2">
              Dosya Seç (.txt)
            </label>
            <input
              type="file"
              accept=".txt"
              onChange={handleFileSelect}
              className="w-full px-4 py-2 bg-bg-primary border border-white/10 rounded-lg text-sm file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-700"
              data-testid="whatsapp-file-input"
            />
          </div>

          {file && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mb-4 p-3 bg-bg-primary rounded-lg"
            >
              <p className="text-sm font-medium">{file.name}</p>
              <p className="text-xs text-gray-500">
                {(file.size / 1024).toFixed(2)} KB
              </p>
            </motion.div>
          )}

          {error && (
            <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
              {error}
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="w-full py-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg font-medium transition-all"
            data-testid="btn-parse-whatsapp"
          >
            {uploading ? 'İşleniyor...' : 'Analiz Et ve Görevleri Oluştur'}
          </button>
        </div>

        {/* Right: Instructions */}
        <div className="bg-bg-surface border border-white/5 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">Nasıl Export Alınır?</h3>
          
          <div className="space-y-4 text-sm text-gray-400">
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 rounded-full bg-indigo-600 flex items-center justify-center text-white text-xs flex-shrink-0">
                1
              </div>
              <div>
                <p className="text-white font-medium mb-1">WhatsApp Uygulamasını Açın</p>
                <p>Görüşmeleri export etmek istediğiniz grup veya kişiyi seçin</p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 rounded-full bg-indigo-600 flex items-center justify-center text-white text-xs flex-shrink-0">
                2
              </div>
              <div>
                <p className="text-white font-medium mb-1">Ayarlar > Export Chat</p>
                <p>3 nokta menüsünden "Export chat" seçeneğini tıklayın</p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 rounded-full bg-indigo-600 flex items-center justify-center text-white text-xs flex-shrink-0">
                3
              </div>
              <div>
                <p className="text-white font-medium mb-1">Medya Olmadan Export</p>
                <p>"Without media" seçeneğini seçin (sadece metin)</p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 rounded-full bg-indigo-600 flex items-center justify-center text-white text-xs flex-shrink-0">
                4
              </div>
              <div>
                <p className="text-white font-medium mb-1">Kaydet ve Yükle</p>
                <p>.txt dosyasını kaydedin ve bu sayfaya yükleyin</p>
              </div>
            </div>
          </div>

          <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
            <p className="text-xs text-blue-400">
              💡 <strong>İpucu:</strong> Son 7 günlük mesajları export etmek en iyi sonuçları verir
            </p>
          </div>
        </div>
      </div>

      {/* Results */}
      {result && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-bg-surface border border-white/5 rounded-xl p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold flex items-center">
              <CheckCircle className="w-6 h-6 mr-2 text-green-400" />
              İşlem Başarılı!
            </h3>
          </div>

          <div className="grid md:grid-cols-3 gap-6 mb-6">
            <div className="p-4 bg-bg-primary rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-400">Toplam Mesaj</span>
                <MessageSquare className="w-5 h-5 text-indigo-400" />
              </div>
              <p className="text-2xl font-bold">{result.statistics.total_messages}</p>
            </div>

            <div className="p-4 bg-bg-primary rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-400">Kişi Sayısı</span>
                <Users className="w-5 h-5 text-purple-400" />
              </div>
              <p className="text-2xl font-bold">{result.statistics.unique_senders}</p>
            </div>

            <div className="p-4 bg-bg-primary rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-400">Oluşturulan Görev</span>
                <FileText className="w-5 h-5 text-green-400" />
              </div>
              <p className="text-2xl font-bold">{result.statistics.tasks_created}</p>
            </div>
          </div>

          {result.senders && result.senders.length > 0 && (
            <div className="mb-6">
              <h4 className="text-sm font-semibold mb-3">Görüşmeye Katılanlar:</h4>
              <div className="flex flex-wrap gap-2">
                {result.senders.map((sender, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-indigo-500/10 text-indigo-400 text-sm rounded-full"
                  >
                    {sender}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="flex items-center justify-between pt-4 border-t border-white/5">
            <p className="text-sm text-gray-400">
              Görevler "Görevler" sayfasında görüntülenebilir
            </p>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-white/5 hover:bg-white/10 rounded-lg text-sm font-medium transition-all"
            >
              Yeni Analiz
            </button>
          </div>
        </motion.div>
      )}

      {/* Features */}
      <div className="grid md:grid-cols-3 gap-6 mt-8">
        <div className="bg-bg-surface border border-white/5 rounded-xl p-6">
          <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center mb-4">
            <MessageSquare className="w-5 h-5 text-green-400" />
          </div>
          <h4 className="font-semibold mb-2">Sipariş Tespiti</h4>
          <p className="text-sm text-gray-400">
            "50 adet yumurta lazım" gibi mesajlardan otomatik sipariş görevleri oluşturur
          </p>
        </div>

        <div className="bg-bg-surface border border-white/5 rounded-xl p-6">
          <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center mb-4">
            <CheckCircle className="w-5 h-5 text-blue-400" />
          </div>
          <h4 className="font-semibold mb-2">Talep Çıkarımı</h4>
          <p className="text-sm text-gray-400">
            "Oda 5'i hazırla", "Kahvaltı 8'de" gibi isteklerden görev ve hatırlatıcı yapar
          </p>
        </div>

        <div className="bg-bg-surface border border-white/5 rounded-xl p-6">
          <div className="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center mb-4">
            <FileText className="w-5 h-5 text-red-400" />
          </div>
          <h4 className="font-semibold mb-2">Şikayet Bildirimi</h4>
          <p className="text-sm text-gray-400">
            "Bozuk", "Çalışmıyor" gibi sorunları yüksek öncelikli görev olarak işaretler
          </p>
        </div>
      </div>
    </div>
  );
};

export default WhatsAppPage;
