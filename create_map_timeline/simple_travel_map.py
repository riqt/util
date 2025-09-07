import json
import folium
from datetime import datetime
import numpy as np

class SimpleTravelMap:
    def __init__(self, timeline_file):
        """Googleタイムラインから旅行マップを作成"""
        with open(timeline_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.places = []
        self.routes = []
        self.extract_data()
    
    def extract_data(self):
        """必要なデータを抽出"""
        # データがリスト形式の場合はそのまま使用
        timeline_objects = self.data if isinstance(self.data, list) else self.data.get('timelineObjects', [])
        
        for item in timeline_objects:
            # Records形式: visit (訪問場所)
            if 'visit' in item:
                visit = item['visit']
                candidate = visit.get('topCandidate', {})
                
                # 座標データを抽出 (geo:lat,lng形式)
                geo_str = candidate.get('placeLocation', candidate.get('location', ''))
                if geo_str and geo_str.startswith('geo:'):
                    coords = geo_str[4:].split(',')
                    if len(coords) >= 2:
                        lat, lng = float(coords[0]), float(coords[1])
                        
                        self.places.append({
                            'name': candidate.get('semanticType', 'Unknown'),
                            'lat': lat,
                            'lng': lng,
                            'time': item.get('startTime', ''),
                            'address': candidate.get('address', '')
                        })
            
            # Records形式: activity (移動)
            elif 'activity' in item:
                activity = item['activity']
                start_geo = activity.get('start', '')
                end_geo = activity.get('end', '')
                
                if start_geo.startswith('geo:') and end_geo.startswith('geo:'):
                    start_coords = start_geo[4:].split(',')
                    end_coords = end_geo[4:].split(',')
                    
                    if len(start_coords) >= 2 and len(end_coords) >= 2:
                        candidate = activity.get('topCandidate', {})
                        activity_type = candidate.get('type', 'UNKNOWN').upper()
                        
                        self.routes.append({
                            'start_lat': float(start_coords[0]),
                            'start_lng': float(start_coords[1]),
                            'end_lat': float(end_coords[0]),
                            'end_lng': float(end_coords[1]),
                            'type': activity_type
                        })
            
            # 従来のtimelineObjects形式もサポート
            elif 'placeVisit' in item and 'location' in item['placeVisit']:
                place = item['placeVisit']
                location = place['location']
                
                self.places.append({
                    'name': location.get('name', 'Unknown'),
                    'lat': location.get('latitudeE7', 0) / 1e7,
                    'lng': location.get('longitudeE7', 0) / 1e7,
                    'time': place.get('duration', {}).get('startTimestamp', ''),
                    'address': location.get('address', '')
                })
            
            # 従来のactivitySegment形式もサポート
            elif 'activitySegment' in item:
                segment = item['activitySegment']
                if 'startLocation' in segment and 'endLocation' in segment:
                    self.routes.append({
                        'start_lat': segment['startLocation'].get('latitudeE7', 0) / 1e7,
                        'start_lng': segment['startLocation'].get('longitudeE7', 0) / 1e7,
                        'end_lat': segment['endLocation'].get('latitudeE7', 0) / 1e7,
                        'end_lng': segment['endLocation'].get('longitudeE7', 0) / 1e7,
                        'type': segment.get('activityType', 'UNKNOWN')
                    })
    
    def create_map(self, start_date=None, end_date=None, show_routes=True):
        """旅行マップを作成"""
        # 日付でフィルター
        filtered_places = self.filter_by_date(start_date, end_date)
        
        if not filtered_places:
            print("指定期間にデータがありません")
            return None
        
        # 地図の中心を計算
        center_lat = np.mean([p['lat'] for p in filtered_places])
        center_lng = np.mean([p['lng'] for p in filtered_places])
        
        # 地図作成
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=12,
            tiles='OpenStreetMap'
        )
        
        # 訪問場所をマーカーで表示
        for i, place in enumerate(filtered_places):
            # 時刻を読みやすく変換
            time_str = self.format_time(place['time'])
            
            # ポップアップ内容
            popup_text = f"""
            <b>{place['name']}</b><br>
            📅 {time_str}<br>
            📍 {place['address'][:50]}...
            """
            
            # マーカー追加（番号付き）
            folium.Marker(
                location=[place['lat'], place['lng']],
                popup=folium.Popup(popup_text, max_width=250),
                tooltip=f"{i+1}. {place['name']}",
                icon=folium.Icon(
                    color='red', 
                    icon='info-sign',
                    prefix='glyphicon'
                )
            ).add_to(m)
            
            # 番号ラベルを追加
            folium.map.Marker(
                [place['lat'], place['lng']],
                icon=folium.DivIcon(
                    html=f"<div style='font-size: 12pt; color: white; font-weight: bold;'>{i+1}</div>",
                    icon_size=(20, 20),
                    icon_anchor=(10, 10),
                )
            ).add_to(m)
        
        # 移動ルートを表示
        if show_routes and self.routes:
            for route in self.routes:
                color = self.get_route_color(route['type'])
                folium.PolyLine(
                    locations=[[route['start_lat'], route['start_lng']], 
                              [route['end_lat'], route['end_lng']]],
                    color=color,
                    weight=3,
                    opacity=0.7,
                    popup=f"移動: {route['type']}"
                ).add_to(m)
        
        # 訪問順序の線
        if len(filtered_places) > 1:
            coordinates = [[p['lat'], p['lng']] for p in filtered_places]
            folium.PolyLine(
                coordinates,
                color='blue',
                weight=2,
                opacity=0.8,
                dash_array='10, 5'
            ).add_to(m)
        
        return m
    
    def filter_by_date(self, start_date, end_date):
        """日付範囲でフィルター"""
        if not start_date or not end_date:
            return self.places
        
        filtered = []
        for place in self.places:
            place_date = self.extract_date(place['time'])
            if place_date and start_date <= place_date <= end_date:
                filtered.append(place)
        
        return filtered
    
    def extract_date(self, timestamp):
        """タイムスタンプから日付を抽出"""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.date()
        except:
            return None
    
    def format_time(self, timestamp):
        """時刻を読みやすい形式に変換"""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime('%m/%d %H:%M')
        except:
            return '時刻不明'
    
    def get_route_color(self, activity_type):
        """移動手段に応じた色を返す"""
        colors = {
            'WALKING': 'green',
            'CYCLING': 'blue', 
            'IN_VEHICLE': 'red',
            'FLYING': 'purple',
            'IN_PASSENGER_VEHICLE': 'orange',
            'DRIVING': 'red',
            'RUNNING': 'darkgreen'
        }
        return colors.get(activity_type.upper(), 'gray')


