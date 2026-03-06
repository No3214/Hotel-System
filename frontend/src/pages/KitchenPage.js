import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  getKitchenOrders, createKitchenOrder, updateKitchenOrderStatus, 
  cancelKitchenOrder, getKitchenSummary, getKitchenNotifications, getKitchenAIForecast 
} from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { 
  ChefHat, Plus, Clock, AlertTriangle, CheckCircle, 
  XCircle, Play, Bell, Package, Users, Utensils, 
  Coffee, Moon, RefreshCw, Trash2, Eye, Sparkles, Loader2
} from 'lucide-react';

const STATUS_CONFIG = {
  pending: { label: 'Bekliyor', color: 'bg-yellow-500/20 text-yellow-400', icon: Clock },
  preparing: { label: 'Hazirlaniyor', color: 'bg-blue-500/20 text-blue-400', icon: Play },
  ready: { label: 'Hazir', color: 'bg-green-500/20 text-green-400', icon: CheckCircle },
  served: { label: 'Servis Edildi', color: 'bg-purple-500/20 text-purple-400', icon: Users },
  cancelled: { label: 'Iptal', color: 'bg-red-500/20 text-red-400', icon: XCircle },
};

const ORDER_TYPE_CONFIG = {
  room_service: { label: 'Oda Servisi', icon: Coffee },
  restaurant: { label: 'Restoran', icon: Utensils },
  event: { label: 'Etkinlik', icon: Users },
  takeaway: { label: 'Paket', icon: Package },
};

const PRIORITY_CONFIG = {
  low: { label: 'Dusuk', color: 'text-gray-400' },
  normal: { label: 'Normal', color: 'text-white' },
  high: { label: 'Yuksek', color: 'text-orange-400' },
  urgent: { label: 'Acil', color: 'text-red-400' },
};

