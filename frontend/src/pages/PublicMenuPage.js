import React, { useState, useEffect, useMemo, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

/* ─── Category Icons (SVG inline) ─── */
const icons = {
  utensils: <path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 002-2V2M7 2v20M21 15V2a5 5 0 00-5 5v6c0 1.1.9 2 2 2h3zm0 0v7"/>,
  'plus-circle': <><circle cx="12" cy="12" r="10"/><path d="M8 12h8M12 8v8"/></>,
  salad: <><path d="M7 21h10M12 21a9 9 0 009-9H3a9 9 0 009 9z"/><path d="M11.38 12a2.4 2.4 0 01-.4-4.77 2.4 2.4 0 013.2-2.77 2.4 2.4 0 014.09.52 2.4 2.4 0 01.93 4.6"/></>,
  pizza: <><circle cx="12" cy="12" r="10"/><path d="M15 11h.01M11 15h.01M16 16h.01"/></>,
  cheese: <path d="M2 12l5.5-9.5L22 7l-2 5-8.5 8.5L2 12zM10 16l2-5 5-2"/>,
  flame: <path d="M8.5 14.5A2.5 2.5 0 0011 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 11-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 002.5 2.5z"/>,
  soup: <><path d="M12 21a9 9 0 009-9H3a9 9 0 009 9z"/><path d="M7 21h10"/><path d="M9.5 4c0 .5.5 1 1.5 1s1.5-.5 1.5-1-.5-1-1.5-1-1.5.5-1.5 1z"/></>,
  leaf: <><path d="M11 20A7 7 0 019.8 6.9C15.5 4.9 17 3.5 17 3.5s-.3 3.5-1.5 6C14 13 11 15 11 20z"/><path d="M6.7 17.3l4.3-4.3"/></>,
  cake: <><path d="M20 21v-8a2 2 0 00-2-2H6a2 2 0 00-2 2v8"/><path d="M4 16s.5-1 2-1 2.5 2 4 2 2.5-2 4-2 2.5 2 4 2 2-1 2-1"/><path d="M2 21h20"/><path d="M7 8v3M12 8v3M17 8v3"/></>,
  coffee: <><path d="M17 8h1a4 4 0 010 8h-1"/><path d="M3 8h14v9a4 4 0 01-4 4H7a4 4 0 01-4-4V8z"/><path d="M6 2v4M10 2v4M14 2v4"/></>,
  'glass-water': <><path d="M15.2 22H8.8a2 2 0 01-2-1.79L5 3h14l-1.81 17.21A2 2 0 0115.2 22z"/><path d="M6 12a5 5 0 006 0 5 5 0 006 0"/></>,
  wine: <path d="M8 22h8M12 18v4M12 18a7 7 0 007-7c0-2-1-3.9-3-5.5s-3.5-4-4-6.5c-.5 2.5-2 4.9-4 6.5C6 7.1 5 9 5 11a7 7 0 007 7z"/>,
  cocktail: <><path d="M8 22h8M12 18v4"/><path d="M2 2l10 10L22 2H2z"/></>,
  beer: <><path d="M17 11h1a3 3 0 010 6h-1"/><path d="M2 11h15v7a4 4 0 01-4 4H6a4 4 0 01-4-4v-7z"/><path d="M6 7v4M10 7v4"/></>,
  whiskey: <path d="M8 22h8M12 18v4M5 3l2.5 15H16.5L19 3H5z"/>,
  glass: <path d="M8 22h8M12 18v4M5 3l2.5 15H16.5L19 3H5z"/>,
};

function Icon({ name, className }) {
  const path = icons[name] || icons.utensils;
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className={className || 'w-4 h-4'}>
      {path}
    </svg>
  );
}

/* ─── Animations ─── */
const stagger = { hidden: {}, visible: { transition: { staggerChildren: 0.06 } } };
const fadeUp = { hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [.25, .46, .45, .94] } } };
const fadeIn = { hidden: { opacity: 0 }, visible: { opacity: 1, transition: { duration: 0.5 } } };
const scaleIn = { hidden: { opacity: 0, scale: 0.95 }, visible: { opacity: 1, scale: 1, transition: { duration: 0.35 } } };

