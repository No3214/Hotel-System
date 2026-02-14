import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, Clock, AlertCircle, ChevronRight } from 'lucide-react';
import { listTasks, updateTaskStatus } from '../api';

const TasksPage = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    fetchTasks();
  }, [filterStatus]);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const params = filterStatus !== 'all' ? { status: filterStatus } : {};
      const data = await listTasks(params);
      setTasks(data.tasks || []);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (taskId, newStatus) => {
    try {
      await updateTaskStatus(taskId, newStatus);
      // Update local state
      setTasks(prev => prev.map(task => 
        task.id === taskId ? { ...task, status: newStatus } : task
      ));
    } catch (error) {
      console.error('Error updating task status:', error);
    }
  };

  const getPriorityColor = (priority) => {
    const colors = {
      urgent: 'text-red-400 bg-red-500/10 border-red-500/20',
      high: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
      normal: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
      low: 'text-gray-400 bg-gray-500/10 border-gray-500/20'
    };
    return colors[priority] || colors.normal;
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-5 h-5 text-emerald-400" />;
      case 'in_progress': return <Clock className="w-5 h-5 text-blue-400 animate-pulse" />;
      case 'pending': return <Clock className="w-5 h-5 text-amber-400" />;
      default: return <AlertCircle className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusLabel = (status) => {
    const labels = {
      pending: 'Bekliyor',
      in_progress: 'Devam Ediyor',
      completed: 'Tamamlandı',
      cancelled: 'İptal'
    };
    return labels[status] || status;
  };

  return (
    <div className="p-6 max-w-7xl mx-auto" data-testid="tasks-page">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-4xl font-heading font-bold mb-2">Görevler</h1>
        <p className="text-gray-400">Dokümanlardan otomatik oluşturulan ve manuel görevler</p>
      </motion.div>

      {/* Filters */}
      <div className="bg-bg-surface border border-white/5 rounded-xl p-6 mb-6">
        <div className="flex flex-wrap items-center gap-3">
          <span className="text-sm text-gray-400">Durum:</span>
          {['all', 'pending', 'in_progress', 'completed'].map(status => (
            <button
              key={status}
              onClick={() => setFilterStatus(status)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                filterStatus === status
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white/5 text-gray-400 hover:bg-white/10'
              }`}
              data-testid={`filter-${status}`}
            >
              {status === 'all' ? 'Tümü' :
               status === 'pending' ? 'Bekliyor' :
               status === 'in_progress' ? 'Devam Ediyor' :
               'Tamamlandı'}
            </button>
          ))}
        </div>
      </div>

      {/* Tasks List */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
        </div>
      ) : tasks.length === 0 ? (
        <div className="bg-bg-surface border border-white/5 rounded-xl p-12 text-center">
          <CheckCircle className="w-16 h-16 mx-auto mb-4 text-gray-600" />
          <h3 className="text-xl font-semibold mb-2">Görev bulunamadı</h3>
          <p className="text-gray-400">Henüz hiç görev oluşturulmadı.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {tasks.map((task, index) => (
            <motion.div
              key={task.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className="bg-bg-surface border border-white/5 rounded-xl p-6 card-hover"
              data-testid="task-item"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4 flex-1">
                  {getStatusIcon(task.status)}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold">{task.title}</h3>
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${getPriorityColor(task.priority)}`}>
                        {task.priority === 'urgent' ? 'Acil' :
                         task.priority === 'high' ? 'Yüksek' :
                         task.priority === 'normal' ? 'Normal' : 'Düşük'}
                      </span>
                    </div>

                    {task.description && (
                      <p className="text-gray-400 text-sm mb-3">{task.description}</p>
                    )}

                    <div className="flex flex-wrap items-center gap-4 text-xs text-gray-500">
                      {task.assignee_role && (
                        <span>Sorumlu: <span className="text-white">{task.assignee_role}</span></span>
                      )}
                      {task.due_date && (
                        <span>Teslim: <span className="text-white">
                          {new Date(task.due_date).toLocaleDateString('tr-TR')}
                        </span></span>
                      )}
                      <span>Kaynak: <span className="text-white">{task.source === 'ai' ? 'AI' : 'Manuel'}</span></span>
                    </div>
                  </div>
                </div>

                {/* Status Actions */}
                <div className="flex items-center space-x-2">
                  {task.status === 'pending' && (
                    <button
                      onClick={() => handleStatusChange(task.id, 'in_progress')}
                      className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium transition-all"
                      data-testid="btn-start-task"
                    >
                      Başlat
                    </button>
                  )}
                  {task.status === 'in_progress' && (
                    <button
                      onClick={() => handleStatusChange(task.id, 'completed')}
                      className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 rounded-lg text-sm font-medium transition-all"
                      data-testid="btn-complete-task"
                    >
                      Tamamla
                    </button>
                  )}
                  <ChevronRight className="w-5 h-5 text-gray-600" />
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TasksPage;