export default function KitchenPage() {
  const [orders, setOrders] = useState([]);
  const [stats, setStats] = useState({});
  const [notifications, setNotifications] = useState({ urgent: [], delayed: [] });
  const [loading, setLoading] = useState(true);
  const [aiForecast, setAiForecast] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [filter, setFilter] = useState('active');
  const [open, setOpen] = useState(false);
  const [detailOrder, setDetailOrder] = useState(null);
  const [form, setForm] = useState({
    order_type: 'restaurant',
    items: [{ name: '', quantity: 1, notes: '' }],
    table_number: '',
    room_number: '',
    guest_name: '',
    special_notes: '',
    priority: 'normal',
  });

  const load = useCallback(async () => {
    try {
      const [ordersRes, notifRes] = await Promise.all([
        getKitchenOrders({ status: filter }),
        getKitchenNotifications(),
      ]);
      setOrders(ordersRes.data.orders);
      setStats(ordersRes.data.stats);
      setNotifications(notifRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => { load(); }, [load]);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(load, 30000);
    return () => clearInterval(interval);
  }, [load]);

  const handleCreate = async () => {
    const validItems = form.items.filter(i => i.name.trim());
    if (validItems.length === 0) return;

    await createKitchenOrder({
      ...form,
      items: validItems,
      table_number: form.table_number ? parseInt(form.table_number) : null,
    });
    setForm({
      order_type: 'restaurant',
      items: [{ name: '', quantity: 1, notes: '' }],
      table_number: '',
      room_number: '',
      guest_name: '',
      special_notes: '',
      priority: 'normal',
    });
    setOpen(false);
    load();
  };

  const handleStatusChange = async (orderId, newStatus) => {
    await updateKitchenOrderStatus(orderId, { status: newStatus });
    load();
  };

  const handleCancel = async (orderId) => {
    if (window.confirm('Siparisi iptal etmek istediginize emin misiniz?')) {
      await cancelKitchenOrder(orderId);
      load();
    }
  };

  const loadAiForecast = async () => {
    setAiLoading(true);
    try {
      const res = await getKitchenAIForecast();
      if (res.data.success) {
        setAiForecast(res.data.forecast);
      }
    } catch (e) {
      console.error(e);
      alert('AI Tahminlemesi su an kullanilamiyor.');
    }
    setAiLoading(false);
  };

  const addItem = () => {
    setForm({ ...form, items: [...form.items, { name: '', quantity: 1, notes: '' }] });
  };

  const updateItem = (index, field, value) => {
    const newItems = [...form.items];
    newItems[index][field] = value;
    setForm({ ...form, items: newItems });
  };

  const removeItem = (index) => {
    if (form.items.length > 1) {
      setForm({ ...form, items: form.items.filter((_, i) => i !== index) });
    }
  };

  const getNextStatus = (currentStatus) => {
    const flow = { pending: 'preparing', preparing: 'ready', ready: 'served' };
    return flow[currentStatus];
  };

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1600px]" data-testid="kitchen-page">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A] flex items-center gap-3">
            <ChefHat className="w-8 h-8" />
            Mutfak Dashboard
          </h1>
          <p className="text-[#7e7e8a] text-sm mt-1">Siparis yonetimi ve hazirlik takibi</p>
        </div>
        <div className="flex items-center gap-3">
          <Button onClick={load} variant="outline" className="border-[#C4972A]/30 text-[#C4972A]" data-testid="refresh-btn">
            <RefreshCw className="w-4 h-4 mr-2" /> Yenile
          </Button>
          <Button onClick={loadAiForecast} disabled={aiLoading} className="bg-emerald-600 hover:bg-emerald-500 text-white" data-testid="ai-forecast-btn">
            {aiLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Sparkles className="w-4 h-4 mr-2" />}
            AI Tahmin
          </Button>
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <Button className="bg-[#C4972A] hover:bg-[#a87a1f] text-white" data-testid="new-order-btn">
                <Plus className="w-4 h-4 mr-2" /> Yeni Siparis
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-[#1a1a22] border-[#C4972A]/20 max-w-lg max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle className="text-[#C4972A]">Yeni Siparis</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                {/* Order Type */}
                <div>
                  <label className="text-xs text-[#7e7e8a] mb-2 block">Siparis Turu</label>
                  <div className="grid grid-cols-2 gap-2">
                    {Object.entries(ORDER_TYPE_CONFIG).map(([key, { label, icon: Icon }]) => (
                      <button
                        key={key}
                        onClick={() => setForm({ ...form, order_type: key })}
                        className={`p-3 rounded-lg border transition-all flex items-center gap-2 ${
                          form.order_type === key 
                            ? 'border-[#C4972A] bg-[#C4972A]/10 text-[#C4972A]' 
                            : 'border-white/10 text-[#7e7e8a] hover:border-white/20'
                        }`}
                      >
                        <Icon className="w-4 h-4" />
                        <span className="text-sm">{label}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Location Info */}
                <div className="grid grid-cols-2 gap-3">
                  {form.order_type === 'restaurant' && (
                    <Input
                      placeholder="Masa No"
                      value={form.table_number}
                      onChange={e => setForm({ ...form, table_number: e.target.value })}
                      className="bg-white/5 border-white/10"
                      data-testid="table-number-input"
                    />
                  )}
                  {form.order_type === 'room_service' && (
                    <Input
                      placeholder="Oda No"
                      value={form.room_number}
                      onChange={e => setForm({ ...form, room_number: e.target.value })}
                      className="bg-white/5 border-white/10"
                      data-testid="room-number-input"
                    />
                  )}
                  <Input
                    placeholder="Misafir Adi"
                    value={form.guest_name}
                    onChange={e => setForm({ ...form, guest_name: e.target.value })}
                    className="bg-white/5 border-white/10"
                    data-testid="guest-name-input"
                  />
                </div>

                {/* Priority */}
                <div>
                  <label className="text-xs text-[#7e7e8a] mb-2 block">Oncelik</label>
                  <div className="flex gap-2">
                    {Object.entries(PRIORITY_CONFIG).map(([key, { label, color }]) => (
                      <button
                        key={key}
                        onClick={() => setForm({ ...form, priority: key })}
                        className={`px-3 py-1.5 rounded-lg border transition-all text-sm ${
                          form.priority === key 
                            ? `border-[#C4972A] bg-[#C4972A]/10 ${color}` 
                            : 'border-white/10 text-[#7e7e8a]'
                        }`}
                      >
                        {label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Items */}
                <div>
                  <label className="text-xs text-[#7e7e8a] mb-2 block">Urunler</label>
                  <div className="space-y-2">
                    {form.items.map((item, idx) => (
                      <div key={idx} className="flex gap-2">
                        <Input
                          placeholder="Urun adi"
                          value={item.name}
                          onChange={e => updateItem(idx, 'name', e.target.value)}
                          className="flex-1 bg-white/5 border-white/10"
                          data-testid={`item-name-${idx}`}
                        />
                        <Input
                          type="number"
                          min="1"
                          value={item.quantity}
                          onChange={e => updateItem(idx, 'quantity', parseInt(e.target.value) || 1)}
                          className="w-16 bg-white/5 border-white/10 text-center"
                          data-testid={`item-qty-${idx}`}
                        />
                        <Input
                          placeholder="Not"
                          value={item.notes}
                          onChange={e => updateItem(idx, 'notes', e.target.value)}
                          className="w-24 bg-white/5 border-white/10"
                        />
                        {form.items.length > 1 && (
                          <button onClick={() => removeItem(idx)} className="text-red-400 hover:text-red-300">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    ))}
                    <Button variant="ghost" size="sm" onClick={addItem} className="text-[#C4972A]">
                      <Plus className="w-4 h-4 mr-1" /> Urun Ekle
                    </Button>
                  </div>
                </div>

                {/* Special Notes */}
                <textarea
                  placeholder="Ozel notlar (alerji, tercihler vb.)"
                  value={form.special_notes}
                  onChange={e => setForm({ ...form, special_notes: e.target.value })}
                  className="w-full p-3 rounded-lg bg-white/5 border border-white/10 text-sm min-h-[60px] resize-none focus:border-[#C4972A]/50 focus:outline-none"
                />

                <Button onClick={handleCreate} className="w-full bg-[#C4972A] hover:bg-[#a87a1f]" data-testid="submit-order-btn">
                  Siparis Olustur
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Notifications */}
      {(notifications.urgent_count > 0 || notifications.delayed_count > 0) && (
        <motion.div 
          initial={{ opacity: 0, y: -10 }} 
          animate={{ opacity: 1, y: 0 }}
          className="bg-red-500/10 border border-red-500/30 rounded-xl p-4"
        >
          <div className="flex items-center gap-2 text-red-400 mb-2">
            <Bell className="w-5 h-5" />
            <span className="font-semibold">Dikkat!</span>
          </div>
          <div className="flex flex-wrap gap-4 text-sm">
            {notifications.urgent_count > 0 && (
              <span className="text-red-300">{notifications.urgent_count} acil siparis bekliyor</span>
            )}
            {notifications.delayed_count > 0 && (
              <span className="text-orange-300">{notifications.delayed_count} siparis 15+ dakikadir bekliyor</span>
            )}
          </div>
        </motion.div>
      )}

      {/* AI Forecast Panel */}
      <AnimatePresence>
        {aiForecast && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-emerald-900/10 border border-emerald-500/20 rounded-xl p-6 overflow-hidden relative"
          >
            <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/5 rounded-full blur-3xl -mr-10 -mt-10" />
            
            <div className="flex justify-between items-start mb-4 relative z-10">
              <div className="flex items-center gap-2 text-emerald-400">
                <Sparkles className="w-5 h-5" />
                <h3 className="font-semibold text-lg">Smart Kitchen : Yarin Icin Ozet</h3>
              </div>
              <button onClick={() => setAiForecast(null)} className="text-[#7e7e8a] hover:text-white">
                <XCircle className="w-5 h-5" />
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10 text-sm">
              <div className="space-y-2">
                <h4 className="text-emerald-500 font-medium">Genel Tahmin</h4>
                <p className="text-[#e5e5e8] leading-relaxed">{aiForecast.summary}</p>
              </div>
              <div className="space-y-2">
                <h4 className="text-emerald-500 font-medium">En Cok İstenmesi Beklenenler</h4>
                <div className="flex flex-wrap gap-2">
                  {aiForecast.top_predicted?.map((item, i) => (
                    <Badge key={i} className="bg-emerald-500/10 text-emerald-400 border-none">
                      {item}
                    </Badge>
                  ))}
                </div>
              </div>
              <div className="space-y-2">
                <h4 className="text-emerald-500 font-medium">Hazırlık & İsrafı Önleme</h4>
                <p className="text-[#e5e5e8] leading-relaxed">{aiForecast.prep_suggestions}</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-yellow-500/20">
              <Clock className="w-5 h-5 text-yellow-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-[#e5e5e8]">{stats.pending || 0}</p>
              <p className="text-xs text-[#7e7e8a]">Bekliyor</p>
            </div>
          </div>
        </div>
        <div className="glass rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-blue-500/20">
              <Play className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-[#e5e5e8]">{stats.preparing || 0}</p>
              <p className="text-xs text-[#7e7e8a]">Hazirlaniyor</p>
            </div>
          </div>
        </div>
        <div className="glass rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-green-500/20">
              <CheckCircle className="w-5 h-5 text-green-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-[#e5e5e8]">{stats.ready || 0}</p>
              <p className="text-xs text-[#7e7e8a]">Hazir</p>
            </div>
          </div>
        </div>
        <div className="glass rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-purple-500/20">
              <Package className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-[#e5e5e8]">{stats.today_total || 0}</p>
              <p className="text-xs text-[#7e7e8a]">Bugunku Toplam</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {[
          { key: 'active', label: 'Aktif' },
          { key: 'pending', label: 'Bekliyor' },
          { key: 'preparing', label: 'Hazirlaniyor' },
          { key: 'ready', label: 'Hazir' },
          { key: 'served', label: 'Servis Edildi' },
        ].map(f => (
          <button
            key={f.key}
            onClick={() => setFilter(f.key)}
            className={`px-4 py-2 rounded-lg text-sm whitespace-nowrap transition-all ${
              filter === f.key
                ? 'bg-[#C4972A] text-white'
                : 'bg-white/5 text-[#7e7e8a] hover:bg-white/10'
            }`}
            data-testid={`filter-${f.key}`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Orders Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <AnimatePresence>
          {orders.map(order => {
            const statusConfig = STATUS_CONFIG[order.status];
            const typeConfig = ORDER_TYPE_CONFIG[order.order_type];
            const priorityConfig = PRIORITY_CONFIG[order.priority];
            const StatusIcon = statusConfig?.icon || Clock;
            const TypeIcon = typeConfig?.icon || Utensils;
            const nextStatus = getNextStatus(order.status);

            return (
              <motion.div
                key={order.id}
                layout
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className={`glass rounded-xl p-4 border-l-4 ${
                  order.priority === 'urgent' ? 'border-l-red-500' :
                  order.priority === 'high' ? 'border-l-orange-500' :
                  'border-l-[#C4972A]/50'
                }`}
                data-testid={`order-${order.id}`}
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className="p-2 rounded-lg bg-white/5">
                      <TypeIcon className="w-4 h-4 text-[#C4972A]" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-[#e5e5e8]">
                        {order.table_number ? `Masa ${order.table_number}` : 
                         order.room_number ? `Oda ${order.room_number}` : 
                         typeConfig?.label}
                      </p>
                      <p className="text-xs text-[#7e7e8a]">{order.guest_name || 'Misafir'}</p>
                    </div>
                  </div>
                  <Badge className={statusConfig?.color}>
                    <StatusIcon className="w-3 h-3 mr-1" />
                    {statusConfig?.label}
                  </Badge>
                </div>

                {/* Items */}
                <div className="space-y-1 mb-3">
                  {order.items?.slice(0, 4).map((item, idx) => (
                    <div key={idx} className="flex items-center justify-between text-sm">
                      <span className="text-[#a9a9b2]">
                        {item.quantity}x {item.name}
                        {item.notes && <span className="text-xs text-[#7e7e8a] ml-1">({item.notes})</span>}
                      </span>
                    </div>
                  ))}
                  {order.items?.length > 4 && (
                    <p className="text-xs text-[#7e7e8a]">+{order.items.length - 4} daha...</p>
                  )}
                </div>

                {/* Special Notes */}
                {order.special_notes && (
                  <div className="bg-yellow-500/10 rounded-lg p-2 mb-3">
                    <p className="text-xs text-yellow-400">
                      <AlertTriangle className="w-3 h-3 inline mr-1" />
                      {order.special_notes}
                    </p>
                  </div>
                )}

                {/* Footer */}
                <div className="flex items-center justify-between pt-3 border-t border-white/5">
                  <div className="flex items-center gap-2 text-xs text-[#7e7e8a]">
                    <Clock className="w-3 h-3" />
                    {new Date(order.created_at).toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })}
                    <span className={priorityConfig?.color}>{priorityConfig?.label}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => setDetailOrder(order)}
                      className="p-1.5 rounded-lg hover:bg-white/5 text-[#7e7e8a] hover:text-[#C4972A]"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    {nextStatus && (
                      <Button
                        size="sm"
                        onClick={() => handleStatusChange(order.id, nextStatus)}
                        className="bg-[#C4972A]/20 hover:bg-[#C4972A]/30 text-[#C4972A] text-xs"
                        data-testid={`action-${order.id}`}
                      >
                        {nextStatus === 'preparing' ? 'Basla' :
                         nextStatus === 'ready' ? 'Hazir' :
                         nextStatus === 'served' ? 'Servis' : ''}
                      </Button>
                    )}
                    {order.status === 'pending' && (
                      <button
                        onClick={() => handleCancel(order.id)}
                        className="p-1.5 rounded-lg hover:bg-red-500/10 text-[#7e7e8a] hover:text-red-400"
                      >
                        <XCircle className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      {orders.length === 0 && !loading && (
        <div className="text-center py-16 text-[#7e7e8a]">
          <ChefHat className="w-16 h-16 mx-auto mb-4 opacity-30" />
          <p className="text-lg">Siparis bulunamadi</p>
          <p className="text-sm mt-1">Yeni siparis eklemek icin yukardaki butonu kullanin</p>
        </div>
      )}

      {/* Detail Modal */}
      <Dialog open={!!detailOrder} onOpenChange={() => setDetailOrder(null)}>
        <DialogContent className="bg-[#1a1a22] border-[#C4972A]/20 max-w-lg">
          <DialogHeader>
            <DialogTitle className="text-[#C4972A]">Siparis Detayi</DialogTitle>
          </DialogHeader>
          {detailOrder && (
            <div className="space-y-4 mt-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-[#7e7e8a]">Tur</p>
                  <p className="text-[#e5e5e8]">{ORDER_TYPE_CONFIG[detailOrder.order_type]?.label}</p>
                </div>
                <div>
                  <p className="text-xs text-[#7e7e8a]">Durum</p>
                  <Badge className={STATUS_CONFIG[detailOrder.status]?.color}>
                    {STATUS_CONFIG[detailOrder.status]?.label}
                  </Badge>
                </div>
                {detailOrder.table_number && (
                  <div>
                    <p className="text-xs text-[#7e7e8a]">Masa</p>
                    <p className="text-[#e5e5e8]">{detailOrder.table_number}</p>
                  </div>
                )}
                {detailOrder.room_number && (
                  <div>
                    <p className="text-xs text-[#7e7e8a]">Oda</p>
                    <p className="text-[#e5e5e8]">{detailOrder.room_number}</p>
                  </div>
                )}
                <div>
                  <p className="text-xs text-[#7e7e8a]">Misafir</p>
                  <p className="text-[#e5e5e8]">{detailOrder.guest_name || '-'}</p>
                </div>
                <div>
                  <p className="text-xs text-[#7e7e8a]">Olusturulma</p>
                  <p className="text-[#e5e5e8]">{new Date(detailOrder.created_at).toLocaleString('tr-TR')}</p>
                </div>
              </div>

              <div>
                <p className="text-xs text-[#7e7e8a] mb-2">Urunler</p>
                <div className="space-y-2">
                  {detailOrder.items?.map((item, idx) => (
                    <div key={idx} className="flex items-center justify-between bg-white/5 rounded-lg p-2">
                      <span className="text-[#e5e5e8]">{item.quantity}x {item.name}</span>
                      {item.notes && <span className="text-xs text-[#7e7e8a]">{item.notes}</span>}
                    </div>
                  ))}
                </div>
              </div>

              {detailOrder.special_notes && (
                <div className="bg-yellow-500/10 rounded-lg p-3">
                  <p className="text-xs text-[#7e7e8a] mb-1">Ozel Notlar</p>
                  <p className="text-yellow-400 text-sm">{detailOrder.special_notes}</p>
                </div>
              )}

              {detailOrder.status_history && (
                <div>
                  <p className="text-xs text-[#7e7e8a] mb-2">Durum Gecmisi</p>
                  <div className="space-y-1">
                    {detailOrder.status_history.map((h, idx) => (
                      <div key={idx} className="flex items-center justify-between text-xs">
                        <Badge className={STATUS_CONFIG[h.status]?.color} variant="outline">
                          {STATUS_CONFIG[h.status]?.label}
                        </Badge>
                        <span className="text-[#7e7e8a]">
                          {new Date(h.timestamp).toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
