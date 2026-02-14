import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter, FileText, CheckSquare, Shield, Package, BookOpen } from 'lucide-react';
import { listKnowledgeItems, semanticSearch } from '../api';

const KnowledgeBasePage = () => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [searchMode, setSearchMode] = useState('text'); // text or semantic

  useEffect(() => {
    fetchItems();
  }, [filterType]);

  const fetchItems = async () => {
    try {
      setLoading(true);
      const params = filterType !== 'all' ? { item_type: filterType } : {};
      const data = await listKnowledgeItems(params);
      setItems(data.items || []);
    } catch (error) {
      console.error('Error fetching knowledge items:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      fetchItems();
      return;
    }

    try {
      setLoading(true);
      if (searchMode === 'semantic') {
        const data = await semanticSearch(searchQuery);
        setItems(data.results || []);
      } else {
        const data = await listKnowledgeItems({ search: searchQuery });
        setItems(data.items || []);
      }
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'sop': return <FileText className="w-5 h-5 text-green-400" />;
      case 'checklist': return <CheckSquare className="w-5 h-5 text-blue-400" />;
      case 'policy': return <Shield className="w-5 h-5 text-purple-400" />;
      case 'inventory': return <Package className="w-5 h-5 text-amber-400" />;
      default: return <BookOpen className="w-5 h-5 text-gray-400" />;
    }
  };

  const getTypeLabel = (type) => {
    const labels = {
      sop: 'SOP',
      checklist: 'Checklist',
      standard: 'Standart',
      policy: 'Politika',
      inventory: 'Envanter',
      task: 'Görev'
    };
    return labels[type] || type;
  };

  return (
    <div className="p-6 max-w-7xl mx-auto" data-testid="knowledge-page">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-4xl font-heading font-bold mb-2">Bilgi Tabanı</h1>
        <p className="text-gray-400">Dokümanlardan çıkarılmış SOP'ler, checklist'ler ve standartlar</p>
      </motion.div>

      {/* Search and Filters */}
      <div className="bg-bg-surface border border-white/5 rounded-xl p-6 mb-6">
        <div className="flex flex-col md:flex-row gap-4 mb-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Bilgi tabanında ara... (örn: 'kahvaltı hazırlık prosedürü')"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              className="w-full pl-10 pr-4 py-3 bg-bg-primary border border-white/10 rounded-lg focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
              data-testid="search-input"
            />
          </div>
          <button
            onClick={handleSearch}
            className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 rounded-lg font-medium transition-all hover:scale-[1.02]"
            data-testid="btn-search"
          >
            Ara
          </button>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-400">Filtre:</span>
          </div>
          {['all', 'sop', 'checklist', 'policy', 'inventory', 'standard'].map(type => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                filterType === type
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white/5 text-gray-400 hover:bg-white/10'
              }`}
              data-testid={`filter-${type}`}
            >
              {type === 'all' ? 'Tümü' : getTypeLabel(type)}
            </button>
          ))}

          <div className="ml-auto flex items-center space-x-2">
            <span className="text-sm text-gray-400">Arama Modu:</span>
            <button
              onClick={() => setSearchMode(searchMode === 'text' ? 'semantic' : 'text')}
              className="px-3 py-1.5 rounded-lg text-sm font-medium bg-white/5 hover:bg-white/10 transition-all"
              data-testid="toggle-search-mode"
            >
              {searchMode === 'text' ? 'Metin' : 'Semantik'} 🧪
            </button>
          </div>
        </div>
      </div>

      {/* Items Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
        </div>
      ) : items.length === 0 ? (
        <div className="bg-bg-surface border border-white/5 rounded-xl p-12 text-center">
          <BookOpen className="w-16 h-16 mx-auto mb-4 text-gray-600" />
          <h3 className="text-xl font-semibold mb-2">Bilgi öğesi bulunamadı</h3>
          <p className="text-gray-400">Henüz hiç doküman işlenmedi veya arama sonuç bulunamadı.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {items.map((item, index) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="bg-bg-surface border border-white/5 rounded-xl p-6 card-hover"
              data-testid="knowledge-item"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  {getTypeIcon(item.item_type)}
                  <div>
                    <span className="text-xs font-medium text-gray-500 uppercase">
                      {getTypeLabel(item.item_type)}
                    </span>
                    <h3 className="text-lg font-semibold">{item.title}</h3>
                  </div>
                </div>
                {item.similarity && (
                  <div className="text-xs text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded">
                    {(item.similarity * 100).toFixed(0)}% eşleşme
                  </div>
                )}
              </div>

              <p className="text-gray-400 text-sm mb-4 line-clamp-3">{item.content}</p>

              {item.applicable_to && item.applicable_to.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-4">
                  {item.applicable_to.map((area, i) => (
                    <span
                      key={i}
                      className="px-2 py-1 bg-indigo-500/10 text-indigo-400 text-xs rounded-full"
                    >
                      {area}
                    </span>
                  ))}
                </div>
              )}

              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>Öncelik: {item.priority}/10</span>
                <span>{new Date(item.created_at).toLocaleDateString('tr-TR')}</span>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};

export default KnowledgeBasePage;
