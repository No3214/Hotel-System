import React, { useState, useEffect, useMemo, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

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
  const bgStyle = bg.mode === 'gradient' ? { background: bg.value } : { background: colors.bg };

  return (
    <div
      style={{ ...bgStyle, minHeight: '100vh', fontFamily: "'Inter', sans-serif", overflow: 'hidden' }}
      data-testid="public-menu-page"
    >
      <style>{`
        @font-face {
          font-family: 'Alifira';
          src: url('/fonts/Alifira.ttf') format('truetype');
          font-weight: normal;
          font-style: normal;
          font-display: swap;
        }
        .menu-heading { font-family: 'Alifira', serif; }
        .hide-scrollbar::-webkit-scrollbar { display: none; }
        .hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
        .item-divider { background: linear-gradient(90deg, transparent, ${colors.border || '#6A6B60'}30, transparent); height: 1px; }
        @keyframes shimmer {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }
        .search-input::placeholder { color: ${colors.muted || '#D8D1C5'}80; }
      `}</style>

      {/* ═══ HEADER ═══ */}
      <motion.header
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8 }}
        style={{
          padding: '40px 24px 28px',
          textAlign: 'center',
          position: 'relative',
          background: `linear-gradient(180deg, ${colors.bg || '#515249'}00, ${colors.bg || '#515249'}40)`,
        }}
        data-testid="menu-header"
      >
        {/* Search Toggle */}
        <button
          onClick={() => { setSearchOpen(!searchOpen); setSearchQuery(''); }}
          style={{
            position: 'absolute', top: 16, right: 16,
            width: 36, height: 36, borderRadius: 12,
            background: `${colors.border || '#6A6B60'}30`,
            border: 'none', cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: colors.muted,
          }}
          data-testid="search-toggle"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" style={{ width: 18, height: 18 }}>
            {searchOpen
              ? <path d="M18 6L6 18M6 6l12 12"/>
              : <><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></>
            }
          </svg>
        </button>

        {/* Logo */}
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <img
            src="/brand/KOZBEYLI_BEYAZ_LOGO.png"
            alt={theme.brand_name}
            style={{
              maxWidth: 160,
              height: 'auto',
              margin: '0 auto',
              display: 'block',
              filter: 'drop-shadow(0 4px 12px rgba(0,0,0,0.3))',
            }}
            data-testid="menu-logo"
            onError={(e) => {
              e.target.src = '/logo.jpeg';
              e.target.style.maxWidth = '120px';
              e.target.style.borderRadius = '12px';
            }}
          />
        </motion.div>

        {/* Brand Name */}
        <motion.h1
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="menu-heading"
          style={{
            color: colors.text,
            fontSize: 'clamp(24px, 5vw, 36px)',
            margin: '16px 0 4px',
            letterSpacing: `${components.headingTracking || 0.12}em`,
            textTransform: components.headingUppercase ? 'uppercase' : 'none',
            lineHeight: 1.15,
          }}
          data-testid="menu-brand-name"
        >
          {theme.brand_name || 'Kozbeyli Konagi'}
        </motion.h1>

        {/* Divider */}
        <motion.div
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12, marginTop: 12 }}
        >
          <div style={{ width: 50, height: 1, background: `${colors.text}40` }} />
          <span className="menu-heading" style={{ color: colors.muted, fontSize: 12, letterSpacing: '0.18em', textTransform: 'uppercase' }}>
            {data.restaurant}
          </span>
          <div style={{ width: 50, height: 1, background: `${colors.text}40` }} />
        </motion.div>
      </motion.header>

      {/* ═══ SEARCH BAR ═══ */}
      <AnimatePresence>
        {searchOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            style={{ overflow: 'hidden', padding: '0 16px' }}
          >
            <div style={{ padding: '0 0 12px' }}>
              <input
                type="text"
                className="search-input"
                placeholder="Menu'de ara..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                autoFocus
                style={{
                  width: '100%', padding: '10px 16px',
                  borderRadius: components.radius || 18,
                  border: `1px solid ${colors.border}40`,
                  background: `${colors.bg}80`,
                  color: colors.text, fontSize: 14,
                  outline: 'none', backdropFilter: 'blur(8px)',
                }}
                data-testid="menu-search-input"
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ═══ CATEGORY NAVIGATION ═══ */}
      {!searchResults && (
        <motion.nav
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.4 }}
          ref={navRef}
          className="hide-scrollbar"
          style={{
            padding: '8px 16px 12px',
            overflowX: 'auto',
            display: 'flex',
            gap: 6,
            WebkitOverflowScrolling: 'touch',
            position: 'sticky',
            top: 0, zIndex: 20,
            background: colors.bg,
            borderBottom: `1px solid ${colors.border}20`,
          }}
          data-testid="menu-categories"
        >
          {categories.map(catKey => {
            const cat = data.menu[catKey];
            const isActive = activeCategory === catKey;
            return (
              <button
                key={catKey}
                ref={isActive ? activeBtnRef : null}
                onClick={() => setActiveCategory(catKey)}
                style={{
                  flexShrink: 0, display: 'flex', alignItems: 'center', gap: 5,
                  padding: '7px 14px', borderRadius: 24,
                  border: isActive ? `1.5px solid ${colors.text}` : `1px solid transparent`,
                  background: isActive ? `${colors.text}18` : 'transparent',
                  color: isActive ? colors.text : `${colors.muted}99`,
                  fontSize: 12, fontWeight: isActive ? 600 : 400, cursor: 'pointer',
                  whiteSpace: 'nowrap', letterSpacing: '0.02em',
                  transition: 'all 0.25s ease',
                }}
                data-testid={`cat-${catKey}`}
              >
                <Icon name={cat.icon} className="w-3.5 h-3.5" />
                {cat.name_tr}
              </button>
            );
          })}
        </motion.nav>
      )}

      {/* ═══ MENU ITEMS ═══ */}
      <main style={{ padding: '16px 16px 100px', maxWidth: 700, margin: '0 auto' }}>
        {/* Search Results */}
        {searchResults && (
          <motion.div variants={stagger} initial="hidden" animate="visible">
            <div style={{ marginBottom: 16, textAlign: 'center' }}>
              <span style={{ color: colors.muted, fontSize: 12 }}>
                {searchResults.length} sonuc bulundu
              </span>
            </div>
            {searchResults.map((item, i) => (
              <motion.div key={i} variants={fadeUp}>
                <MenuItem item={item} colors={colors} components={components} subtitle={item.categoryName} />
              </motion.div>
            ))}
            {searchResults.length === 0 && (
              <div style={{ textAlign: 'center', padding: 40, color: colors.muted }}>
                <p style={{ fontSize: 14 }}>Sonuc bulunamadi</p>
              </div>
            )}
          </motion.div>
        )}

        {/* Category Items */}
        {!searchResults && activeCat && (
          <AnimatePresence mode="wait">
            <motion.div
              key={activeCategory}
              initial="hidden"
              animate="visible"
              exit={{ opacity: 0, y: -8 }}
              variants={stagger}
            >
              {/* Category Title */}
              <motion.div variants={fadeIn} style={{ marginBottom: 20, textAlign: 'center' }}>
                <h2
                  className="menu-heading"
                  style={{
                    color: colors.text, fontSize: 20,
                    letterSpacing: '0.12em',
                    textTransform: components.headingUppercase ? 'uppercase' : 'none',
                    margin: 0,
                  }}
                  data-testid="active-category-title"
                >
                  {activeCat.name_tr}
                </h2>
                <div style={{ width: 32, height: 2, background: `${colors.text}60`, margin: '8px auto 0', borderRadius: 2 }} />
              </motion.div>

              {/* Items */}
              {activeCat.items.map((item, i) => (
                <motion.div key={item.id || i} variants={fadeUp}>
                  <MenuItem item={item} colors={colors} components={components} />
                  {i < activeCat.items.length - 1 && <div className="item-divider" style={{ margin: '0 20px' }} />}
                </motion.div>
              ))}
            </motion.div>
          </AnimatePresence>
        )}
      </main>

      {/* ═══ FOOTER - WiFi, Sosyal Medya, Yorum ═══ */}
      <footer style={{ padding: '24px 16px 40px', borderTop: `1px solid ${colors.border}20` }}>
        
        {/* WiFi Box */}
        <div style={{
          background: `${colors.card}20`,
          borderRadius: 16,
          padding: '16px 20px',
          marginBottom: 20,
          border: `1px solid ${colors.border}30`,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{
              width: 40, height: 40, borderRadius: 12,
              background: `${colors.text}15`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <svg viewBox="0 0 24 24" fill="none" stroke={colors.text} strokeWidth="1.5" style={{ width: 20, height: 20 }}>
                <path d="M5 12.55a11 11 0 0114.08 0M1.42 9a16 16 0 0121.16 0M8.53 16.11a6 6 0 016.95 0M12 20h.01"/>
              </svg>
            </div>
            <div>
              <p style={{ color: colors.muted, fontSize: 10, margin: 0, letterSpacing: '0.08em', textTransform: 'uppercase' }}>WiFi Sifresi</p>
              <p style={{ color: colors.text, fontSize: 15, fontWeight: 600, margin: '2px 0 0' }}>KozbeyliKonagi2024</p>
            </div>
          </div>
        </div>

        {/* Social Media & Review Links */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: 12, marginBottom: 20, flexWrap: 'wrap' }}>
          {/* Instagram */}
          <a href="https://instagram.com/kozbeylikonagi" target="_blank" rel="noopener noreferrer" style={{
            width: 44, height: 44, borderRadius: 12,
            background: `${colors.text}12`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            textDecoration: 'none',
          }}>
            <svg viewBox="0 0 24 24" fill="none" stroke={colors.text} strokeWidth="1.5" style={{ width: 20, height: 20 }}>
              <rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="18" cy="6" r="1.5" fill={colors.text}/>
            </svg>
          </a>
          {/* Facebook */}
          <a href="https://facebook.com/kozbeylikonagi" target="_blank" rel="noopener noreferrer" style={{
            width: 44, height: 44, borderRadius: 12,
            background: `${colors.text}12`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            textDecoration: 'none',
          }}>
            <svg viewBox="0 0 24 24" fill="none" stroke={colors.text} strokeWidth="1.5" style={{ width: 20, height: 20 }}>
              <path d="M18 2h-3a5 5 0 00-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 011-1h3V2z"/>
            </svg>
          </a>
          {/* Google Maps */}
          <a href="https://maps.google.com/?q=Kozbeyli+Konagi+Foca" target="_blank" rel="noopener noreferrer" style={{
            width: 44, height: 44, borderRadius: 12,
            background: `${colors.text}12`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            textDecoration: 'none',
          }}>
            <svg viewBox="0 0 24 24" fill="none" stroke={colors.text} strokeWidth="1.5" style={{ width: 20, height: 20 }}>
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/>
            </svg>
          </a>
          {/* Phone */}
          <a href="tel:+902328261112" style={{
            width: 44, height: 44, borderRadius: 12,
            background: `${colors.text}12`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            textDecoration: 'none',
          }}>
            <svg viewBox="0 0 24 24" fill="none" stroke={colors.text} strokeWidth="1.5" style={{ width: 20, height: 20 }}>
              <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72 12.84 12.84 0 00.7 2.81 2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45 12.84 12.84 0 002.81.7A2 2 0 0122 16.92z"/>
            </svg>
          </a>
        </div>

        {/* Review Button */}
        <a
          href="https://g.page/kozbeylikonagi/review"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 8,
            padding: '12px 24px',
            background: `${colors.text}15`,
            borderRadius: 12,
            textDecoration: 'none',
            marginBottom: 20,
          }}
        >
          <svg viewBox="0 0 24 24" fill={colors.text} style={{ width: 18, height: 18 }}>
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
          </svg>
          <span style={{ color: colors.text, fontSize: 13, fontWeight: 500 }}>Bizi Degerlendirin</span>
        </a>

        {/* Brand */}
        <p style={{ color: colors.muted, fontSize: 11, opacity: 0.5, margin: 0, letterSpacing: '0.05em', textAlign: 'center' }}>
          {theme.brand_name || 'Kozbeyli Konagi'} - Antakya Sofrasi
        </p>
      </footer>
    </div>
  );
}

