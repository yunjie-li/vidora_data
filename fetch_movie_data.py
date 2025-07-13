import requests
import json
import os
from typing import Dict, List, Any, Optional

class MovieDataFetcher:
    def __init__(self, api_key: str, mdblist_api_key: str):
        self.api_key = api_key
        self.mdblist_api_key = mdblist_api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.mdblist_base_url = "https://api.mdblist.com/tmdb"
        self.session = requests.Session()
    
    def get_trending_data(self, time_window: str = 'week') -> Dict[str, Any]:
        """获取热门趋势数据"""
        url = f"{self.base_url}/trending/all/{time_window}"
        params = {
            'api_key': self.api_key,
            'language': 'zh'
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"获取趋势数据失败: {e}")
            return {}
    
    def get_popular_movies(self, page: int = 1) -> Dict[str, Any]:
        """获取热门电影"""
        url = f"{self.base_url}/movie/popular"
        params = {
            'api_key': self.api_key,
            'language': 'zh',
            'page': page
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"获取热门电影失败: {e}")
            return {}
    
    def get_popular_tv(self, page: int = 1) -> Dict[str, Any]:
        """获取热门电视剧"""
        url = f"{self.base_url}/tv/popular"
        params = {
            'api_key': self.api_key,
            'language': 'zh',
            'page': page
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"获取热门电视剧失败: {e}")
            return {}
    
    def get_top_rated_movies(self, page: int = 1) -> Dict[str, Any]:
        """获取高评分电影"""
        url = f"{self.base_url}/movie/top_rated"
        params = {
            'api_key': self.api_key,
            'language': 'zh',
            'page': page
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"获取高评分电影失败: {e}")
            return {}
    
    def get_top_rated_tv(self, page: int = 1) -> Dict[str, Any]:
        """获取高评分电视剧"""
        url = f"{self.base_url}/tv/top_rated"
        params = {
            'api_key': self.api_key,
            'language': 'zh',
            'page': page
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"获取高评分电视剧失败: {e}")
            return {}
    
    def get_now_playing_movies(self, page: int = 1) -> Dict[str, Any]:
        """获取正在上映的电影"""
        url = f"{self.base_url}/movie/now_playing"
        params = {
            'api_key': self.api_key,
            'language': 'zh',
            'page': page
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"获取正在上映电影失败: {e}")
            return {}
    
    def get_upcoming_movies(self, page: int = 1) -> Dict[str, Any]:
        """获取即将上映的电影"""
        url = f"{self.base_url}/movie/upcoming"
        params = {
            'api_key': self.api_key,
            'language': 'zh',
            'page': page
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"获取即将上映电影失败: {e}")
            return {}
    
    def get_movie_details(self, movie_id: int) -> Dict[str, Any]:
        """获取电影详细信息"""
        url = f"{self.base_url}/movie/{movie_id}"
        params = {
            'api_key': self.api_key,
            'language': 'zh',
            'append_to_response': 'credits,videos'
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"获取电影 {movie_id} 详细信息失败: {e}")
            return {}
    
    def get_tv_details(self, tv_id: int) -> Dict[str, Any]:
        """获取电视剧详细信息"""
        url = f"{self.base_url}/tv/{tv_id}"
        params = {
            'api_key': self.api_key,
            'language': 'zh',
            'append_to_response': 'credits,videos'
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"获取电视剧 {tv_id} 详细信息失败: {e}")
            return {}
    
    def get_mdblist_data(self, media_type: str, tmdb_id: int) -> Optional[Dict[str, Any]]:
        """从 mdblist API 获取额外数据"""
        mdb_media_type = 'show' if media_type == 'tv' else 'movie'
        
        url = f"{self.mdblist_base_url}/{mdb_media_type}/{tmdb_id}"
        params = {'apikey': self.mdblist_api_key}
        
        try:
            response = self.session.get(url, params=params, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None
    
    def filter_valid_ratings(self, ratings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """过滤评分数据，移除 value 为 null 的评分"""
        if not ratings:
            return []
        
        valid_ratings = []
        for rating in ratings:
            value = rating.get('value')
            if value is not None and value != '' and value != 0:
                valid_ratings.append(rating)
        
        return valid_ratings
    
    def compress_cast_data(self, cast: List[Dict[str, Any]], limit: int = 8) -> List[Dict[str, Any]]:
        """压缩演员数据，只保留核心信息"""
        if not cast:
            return []
        
        compressed_cast = []
        for actor in cast[:limit]:  # 限制演员数量
            compressed_actor = {
                'id': actor.get('id'),
                'name': actor.get('name'),
                'character': actor.get('character'),
                'profile_path': actor.get('profile_path')
            }
            # 移除空值
            compressed_actor = {k: v for k, v in compressed_actor.items() if v is not None and v != ''}
            if compressed_actor:
                compressed_cast.append(compressed_actor)
        
        return compressed_cast
    
    def compress_crew_data(self, crew: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """压缩制作人员数据，只保留导演和重要职位"""
        if not crew:
            return []
        
        important_jobs = ['Director', 'Producer', 'Executive Producer', 'Screenplay', 'Writer']
        compressed_crew = []
        
        for person in crew:
            job = person.get('job', '')
            if job in important_jobs:
                compressed_person = {
                    'id': person.get('id'),
                    'name': person.get('name'),
                    'job': job,
                    'profile_path': person.get('profile_path')
                }
                # 移除空值
                compressed_person = {k: v for k, v in compressed_person.items() if v is not None and v != ''}
                if compressed_person:
                    compressed_crew.append(compressed_person)
        
        return compressed_crew
    
    def compress_videos_data(self, videos: List[Dict[str, Any]], limit: int = 3) -> List[Dict[str, Any]]:
        """压缩视频数据"""
        if not videos:
            return []
        
        # 优先选择预告片和花絮
        priority_types = ['Trailer', 'Teaser', 'Clip']
        compressed_videos = []
        
        # 先添加优先类型的视频
        for video_type in priority_types:
            for video in videos:
                if video.get('type') == video_type and len(compressed_videos) < limit:
                    compressed_video = {
                        'id': video.get('id'),
                        'key': video.get('key'),
                        'name': video.get('name'),
                        'type': video.get('type'),
                        'site': video.get('site')
                    }
                    compressed_videos.append(compressed_video)
        
        # 如果还没达到限制，添加其他视频
        if len(compressed_videos) < limit:
            for video in videos:
                if len(compressed_videos) >= limit:
                    break
                if video.get('type') not in priority_types:
                    compressed_video = {
                        'id': video.get('id'),
                        'key': video.get('key'),
                        'name': video.get('name'),
                        'type': video.get('type'),
                        'site': video.get('site')
                    }
                    compressed_videos.append(compressed_video)
        
        return compressed_videos
    
    def compress_item_data(self, item: Dict[str, Any], details: Dict[str, Any] = None, media_type: str = None) -> Dict[str, Any]:
        """
        压缩单个项目数据，保留重要字段
        """
        # 确定媒体类型
        if not media_type:
            media_type = item.get('media_type', 'movie')
        
        # 基础字段（必需）
        compressed = {
            'id': item.get('id'),
            'media_type': media_type,
            'title': item.get('title') or item.get('name'),
            'original_title': item.get('original_title') or item.get('original_name'),
            'poster_path': item.get('poster_path'),
            'backdrop_path': item.get('backdrop_path'),
            'overview': item.get('overview', '')[:2000] if item.get('overview') else '',  # 适当限制简介长度
            'vote_average': round(item.get('vote_average', 0), 1),
            'vote_count': item.get('vote_count', 0),
            'popularity': round(item.get('popularity', 0), 1),
            'release_date': item.get('release_date') or item.get('first_air_date'),
            'genre_ids': item.get('genre_ids', []),
            'adult': item.get('adult', False),
            'original_language': item.get('original_language')
        }
        
        # 如果有详细信息，添加更多字段
        if details:
            # 通用详细字段
            detail_fields = {
                'budget': details.get('budget'),
                'revenue': details.get('revenue'),
                'runtime': details.get('runtime'),
                'status': details.get('status'),
                'tagline': details.get('tagline'),
                'homepage': details.get('homepage'),
                'imdb_id': details.get('imdb_id'),
                'spoken_languages': details.get('spoken_languages', []),
                'production_companies': details.get('production_companies', [])[:5],
                'production_countries': details.get('production_countries', []),
                'genres': details.get('genres', [])
            }
            
            # 电视剧特有字段
            if media_type == 'tv':
                tv_fields = {
                    'first_air_date': details.get('first_air_date'),
                    'last_air_date': details.get('last_air_date'),
                    'number_of_episodes': details.get('number_of_episodes'),
                    'number_of_seasons': details.get('number_of_seasons'),
                    'episode_run_time': details.get('episode_run_time', []),
                    'in_production': details.get('in_production'),
                    'networks': details.get('networks', [])[:5],
                    'origin_country': details.get('origin_country', []),
                    'type': details.get('type')
                }
                detail_fields.update(tv_fields)
            
            # 电影特有字段
            elif media_type == 'movie':
                movie_fields = {
                    'belongs_to_collection': details.get('belongs_to_collection')
                }
                detail_fields.update(movie_fields)
            
            # 演职员信息（重要！）
            if 'credits' in details:
                credits = details['credits']
                if 'cast' in credits:
                    compressed_cast = self.compress_cast_data(credits['cast'])
                    if compressed_cast:
                        detail_fields['cast'] = compressed_cast
                
                if 'crew' in credits:
                    compressed_crew = self.compress_crew_data(credits['crew'])
                    if compressed_crew:
                        detail_fields['crew'] = compressed_crew
            
            # 视频信息
            if 'videos' in details and details['videos'].get('results'):
                compressed_videos = self.compress_videos_data(details['videos']['results'])
                if compressed_videos:
                    detail_fields['videos'] = compressed_videos
            
            # 只添加有值的详细字段
            for key, value in detail_fields.items():
                if value is not None and value != '' and value != []:
                    compressed[key] = value
        
        # 获取并压缩 mdblist 数据（只保留主要评分源）
        mdb_data = self.get_mdblist_data(media_type, item.get('id'))
        if mdb_data:
            # 压缩评分数据 - 只保留主要评分源
            if 'ratings' in mdb_data and mdb_data['ratings']:
                valid_ratings = self.filter_valid_ratings(mdb_data['ratings'])
                if valid_ratings:
                    # 只保留主要评分源
                    main_sources = ['imdb', 'metacritic', "tomatoes", 'popcorn', "tmdb", 'letterboxd']
                    main_ratings = {}
                    
                    for rating in valid_ratings:
                        source = rating.get('source')
                        value = rating.get('value')
                        if source in main_sources and value is not None:
                            main_ratings[source] = round(float(value), 1)
                    
                    if main_ratings:
                        compressed['external_ratings'] = main_ratings
            
            # 其他重要的 mdblist 数据
            if mdb_data.get('certification'):
                compressed['certification'] = mdb_data['certification']
            if mdb_data.get('age_rating'):
                compressed['age_rating'] = mdb_data['age_rating']
            if mdb_data.get('trailer'):
                compressed['trailer'] = mdb_data['trailer']
        
        # 移除空值
        return {k: v for k, v in compressed.items() if v is not None and v != '' and v != []}
    
    def process_data_list(self, data: Dict[str, Any], media_type: str = None, limit: int = 20, fetch_details: bool = True) -> List[Dict[str, Any]]:
        """处理数据列表，返回压缩后的数据，过滤掉没有overview的项目"""
        if 'results' not in data:
            return []
        
        processed_items = []
        items = data['results']
        
        # 先过滤掉没有overview的项目
        filtered_items = []
        for item in items:
            overview = item.get('overview', '').strip()
            if overview:  # 只保留有overview且不为空的项目
                filtered_items.append(item)
        
        print(f"  📋 原始数据: {len(items)} 个项目")
        print(f"  ✅ 过滤后: {len(filtered_items)} 个项目 (移除了 {len(items) - len(filtered_items)} 个无简介项目)")
        
        # 限制数量
        filtered_items = filtered_items[:limit]
        
        for i, item in enumerate(filtered_items, 1):
            # 确定媒体类型
            item_media_type = media_type or item.get('media_type', 'movie')
            item_id = item.get('id')
            item_title = item.get('title') or item.get('name', 'Unknown')
            
            print(f"  处理 {i}/{len(filtered_items)}: {item_title} (ID: {item_id})")
            
            # 获取详细信息
            details = None
            if fetch_details and item_id:
                if item_media_type == 'movie':
                    details = self.get_movie_details(item_id)
                elif item_media_type == 'tv':
                    details = self.get_tv_details(item_id)
            
            # 压缩数据
            compressed_item = self.compress_item_data(item, details, item_media_type)
            
            if compressed_item:
                processed_items.append(compressed_item)
                
                # 显示获取到的信息
                info_parts = []
                if 'cast' in compressed_item:
                    info_parts.append(f"{len(compressed_item['cast'])}个演员")
                if 'crew' in compressed_item:
                    info_parts.append(f"{len(compressed_item['crew'])}个制作人员")
                if 'external_ratings' in compressed_item:
                    rating_sources = list(compressed_item['external_ratings'].keys())
                    info_parts.append(f"评分源: {', '.join(rating_sources)}")
                if 'videos' in compressed_item:
                    info_parts.append(f"{len(compressed_item['videos'])}个视频")
                if 'trailer' in compressed_item:
                    info_parts.append("预告片")
                
                if info_parts:
                    print(f"    ✅ 获取到: {', '.join(info_parts)}")
        
        return processed_items
    
    def generate_homepage_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """生成主页数据"""
        homepage_data = {}
        
        # 数据源配置 (key, name, fetch_func, media_type, limit, fetch_details)
        data_sources = [
            ('trending', '趋势数据', lambda: self.get_trending_data('week'), None, 15, True),
            ('popularMovie', '热门电影', lambda: self.get_popular_movies(), 'movie', 20, True),
            ('popularTv', '热门电视剧', lambda: self.get_popular_tv(), 'tv', 20, True),
            ('topRatedMovie', '高评分电影', lambda: self.get_top_rated_movies(), 'movie', 15, True),
            ('topRatedTv', '高评分电视剧', lambda: self.get_top_rated_tv(), 'tv', 15, True),
            ('nowPlaying', '正在上映', lambda: self.get_now_playing_movies(), 'movie', 15, False),  # 正在上映不需要详细信息
            ('upcoming', '即将上映', lambda: self.get_upcoming_movies(), 'movie', 15, False)  # 即将上映不需要详细信息
        ]
        
        for key, name, fetch_func, media_type, limit, fetch_details in data_sources:
            print(f"📥 获取{name}...")
            try:
                raw_data = fetch_func()
                if raw_data:
                    processed_data = self.process_data_list(raw_data, media_type, limit, fetch_details)
                    homepage_data[key] = processed_data
                    print(f"✅ {name}: {len(processed_data)} 个项目")
                else:
                    homepage_data[key] = []
                    print(f"❌ {name}: 获取失败")
            except Exception as e:
                print(f"❌ {name} 处理失败: {e}")
                homepage_data[key] = []
            
            print("-" * 40)
        
        return homepage_data
    
    def save_to_file(self, data: Dict[str, List[Dict[str, Any]]], filename: str = 'homepage.json'):
        """保存数据到文件（压缩格式）"""
        try:
            # 保存压缩版本（无缩进，无空格）
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
            
            # 计算文件大小
            file_size = os.path.getsize(filename)
            file_size_mb = file_size / (1024 * 1024)
            
            print("=" * 60)
            print(f"✅ 数据已保存到 {filename}")
            print(f"📁 文件大小: {file_size:,} 字节 ({file_size_mb:.2f} MB)")
            
            # 统计各类型数据
            total_items = 0
            for category, items in data.items():
                count = len(items)
                total_items += count
                print(f"📊 {category}: {count} 个项目")
            
            print(f"🎯 总计: {total_items} 个项目")
            
            # 统计详细信息
            items_with_cast = 0
            items_with_crew = 0
            items_with_ratings = 0
            items_with_videos = 0
            items_with_trailers = 0
            total_cast = 0
            total_crew = 0
            
            for category, items in data.items():
                for item in items:
                    if 'cast' in item:
                        items_with_cast += 1
                        total_cast += len(item['cast'])
                    if 'crew' in item:
                        items_with_crew += 1
                        total_crew += len(item['crew'])
                    if 'external_ratings' in item:
                        items_with_ratings += 1
                    if 'videos' in item:
                        items_with_videos += 1
                    if 'trailer' in item:
                        items_with_trailers += 1
            
            print(f"👥 演员信息: {items_with_cast} 个项目，共 {total_cast} 个演员")
            print(f"🎬 制作人员: {items_with_crew} 个项目，共 {total_crew} 个制作人员")
            print(f"⭐ 外部评分: {items_with_ratings} 个项目")
            print(f"📹 视频信息: {items_with_videos} 个项目")
            print(f"🎞️  预告片: {items_with_trailers} 个项目")
            
            # 保存一个可读版本用于调试（可选）
            debug_filename = filename.replace('.json', '_debug.json')
            with open(debug_filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            debug_size = os.path.getsize(debug_filename)
            compression_ratio = (1 - file_size / debug_size) * 100
            print(f"🗜️  压缩率: {compression_ratio:.1f}% (调试版: {debug_size:,} 字节)")
            
        except Exception as e:
            print(f"❌ 保存文件失败: {e}")

def main():
    # 从环境变量获取 API 密钥
    tmdb_api_key = os.getenv('TMDB_API_KEY', '')
    mdblist_api_key = os.getenv('MDBLIST_API_KEY', '')
    
    if not tmdb_api_key:
        print("❌ 错误: 未找到 TMDB API 密钥")
        return
    
    if not mdblist_api_key:
        print("❌ 错误: 未找到 MDBLIST API 密钥")
        return
    
    fetcher = MovieDataFetcher(tmdb_api_key, mdblist_api_key)
    
    print("🎬 开始生成主页数据...")
    print("=" * 60)
    
    homepage_data = fetcher.generate_homepage_data()
    
    if homepage_data:
        fetcher.save_to_file(homepage_data)
        print("🎉 任务完成!")
    else:
        print("❌ 生成数据失败")

if __name__ == "__main__":
    main()
