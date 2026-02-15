import React, { useState, useEffect, useMemo } from 'react';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

const CATEGORY_ICONS = {
  utensils: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-5 h-5">
      <path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 002-2V2M7 2v20M21 15V2v0a5 5 0 00-5 5v6c0 1.1.9 2 2 2h3zm0 0v7"/>
    </svg>
  ),
  coffee: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-5 h-5">
      <path d="M17 8h1a4 4 0 010 8h-1M3 8h14v9a4 4 0 01-4 4H7a4 4 0 01-4-4V8zM6 2v4M10 2v4M14 2v4"/>
    </svg>
  ),
  wine: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-5 h-5">
      <path d="M8 22h8M12 18v4M12 18a7 7 0 007-7c0-2-1-3.9-3-5.5s-3.5-4-4-6.5c-.5 2.5-2 4.9-4 6.5C6 7.1 5 9 5 11a7 7 0 007 7z"/>
    </svg>
  ),
  flame: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-5 h-5">
      <path d="M8.5 14.5A2.5 2.5 0 0011 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 11-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 002.5 2.5z"/>
    </svg>
  ),
  cake: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-5 h-5">
      <path d="M20 21v-8a2 2 0 00-2-2H6a2 2 0 00-2 2v8M4 16s.5-1 2-1 2.5 2 4 2 2.5-2 4-2 2.5 2 4 2 2-1 2-1M2 21h20M7 8v3M12 8v3M17 8v3M7 4h.01M12 4h.01M17 4h.01"/>
    </svg>
  ),
  leaf: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-5 h-5">
      <path d="M11 20A7 7 0 019.8 6.9C15.5 4.9 17 3.5 17 3.5s-.3 3.5-1.5 6C14 13 11 15 11 20zM6.7 17.3l4.3-4.3"/>
    </svg>
  ),
  salad: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-5 h-5">
      <path d="M7 21h10M12 21a9 9 0 009-9H3a9 9 0 009 9zM11.38 12a2.4 2.4 0 01-.4-4.77 2.4 2.4 0 013.2-2.77 2.4 2.4 0 014.09.52 2.4 2.4 0 01.93 4.6"/>
    </svg>
  ),
  pizza: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-5 h-5">
      <path d="M15 11h.01M11 15h.01M16 16h.01M2 16.5A10.65 10.65 0 017.5 2a10 10 0 00 9 14.5z"/>
    </svg>
  ),
  beer: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-5 h-5">
      <path d="M17 11h1a3 3 0 010 6h-1M2 11h15v7a4 4 0 01-4 4H6a4 4 0 01-4-4v-7zM6 7v4M10 7v4"/>
    </svg>
  ),
  glass: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-5 h-5">
      <path d="M8 22h8M12 18v4M5 3l2.5 15H16.5L19 3H5z"/>
    </svg>
  ),
  cocktail: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-5 h-5">
      <path d="M8 22h8M12 18v4M2 2l10 10L22 2H2z"/>
    </svg>
  ),
  whiskey: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-5 h-5">
      <path d="M8 22h8M12 18v4M5 3l2.5 15H16.5L19 3H5z"/>
    </svg>
  ),
  'glass-water': (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-5 h-5">
      <path d="M15.2 22H8.8a2 2 0 01-2-1.79L5 3h14l-1.81 17.21A2 2 0 0115.2 22zM6 12a5 5 0 006 0 5 5 0 006 0"/>
    </svg>
  ),
};

