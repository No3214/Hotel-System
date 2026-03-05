import React from 'react';
import { AlertCircle, RefreshCw, Wifi, WifiOff } from 'lucide-react';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, retryCount: 0, autoRecovering: false };
    this._autoRecoverTimer = null;
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);

    // Auto-recovery: try to recover after 5 seconds (max 3 attempts)
    if (this.state.retryCount < 3) {
      this.setState({ autoRecovering: true });
      this._autoRecoverTimer = setTimeout(() => {
        this.setState(prev => ({
          hasError: false,
          error: null,
          retryCount: prev.retryCount + 1,
          autoRecovering: false,
        }));
      }, 5000);
    }
  }

  componentWillUnmount() {
    if (this._autoRecoverTimer) clearTimeout(this._autoRecoverTimer);
  }

  handleManualRetry = () => {
    if (this._autoRecoverTimer) clearTimeout(this._autoRecoverTimer);
    this.setState({ hasError: false, error: null, autoRecovering: false });
  };

  handleFullReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex items-center justify-center min-h-[400px] p-8">
          <div className="text-center space-y-4 max-w-md">
            <div className="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center mx-auto">
              <AlertCircle className="w-8 h-8 text-red-400" />
            </div>
            <h2 className="text-lg font-semibold text-white">Bir hata olustu</h2>
            <p className="text-sm text-[#7e7e8a]">
              Bu sayfa yuklenirken bir sorunla karsilasildi.
              {this.state.autoRecovering && (
                <span className="block text-[#C4972A] mt-1">
                  Otomatik toparlanma deneniyor... ({this.state.retryCount + 1}/3)
                </span>
              )}
            </p>
            {this.state.error && (
              <p className="text-xs text-red-400/70 bg-red-400/5 rounded p-2 font-mono">
                {this.state.error.message}
              </p>
            )}
            <div className="flex gap-2 justify-center">
              <button
                onClick={this.handleManualRetry}
                className="inline-flex items-center gap-2 px-4 py-2 bg-[#C4972A] hover:bg-[#a87a1f] text-white rounded-lg transition-colors"
              >
                <RefreshCw className={`w-4 h-4 ${this.state.autoRecovering ? 'animate-spin' : ''}`} />
                Tekrar Dene
              </button>
              <button
                onClick={this.handleFullReload}
                className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/15 text-[#a9a9b2] rounded-lg transition-colors"
              >
                Sayfayi Yenile
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

/**
 * Network status monitor - shows offline/online banner
 */
export function NetworkStatusMonitor() {
  const [isOnline, setIsOnline] = React.useState(navigator.onLine);
  const [showBanner, setShowBanner] = React.useState(false);

  React.useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      // Show "back online" briefly
      setShowBanner(true);
      setTimeout(() => setShowBanner(false), 3000);
    };
    const handleOffline = () => {
      setIsOnline(false);
      setShowBanner(true);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (!showBanner) return null;

  return (
    <div className={`fixed top-0 left-0 right-0 z-[9999] px-4 py-2 text-center text-sm font-medium transition-all duration-300 ${
      isOnline
        ? 'bg-emerald-600 text-white'
        : 'bg-red-600 text-white'
    }`}>
      <div className="flex items-center justify-center gap-2">
        {isOnline ? (
          <>
            <Wifi className="w-4 h-4" />
            <span>Baglanti yeniden kuruldu</span>
          </>
        ) : (
          <>
            <WifiOff className="w-4 h-4" />
            <span>Internet baglantisi kesildi - Baglanti bekleniyor...</span>
          </>
        )}
      </div>
    </div>
  );
}
