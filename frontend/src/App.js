import React, { useState, useEffect } from 'react';
import './App.css';

const App = () => {
  const [file, setFile] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState('idle');
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [apiUrl, setApiUrl] = useState(process.env.REACT_APP_API_URL || 'http://localhost:8000');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && (selectedFile.name.toLowerCase().endsWith('.dwg') || selectedFile.name.toLowerCase().endsWith('.dxf'))) {
      setFile(selectedFile);
      setError(null);
    } else {
      setError('Please select a valid DWG or DXF file');
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setStatus('uploading');
    setProgress(0);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${apiUrl}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setJobId(data.job_id);
        setStatus('processing');
        pollJobStatus(data.job_id);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Upload failed');
        setStatus('idle');
      }
    } catch (err) {
      setError('Network error: ' + err.message);
      setStatus('idle');
    }
  };

  const pollJobStatus = async (id) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`${apiUrl}/jobs/${id}`);
        if (response.ok) {
          const job = await response.json();
          setProgress(job.progress);

          if (job.status === 'completed') {
            setStatus('completed');
            clearInterval(interval);
          } else if (job.status === 'failed') {
            setError(job.error_message || 'Processing failed');
            setStatus('idle');
            clearInterval(interval);
          }
        }
      } catch (err) {
        setError('Error checking status: ' + err.message);
        clearInterval(interval);
      }
    }, 2000);
  };

  const handleDownload = async () => {
    if (!jobId) return;

    try {
      const response = await fetch(`${apiUrl}/download/${jobId}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `translated_${file.name}`;
        a.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (err) {
      setError('Download failed: ' + err.message);
    }
  };

  const resetForm = () => {
    setFile(null);
    setJobId(null);
    setStatus('idle');
    setProgress(0);
    setError(null);
  };

  const getStatusMessage = () => {
    switch (status) {
      case 'uploading':
        return 'ファイルをアップロード中...';
      case 'processing':
        return '処理中...';
      case 'completed':
        return '翻訳完了！';
      default:
        return '';
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AutoCAD DWG 中国語→日本語 翻訳ツール</h1>
        <p className="subtitle">
          AutoCAD DWGファイル内の中国語テキストを自動翻訳し、元のフォーマットを保持したまま日本語に変換します
        </p>
      </header>

      <main className="App-main">
        <div className="upload-section">
          {status === 'idle' && (
            <div className="file-upload">
              <div className="upload-area">
                <input
                  type="file"
                  accept=".dwg"
                  onChange={handleFileChange}
                  id="file-input"
                  className="file-input"
                />
                <label htmlFor="file-input" className="file-label">
                  <div className="upload-icon">📁</div>
                  <p>DWGファイルを選択またはドラッグ＆ドロップ</p>
                  <p className="file-hint">AutoCAD 2012以降のDWGファイルに対応</p>
                </label>
              </div>

              {file && (
                <div className="selected-file">
                  <p>選択されたファイル: <strong>{file.name}</strong></p>
                  <button
                    onClick={handleUpload}
                    className="upload-button"
                  >
                    アップロードして翻訳開始
                  </button>
                </div>
              )}
            </div>
          )}

          {(status === 'uploading' || status === 'processing') && (
            <div className="progress-section">
              <h3>{getStatusMessage()}</h3>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
              <p className="progress-text">{progress}% 完了</p>
              <div className="progress-steps">
                <div className={`step ${progress >= 10 ? 'active' : ''}`}>
                  <span className="step-number">1</span>
                  <span className="step-text">テキスト抽出</span>
                </div>
                <div className={`step ${progress >= 30 ? 'active' : ''}`}>
                  <span className="step-number">2</span>
                  <span className="step-text">翻訳処理</span>
                </div>
                <div className={`step ${progress >= 70 ? 'active' : ''}`}>
                  <span className="step-number">3</span>
                  <span className="step-text">テキスト置換</span>
                </div>
                <div className={`step ${progress >= 100 ? 'active' : ''}`}>
                  <span className="step-number">4</span>
                  <span className="step-text">完了</span>
                </div>
              </div>
            </div>
          )}

          {status === 'completed' && (
            <div className="completion-section">
              <div className="success-icon">✅</div>
              <h3>翻訳が完了しました！</h3>
              <p>中国語テキストが日本語に翻訳され、元のフォーマットが保持されています。</p>
              <div className="download-actions">
                <button
                  onClick={handleDownload}
                  className="download-button"
                >
                  翻訳済みファイルをダウンロード
                </button>
                <button
                  onClick={resetForm}
                  className="reset-button"
                >
                  別のファイルを翻訳
                </button>
              </div>
            </div>
          )}

          {error && (
            <div className="error-section">
              <div className="error-icon">❌</div>
              <h3>エラーが発生しました</h3>
              <p>{error}</p>
              <button
                onClick={resetForm}
                className="retry-button"
              >
                再試行
              </button>
            </div>
          )}
        </div>

        <div className="features-section">
          <h2>主な機能</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🔍</div>
              <h3>テキスト抽出</h3>
              <p>MTEXT、TEXT、ATTRIB、DIMTEXTなどの各種エンティティからテキストを抽出</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🌐</div>
              <h3>高精度翻訳</h3>
              <p>DeepLまたはGoogle翻訳APIを使用した専門的な技術翻訳</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📐</div>
              <h3>フォーマット保持</h3>
              <p>元のフォント、サイズ、位置、レイヤーなどの書式を完全に保持</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3>高速処理</h3>
              <p>バックグラウンド処理による高速な翻訳とリアルタイム進捗表示</p>
            </div>
          </div>
        </div>

        <div className="info-section">
          <h2>対応ファイル形式</h2>
          <ul>
            <li>AutoCAD DWGファイル（2012以降）</li>
            <li>ファイルサイズ: 最大100MB</li>
            <li>文字コード: 各種中国語文字コードに対応</li>
          </ul>

          <h2>翻訳対応言語</h2>
          <ul>
            <li>中国語（簡体字・繁体字）→ 日本語</li>
            <li>技術用語専門辞書内蔵</li>
            <li>建築・機械用語に最適化</li>
          </ul>
        </div>
      </main>

      <footer className="App-footer">
        <p>&copy; 2024 AutoCAD DWG Translator. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default App;