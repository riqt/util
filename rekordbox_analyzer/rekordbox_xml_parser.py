import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
import html

class RekordboxXMLParser:
    def __init__(self, xml_file_path: str):
        self.xml_file_path = xml_file_path
        self.tree = None
        self.root = None
        self._load_xml()
    
    def _load_xml(self):
        """XMLファイルを読み込む"""
        try:
            self.tree = ET.parse(self.xml_file_path)
            self.root = self.tree.getroot()
        except Exception as e:
            raise Exception(f"XMLファイルの読み込みに失敗しました: {e}")
    
    def get_track_by_id(self, track_id: str) -> Optional[Dict]:
        """TrackIDで特定のトラックを取得"""
        collection = self.root.find('COLLECTION')
        if collection is None:
            return None
        
        for track in collection.findall('TRACK'):
            if track.get('TrackID') == track_id:
                return self._parse_track(track)
        return None
    
    def get_tracks_by_name(self, name: str) -> List[Dict]:
        """名前でトラックを検索"""
        collection = self.root.find('COLLECTION')
        if collection is None:
            return []
        
        tracks = []
        for track in collection.findall('TRACK'):
            if name.lower() in track.get('Name', '').lower():
                tracks.append(self._parse_track(track))
        return tracks
    
    def get_tracks_by_artist(self, artist: str) -> List[Dict]:
        """アーティスト名でトラックを検索"""
        collection = self.root.find('COLLECTION')
        if collection is None:
            return []
        
        tracks = []
        for track in collection.findall('TRACK'):
            if artist.lower() in track.get('Artist', '').lower():
                tracks.append(self._parse_track(track))
        return tracks
    
    def get_all_tracks(self) -> List[Dict]:
        """すべてのトラックを取得"""
        collection = self.root.find('COLLECTION')
        if collection is None:
            return []
        
        tracks = []
        for track in collection.findall('TRACK'):
            tracks.append(self._parse_track(track))
        return tracks
    
    def _parse_track(self, track_element) -> Dict:
        """TRACKエレメントから情報を抽出"""
        track_info = {
            'TrackID': track_element.get('TrackID'),
            'Name': html.unescape(track_element.get('Name', '')),
            'Artist': html.unescape(track_element.get('Artist', '')),
            'Composer': html.unescape(track_element.get('Composer', '')),
            'Album': html.unescape(track_element.get('Album', '')),
            'Grouping': track_element.get('Grouping'),
            'Genre': track_element.get('Genre'),
            'Kind': track_element.get('Kind'),
            'Size': track_element.get('Size'),
            'TotalTime': track_element.get('TotalTime'),
            'DiscNumber': track_element.get('DiscNumber'),
            'TrackNumber': track_element.get('TrackNumber'),
            'Year': track_element.get('Year'),
            'AverageBpm': track_element.get('AverageBpm'),
            'DateAdded': track_element.get('DateAdded'),
            'BitRate': track_element.get('BitRate'),
            'SampleRate': track_element.get('SampleRate'),
            'Comments': track_element.get('Comments'),
            'PlayCount': track_element.get('PlayCount'),
            'Rating': track_element.get('Rating'),
            'Location': track_element.get('Location'),
            'Remixer': track_element.get('Remixer'),
            'Tonality': track_element.get('Tonality'),
            'Label': track_element.get('Label'),
            'Mix': track_element.get('Mix'),
        }
        
        # TEMPOエレメントを取得
        tempo_elements = track_element.findall('TEMPO')
        if tempo_elements:
            track_info['TEMPO'] = []
            for tempo in tempo_elements:
                track_info['TEMPO'].append({
                    'Inizio': tempo.get('Inizio'),
                    'Bpm': tempo.get('Bpm'),
                    'Metro': tempo.get('Metro'),
                    'Battito': tempo.get('Battito')
                })
        
        # POSITION_MARKエレメントを取得
        position_marks = track_element.findall('POSITION_MARK')
        if position_marks:
            track_info['POSITION_MARK'] = []
            for mark in position_marks:
                track_info['POSITION_MARK'].append({
                    'Name': mark.get('Name'),
                    'Type': mark.get('Type'),
                    'Start': mark.get('Start'),
                    'Num': mark.get('Num'),
                    'Red': mark.get('Red'),
                    'Green': mark.get('Green'),
                    'Blue': mark.get('Blue')
                })
        
        return track_info
    
    def display_track_info(self, track_info: Dict):
        """トラック情報を見やすく表示"""
        if not track_info:
            print("トラック情報がありません")
            return
        
        print("=" * 80)
        print(f"🎵 TRACK INFORMATION")
        print("=" * 80)
        
        # 基本情報
        print(f"📀 基本情報:")
        print(f"   ID       : {track_info['TrackID']}")
        print(f"   曲名     : {track_info['Name']}")
        print(f"   アーティスト: {track_info['Artist']}")
        print(f"   作曲者   : {track_info['Composer']}")
        print(f"   アルバム : {track_info['Album']}")
        print(f"   ジャンル : {track_info['Genre']}")
        print(f"   レーベル : {track_info['Label']}")
        print()
        
        # ファイル情報
        print(f"💾 ファイル情報:")
        print(f"   種類     : {track_info['Kind']}")
        print(f"   サイズ   : {self._format_file_size(track_info['Size'])}")
        print(f"   再生時間 : {self._format_duration(track_info['TotalTime'])}")
        print(f"   ビットレート: {track_info['BitRate']} kbps")
        print(f"   サンプルレート: {track_info['SampleRate']} Hz")
        print(f"   場所     : {self._format_location(track_info['Location'])}")
        print()
        
        # アルバム情報
        print(f"💿 アルバム情報:")
        print(f"   年       : {track_info['Year']}")
        print(f"   ディスク番号: {track_info['DiscNumber']}")
        print(f"   トラック番号: {track_info['TrackNumber']}")
        print()
        
        # DJ情報
        print(f"🎧 DJ情報:")
        print(f"   平均BPM  : {track_info['AverageBpm']}")
        print(f"   キー     : {track_info['Tonality']}")
        print(f"   再生回数 : {track_info['PlayCount']}")
        print(f"   評価     : {self._format_rating(track_info['Rating'])}")
        print(f"   追加日   : {track_info['DateAdded']}")
        print()
        
        # TEMPO情報
        if track_info.get('TEMPO'):
            print(f"🎼 TEMPO情報:")
            for i, tempo in enumerate(track_info['TEMPO'], 1):
                start_time = self._format_time(tempo['Inizio'])
                print(f"   {i}: {start_time} - {tempo['Bpm']} BPM ({tempo['Metro']}, Beat:{tempo['Battito']})")
            print()
        
        # POSITION_MARK情報
        if track_info.get('POSITION_MARK'):
            print(f"📍 POSITION MARK情報:")
            cue_marks = []
            loop_marks = []
            
            for mark in track_info['POSITION_MARK']:
                start_time = self._format_time(mark['Start'])
                num = mark['Num']
                
                if num and num != '-1':
                    # Cue Point
                    color = self._format_color(mark.get('Red'), mark.get('Green'), mark.get('Blue'))
                    cue_marks.append(f"   Cue {num}: {start_time} {color}")
                else:
                    # Memory Cue or Beat Grid
                    loop_marks.append(f"   Memory: {start_time}")
            
            if cue_marks:
                print("   🎯 Cue Points:")
                for cue in sorted(cue_marks):
                    print(cue)
            
            if loop_marks:
                print("   🔄 Memory Cues:")
                for loop in loop_marks:
                    print(loop)
            print()
        
        # コメント
        if track_info.get('Comments'):
            print(f"💬 コメント:")
            print(f"   {track_info['Comments']}")
            print()
        
        print("=" * 80)
    
    def _format_file_size(self, size_str: str) -> str:
        """ファイルサイズを読みやすい形式に変換"""
        if not size_str:
            return "不明"
        
        try:
            size = int(size_str)
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            elif size < 1024 * 1024 * 1024:
                return f"{size / (1024 * 1024):.1f} MB"
            else:
                return f"{size / (1024 * 1024 * 1024):.1f} GB"
        except:
            return size_str
    
    def _format_duration(self, time_str: str) -> str:
        """再生時間を読みやすい形式に変換"""
        if not time_str:
            return "不明"
        
        try:
            seconds = int(time_str)
            minutes = seconds // 60
            seconds = seconds % 60
            return f"{minutes}:{seconds:02d}"
        except:
            return time_str
    
    def _format_time(self, time_str: str) -> str:
        """時間を読みやすい形式に変換"""
        if not time_str:
            return "0:00"
        
        try:
            seconds = float(time_str)
            minutes = int(seconds // 60)
            seconds = seconds % 60
            return f"{minutes}:{seconds:05.2f}"
        except:
            return time_str
    
    def _format_rating(self, rating_str: str) -> str:
        """評価を星形式に変換"""
        if not rating_str:
            return "未評価"
        
        try:
            rating = int(rating_str)
            if rating == 0:
                return "未評価"
            else:
                stars = "★" * rating + "☆" * (5 - rating)
                return f"{stars} ({rating}/5)"
        except:
            return rating_str
    
    def _format_color(self, red: str, green: str, blue: str) -> str:
        """RGB値から色の説明を生成"""
        if not all([red, green, blue]):
            return ""
        
        try:
            r, g, b = int(red), int(green), int(blue)
            if r > 200 and g < 100 and b < 100:
                return "(赤)"
            elif r < 100 and g > 200 and b < 100:
                return "(緑)"
            elif r < 100 and g < 100 and b > 200:
                return "(青)"
            elif r > 200 and g > 200 and b < 100:
                return "(黄)"
            elif r > 200 and g < 100 and b > 200:
                return "(紫)"
            elif r < 100 and g > 200 and b > 200:
                return "(シアン)"
            else:
                return f"(RGB:{r},{g},{b})"
        except:
            return ""
    
    def _format_location(self, location: str) -> str:
        """ファイルパスを読みやすく変換"""
        if not location:
            return "不明"
        
        # URL デコード
        import urllib.parse
        decoded = urllib.parse.unquote(location)
        
        # file://localhost を除去
        if decoded.startswith('file://localhost'):
            decoded = decoded[16:]
        
        return decoded

# 使用例
if __name__ == "__main__":
    # XMLファイルのパスを指定
    xml_path = "rekordbox_analyzer/rekordbox_xml/collections.xml"
    
    # パーサーを初期化
    parser = RekordboxXMLParser(xml_path)
    
    # 特定のTrackIDでトラックを取得して詳細表示
    track = parser.get_track_by_id("109686241")
    if track:
        parser.display_track_info(track)
    
    # LiSAの楽曲を検索
    lisa_tracks = parser.get_tracks_by_artist("LiSA")
    print(f"\nLiSAの楽曲を {len(lisa_tracks)} 曲見つけました:")
    for track in lisa_tracks[:3]:  # 最初の3曲を表示
        print(f"\n{'-' * 40}")
        parser.display_track_info(track)