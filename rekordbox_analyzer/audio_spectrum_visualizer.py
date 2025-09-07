import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
from pathlib import Path
import urllib.parse
from typing import Optional, Tuple

# 日本語フォント設定
plt.rcParams['font.family'] = ['Hiragino Sans', 'Yu Gothic', 'Meiryo', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']
plt.rcParams['axes.unicode_minus'] = False

class AudioSpectrumVisualizer:
    def __init__(self):
        """オーディオスペクトラム可視化クラス"""
        pass
    
    def load_audio(self, file_path: str, sr: Optional[int] = None) -> Tuple[np.ndarray, int]:
        """オーディオファイルを読み込む"""
        try:
            # URL デコード（rekordboxのLocationから使用する場合）
            if file_path.startswith('file://localhost'):
                file_path = urllib.parse.unquote(file_path[16:])
            
            # ファイル存在確認
            if not Path(file_path).exists():
                raise FileNotFoundError(f"オーディオファイルが見つかりません: {file_path}")
            
            # オーディオ読み込み
            y, sr = librosa.load(file_path, sr=sr)
            print(f"✅ オーディオファイルを読み込みました: {Path(file_path).name}")
            print(f"   サンプルレート: {sr} Hz")
            print(f"   長さ: {len(y)/sr:.2f} 秒")
            
            return y, sr
            
        except Exception as e:
            raise Exception(f"オーディオファイルの読み込みに失敗しました: {e}")
    
    def create_spectrogram(self, y: np.ndarray, sr: int, n_fft: int = 2048, hop_length: int = 512) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """スペクトログラムを作成"""
        # 短時間フーリエ変換
        stft = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
        magnitude = np.abs(stft)
        
        # dB変換
        magnitude_db = librosa.amplitude_to_db(magnitude, ref=np.max)
        
        # 時間軸と周波数軸
        times = librosa.times_like(stft, sr=sr, hop_length=hop_length)
        freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
        
        return magnitude_db, times, freqs
    
    def create_mel_spectrogram(self, y: np.ndarray, sr: int, n_mels: int = 128) -> Tuple[np.ndarray, np.ndarray]:
        """メル・スペクトログラムを作成"""
        # メル・スペクトログラム
        mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels)
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        
        # 時間軸
        times = librosa.times_like(mel_spec, sr=sr)
        
        return mel_spec_db, times
    
    def plot_waveform(self, y: np.ndarray, sr: int, title: str = "Waveform"):
        """波形を表示"""
        plt.figure(figsize=(14, 4))
        times = np.arange(len(y)) / sr
        plt.plot(times, y, alpha=0.8)
        plt.xlabel('時間 (秒)')
        plt.ylabel('振幅')
        plt.title(title)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        return plt.gcf()
    
    def plot_spectrogram(self, magnitude_db: np.ndarray, times: np.ndarray, freqs: np.ndarray, title: str = "Spectrogram"):
        """スペクトログラムを表示"""
        plt.figure(figsize=(14, 8))
        librosa.display.specshow(magnitude_db, 
                                x_axis='time', 
                                y_axis='hz', 
                                sr=len(freqs)*2-1,
                                hop_length=len(times),
                                cmap='magma')
        plt.colorbar(format='%+2.0f dB')
        plt.xlabel('時間 (秒)')
        plt.ylabel('周波数 (Hz)')
        plt.title(title)
        plt.tight_layout()
        return plt.gcf()
    
    def plot_mel_spectrogram(self, mel_spec_db: np.ndarray, times: np.ndarray, sr: int, title: str = "Mel Spectrogram"):
        """メル・スペクトログラムを表示"""
        plt.figure(figsize=(14, 8))
        librosa.display.specshow(mel_spec_db, 
                                x_axis='time', 
                                y_axis='mel',
                                sr=sr,
                                cmap='magma')
        plt.colorbar(format='%+2.0f dB')
        plt.xlabel('時間 (秒)')
        plt.ylabel('メル周波数')
        plt.title(title)
        plt.tight_layout()
        return plt.gcf()
    
    def plot_chromagram(self, y: np.ndarray, sr: int, title: str = "Chromagram"):
        """クロマグラムを表示"""
        plt.figure(figsize=(14, 6))
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        librosa.display.specshow(chroma, 
                                x_axis='time', 
                                y_axis='chroma',
                                sr=sr,
                                cmap='coolwarm')
        plt.colorbar()
        plt.xlabel('時間 (秒)')
        plt.ylabel('音名')
        plt.title(title)
        plt.tight_layout()
        return plt.gcf()
    
    def analyze_audio_file(self, file_path: str, show_plots: bool = True, save_plots: bool = False, output_dir: str = "output"):
        """音楽ファイルの総合分析"""
        try:
            # オーディオ読み込み
            y, sr = self.load_audio(file_path)
            
            # ファイル名取得
            filename = Path(file_path).stem
            
            print(f"\n🎵 音楽分析開始: {filename}")
            print("-" * 50)
            
            figures = []
            
            # 1. 波形表示
            print("📊 波形を生成中...")
            fig_wave = self.plot_waveform(y, sr, f"波形 - {filename}")
            figures.append(("waveform", fig_wave))
            
            # 2. スペクトログラム
            print("🌈 スペクトログラムを生成中...")
            magnitude_db, times, freqs = self.create_spectrogram(y, sr)
            fig_spec = self.plot_spectrogram(magnitude_db, times, freqs, f"スペクトログラム - {filename}")
            figures.append(("spectrogram", fig_spec))
            
            # 3. メル・スペクトログラム
            print("🎼 メル・スペクトログラムを生成中...")
            mel_spec_db, mel_times = self.create_mel_spectrogram(y, sr)
            fig_mel = self.plot_mel_spectrogram(mel_spec_db, mel_times, sr, f"メル・スペクトログラム - {filename}")
            figures.append(("mel_spectrogram", fig_mel))
            
            # 4. クロマグラム（音名分析）
            print("🎹 クロマグラムを生成中...")
            fig_chroma = self.plot_chromagram(y, sr, f"クロマグラム - {filename}")
            figures.append(("chromagram", fig_chroma))
            
            # 保存
            if save_plots:
                output_path = Path(output_dir)
                output_path.mkdir(exist_ok=True)
                
                print(f"\n💾 画像を保存中... ({output_path})")
                for name, fig in figures:
                    save_path = output_path / f"{filename}_{name}.png"
                    fig.savefig(save_path, dpi=150, bbox_inches='tight')
                    print(f"   ✅ {save_path}")
            
            # 表示
            if show_plots:
                print(f"\n🖼️  画像を表示中...")
                plt.show()
            
            print(f"\n✅ 分析完了: {filename}")
            return figures
            
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
            raise

# 使用例とテスト用コード
if __name__ == "__main__":
    # 可視化オブジェクト作成
    visualizer = AudioSpectrumVisualizer()
    
    # テスト用ファイルパス（rekordboxのLocation形式）
    test_file = "file://localhost/Volumes/NO%20NAME/iTunes/iTunes%20Media/Music/LiSA/LOVER_S_MiLE/02%20oath%20sign.m4a"
    
    # または直接パス
    # test_file = "/Volumes/NO NAME/iTunes/iTunes Media/Music/LiSA/LOVER_S_MiLE/02 oath sign.m4a"
    
    try:
        # 音楽分析実行
        figures = visualizer.analyze_audio_file(
            test_file, 
            show_plots=True,
            save_plots=True,
            output_dir="spectrum_output"
        )
        
    except Exception as e:
        print(f"実行エラー: {e}")
        print("\n💡 ヒント:")
        print("- ファイルパスが正しいか確認してください")
        print("- 必要なライブラリがインストールされているか確認してください:")
        print("  pip install librosa matplotlib numpy")