/* ─── Menu Item Component ─── */
function MenuItem({ item, colors, components, subtitle }) {
  return (
    <div
      style={{
        padding: '14px 4px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        gap: 16,
      }}
    >
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <h3 style={{
            color: colors.text, fontSize: 14.5, fontWeight: 500,
            margin: 0, letterSpacing: '0.01em', lineHeight: 1.35,
          }}>
            {item.name}
          </h3>
        </div>
        {subtitle && (
          <span style={{ color: colors.muted, fontSize: 10, letterSpacing: '0.06em', textTransform: 'uppercase', opacity: 0.7 }}>
            {subtitle}
          </span>
        )}
        {item.desc && (
          <p style={{
            color: `${colors.muted}B0`, fontSize: 12,
            margin: '3px 0 0', lineHeight: 1.5,
          }}>
            {item.desc}
          </p>
        )}
      </div>
      <div style={{ flexShrink: 0, textAlign: 'right', paddingTop: 1 }}>
        <span style={{
          color: colors.text, fontSize: 15, fontWeight: 600,
          fontFamily: "'Inter', sans-serif",
        }}>
          {item.price_try}
        </span>
        <span style={{ color: `${colors.muted}80`, fontSize: 10, marginLeft: 2 }}>TL</span>
      </div>
    </div>
  );
}
