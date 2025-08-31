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
    
    def get_movie_details(self, movie_id: int) -> Dict[str, Any]:
        """获取电影详细信息"""
        url = f"{self.base_url}/movie/{movie_id}"
        params = {
            'api_key': self.api_key,
            'language': 'zh',
            'append_to_response': 'credits,videos,images',
            'include_image_language': 'zh,en,null'
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
            'append_to_response': 'images',
            'include_image_language': 'zh,en,null'
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

    def filter_images(self, images: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        if not images:
            return images
    
        per_language_limit = 2  # 每种语言最多返回 2 条
    
        for key in ("backdrops", "posters", "logos"):
            raw = images.get(key, [])
    
            # 按语言分组
            grouped_by_lang = {
                "zh": [],
                "en": [],
                None: []
            }
    
            for img in raw:
                lang = img.get("iso_639_1")
                if lang in grouped_by_lang:
                    grouped_by_lang[lang].append(img)
    
            # 每种语言按 width 和 vote_average 排序，取前 per_language_limit 条
            filtered = []
            for lang, lang_images in grouped_by_lang.items():
                # 按 width 倒序排序，再按 vote_average 倒序排序
                sorted_lang = sorted(
                    lang_images,
                    key=lambda img: (-img.get("width", 0), -img.get("vote_average", 0))
                )
                filtered.extend(sorted_lang[:per_language_limit])  # 每种语言最多返回 per_language_limit 张图片
    
            # 合并后的结果按 vote_average 倒序排序，取前 6 条图片
            images[key] = sorted(
                filtered,
                key=lambda img: -img.get("vote_average", 0)
            )[:6]  # 每个分类最多返回 6 张图片
    
        return images
    
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

            # 图片信息 - 使用新的过滤和排序逻辑
            if 'images' in details:
                detail_fields['images'] = self.filter_images(details["images"])
            
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
                    main_sources = ['imdb', "trakt", 'metacritic', "tomatoes", 'popcorn', "tmdb", 'letterboxd']
                    main_ratings = {}
                    
                    for rating in valid_ratings:
                        source = rating.get('source')
                        value = rating.get('value')
                        if source in main_sources and value is not None:
                            main_ratings[source] = round(float(value), 1)
                    
                    if main_ratings:
                        compressed['rating'] = main_ratings
            
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
                
        return processed_items
    
    def generate_homepage_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """生成主页数据"""
        homepage_data = {}
        
        # 数据源配置 (key, name, fetch_func, media_type, limit, fetch_details)
        data_sources = [
            ('trending', '趋势数据', lambda: self.get_trending_data('week'), None, 15, True),
            # ('popularMovie', '热门电影', lambda: self.get_popular_movies(), 'movie', 20, True),
            # ('popularTv', '热门电视剧', lambda: self.get_popular_tv(), 'tv', 20, True),
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

            # 保存一个可读版本用于调试（可选）
            debug_filename = filename.replace('.json', '_debug.json')
            with open(debug_filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
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
