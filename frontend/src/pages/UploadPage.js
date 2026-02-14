import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Upload, FileText, Image, File, CheckCircle, XCircle, Loader } from 'lucide-react';
import { uploadDocument } from '../api';

const UploadPage = () => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  }, []);

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = (fileList) => {
    const newFiles = Array.from(fileList).map(file => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      status: 'pending',
      progress: 0
    }));
    setFiles(prev => [...prev, ...newFiles]);
  };

  const uploadFiles = async () => {
    setUploading(true);
    
    for (const fileItem of files) {
      if (fileItem.status !== 'pending') continue;
      
      try {
        // Update status to uploading
        setFiles(prev => prev.map(f => 
          f.id === fileItem.id ? { ...f, status: 'uploading', progress: 50 } : f
        ));

        // Upload file
        const result = await uploadDocument(fileItem.file);
        
        // Update status to success
        setFiles(prev => prev.map(f => 
          f.id === fileItem.id ? { 
            ...f, 
            status: 'success', 
            progress: 100,
            documentId: result.document_id 
          } : f
        ));
      } catch (error) {
        // Update status to error
        setFiles(prev => prev.map(f => 
          f.id === fileItem.id ? { 
            ...f, 
            status: 'error', 
            progress: 0,
            error: error.message 
          } : f
        ));
      }
    }
    
    setUploading(false);
  };

  const removeFile = (id) => {
    setFiles(prev => prev.filter(f => f.id !== id));
  };

  const getFileIcon = (file) => {
    const type = file.type;
    if (type.startsWith('image/')) return <Image className="w-8 h-8 text-purple-400" />;
    if (type === 'application/pdf') return <FileText className="w-8 h-8 text-red-400" />;
    return <File className="w-8 h-8 text-blue-400" />;
  };

  return (
    <div className="p-6 max-w-5xl mx-auto" data-testid="upload-page">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-4xl font-heading font-bold mb-2">Doküman Yükle</h1>
        <p className="text-gray-400">PDF, görsel, metin dosyalarınızı yükleyin ve AI analizi ile yapılandırılmış bilgiye dönüştürün.</p>
      </motion.div>

      {/* Drop Zone */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="mb-8"
      >
        <div
          className={`relative border-2 border-dashed rounded-xl p-12 text-center transition-all ${
            dragActive 
              ? 'border-indigo-500 bg-indigo-500/10' 
              : 'border-white/10 bg-bg-surface hover:border-white/20'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          data-testid="drop-zone"
        >
          <input
            type="file"
            multiple
            onChange={handleFileInput}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            data-testid="file-input"
          />
          <Upload className="w-16 h-16 mx-auto mb-4 text-indigo-400" />
          <h3 className="text-xl font-semibold mb-2">Dosyaları buraya sürükleyin</h3>
          <p className="text-gray-400 mb-4">veya tıklayarak seçin</p>
          <p className="text-sm text-gray-500">Desteklenen formatlar: PDF, JPG, PNG, DOCX, XLSX</p>
        </div>
      </motion.div>

      {/* File List */}
      {files.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-bg-surface border border-white/5 rounded-xl p-6 mb-6"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-heading font-bold">Yüklenecek Dosyalar ({files.length})</h3>
            {!uploading && files.some(f => f.status === 'pending') && (
              <button
                onClick={uploadFiles}
                className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 rounded-lg font-medium transition-all hover:scale-[1.02]"
                data-testid="btn-start-upload"
              >
                Yüklemeyi Başlat
              </button>
            )}
          </div>

          <div className="space-y-3">
            {files.map((fileItem, index) => (
              <motion.div
                key={fileItem.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="flex items-center justify-between p-4 bg-bg-primary rounded-lg border border-white/5"
                data-testid="file-item"
              >
                <div className="flex items-center space-x-4 flex-1">
                  {getFileIcon(fileItem.file)}
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{fileItem.file.name}</p>
                    <p className="text-sm text-gray-500">
                      {(fileItem.file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  {fileItem.status === 'pending' && (
                    <button
                      onClick={() => removeFile(fileItem.id)}
                      className="text-gray-400 hover:text-red-400"
                      data-testid="btn-remove-file"
                    >
                      <XCircle className="w-5 h-5" />
                    </button>
                  )}
                  {fileItem.status === 'uploading' && (
                    <Loader className="w-5 h-5 text-blue-400 animate-spin" />
                  )}
                  {fileItem.status === 'success' && (
                    <CheckCircle className="w-5 h-5 text-emerald-400" />
                  )}
                  {fileItem.status === 'error' && (
                    <XCircle className="w-5 h-5 text-red-400" />
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-bg-surface border border-white/5 rounded-xl p-6">
          <div className="w-10 h-10 rounded-lg bg-indigo-500/10 flex items-center justify-center mb-4">
            <FileText className="w-5 h-5 text-indigo-400" />
          </div>
          <h4 className="font-semibold mb-2">Otomatik Analiz</h4>
          <p className="text-sm text-gray-400">
            AI ile dokümanlarınızı otomatik olarak analiz edip kategorilendirir.
          </p>
        </div>

        <div className="bg-bg-surface border border-white/5 rounded-xl p-6">
          <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center mb-4">
            <CheckCircle className="w-5 h-5 text-emerald-400" />
          </div>
          <h4 className="font-semibold mb-2">Bilgi Çıkarımı</h4>
          <p className="text-sm text-gray-400">
            SOP, checklist, standart ve politikaları otomatik olarak çıkarır.
          </p>
        </div>

        <div className="bg-bg-surface border border-white/5 rounded-xl p-6">
          <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center mb-4">
            <Upload className="w-5 h-5 text-purple-400" />
          </div>
          <h4 className="font-semibold mb-2">Görev Oluşturma</h4>
          <p className="text-sm text-gray-400">
            İçerikten uygulanabilir görevleri otomatik olarak oluşturur.
          </p>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;
