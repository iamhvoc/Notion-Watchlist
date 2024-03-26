import json
import requests


class TMDBClient:
    def __init__(self, token):
        self.token = token
        self.headers = {'Authorization': 'Bearer ' + self.token,
                        'Content-Type': 'application/json;charset=utf-8'

                        }

    def _get_json_response(self, url):
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def movie(self, movie_name):
        request_url =\
            f"https://api.themoviedb.org/3/search/movie?api_key={self.token}&query={movie_name.replace(' ','+')}"
        res = requests.get(request_url)
        res_json = json.dumps(res.json())
        res_dict = json.loads(res_json)
        self.movie_id = res_dict['results'][0]['id']

    def movie_details(self):
        movie_details_url = f"https://api.themoviedb.org/3/movie/{self.movie_id}?api_key={self.token}"
        res = requests.get(movie_details_url, headers=self.headers)
        res_dict = res.json()

        self.original_title_m = res_dict['original_title']
        self.release_date_m = res_dict['release_date']
        self.overview_m = res_dict['overview']
        self.tagline_m = res_dict['tagline']
        self.runtime_m = res_dict['runtime']
        self.language_m = res_dict['original_language']
        self.rating_m = res_dict['vote_average']
        self.imdb_id_m = res_dict['imdb_id']
        self.status_m = res_dict['status']
        self.genre_m = [_['name'] for _ in res_dict['genres']]
        self.poster_m = f"https://www.themoviedb.org/t/p/original{res_dict['poster_path']}"
        self.backdrop_m = f"https://www.themoviedb.org/t/p/original{res_dict['backdrop_path']}"

    def movie_credits(self):
        movie_credits_url = f"https://api.themoviedb.org/3/movie/{self.movie_id}/credits?api_key={self.token}"
        res = requests.get(movie_credits_url, headers=self.headers)
        res.raise_for_status()
        res_dict = res.json()

        self.cast_m = [_["name"] for _ in res_dict['cast']][:4]
        self.director_m = [_['name'] for _ in res_dict["crew"] if _['job'] == "Director"][:1]

    def movie_videos(self):
        movie_videos_url = f"https://api.themoviedb.org/3/movie/{self.movie_id}/videos?api_key={self.token}"
        res = requests.get(movie_videos_url, headers=self.headers)
        res_dict = res.json()

        self.trailer_m = [_['key'] for _ in res_dict["results"] if _["type"] == "Trailer"]
        self.teaser_m = [_['key'] for _ in res_dict["results"] if _["type"] == "Teaser"]

    # -------------------------------------[TV Shows]-------------------------------------#

    def tv(self, series_name):
        request_url = f"https://api.themoviedb.org/3/search/tv?api_key={self.token}&query={series_name.replace(' ', '+')}"
        res = requests.get(request_url)
        res_json = json.dumps(res.json())
        res_dict = json.loads(res_json)
        self.series_id = res_dict["results"][0]["id"]

    def tv_details(self):
        tv_details_url = f"https://api.themoviedb.org/3/tv/{self.series_id}?api_key={self.token}"
        res = requests.get(
            tv_details_url,
            headers=self.headers
        )
        res_dict = res.json()

        self.original_title_s = res_dict['original_name']
        self.release_date_s = res_dict['first_air_date']
        self.overview_s = res_dict['overview']
        self.tagline_s = res_dict['tagline']
        self.language_s = res_dict['original_language']
        self.rating_s = res_dict['vote_average']
        self.number_of_seasons = res_dict["number_of_seasons"]
        self.number_of_episodes = res_dict["number_of_episodes"]
        self.status_s = res_dict['status']
        self.genre_s = [_['name'] for _ in res_dict['genres']]
        self.poster_s = f"https://www.themoviedb.org/t/p/original{res_dict['poster_path']}"
        self.backdrop_s = f"https://www.themoviedb.org/t/p/original{res_dict['backdrop_path']}"

    def tv_ids(self):
        tv_imdb_id_url = f"https://api.themoviedb.org/3/tv/{self.series_id}/external_ids?api_key={self.token}"
        res = requests.get(tv_imdb_id_url, headers=self.headers)
        res_dict = res.json()

        self.imdb_id_s = res_dict['imdb_id']

    def tv_videos(self):
        tv_videos_url = f"https://api.themoviedb.org/3/tv/{self.series_id}/videos?api_key={self.token}"
        res = requests.get(tv_videos_url, headers=self.headers)
        res_dict = res.json()

        self.trailer_s = [_['key'] for _ in res_dict["results"] if _["type"] == "Trailer"]
        self.teaser_s = [_['key'] for _ in res_dict["results"] if _["type"] == "Teaser"]

    def tv_credits(self):
        tv_credits_url = f"https://api.themoviedb.org/3/tv/{self.series_id}/aggregate_credits?api_key={self.token}"
        res = requests.get(tv_credits_url, headers=self.headers)
        res_dict = res.json()

        self.cast_s = [_["name"] for _ in res_dict['cast']][:4]
        self.director_s = [_['name'] for _ in res_dict["crew"] if any(job['job'] == "Director" for job in _['jobs'])][:1]