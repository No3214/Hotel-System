import React, { useState, useEffect } from 'react';
import { getRooms } from '../api';
import { Badge } from '../components/ui/badge';
import { BedDouble, Users, Maximize2, Wifi, Wind, Tv } from 'lucide-react';

export default function RoomsPage() {
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getRooms()
      .then(r => setRooms(r.data.rooms))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="p-8 space-y-4">
        <div className="h-8 w-48 bg-white/5 rounded animate-pulse" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[...Array(4)].map((_, i) => <div key={i} className="h-64 bg-white/5 rounded-xl animate-pulse" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-[1400px]" data-testid="rooms-page">
      <div>
        <h1 className="text-2xl lg:text-3xl font-bold text-[#C4972A]">Odalar</h1>
        <p className="text-[#7e7e8a] text-sm mt-1">16 oda - 8 farkli tip</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {rooms.map((room) => (
          <div
            key={room.room_id}
            className="glass rounded-xl overflow-hidden hover:gold-glow transition-all duration-300"
            data-testid={`room-${room.room_id}`}
          >
            {/* Room header */}
            <div className="bg-gradient-to-r from-[#C4972A]/20 to-transparent p-5">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-[#C4972A]">{room.name_tr}</h3>
                  <p className="text-xs text-[#7e7e8a]">{room.name_en}</p>
                </div>
                <Badge className="bg-[#C4972A]/20 text-[#C4972A] border-[#C4972A]/30">
                  {room.count} oda
                </Badge>
              </div>
            </div>

            {/* Room details */}
            <div className="p-5 space-y-4">
              <p className="text-sm text-[#a9a9b2]">{room.description_tr}</p>

              <div className="flex items-center gap-4 text-sm">
                <div className="flex items-center gap-1.5 text-[#7e7e8a]">
                  <Users className="w-4 h-4" />
                  <span>{room.capacity} kisi</span>
                </div>
                <div className="flex items-center gap-1.5 text-[#7e7e8a]">
                  <Maximize2 className="w-4 h-4" />
                  <span>{room.size_m2} m2</span>
                </div>
              </div>

              {/* Features */}
              <div className="flex flex-wrap gap-2">
                {(room.features || []).slice(0, 5).map((f, i) => (
                  <span key={i} className="text-xs px-2 py-1 rounded-full bg-white/5 text-[#a9a9b2]">
                    {f}
                  </span>
                ))}
              </div>

              {/* Price */}
              <div className="flex items-center justify-between pt-3 border-t border-white/5">
                <div>
                  <span className="text-2xl font-bold text-[#C4972A]">{room.base_price_try?.toLocaleString('tr-TR')}</span>
                  <span className="text-sm text-[#7e7e8a] ml-1">TL / gece</span>
                </div>
                <div className="text-sm text-[#7e7e8a]">
                  {room.base_price_eur} EUR
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
