import React, { useState, useEffect } from 'react';
import { getGuests, createGuest } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Users, Plus, Search, Phone, Mail, Globe } from 'lucide-react';

export default function GuestsPage() {
  const [guests, setGuests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ name: '', email: '', phone: '', nationality: '', notes: '' });

  const load = () => {
    getGuests({ search: search || undefined })
      .then(r => setGuests(r.data.guests))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [search]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleCreate = async () => {
    if (!form.name) return;
    await createGuest(form);
    setForm({ name: '', email: '', phone: '', nationality: '', notes: '' });
    setOpen(false);
    load();
  };

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1400px]" data-testid="guests-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A]">Misafirler</h1>
          <p className="text-[#7e7e8a] text-sm mt-1">{guests.length} kayitli misafir</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="bg-[#C4972A] hover:bg-[#a87a1f] text-white" data-testid="add-guest-btn">
              <Plus className="w-4 h-4 mr-2" /> Misafir Ekle
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-[#1a1a22] border-[#C4972A]/20">
            <DialogHeader>
              <DialogTitle className="text-[#C4972A]">Yeni Misafir</DialogTitle>
            </DialogHeader>
            <div className="space-y-3">
              <Input placeholder="Ad Soyad *" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })}
                className="bg-white/5 border-white/10" data-testid="guest-name-input" />
              <Input placeholder="E-posta" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })}
                className="bg-white/5 border-white/10" />
              <Input placeholder="Telefon" value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })}
                className="bg-white/5 border-white/10" />
              <Input placeholder="Uyruk" value={form.nationality} onChange={e => setForm({ ...form, nationality: e.target.value })}
                className="bg-white/5 border-white/10" />
              <Input placeholder="Notlar" value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })}
                className="bg-white/5 border-white/10" />
              <Button onClick={handleCreate} className="w-full bg-[#C4972A] hover:bg-[#a87a1f]" data-testid="save-guest-btn">
                Kaydet
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#7e7e8a]" />
        <Input
          placeholder="Misafir ara..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="pl-10 bg-white/5 border-white/10"
          data-testid="guest-search"
        />
      </div>

      {/* Guest List */}
      <div className="space-y-3">
        {guests.map(g => (
          <div key={g.id} className="glass rounded-xl p-4 flex items-center gap-4 hover:gold-glow transition-all" data-testid={`guest-${g.id}`}>
            <div className="w-10 h-10 rounded-full bg-[#C4972A]/20 flex items-center justify-center text-[#C4972A] font-bold">
              {g.name?.[0] || '?'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-medium truncate">{g.name}</p>
              <div className="flex items-center gap-3 text-xs text-[#7e7e8a]">
                {g.phone && <span className="flex items-center gap-1"><Phone className="w-3 h-3" />{g.phone}</span>}
                {g.email && <span className="flex items-center gap-1"><Mail className="w-3 h-3" />{g.email}</span>}
                {g.nationality && <span className="flex items-center gap-1"><Globe className="w-3 h-3" />{g.nationality}</span>}
              </div>
            </div>
            {g.vip && <Badge className="bg-[#C4972A]/20 text-[#C4972A]">VIP</Badge>}
          </div>
        ))}
        {guests.length === 0 && !loading && (
          <div className="text-center py-12 text-[#7e7e8a]">
            <Users className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>Henuz misafir kaydi yok</p>
          </div>
        )}
      </div>
    </div>
  );
}
