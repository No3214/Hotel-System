import React, { useState, useEffect } from 'react';
import { getTasks, createTask, updateTask, deleteTask } from '../api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { CheckSquare, Plus, Trash2, Clock, AlertCircle } from 'lucide-react';

const PRIORITY_COLORS = {
  low: 'bg-gray-500/20 text-gray-400',
  normal: 'bg-blue-500/20 text-blue-400',
  high: 'bg-orange-500/20 text-orange-400',
  urgent: 'bg-red-500/20 text-red-400',
};

const STATUS_COLORS = {
  pending: 'bg-yellow-500/20 text-yellow-400',
  in_progress: 'bg-blue-500/20 text-blue-400',
  completed: 'bg-green-500/20 text-green-400',
  cancelled: 'bg-gray-500/20 text-gray-400',
};

export default function TasksPage() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ title: '', description: '', priority: 'normal', assignee_role: '' });

  const [aiText, setAiText] = useState('');
  const [aiLoading, setAiLoading] = useState(false);

  const load = () => {
    const params = filter !== 'all' ? { status: filter } : {};
    getTasks(params).then(r => setTasks(r.data.tasks)).catch(console.error).finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [filter]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleCreate = async () => {
    if (!form.title) return;
    await createTask(form);
    setForm({ title: '', description: '', priority: 'normal', assignee_role: '' });
    setOpen(false);
    load();
  };

  const handleAIAutoAssign = async () => {
    if (!aiText) return;
    setAiLoading(true);
    try {
      await api.post('/tasks/ai-auto-assign', { text: aiText });
      setAiText('');
      load();
    } catch(e) {
      alert("AI Görev atarken hata oluştu!");
    } finally {
      setAiLoading(false);
    }
  };

  const handleStatusChange = async (id, status) => {
    await updateTask(id, { status });
    load();
  };

  const handleDelete = async (id) => {
    await deleteTask(id);
    load();
  };

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1400px]" data-testid="tasks-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A]">Gorevler</h1>
          <p className="text-[#7e7e8a] text-sm mt-1">{tasks.length} gorev</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="bg-[#C4972A] hover:bg-[#a87a1f] text-white" data-testid="add-task-btn">
              <Plus className="w-4 h-4 mr-2" /> Gorev Ekle
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-[#1a1a22] border-[#C4972A]/20">
            <DialogHeader><DialogTitle className="text-[#C4972A]">Yeni Gorev</DialogTitle></DialogHeader>
            <div className="space-y-3">
              <Input placeholder="Gorev basligi *" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })}
                className="bg-white/5 border-white/10" data-testid="task-title-input" />
              <Input placeholder="Aciklama" value={form.description} onChange={e => setForm({ ...form, description: e.target.value })}
                className="bg-white/5 border-white/10" />
              <Select value={form.priority} onValueChange={v => setForm({ ...form, priority: v })}>
                <SelectTrigger className="bg-white/5 border-white/10"><SelectValue /></SelectTrigger>
                <SelectContent className="bg-[#1a1a22] border-[#C4972A]/20">
                  <SelectItem value="low">Dusuk</SelectItem>
                  <SelectItem value="normal">Normal</SelectItem>
                  <SelectItem value="high">Yuksek</SelectItem>
                  <SelectItem value="urgent">Acil</SelectItem>
                </SelectContent>
              </Select>
              <Input placeholder="Atanan rol (mutfak/resepsiyon/kat)" value={form.assignee_role} onChange={e => setForm({ ...form, assignee_role: e.target.value })}
                className="bg-white/5 border-white/10" />
              <Button onClick={handleCreate} className="w-full bg-[#C4972A] hover:bg-[#a87a1f]" data-testid="save-task-btn">Kaydet</Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* AI Smart Input */}
      <div className="glass rounded-xl p-4 md:p-6 mb-6">
         <div className="flex flex-col md:flex-row gap-4 items-center">
            <div className="w-12 h-12 rounded-full bg-indigo-500/20 flex items-center justify-center flex-shrink-0">
               <AlertCircle className="w-6 h-6 text-indigo-400" />
            </div>
            <div className="flex-1 w-full">
               <h3 className="text-[#e5e5e8] font-medium mb-1">Akıllı Görev Bildirimi</h3>
               <p className="text-[#7e7e8a] text-sm mb-3">Arıza veya sorunu sadece metin olarak yazın, Yapay Zeka anlasın ve doğru departmana Aciliyet koduyla atasın.</p>
               <div className="flex gap-2">
                  <Input 
                     placeholder='Örn: "201 Nolu odada klima su akıtıyor, hızlı müdahale lazım"' 
                     value={aiText} 
                     onChange={e => setAiText(e.target.value)} 
                     className="bg-[#1a1a22] border-indigo-500/30 flex-1"
                     onKeyDown={(e) => e.key === 'Enter' && handleAIAutoAssign()}
                  />
                  <Button onClick={handleAIAutoAssign} disabled={aiLoading || !aiText} className="bg-indigo-600 hover:bg-indigo-700 text-white whitespace-nowrap">
                     {aiLoading ? 'İşleniyor...' : 'AI Analiz & Ata'}
                  </Button>
               </div>
            </div>
         </div>
      </div>

      {/* Filters */}
      <div className="flex gap-2 flex-wrap">
        {['all', 'pending', 'in_progress', 'completed'].map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded-full text-xs transition-all ${
              filter === f ? 'bg-[#C4972A]/20 text-[#C4972A]' : 'bg-white/5 text-[#7e7e8a] hover:bg-white/10'
            }`}
            data-testid={`filter-${f}`}
          >
            {f === 'all' ? 'Tumu' : f === 'pending' ? 'Bekleyen' : f === 'in_progress' ? 'Devam Eden' : 'Tamamlanan'}
          </button>
        ))}
      </div>

      {/* Task List */}
      <div className="space-y-3">
        {tasks.map(task => (
          <div key={task.id} className="glass rounded-xl p-4 hover:gold-glow transition-all" data-testid={`task-${task.id}`}>
            <div className="flex items-start gap-3">
              <button
                onClick={() => handleStatusChange(task.id, task.status === 'completed' ? 'pending' : 'completed')}
                className={`w-5 h-5 rounded border-2 flex-shrink-0 mt-0.5 flex items-center justify-center transition-all ${
                  task.status === 'completed' ? 'bg-[#C4972A] border-[#C4972A]' : 'border-[#7e7e8a] hover:border-[#C4972A]'
                }`}
              >
                {task.status === 'completed' && <CheckSquare className="w-3 h-3 text-white" />}
              </button>
              <div className="flex-1 min-w-0">
                <p className={`font-medium ${task.status === 'completed' ? 'line-through text-[#7e7e8a]' : ''}`}>{task.title}</p>
                {task.description && <p className="text-xs text-[#7e7e8a] mt-1">{task.description}</p>}
                <div className="flex items-center gap-2 mt-2">
                  <Badge className={PRIORITY_COLORS[task.priority]}>{task.priority}</Badge>
                  <Badge className={STATUS_COLORS[task.status]}>{task.status}</Badge>
                  {task.assignee_role && <span className="text-xs text-[#7e7e8a]">{task.assignee_role}</span>}
                  {task.source && <span className="text-xs text-[#C4972A]/50">{task.source}</span>}
                </div>
              </div>
              <button onClick={() => handleDelete(task.id)} className="text-[#7e7e8a] hover:text-red-400 transition-colors">
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
        {tasks.length === 0 && !loading && (
          <div className="text-center py-12 text-[#7e7e8a]">
            <CheckSquare className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>Gorev bulunamadi</p>
          </div>
        )}
      </div>
    </div>
  );
}
