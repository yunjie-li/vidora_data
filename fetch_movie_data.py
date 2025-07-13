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
    
    def get_trending_data(self) -> Dict[str, Any]:
        """获取热门趋势数据"""
        url = f"{self.base_url}/trending/all/week"
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
    
    def get_movie_details(self, movie_id: int) -> Dict[str, Any]:
        """获取电影详细信息"""
        url = f"{self.base_url}/movie/{movie_id}"
        params = {
            'api_key': self.api_key,
            'language': 'zh',
            # 修改：包含更多语言，包括 null 值图片
            'include_image_language': 'zh,en',
            'append_to_response': 'images,credits,videos'
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
            # 修改：包含更多语言，包括 null 值图片
            'include_image_language': 'zh,en',
            'append_to_response': 'images,credits,videos'
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
        params = {
            'append_to_response': 'keyword',
            'apikey': self.mdblist_api_key
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"  获取 mdblist 数据失败 ({media_type} {tmdb_id}): {e}")
            return None
    
    def filter_valid_ratings(self, ratings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """过滤评分数据，移除 value 为 null 的评分"""
        if not ratings:
            return []
        
        valid_ratings = []
        filtered_count = 0
        
        for rating in ratings:
            value = rating.get('value')
            if value is not None and value != '' and value != 0:
                valid_ratings.append(rating)
            else:
                filtered_count += 1
                source = rating.get('source', 'unknown')
                print(f"    ⚠️  过滤掉无效评分: {source} (value: {value})")
        
        if filtered_count > 0:
            print(f"    📊 过滤掉 {filtered_count} 个无效评分，保留 {len(valid_ratings)} 个有效评分")
        
        return valid_ratings
    
    def extract_mdblist_data(self, mdb_data: Dict[str, Any]) -> Dict[str, Any]:
        """从 mdblist 数据中提取需要的字段"""
        extracted = {}
        
        # 提取评分数据并过滤无效评分
        if 'ratings' in mdb_data and mdb_data['ratings']:
            print(f"    🔍 原始评分数据: {len(mdb_data['ratings'])} 个")
            valid_ratings = self.filter_valid_ratings(mdb_data['ratings'])
            if valid_ratings:
                extracted['ratings'] = valid_ratings
                
                # 统计各评分源
                sources = [rating.get('source', 'unknown') for rating in valid_ratings]
                sources_summary = {}
                for source in sources:
                    sources_summary[source] = sources_summary.get(source, 0) + 1
                
                sources_list = [f"{source}({count})" for source, count in sources_summary.items()]
                print(f"    ✅ 有效评分源: {', '.join(sources_list)}")
            else:
                print(f"    ❌ 没有找到有效的评分数据")
        
        # 提取认证信息
        if 'certification' in mdb_data and mdb_data['certification']:
            extracted['certification'] = mdb_data['certification']
        
        # 提取年龄评级
        if 'age_rating' in mdb_data and mdb_data['age_rating'] is not None:
            extracted['age_rating'] = mdb_data['age_rating']
        
        # 提取预告片链接
        if 'trailer' in mdb_data and mdb_data['trailer']:
            extracted['trailer'] = mdb_data['trailer']
        
        return extracted
    
    def filter_and_sort_images(self, images: List[Dict[str, Any]], image_type: str = "") -> List[Dict[str, Any]]:
        """
        修改后的图片过滤和排序逻辑
        - 保留 iso_639_1 为 'zh'、'en' 或 null 的图片
        - 按 vote_average 和 width 排序
        - 限制数量
        """
        if not images:
            print(f"    ❌ 没有{image_type}图片数据")
            return []
        
        print(f"    🔍 原始{image_type}图片: {len(images)} 张")
        
        # 修改过滤逻辑：包含 null 值图片（通用图片）
        filtered_images = []
        for img in images:
            iso_639_1 = img.get('iso_639_1')
            # 保留中文、英文和通用图片（null）
            if iso_639_1 in ['zh', 'en', None]:
                filtered_images.append(img)
        
        print(f"    📋 过滤后{image_type}图片: {len(filtered_images)} 张")
        
        if not filtered_images:
            print(f"    ❌ 过滤后没有可用的{image_type}图片")
            return []
        
        # 按语言分组
        zh_images = [img for img in filtered_images if img.get('iso_639_1') == 'zh']
        en_images = [img for img in filtered_images if img.get('iso_639_1') == 'en']
        null_images = [img for img in filtered_images if img.get('iso_639_1') is None]
        
        print(f"    🇨🇳 中文{image_type}: {len(zh_images)} 张")
        print(f"    🇺🇸 英文{image_type}: {len(en_images)} 张")
        print(f"    🌐 通用{image_type}: {len(null_images)} 张")
        
        # 改进的排序逻辑：优先按评分，再按尺寸
        def sort_images(img_list, limit=3):
            if not img_list:
                return []
            
            # 按 vote_average 降序，然后按 width 降序
            sorted_imgs = sorted(img_list, key=lambda x: (
                x.get('vote_average', 0),  # 优先评分
                x.get('width', 0)          # 再按尺寸
            ), reverse=True)
            
            return sorted_imgs[:limit]
        
        result_images = []
        
        # 优先选择中文图片
        if zh_images:
            sorted_zh = sort_images(zh_images, 2)
            result_images.extend(sorted_zh)
            print(f"    ✅ 选择了 {len(sorted_zh)} 张中文{image_type}图片")
        
        # 然后选择英文图片
        if en_images and len(result_images) < 4:
            remaining_slots = 4 - len(result_images)
            sorted_en = sort_images(en_images, remaining_slots)
            result_images.extend(sorted_en)
            print(f"    ✅ 选择了 {len(sorted_en)} 张英文{image_type}图片")
        
        # 最后选择通用图片
        if null_images and len(result_images) < 4:
            remaining_slots = 4 - len(result_images)
            sorted_null = sort_images(null_images, remaining_slots)
            result_images.extend(sorted_null)
            print(f"    ✅ 选择了 {len(sorted_null)} 张通用{image_type}图片")
        
        print(f"    🎯 最终选择: {len(result_images)} 张{image_type}图片")
        return result_images
    
    def merge_item_data(self, basic_item: Dict[str, Any], details: Dict[str, Any]) -> Dict[str, Any]:
        # 从基础数据开始
        merged_item = {
            'id': basic_item.get('id'),
            'media_type': basic_item.get('media_type'),
            'title': basic_item.get('title') or basic_item.get('name'),
            'original_title': basic_item.get('original_title') or basic_item.get('original_name'),
            'overview': basic_item.get('overview'),
            'poster_path': basic_item.get('poster_path'),
            'backdrop_path': basic_item.get('backdrop_path'),
            'vote_average': basic_item.get('vote_average'),
            'vote_count': basic_item.get('vote_count'),
            'popularity': basic_item.get('popularity'),
            'release_date': basic_item.get('release_date') or basic_item.get('first_air_date'),
            'genre_ids': basic_item.get('genre_ids', []),
            'adult': basic_item.get('adult', False),
        }
        
        # 添加详细信息字段
        if details:
            # 通用字段
            merged_item.update({
                'budget': details.get('budget'),
                'revenue': details.get('revenue'),
                'runtime': details.get('runtime'),
                'status': details.get('status'),
                'tagline': details.get('tagline'),
                'homepage': details.get('homepage'),
                'imdb_id': details.get('imdb_id'),
                'original_language': details.get('original_language'),
                'spoken_languages': details.get('spoken_languages', []),
                'production_companies': details.get('production_companies', []),
                'production_countries': details.get('production_countries', []),
                'genres': details.get('genres', []),
            })
            
            # 电视剧特有字段
            if basic_item.get('media_type') == 'tv':
                merged_item.update({
                    'first_air_date': details.get('first_air_date'),
                    'last_air_date': details.get('last_air_date'),
                    'number_of_episodes': details.get('number_of_episodes'),
                    'number_of_seasons': details.get('number_of_seasons'),
                    'episode_run_time': details.get('episode_run_time', []),
                    'in_production': details.get('in_production'),
                    'languages': details.get('languages', []),
                    'last_episode_to_air': details.get('last_episode_to_air'),
                    'next_episode_to_air': details.get('next_episode_to_air'),
                    'networks': details.get('networks', []),
                    'origin_country': details.get('origin_country', []),
                    'seasons': details.get('seasons', []),
                    'type': details.get('type'),
                })
            
            # 电影特有字段
            elif basic_item.get('media_type') == 'movie':
                merged_item.update({
                    'belongs_to_collection': details.get('belongs_to_collection'),
                    'release_date': details.get('release_date'),
                })
            
            # 演职员信息
            if 'credits' in details:
                credits = details['credits']
                merged_item.update({
                    'cast': credits.get('cast', [])[:10]
                })
            
            # 视频信息
            if 'videos' in details and details['videos'].get('results'):
                merged_item['videos'] = details['videos']['results'][:5]
            
            # 获取 mdblist 额外数据
            media_type = basic_item.get('media_type')
            media_id = basic_item.get('id')
            
            print(f"  获取 mdblist 评分数据...")
            mdb_data = self.get_mdblist_data(media_type, media_id)
            if mdb_data:
                mdb_extracted = self.extract_mdblist_data(mdb_data)
                merged_item.update(mdb_extracted)
                
                # 统计获取到的数据
                data_types = []
                if 'ratings' in mdb_extracted:
                    ratings_count = len(mdb_extracted['ratings'])
                    data_types.append(f"{ratings_count}个有效评分")
                if 'certification' in mdb_extracted:
                    data_types.append("认证信息")
                if 'age_rating' in mdb_extracted:
                    data_types.append("年龄评级")
                if 'trailer' in mdb_extracted:
                    data_types.append("预告片")
                
                if data_types:
                    print(f"  ✅ 获取到: {', '.join(data_types)}")
                else:
                    print(f"  ⚠️  未获取到有效的额外数据")
            
            # 图片信息处理 - 添加详细调试
            if 'images' in details:
                images = details['images']
                item_title = merged_item.get('title', 'Unknown')
                
                print(f"  🖼️  处理 {item_title} 的图片:")
                
                # 先检查原始图片数据
                backdrop_count = len(images.get('backdrops', []))
                poster_count = len(images.get('posters', []))
                logo_count = len(images.get('logos', []))
                
                print(f"    📊 原始图片统计: 背景 {backdrop_count} 张, 海报 {poster_count} 张, Logo {logo_count} 张")
                
                # 处理背景图片
                if 'backdrops' in images and images['backdrops']:
                    print(f"    🎨 处理背景图片...")
                    filtered_backdrops = self.filter_and_sort_images(images['backdrops'], '背景')
                    if filtered_backdrops:
                        merged_item['backdrops'] = filtered_backdrops
                        print(f"    ✅ 背景图片: 保存了 {len(filtered_backdrops)} 张")
                    else:
                        print(f"    ❌ 背景图片: 过滤后没有可用图片")
                else:
                    print(f"    ⚠️  没有背景图片数据")
                
                # 处理海报图片
                if 'posters' in images and images['posters']:
                    print(f"    🎨 处理海报图片...")
                    filtered_posters = self.filter_and_sort_images(images['posters'], '海报')
                    if filtered_posters:
                        merged_item['posters'] = filtered_posters
                        print(f"    ✅ 海报图片: 保存了 {len(filtered_posters)} 张")
                    else:
                        print(f"    ❌ 海报图片: 过滤后没有可用图片")
                else:
                    print(f"    ⚠️  没有海报图片数据")

                # 处理logo图片
                if 'logos' in images and images['logos']:
                    print(f"    🎨 处理Logo图片...")
                    filtered_logos = self.filter_and_sort_images(images['logos'], 'Logo')
                    if filtered_logos:
                        merged_item['logos'] = filtered_logos
                        print(f"    ✅ Logo图片: 保存了 {len(filtered_logos)} 张")
                    else:
                        print(f"    ❌ Logo图片: 过滤后没有可用图片")
                else:
                    print(f"    ⚠️  没有Logo图片数据")
            else:
                print(f"  ❌ 详细信息中没有图片数据")
        
        # 移除值为 None 的字段
        return {k: v for k, v in merged_item.items() if v is not None}
    
    def process_trending_items(self, trending_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """处理趋势数据，获取详细信息"""
        if 'results' not in trending_data:
            return []
        
        processed_items = []
        
        for item in trending_data['results']:
            media_type = item.get('media_type')
            item_id = item.get('id')
            
            if not item_id:
                continue
            
            # 获取详细信息
            if media_type == 'movie':
                details = self.get_movie_details(item_id)
            elif media_type == 'tv':
                details = self.get_tv_details(item_id)
            else:
                continue
            
            # 合并基础信息和详细信息
            merged_item = self.merge_item_data(item, details)
            
            if merged_item:
                processed_items.append(merged_item)
                print(f"✅ 已处理 {media_type}: {merged_item['title']} (ID: {item_id})")
                print("=" * 60)
        
        return processed_items
    
    def generate_homepage_data(self) -> List[Dict[str, Any]]:
        print("开始获取趋势数据...")
        trending_data = self.get_trending_data()
        
        if not trending_data:
            print("未能获取到趋势数据")
            return []
        
        print(f"获取到 {len(trending_data.get('results', []))} 个趋势项目")
        print("=" * 50)
        
        print("开始处理详细信息...")
        processed_items = self.process_trending_items(trending_data)
        
        return processed_items
    
    def save_to_file(self, data: List[Dict[str, Any]], filename: str = 'homepage.json'):
        """保存数据到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("=" * 50)
            print(f"✅ 数据已保存到 {filename}")
            print(f"📊 共保存了 {len(data)} 个项目")
            
            # 统计图片信息
            items_with_backdrops = sum(1 for item in data if 'backdrops' in item)
            items_with_posters = sum(1 for item in data if 'posters' in item)
            items_with_logos = sum(1 for item in data if 'logos' in item)
            
            total_backdrops = sum(len(item.get('backdrops', [])) for item in data)
            total_posters = sum(len(item.get('posters', [])) for item in data)
            total_logos = sum(len(item.get('logos', [])) for item in data)
            
            print(f"🖼️  图片统计:")
            print(f"   背景图片: {items_with_backdrops} 个项目，共 {total_backdrops} 张")
            print(f"   海报图片: {items_with_posters} 个项目，共 {total_posters} 张")
            print(f"   Logo图片: {items_with_logos} 个项目，共 {total_logos} 张")
            
            # 统计评分信息
            items_with_ratings = sum(1 for item in data if 'ratings' in item)
            items_with_certification = sum(1 for item in data if 'certification' in item)
            items_with_age_rating = sum(1 for item in data if 'age_rating' in item)
            items_with_trailer = sum(1 for item in data if 'trailer' in item)
            
            total_ratings = sum(len(item.get('ratings', [])) for item in data)
            
            print(f"⭐ 评分数据: {items_with_ratings} 个项目，共 {total_ratings} 个有效评分")
            print(f"🔒 认证信息: {items_with_certification} 个项目")
            print(f"🎯 年龄评级: {items_with_age_rating} 个项目")
            print(f"🎬 预告片链接: {items_with_trailer} 个项目")
            
            # 统计评分来源分布
            if total_ratings > 0:
                all_sources = []
                for item in data:
                    if 'ratings' in item:
                        for rating in item['ratings']:
                            source = rating.get('source', 'unknown')
                            all_sources.append(source)
                
                source_counts = {}
                for source in all_sources:
                    source_counts[source] = source_counts.get(source, 0) + 1
                
                print("📈 评分来源统计:")
                for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
                    print(f"   {source}: {count} 个")
            
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
    homepage_data = fetcher.generate_homepage_data()
    
    if homepage_data:
        fetcher.save_to_file(homepage_data)
        print("🎉 任务完成!")
    else:
        print("❌ 生成数据失败")

if __name__ == "__main__":
    main()