# 使用例
def create_travel_map(json_file, output_file='travel_map.html', 
                     start_date=None, end_date=None):
    """
    使いやすい関数版
    
    Parameters:
    json_file: GoogleタイムラインのJSONファイルパス
    output_file: 出力HTMLファイル名
    start_date: 開始日 (datetime.date形式)
    end_date: 終了日 (datetime.date形式)
    """
    
    travel_map = SimpleTravelMap(json_file)
    map_obj = travel_map.create_map(start_date, end_date)
    
    if map_obj:
        map_obj.save(output_file)
        print(f"旅行マップが {output_file} に保存されました")
        
        # 統計情報も表示
        filtered_places = travel_map.filter_by_date(start_date, end_date)
        print(f"\n📊 旅行統計:")
        print(f"  訪問場所数: {len(filtered_places)}箇所")
        
        if filtered_places:
            dates = [travel_map.extract_date(p['time']) for p in filtered_places]
            dates = [d for d in dates if d]
            if dates:
                print(f"  期間: {min(dates)} 〜 {max(dates)}")
                print(f"  日数: {(max(dates) - min(dates)).days + 1}日")
        
        return map_obj
    else:
        print("マップを作成できませんでした")
        return None


# 簡単な使用例
if __name__ == "__main__":
    from datetime import date
    
    # 2025/08/12から2025/08/15の期間で限定
    create_travel_map(
        'create_map_timeline/location-history.json',
        'create_map_timeline/travel_map_2025_08.html',
        start_date=date(2025, 8, 12),
        end_date=date(2025, 8, 15)
    )
