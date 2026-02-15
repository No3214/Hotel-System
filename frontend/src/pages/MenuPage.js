import React, { useState, useEffect } from 'react';
import { getMenu } from '../api';
import { UtensilsCrossed, Coffee, Wine, Beer } from 'lucide-react';

const CATEGORY_LABELS = {
  kahvalti: 'Kahvalti',
  baslangic: 'Baslangiclar',
  meze: 'Mezeler',
  ana_yemek: 'Ana Yemekler',
  pizza_sandvic: 'Pizza & Sandvic',
  tatli: 'Tatlilar',
  sicak_icecekler: 'Sicak Icecekler',
  soguk_icecekler: 'Soguk Icecekler',
  sarap: 'Saraplar',
  bira: 'Biralar',
  raki: 'Raki',
  viski: 'Viskiler',
};

const CATEGORY_ICONS = {
  kahvalti: UtensilsCrossed,
  sicak_icecekler: Coffee,
  soguk_icecekler: Coffee,
  sarap: Wine,
  bira: Beer,
  raki: Wine,
  viski: Wine,
};

export default function MenuPage() {
  const [menu, setMenu] = useState(null);
  const [restaurant, setRestaurant] = useState('');
  const [activeCategory, setActiveCategory] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMenu()
      .then(r => {
        setMenu(r.data.menu);
        setRestaurant(r.data.restaurant);
        const firstCat = Object.keys(r.data.menu)[0];
        setActiveCategory(firstCat);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading || !menu) {
    return <div className="p-8"><div className="h-8 w-48 bg-white/5 rounded animate-pulse" /></div>;
  }

  const categories = Object.keys(menu);

  return (
    <div className="p-6 lg:p-8 max-w-[1400px]" data-testid="menu-page">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl lg:text-4xl font-bold text-[#C4972A]">{restaurant}</h1>
        <p className="text-[#7e7e8a] mt-2">Kozbeyli Konagi Restoran Menusu</p>
        <div className="w-24 h-0.5 bg-[#C4972A]/50 mx-auto mt-4" />
      </div>

      {/* Category Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-3 mb-6 scrollbar-thin">
        {categories.map(cat => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`px-4 py-2 rounded-full text-xs font-medium whitespace-nowrap transition-all ${
              activeCategory === cat
                ? 'bg-[#C4972A] text-white'
                : 'bg-white/5 text-[#7e7e8a] hover:bg-white/10'
            }`}
            data-testid={`menu-cat-${cat}`}
          >
            {CATEGORY_LABELS[cat] || cat}
          </button>
        ))}
      </div>

      {/* Menu Items */}
      {activeCategory && (
        <div className="space-y-3">
          <h2 className="text-xl font-semibold text-[#C4972A] mb-4">{CATEGORY_LABELS[activeCategory]}</h2>
          {menu[activeCategory].map((item, i) => (
            <div key={i} className="glass rounded-xl p-4 flex items-center justify-between hover:gold-glow transition-all" data-testid={`menu-item-${i}`}>
              <div className="flex-1 mr-4">
                <h3 className="font-medium text-[#e5e5e8]">{item.name}</h3>
                {item.desc && <p className="text-xs text-[#7e7e8a] mt-1">{item.desc}</p>}
              </div>
              <div className="text-right flex-shrink-0">
                <span className="text-lg font-bold text-[#C4972A]">{item.price_try}</span>
                <span className="text-xs text-[#7e7e8a] ml-1">TL</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
