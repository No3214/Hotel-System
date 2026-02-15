import React, { useState, useEffect } from 'react';
import { getKnowledge, createKnowledge, deleteKnowledge } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { BookOpen, Plus, Trash2, Search } from 'lucide-react';

export default function KnowledgePage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ title: '', content: '', category: 'general', tags: '' });

  const load = () => {
    getKnowledge({ search: search || undefined })
      .then(r => setItems(r.data.items))
      .catch(console.error)
      .finally(() => setLoading(false));
  };
  useEffect(() => { load(); }, [search]);

  const handleCreate = async () => {
    if (!form.title || !form.content) return;
    await createKnowledge({
      ...form,
      tags: form.tags ? form.tags.split(',').map(t => t.trim()) : [],
    });
    setForm({ title: '', content: '', category: 'general', tags: '' });
    setOpen(false);
    load();
  };

  const CATEGORIES = {
    policy: 'Politika',
    service: 'Hizmet',
    sop: 'SOP',
    general: 'Genel',
  };

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1400px]" data-testid="knowledge-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A]">Bilgi Bankasi</h1>
          <p className="text-[#7e7e8a] text-sm mt-1">{items.length} bilgi ogesi</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="bg-[#C4972A] hover:bg-[#a87a1f] text-white" data-testid="add-knowledge-btn">
              <Plus className="w-4 h-4 mr-2" /> Bilgi Ekle
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-[#1a1a22] border-[#C4972A]/20">
            <DialogHeader><DialogTitle className="text-[#C4972A]">Yeni Bilgi</DialogTitle></DialogHeader>
            <div className="space-y-3">
              <Input placeholder="Baslik *" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })}
                className="bg-white/5 border-white/10" data-testid="knowledge-title-input" />
              <textarea placeholder="Icerik *" value={form.content} onChange={e => setForm({ ...form, content: e.target.value })}
                className="w-full min-h-[100px] p-3 rounded-md bg-white/5 border border-white/10 text-sm resize-none focus:border-[#C4972A]/50 focus:outline-none" />
              <Input placeholder="Etiketler (virgul ile)" value={form.tags} onChange={e => setForm({ ...form, tags: e.target.value })}
                className="bg-white/5 border-white/10" />
              <Button onClick={handleCreate} className="w-full bg-[#C4972A] hover:bg-[#a87a1f]" data-testid="save-knowledge-btn">Kaydet</Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#7e7e8a]" />
        <Input placeholder="Bilgi ara..." value={search} onChange={e => setSearch(e.target.value)}
          className="pl-10 bg-white/5 border-white/10" data-testid="knowledge-search" />
      </div>

      <div className="space-y-3">
        {items.map(item => (
          <div key={item.id} className="glass rounded-xl p-5 hover:gold-glow transition-all" data-testid={`knowledge-${item.id}`}>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="font-semibold text-[#e5e5e8]">{item.title}</h3>
                <p className="text-sm text-[#a9a9b2] mt-2 whitespace-pre-wrap">{item.content}</p>
                <div className="flex items-center gap-2 mt-3">
                  <Badge className="bg-[#C4972A]/20 text-[#C4972A] text-xs">{CATEGORIES[item.category] || item.category}</Badge>
                  {(item.tags || []).map((tag, i) => (
                    <span key={i} className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-[#7e7e8a]">{tag}</span>
                  ))}
                </div>
              </div>
              <button onClick={() => { deleteKnowledge(item.id).then(load); }} className="text-[#7e7e8a] hover:text-red-400 ml-3">
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
        {items.length === 0 && !loading && (
          <div className="text-center py-12 text-[#7e7e8a]">
            <BookOpen className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>Bilgi bulunamadi</p>
          </div>
        )}
      </div>
    </div>
  );
}