export default function PublicMenuPage() {
  const [data, setData] = useState(null);
  const [activeCategory, setActiveCategory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchOpen, setSearchOpen] = useState(false);
  const navRef = useRef(null);
  const activeBtnRef = useRef(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/public/menu`)
      .then(r => r.json())
      .then(d => {
        setData(d);
        const cats = Object.keys(d.menu);
        if (cats.length > 0) setActiveCategory(cats[0]);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  // Auto-scroll nav to active category
  useEffect(() => {
    if (activeBtnRef.current && navRef.current) {
      const nav = navRef.current;
      const btn = activeBtnRef.current;
      const scrollLeft = btn.offsetLeft - nav.offsetWidth / 2 + btn.offsetWidth / 2;
      nav.scrollTo({ left: scrollLeft, behavior: 'smooth' });
    }
  }, [activeCategory]);

  const theme = data?.theme || {};
  const colors = theme.colors || {};
  const components = theme.components || {};
  const bg = theme.background || {};

  // Search results
  const searchResults = useMemo(() => {
    if (!searchQuery.trim() || !data) return null;
    const q = searchQuery.toLowerCase();
    const results = [];
    Object.entries(data.menu).forEach(([catKey, cat]) => {
      cat.items.forEach(item => {
        if (item.name.toLowerCase().includes(q) || (item.desc && item.desc.toLowerCase().includes(q))) {
          results.push({ ...item, categoryName: cat.name_tr });
        }
      });
    });
    return results;
  }, [searchQuery, data]);

  if (loading) {
    return (
      <div style={{ background: '#7A8B6F', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 16 }}>
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          style={{ width: 36, height: 36, border: '2.5px solid #9AAD8F40', borderTopColor: '#FFFFFF', borderRadius: '50%' }}
        />
        <span style={{ color: '#E8E4DC', fontSize: 13, letterSpacing: '0.1em' }}>MENU YUKLENIYOR</span>
      </div>
    );
  }

  if (!data) {
    return (
      <div style={{ background: '#7A8B6F', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#FFFFFF' }}>
        <p>Menu yuklenemedi</p>
      </div>
    );
  }

  const categories = Object.keys(data.menu);
  const activeCat = data.menu[activeCategory];
  // background: '#0D150E' according to the html 'var(--bg)'
  const bgStyle = { background: '#0D150E' };

  // To format prices
  const fmt = (n) => n >= 1000 ? n.toLocaleString('tr-TR') : n;

  return (
    <div
      style={{ ...bgStyle, minHeight: '100vh', fontFamily: "'Montserrat', sans-serif", overflow: 'hidden', paddingBottom: 60 }}
      data-testid="public-menu-page"
    >
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,600;1,600&display=swap');
        
        :root {
          --bg: #0D150E;
          --gold: #C5A55A;
          --text: #F4F1EB;
          --muted: #8AA392;
          --fd: "Playfair Display", serif;
          --fm: "Montserrat", sans-serif;
        }

        .scroll-prog{position:fixed;top:0;left:0;height:3px;background:var(--gold);z-index:999;transition:width .1s;width:0%}

        .gcol {
          max-width: 600px;
          margin: 0 auto;
          background: var(--bg);
          min-height: 100vh;
          box-shadow: 0 0 30px rgba(0,0,0,.5);
          position: relative;
          color: var(--text);
        }

        .hero {
          text-align: center;
          padding: 30px 20px 20px;
          position: relative;
        }
        .hero::after {
          content: "";
          position: absolute;
          bottom: 0;
          left: 50%;
          transform: translateX(-50%);
          width: 50px;
          height: 1px;
          background: rgba(197,165,90,.3);
        }
        .hero-logo {
          width: 80px;
          margin-bottom: 15px;
        }
        .hero h1 {
          font-family: var(--fd);
          color: var(--gold);
          font-size: 2rem;
          margin: 0 0 5px;
          font-weight: 600;
          letter-spacing: .05em;
        }
        .hero-sub {
          font-size: .8rem;
          color: rgba(244,241,235,.6);
          letter-spacing: .15em;
          text-transform: uppercase;
        }

        .nav-scroller {
          display: flex;
          overflow-x: auto;
          gap: 12px;
          padding: 20px;
          background: var(--bg);
          position: sticky;
          top: 0;
          z-index: 100;
          border-bottom: 1px solid rgba(255,255,255,.05);
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
        .nav-scroller::-webkit-scrollbar { display: none; }
        
        .nav-btn {
          background: transparent;
          border: 1px solid rgba(255,255,255,.1);
          color: rgba(255,255,255,.6);
          padding: 8px 16px;
          border-radius: 20px;
          font-family: var(--fm);
          font-size: .85rem;
          font-weight: 500;
          cursor: pointer;
          white-space: nowrap;
          transition: all .3s ease;
        }
        .nav-btn.active {
          background: var(--gold);
          color: var(--bg);
          border-color: var(--gold);
          font-weight: 600;
        }

        .content { padding: 20px 20px 40px; }
        .cat-section { margin-bottom: 40px; }
        .cat-title {
          font-family: var(--fd);
          font-size: 1.4rem;
          color: var(--gold);
          margin: 0 0 15px;
          padding-bottom: 8px;
          border-bottom: 1px solid rgba(197,165,90,.2);
        }

        .item {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          padding: 12px 0;
          gap: 15px;
        }
        .item-div { height: 1px; background: rgba(255,255,255,.05); margin: 0 10%; }
        .item-name {
          font-size: .95rem;
          font-weight: 600;
          color: var(--text);
          margin-bottom: 4px;
        }
        .item-desc {
          font-size: .8rem;
          color: rgba(255,255,255,.5);
          line-height: 1.4;
          margin-bottom: 4px;
        }
        .item-allergen {
          font-size: .75rem;
          color: var(--muted);
          font-style: italic;
        }
        .item-price {
          font-family: var(--fm);
          font-size: .95rem;
          font-weight: 600;
          color: var(--gold);
          white-space: nowrap;
        }

        .wine-tag {
          display: inline-block;
          font-size: .65rem;
          padding: 2px 6px;
          border: 1px solid rgba(197,165,90,.3);
          border-radius: 3px;
          color: var(--gold);
          margin-top: 5px;
        }

        .badge {
          display: inline-block;
          font-size: .65rem;
          font-weight: 600;
          padding: 2px 6px;
          border-radius: 3px;
          margin-top: 5px;
          text-transform: uppercase;
        }
        .badge-new { background: rgba(197,165,90,.15); color: var(--gold); border: 1px solid rgba(197,165,90,.3); }
        .badge-vegan { background: rgba(138,163,146,.15); color: var(--muted); border: 1px solid rgba(138,163,146,.3); }

        .search-box {
          position: relative;
          margin: 0 20px 20px;
        }
        .search-input {
          width: 100%;
          background: rgba(255,255,255,.03);
          border: 1px solid rgba(255,255,255,.1);
          border-radius: 20px;
          padding: 10px 15px 10px 35px;
          color: var(--text);
          font-family: var(--fm);
          font-size: .85rem;
          outline: none;
        }
        .search-icon {
          position: absolute;
          left: 12px;
          top: 50%;
          transform: translateY(-50%);
          width: 16px;
          height: 16px;
          color: rgba(255,255,255,.4);
        }

        .footer {
          margin-top: 40px;
          padding: 30px 20px;
          text-align: center;
          background: rgba(255,255,255,.02);
          border-top: 1px solid rgba(255,255,255,.05);
        }
        .f-wifi {
          background: rgba(197,165,90,.05);
          border: 1px solid rgba(197,165,90,.15);
          border-radius: 8px;
          padding: 15px;
          margin-bottom: 24px;
          display: inline-block;
          text-align: left;
        }
        .f-wifi-lbl { font-size: .6rem; letter-spacing: .15em; text-transform: uppercase; color: rgba(255,255,255,.35); margin-bottom: 2px; }
        .f-wifi-val { font-size: .9rem; font-weight: 600; color: #fff; letter-spacing: .04em; }
        .f-links { display: flex; justify-content: center; gap: 14px; margin-bottom: 16px; flex-wrap: wrap; }
        .f-links a { color: rgba(255,255,255,.4); text-decoration: none; font-size: .72rem; transition: color .3s; }
        .f-links a:hover { color: var(--gold); }
        .f-review { display: inline-block; padding: 8px 20px; border: 1px solid rgba(197,165,90,.3); border-radius: 3px; color: var(--gold); text-decoration: none; font-size: .72rem; margin-bottom: 16px; transition: all .3s; }
        .f-review:hover { background: rgba(197,165,90,.08); border-color: var(--gold); }
        .f-brand { font-family: var(--fd); font-size: .78rem; color: rgba(255,255,255,.2); }
        .f-kdv { font-size: .6rem; color: rgba(255,255,255,.25); margin-top: 8px; }
      `}</style>

      <div className="gcol">
        {/* ═══ HEADER ═══ */}
        <header className="hero">
          <img
            className="hero-logo"
            src="/brand/KOZBEYLI_BEYAZ_LOGO.png"
            alt={theme.brand_name || 'Kozbeyli Konagi'}
            onError={(e) => {
              e.target.src = '/logo.jpeg';
              e.target.style.borderRadius = '50%';
            }}
          />
          <h1 className="menu-heading">{theme.brand_name || 'Kozbeyli Konagi'}</h1>
          <div className="hero-sub">{data.restaurant || 'Antakya Sofrasi'}</div>
        </header>

        {/* ═══ SEARCH BAR ═══ */}
        <div style={{ padding: '20px 0 0' }}>
          <div className="search-box">
            <svg className="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
            </svg>
            <input
              type="text"
              className="search-input"
              placeholder="Menü'de ara..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        {/* ═══ CATEGORY NAVIGATION ═══ */}
        {!searchResults && (
          <div className="nav-scroller" ref={navRef}>
            {categories.map(catKey => {
              const cat = data.menu[catKey];
              const isActive = activeCategory === catKey;
              return (
                <button
                  key={catKey}
                  ref={isActive ? activeBtnRef : null}
                  onClick={() => setActiveCategory(catKey)}
                  className={`nav-btn ${isActive ? 'active' : ''}`}
                >
                  {cat.name_tr}
                </button>
              );
            })}
          </div>
        )}

        {/* ═══ MENU ITEMS ═══ */}
        <div className="content">
          {searchResults ? (
            <motion.div variants={stagger} initial="hidden" animate="visible">
              <div style={{ marginBottom: 16, textAlign: 'center', fontSize: '0.8rem', color: 'rgba(255,255,255,0.5)' }}>
                {searchResults.length} sonuç bulundu
              </div>
              {searchResults.map((item, i) => (
                <motion.div key={i} variants={fadeUp}>
                  <div className="item">
                    <div className="item-left">
                      <div className="item-name">{item.name} <span style={{fontSize: '0.7em', color: 'rgba(255,255,255,0.3)', fontWeight: 'normal'}}>- {item.categoryName}</span></div>
                      {item.desc && <div className="item-desc">{item.desc}</div>}
                    </div>
                    <div className="item-price">{fmt(parseInt(item.price_try || 0))} ₺</div>
                  </div>
                  {i < searchResults.length - 1 && <div className="item-div"></div>}
                </motion.div>
              ))}
              {searchResults.length === 0 && (
                <div style={{ textAlign: 'center', padding: '40px 20px', color: 'rgba(255,255,255,0.5)' }}>
                  Sonuç bulunamadı.
                </div>
              )}
            </motion.div>
          ) : (
            activeCat && (
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeCategory}
                  initial="hidden"
                  animate="visible"
                  exit={{ opacity: 0, y: -8 }}
                  variants={stagger}
                  className="cat-section"
                >
                  <h2 className="cat-title">{activeCat.name_tr}</h2>
                  {activeCat.items.map((item, i) => (
                    <motion.div key={item.id || i} variants={fadeUp}>
                      <div className="item">
                        <div className="item-left">
                          <div className="item-name">{item.name}</div>
                          {item.desc && <div className="item-desc">{item.desc}</div>}
                        </div>
                        <div className="item-price">{fmt(parseInt(item.price_try || 0))} ₺</div>
                      </div>
                      {i < activeCat.items.length - 1 && <div className="item-div"></div>}
                    </motion.div>
                  ))}
                </motion.div>
              </AnimatePresence>
            )
          )}
        </div>

        {/* ═══ FOOTER ═══ */}
        <footer className="footer">
          <div className="f-wifi">
            <div className="f-wifi-lbl">WiFi Şifresi</div>
            <div className="f-wifi-val">KozbeyliKonagi2024</div>
          </div>
          <div className="f-links">
            <a href="https://instagram.com/kozbeylikonagi" target="_blank" rel="noopener noreferrer">Instagram</a>
            <a href="https://facebook.com/kozbeylikonagi" target="_blank" rel="noopener noreferrer">Facebook</a>
            <a href="https://maps.google.com/?q=Kozbeyli+Konagi+Foca" target="_blank" rel="noopener noreferrer">Harita</a>
            <a href="tel:+902328261112">Ara</a>
          </div>
          <a href="https://g.page/kozbeylikonagi/review" target="_blank" rel="noopener noreferrer" className="f-review">
            Bizi Değerlendirin
          </a>
          <div className="f-brand">{theme.brand_name || 'Kozbeyli Konagi'}</div>
          <div className="f-kdv">Fiyatlarımıza KDV dahildir. %10 servis ücreti eklenebilir.</div>
        </footer>
      </div>
    </div>
  );
}
