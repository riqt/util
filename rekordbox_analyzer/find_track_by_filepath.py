#!/usr/bin/env python3
import sys
import urllib.parse
from rekordbox_xml_parser import RekordboxXMLParser

class TrackByFilePathFinder:
    def __init__(self, xml_file_path: str):
        self.parser = RekordboxXMLParser(xml_file_path)
    
    def find_track_by_filepath(self, target_filepath: str) -> dict:
        """指定されたファイルパスに対応するトラック情報を検索"""
        # ファイルパスを正規化（URL エンコードされた形式に変換）
        normalized_target = self._normalize_filepath(target_filepath)
        
        # すべてのトラックを取得
        all_tracks = self.parser.get_all_tracks()
        
        # ファイルパスでマッチングを試行
        for track in all_tracks:
            if track.get('Location'):
                track_location = track['Location']
                normalized_location = self._normalize_filepath(track_location)
                
                # 完全一致チェック
                if normalized_target == normalized_location:
                    return track
                
                # デコードされた形式でもチェック
                decoded_location = urllib.parse.unquote(track_location)
                if decoded_location.startswith('file://localhost'):
                    decoded_location = decoded_location[16:]
                
                decoded_target = urllib.parse.unquote(target_filepath)
                if decoded_target.startswith('file://localhost'):
                    decoded_target = decoded_target[16:]
                
                if decoded_target == decoded_location:
                    return track
        
        return None
    
    def _normalize_filepath(self, filepath: str) -> str:
        """ファイルパスを正規化"""
        # file://localhost プレフィックスを統一
        if not filepath.startswith('file://localhost'):
            if filepath.startswith('/'):
                filepath = 'file://localhost' + filepath
            else:
                filepath = 'file://localhost/' + filepath
        
        # URL エンコード
        # file://localhost 部分は除いてエンコード
        prefix = 'file://localhost'
        path_part = filepath[len(prefix):]
        
        # パス部分をエンコード（ただし既にエンコードされている場合は再エンコードしない）
        try:
            # デコードしてから再エンコードしてみる
            decoded = urllib.parse.unquote(path_part)
            encoded = urllib.parse.quote(decoded, safe='/')
        except:
            # エンコード/デコードに失敗した場合はそのまま使用
            encoded = path_part
        
        return prefix + encoded

def main():
    target_filepath = "file://localhost/Volumes/NO%20NAME/iTunes/iTunes%20Media/Music/LiSA/LOVER_S_MiLE/02%20oath%20sign.m4a"
    xml_path = "rekordbox_analyzer/rekordbox_xml/collections.xml"
    
    try:
        finder = TrackByFilePathFinder(xml_path)
        track = finder.find_track_by_filepath(target_filepath)
        
        if track:
            print("🎵 マッチした楽曲を見つけました！")
            print()
            finder.parser.display_track_info(track)
        else:
            print("❌ 指定されたファイルパスに対応する楽曲が見つかりませんでした。")
            print(f"検索対象: {target_filepath}")
            
    except Exception as e:
        print(f"エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()