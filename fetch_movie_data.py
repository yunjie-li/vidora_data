import requests
import json
import os
from typing import Dict, List, Any

class MovieDataFetcher:
  def __init__(self, api_key: str):
      self.api_key = api_key
      self.base_url = "https://api.themoviedb.org/3"
      self.session = requests.Session()
  
  def get_trending_data(self) -> Dict[str, Any]:
      """获取热门趋势数据"""
      url = f"{self.base_url}/trending/all/day"
      params = {
          'api_key': self.api_key,
          'language': 'zh-CN',
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
          'append_to_response': 'images'
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
          'append_to_response': 'images'
      }
      
      try:
          response = self.session.get(url, params=params)
          response.raise_for_status()
          return response.json()
      except requests.RequestException as e:
          print(f"获取电视剧 {tv_id} 详细信息失败: {e}")
          return {}
  
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
          
          if details:
              # 合并基础信息和详细信息
              combined_item = {
                  'id': item_id,
                  'media_type': media_type,
                  'title': item.get('title') or item.get('name'),
                  'original_title': item.get('original_title') or item.get('original_name'),
                  'overview': item.get('overview'),
                  'poster_path': item.get('poster_path'),
                  'backdrop_path': item.get('backdrop_path'),
                  'vote_average': item.get('vote_average'),
                  'vote_count': item.get('vote_count'),
                  'popularity': item.get('popularity'),
                  'release_date': item.get('release_date') or item.get('first_air_date'),
                  'genre_ids': item.get('genre_ids', []),
                  'adult': item.get('adult', False),
                  'details': details
              }
              processed_items.append(combined_item)
              print(f"已处理 {media_type}: {combined_item['title']} (ID: {item_id})")
      
      return processed_items
  
  def generate_homepage_data(self) -> Dict[str, Any]:
      """生成主页数据"""
      print("开始获取趋势数据...")
      trending_data = self.get_trending_data()
      
      if not trending_data:
          print("未能获取到趋势数据")
          return {}
      
      print(f"获取到 {len(trending_data.get('results', []))} 个趋势项目")
      
      print("开始处理详细信息...")
      processed_items = self.process_trending_items(trending_data)
      
      homepage_data = {
          'last_updated': trending_data.get('dates', {}).get('maximum', ''),
          'total_results': trending_data.get('total_results', 0),
          'total_pages': trending_data.get('total_pages', 0),
          'items': processed_items,
          'metadata': {
              'api_version': '3',
              'language': 'zh-CN',
              'generated_at': trending_data.get('dates', {}).get('maximum', '')
          }
      }
      
      return homepage_data
  
  def save_to_file(self, data: Dict[str, Any], filename: str = 'homepage.json'):
      """保存数据到文件"""
      try:
          with open(filename, 'w', encoding='utf-8') as f:
              json.dump(data, f, ensure_ascii=False, indent=2)
          print(f"数据已保存到 {filename}")
          print(f"共保存了 {len(data.get('items', []))} 个项目")
      except Exception as e:
          print(f"保存文件失败: {e}")

def main():
  # 从环境变量获取 API 密钥
  api_key = os.getenv('TMDB_API_KEY', '9f10dfe93f1fd3b793eaa10c732a07e9')
  
  if not api_key:
      print("错误: 未找到 TMDB API 密钥")
      return
  
  fetcher = MovieDataFetcher(api_key)
  
  print("开始生成主页数据...")
  homepage_data = fetcher.generate_homepage_data()
  
  if homepage_data:
      fetcher.save_to_file(homepage_data)
      print("任务完成!")
  else:
      print("生成数据失败")

if __name__ == "__main__":
  main()