export default function PublicMenuPage() {
  const [data, setData] = useState(null);
  const [activeCategory, setActiveCategory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lang, setLang] = useState('tr');

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

  const theme = data?.theme || {};
  const colors = theme.colors || {};
  const components = theme.components || {};
  const layout = theme.layout || {};
  const bg = theme.background || {};

  const cssVars = useMemo(() => ({
    '--menu-bg': colors.bg || '#515249',
    '--menu-text': colors.text || '#F8F5EF',
    '--menu-muted': colors.muted || '#D8D1C5',
    '--menu-card': colors.card || '#F3EEE4',
    '--menu-border': colors.border || '#6A6B60',
    '--menu-primary': colors.primary || '#8FAA86',
    '--menu-on-primary': colors.on_primary || '#1E1B16',
    '--menu-accent': colors.accent || '#B07A2A',
    '--menu-on-accent': colors.on_accent || '#1E1B16',
    '--menu-link': colors.link || '#A9C3A2',
    '--menu-radius': `${components.radius || 18}px`,
  }), [colors, components]);

  if (loading) {
    return (
      <div style={{ background: '#515249', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ width: 40, height: 40, border: '3px solid #8FAA86', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (!data) {
    return (
      <div style={{ background: '#515249', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#F8F5EF' }}>
        <p>Menu yuklenemedi</p>
      </div>
    );
  }

  const categories = Object.keys(data.menu);
  const activeCat = data.menu[activeCategory];
  const bgStyle = bg.mode === 'gradient'
    ? { background: bg.value }
    : { background: colors.bg };

  return (
    <div
      className="public-menu-root"
      style={{ ...cssVars, ...bgStyle, minHeight: '100vh', fontFamily: `'Inter', sans-serif` }}
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
        .public-menu-root * { box-sizing: border-box; }
        .menu-heading { font-family: 'Alifira', serif; }
        .cat-btn { transition: all 0.3s ease; }
        .cat-btn:hover { transform: translateY(-2px); }
        .cat-btn.active { transform: translateY(-2px); }
        .menu-item-card {
          transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .menu-item-card:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }
        .fade-in {
          animation: fadeIn 0.4s ease-out;
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .lang-btn { transition: opacity 0.2s; }
        .lang-btn:hover { opacity: 1 !important; }
        @media (max-width: 640px) {
          .menu-grid { grid-template-columns: 1fr !important; }
        }
      `}</style>

      {/* Header */}
      <header
        style={{
          background: colors.bg || '#515249',
          padding: '48px 24px 32px',
          textAlign: layout.header?.center ? 'center' : 'left',
          borderBottom: `1px solid ${colors.border}40`,
          position: 'relative',
        }}
        data-testid="menu-header"
      >
        {/* Language Toggle */}
        <div style={{ position: 'absolute', top: 16, right: 16, display: 'flex', gap: 8 }}>
          {['tr', 'en'].map(l => (
            <button
              key={l}
              className="lang-btn"
              onClick={() => setLang(l)}
              style={{
                padding: '4px 10px',
                borderRadius: 8,
                border: `1px solid ${colors.border}60`,
                background: lang === l ? `${colors.primary}30` : 'transparent',
                color: colors.text,
                fontSize: 12,
                fontWeight: lang === l ? 600 : 400,
                cursor: 'pointer',
                opacity: lang === l ? 1 : 0.6,
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
              }}
              data-testid={`lang-${l}`}
            >
              {l === 'tr' ? 'TR' : 'EN'}
            </button>
          ))}
        </div>

        {/* Logo */}
        {layout.header?.showLogo && (
          <div style={{ marginBottom: 16 }}>
            <img
              src="/logo.jpeg"
              alt={theme.brand_name || 'Kozbeyli Konagi'}
              style={{
                maxWidth: Math.min(layout.header?.logoMaxWidth || 200, 200),
                height: 'auto',
                borderRadius: 12,
                margin: '0 auto',
                display: 'block',
              }}
              data-testid="menu-logo"
              onError={(e) => { e.target.style.display = 'none'; }}
            />
          </div>
        )}

        {/* Brand Name */}
        <h1
          className="menu-heading"
          style={{
            color: colors.text,
            fontSize: 'clamp(28px, 6vw, 42px)',
            margin: '8px 0 4px',
            letterSpacing: components.headingTracking ? `${components.headingTracking}em` : '0.12em',
            textTransform: components.headingUppercase ? 'uppercase' : 'none',
            lineHeight: 1.2,
          }}
          data-testid="menu-brand-name"
        >
          {theme.brand_name || 'Kozbeyli Konagi'}
        </h1>

        {/* Tagline */}
        <p style={{ color: colors.muted, fontSize: 14, margin: '4px 0 0', letterSpacing: '0.1em', textTransform: 'uppercase' }}>
          {theme.tagline || 'Tas Otel'}
        </p>

        {/* Restaurant name */}
        <div style={{ marginTop: 20, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12 }}>
          <div style={{ width: 40, height: 1, background: `${colors.accent}80` }} />
          <span className="menu-heading" style={{ color: colors.accent, fontSize: 16, letterSpacing: '0.15em', textTransform: 'uppercase' }}>
            {data.restaurant}
          </span>
          <div style={{ width: 40, height: 1, background: `${colors.accent}80` }} />
        </div>
      </header>

      {/* Category Navigation */}
      <nav
        style={{
          padding: '16px 16px 0',
          overflowX: 'auto',
          display: 'flex',
          gap: 8,
          WebkitOverflowScrolling: 'touch',
          scrollbarWidth: 'none',
          position: 'sticky',
          top: 0,
          zIndex: 10,
          background: bg.mode === 'gradient' ? colors.bg : colors.bg,
          borderBottom: `1px solid ${colors.border}30`,
          paddingBottom: 12,
        }}
        data-testid="menu-categories"
      >
        {categories.map(catKey => {
          const cat = data.menu[catKey];
          const isActive = activeCategory === catKey;
          const icon = CATEGORY_ICONS[cat.icon] || CATEGORY_ICONS['utensils'];

          return (
            <button
              key={catKey}
              className={`cat-btn ${isActive ? 'active' : ''}`}
              onClick={() => setActiveCategory(catKey)}
              style={{
                flexShrink: 0,
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                padding: '8px 16px',
                borderRadius: components.radius || 18,
                border: isActive ? `1.5px solid ${colors.primary}` : `1px solid ${colors.border}50`,
                background: isActive ? `${colors.primary}25` : 'transparent',
                color: isActive ? colors.primary : colors.muted,
                fontSize: 13,
                fontWeight: isActive ? 600 : 400,
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                letterSpacing: '0.02em',
              }}
              data-testid={`cat-${catKey}`}
            >
              {icon}
              {lang === 'tr' ? cat.name_tr : (cat.name_en || cat.name_tr)}
            </button>
          );
        })}
      </nav>

      {/* Menu Items */}
      <main style={{ padding: '20px 16px 80px', maxWidth: 800, margin: '0 auto' }}>
        {activeCat && (
          <div className="fade-in" key={activeCategory}>
            {/* Category Title */}
            <div style={{ marginBottom: 20, textAlign: 'center' }}>
              <h2
                className="menu-heading"
                style={{
                  color: colors.text,
                  fontSize: 22,
                  letterSpacing: '0.12em',
                  textTransform: components.headingUppercase ? 'uppercase' : 'none',
                  margin: 0,
                }}
                data-testid="active-category-title"
              >
                {lang === 'tr' ? activeCat.name_tr : (activeCat.name_en || activeCat.name_tr)}
              </h2>
              <div style={{ width: 40, height: 2, background: colors.accent, margin: '8px auto 0', borderRadius: 2 }} />
            </div>

            {/* Items */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {activeCat.items.map((item, i) => (
                <div
                  key={item.id || i}
                  className="menu-item-card"
                  style={{
                    background: `${colors.card}12`,
                    borderRadius: components.radius || 18,
                    padding: '16px 20px',
                    border: `1px solid ${colors.border}25`,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    gap: 16,
                    backdropFilter: 'blur(8px)',
                  }}
                  data-testid={`menu-item-${i}`}
                >
                  <div style={{ flex: 1 }}>
                    <h3 style={{
                      color: colors.text,
                      fontSize: 15,
                      fontWeight: 500,
                      margin: 0,
                      letterSpacing: '0.01em',
                    }}>
                      {item.name}
                    </h3>
                    {item.desc && (
                      <p style={{
                        color: colors.muted,
                        fontSize: 12,
                        margin: '4px 0 0',
                        lineHeight: 1.5,
                        opacity: 0.85,
                      }}>
                        {item.desc}
                      </p>
                    )}
                  </div>
                  <div style={{
                    flexShrink: 0,
                    textAlign: 'right',
                  }}>
                    <span style={{
                      color: colors.accent,
                      fontSize: 17,
                      fontWeight: 700,
                      fontFamily: `'Inter', sans-serif`,
                    }}>
                      {item.price_try}
                    </span>
                    <span style={{
                      color: colors.muted,
                      fontSize: 11,
                      marginLeft: 2,
                      opacity: 0.7,
                    }}>
                      TL
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer
        style={{
          padding: '24px 16px',
          textAlign: 'center',
          borderTop: `1px solid ${colors.border}30`,
        }}
      >
        <p style={{ color: colors.muted, fontSize: 12, opacity: 0.6, margin: 0 }}>
          {theme.brand_name || 'Kozbeyli Konagi'} &middot; {data.restaurant}
        </p>
      </footer>
    </div>
  );
}
