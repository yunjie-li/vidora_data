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
          'language': 'zh',
          'append_to_response': 'images'
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
      """
      从 mdblist API 获取额外数据
      media_type: 'movie' 或 'tv'
      tmdb_id: TMDB ID
      """
      # 转换媒体类型：tv -> show
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
  
  def extract_mdblist_data(self, mdb_data: Dict[str, Any]) -> Dict[str, Any]:
      """从 mdblist 数据中提取需要的字段"""
      extracted = {}
      
      # 提取评分数据
      if 'ratings' in mdb_data and mdb_data['ratings']:
          extracted['ratings'] = mdb_data['ratings']
      
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
      过滤和排序图片
      - 只保留 iso_639_1='zh' 或 iso_639_1='en' 的图片
      - 按 width 倒序排序
      - 每个 iso_639_1 类型取前2张
      """
      if not images:
          return []
      
      # 过滤图片：只保留中文或英文的图片
      filtered_images = []
      for img in images:
          iso_639_1 = img.get('iso_639_1')
          if iso_639_1 == 'zh' or iso_639_1 == 'en':
              filtered_images.append(img)
      
      if not filtered_images:
          return []
      
      # 按 iso_639_1 分组
      zh_images = [img for img in filtered_images if img.get('iso_639_1') == 'zh']
      en_images = [img for img in filtered_images if img.get('iso_639_1') == 'en']
      
      # 按 width 倒序排序并取前2张
      def sort_by_width_desc(img_list):
          return sorted(img_list, key=lambda x: x.get('width', 0), reverse=True)[:2]
      
      result_images = []
      
      # 处理中文图片
      if zh_images:
          sorted_zh = sort_by_width_desc(zh_images)
          result_images.extend(sorted_zh)
          print(f"  找到 {len(zh_images)} 张中文{image_type}图片，选择了前 {len(sorted_zh)} 张")
      
      # 处理英文图片
      if en_images:
          sorted_en = sort_by_width_desc(en_images)
          result_images.extend(sorted_en)
          print(f"  找到 {len(en_images)} 张英文{image_type}图片，选择了前 {len(sorted_en)} 张")
      
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
              'budget': details.get('budget'),  # 电影预算
              'revenue': details.get('revenue'),  # 电影收入
              'runtime': details.get('runtime'),  # 电影时长
              'status': details.get('status'),  # 状态
              'tagline': details.get('tagline'),  # 标语
              'homepage': details.get('homepage'),  # 官方网站
              'imdb_id': details.get('imdb_id'),  # IMDB ID
              'original_language': details.get('original_language'),  # 原始语言
              'spoken_languages': details.get('spoken_languages', []),  # 语言列表
              'production_companies': details.get('production_companies', []),  # 制作公司
              'production_countries': details.get('production_countries', []),  # 制作国家
              'genres': details.get('genres', []),  # 详细类型信息
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
                  'cast': credits.get('cast', [])[:5]
              })
          
          # 视频信息
          if 'videos' in details and details['videos'].get('results'):
              merged_item['videos'] = details['videos']['results'][:5]  # 只保留前5个视频
          
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
                  ratings_count = len([r for r in mdb_extracted['ratings'] if r.get('value') is not None])
                  data_types.append(f"{ratings_count}个评分")
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
          
          # 图片信息 - 使用新的过滤和排序逻辑
          if 'images' in details:
              images = details['images']
              item_title = merged_item.get('title', 'Unknown')
              
              print(f"处理 {item_title} 的图片:")
              
              # 处理背景图片
              if 'backdrops' in images:
                  filtered_backdrops = self.filter_and_sort_images(images['backdrops'], '背景')
                  if filtered_backdrops:
                      merged_item['backdrops'] = filtered_backdrops
              
              # 处理海报图片
              if 'posters' in images:
                  filtered_posters = self.filter_and_sort_images(images['posters'], '海报')
                  if filtered_posters:
                      merged_item['posters'] = filtered_posters

              # 处理logo图片
              if 'logos' in images:
                  filtered_logos = self.filter_and_sort_images(images['logos'], 'logo')
                  if filtered_logos:
                      merged_item['logos'] = filtered_logos
      
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
              print("---")
      
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
          total_backdrops = sum(len(item.get('backdrops', [])) for item in data)
          total_posters = sum(len(item.get('posters', [])) for item in data)
          total_logos = sum(len(item.get('logos', [])) for item in data)
          print(f"🖼️  共包含 {total_backdrops} 张背景图片，{total_posters} 张海报图片，{total_logos} 张logo图片")
          
          # 统计评分信息
          items_with_ratings = sum(1 for item in data if 'ratings' in item)
          items_with_certification = sum(1 for item in data if 'certification' in item)
          items_with_age_rating = sum(1 for item in data if 'age_rating' in item)
          items_with_trailer = sum(1 for item in data if 'trailer' in item)
          
          print(f"⭐ 评分数据: {items_with_ratings} 个项目")
          print(f"🔒 认证信息: {items_with_certification} 个项目")
          print(f"🎯 年龄评级: {items_with_age_rating} 个项目")
          print(f"🎬 预告片链接: {items_with_trailer} 个项目")
          
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
