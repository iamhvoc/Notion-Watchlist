import json
import requests
from tmdbapi import TMDBClient
import time
import tokens
from datetime import datetime


class NotionClient:
    def __init__(self, token, database_id):
        self.token = token
        self.database_id = database_id
        self.headers = {
            "Authorization": "Bearer " + self.token,
            "Content-Type": "application/json",
            "Notion-Version": "2021-08-16",
        }

    def monitor_database(self):
        while True:
            time.sleep(0.25)
            try:
                res = requests.post(
                    f"https://api.notion.com/v1/databases/{self.database_id}/query",
                    headers=self.headers
                )
                data_dict = res.json()
            except json.decoder.JSONDecodeError:
                continue
            for element in data_dict['results']:
                try:
                    scheme = element["properties"]["Title"]["title"][0]["text"]["content"]
                except IndexError:
                    continue
                try:
                    if (
                        scheme.endswith(";")
                        and element["properties"]["Type"]["select"]["name"] == "Movie"
                    ):
                        self.page_id = element["id"]
                        self.movie_name = scheme[: len(scheme) - 1]
                        self.edit_movie_details()
                        self.edit_movie_videos()
                        self.edit_movie_credits()
                    elif (
                        scheme.endswith(";")
                        and element["properties"]["Type"]["select"]["name"] == "Series"
                    ):
                        self.page_id = element["id"]
                        self.series_name = scheme[: len(scheme) - 1]
                        self.edit_tv_details()
                        self.edit_tv_videos()
                        self.edit_tv_links()
                        self.edit_tv_credits()
                except TypeError:
                    continue


    # ------------------------Movies------------------------#
    def edit_movie_details(self):
        edit_url = f"https://api.notion.com/v1/pages/{self.page_id}"
        client_tmdb = TMDBClient(tokens.tmdb_token)
        try:
            client_tmdb.movie(self.movie_name)
            client_tmdb.movie_details()
        except:
            data = {
                "properties": {
                    "Title": {
                        "title": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"{self.movie_name} : Not Found"
                                },
                            }
                        ]
                    },
                }
            }
            data = json.dumps(data)
            requests.patch(url=edit_url, headers=self.headers, data=data)
        else:
            data = {
                "cover": {
                    "type": "external",
                    "external": {
                        "url": client_tmdb.poster_m
                    },
                },
                "properties": {
                    "Title": {
                        "title": [
                            {
                                "type": "text",
                                "text": {"content": client_tmdb.original_title_m},
                            }
                        ]
                    },
                    "Tag Line": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": client_tmdb.tagline_m},
                            }
                        ]
                    },
                    "Overview": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": client_tmdb.overview_m},
                            }
                        ]
                    },
                    "IMDB ID": {
                      "rich_text": [
                          {
                              "type": "text",
                              "text": {"content": client_tmdb.imdb_id_m},
                          }
                      ]
                    },
                    "Genre": {
                      "multi_select": [
                          {"name": _} for _ in client_tmdb.genre_m
                      ]
                    },
                    "Language": {
                        "select": {
                            "name": "English" if client_tmdb.language_m == "en" else ("Hindi" if client_tmdb.language_m == "hi" else "Other")
                        }
                    },
                    "Release Status": {
                        "select": {
                            "name": client_tmdb.status_m
                        }
                    },
                    "Runtime": {
                        "number": client_tmdb.runtime_m
                    },
                    "Rating": {
                        "number": round(client_tmdb.rating_m, 1)
                    },
                    "Release Date": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": datetime.strptime(client_tmdb.release_date_m, "%Y-%m-%d").strftime("%B %d, %Y")}
                            }
                        ]
                    },
                    "Poster": {
                        "url": client_tmdb.poster_m,
                    },
                    "Cover": {
                        "url": client_tmdb.backdrop_m,
                    },
                },
            }
            data = json.dumps(data)
            requests.patch(url=edit_url, headers=self.headers, data=data)


    def edit_movie_videos(self):
        edit_url = f"https://api.notion.com/v1/pages/{self.page_id}"
        client_tmdb = TMDBClient(tokens.tmdb_token)
        client_tmdb.movie(self.movie_name)
        client_tmdb.movie_videos()
        trailer_content = None
        if client_tmdb.trailer_m:
            trailer_content = client_tmdb.trailer_m[0]
        else:
            client_tmdb.movie_videos()
            if client_tmdb.teaser_m:
                trailer_content = client_tmdb.teaser_m[0]

        data = {
            "properties": {
                "Trailer ID": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": trailer_content
                            },
                        }
                    ]
                },
            }
        }
        print(data)
        data = json.dumps(data)
        requests.patch(url=edit_url, headers=self.headers, data=data)

    def edit_movie_credits(self):
        edit_url = f"https://api.notion.com/v1/pages/{self.page_id}"
        client_tmdb = TMDBClient(tokens.tmdb_token)
        client_tmdb.movie(self.movie_name)
        client_tmdb.movie_credits()

        data = {
            "properties": {
                "Cast": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": client_tmdb.cast_m}
                        }
                    ]
                },
                "Director": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": client_tmdb.director_m}
                        }
                    ]
                },
            }
        }
        print(data)
        data = json.dumps(data)
        requests.patch(url=edit_url, headers=self.headers, data=data)


        #------------------------Series------------------------#
    def edit_tv_details(self):
        edit_url = f"https://api.notion.com/v1/pages/{self.page_id}"
        client_tmdb = TMDBClient(tokens.tmdb_token)
        try:
            client_tmdb.tv(self.series_name)
            client_tmdb.tv_details()
        except Exception as e:
            print(f"An error occurred while fetching TV details: {e}")
            data = {
                "properties": {
                    "Title": {
                        "title": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"{self.series_name} : Not Found"
                                },
                            }
                        ]
                    },
                }
            }
            data = json.dumps(data)
            requests.patch(url=edit_url, headers=self.headers, data=data)
        else:
            data = {
                "cover": {
                    "type": "external",
                    "external": {
                        "url": client_tmdb.poster_s
                    },
                },
                "properties": {
                    "Title": {
                        "title": [
                            {
                                "type": "text",
                                "text": {"content": client_tmdb.original_title_s},
                            }
                        ]
                    },

                    "Tag Line": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": client_tmdb.tagline_s},
                            }
                        ]
                    },
                    "Overview": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": client_tmdb.overview_s},
                            }
                        ]
                    },
                    "Release Date": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": datetime.strptime(client_tmdb.release_date_s, "%Y-%m-%d").strftime("%B %d, %Y")}
                            }
                        ]
                    },
                    "Language": {
                        "select": {
                            "name": "English" if client_tmdb.language_s == "en" else ("Hindi" if client_tmdb.language_s == "hi" else "Other")
                        }
                    },
                    "Rating":{
                        "number": round(client_tmdb.rating_s, 1)
                    },
                    "Release Status": {
                        "select": {
                            "name": client_tmdb.status_s
                        }
                    },
                    "Genre": {
                        "multi_select": [
                            {"name": _} for _ in client_tmdb.genre_s
                        ]
                    },
                    "Seasons": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": f"{client_tmdb.number_of_seasons} Seasons"}
                            }
                        ]
                    },
                    "Episodes": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": f"{client_tmdb.number_of_episodes} Episodes"}
                            }
                        ]
                    },
                    "Poster": {
                        "url": client_tmdb.poster_s
                    },
                    "Cover": {
                        "url": client_tmdb.backdrop_s
                    }
                },
            }
            data = json.dumps(data)
            requests.patch(url=edit_url, headers=self.headers, data=data)

    def edit_tv_videos(self):
        edit_url = f"https://api.notion.com/v1/pages/{self.page_id}"
        client_tmdb = TMDBClient(tokens.tmdb_token)
        client_tmdb.tv(self.series_name)
        client_tmdb.tv_videos()
        trailer_content = None
        if client_tmdb.trailer_s:
            trailer_content = client_tmdb.trailer_s[0]
        else:
            client_tmdb.tv_videos()
            if client_tmdb.teaser_s:
                trailer_content = client_tmdb.teaser_s[0]

        data = {
            "properties": {
                "Trailer ID": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": trailer_content
                            },
                        }
                    ]
                },
            }
        }
        data = json.dumps(data)
        requests.patch(url=edit_url, headers=self.headers, data=data)

    def edit_tv_links(self):
        edit_url = f"https://api.notion.com/v1/pages/{self.page_id}"
        client_tmdb = TMDBClient(tokens.tmdb_token)
        client_tmdb.tv(self.series_name)
        client_tmdb.tv_ids()

        data = {
            "properties": {
                "IMDB ID": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": client_tmdb.imdb_id_s}
                        }
                    ]
                }
            }
        }
        data = json.dumps(data)
        requests.patch(url=edit_url, headers=self.headers, data=data)

    def edit_tv_credits(self):
        edit_url = f"https://api.notion.com/v1/pages/{self.page_id}"
        client_tmdb = TMDBClient(tokens.tmdb_token)
        client_tmdb.tv(self.series_name)
        client_tmdb.tv_credits()

        data = {
            "properties": {
                "Cast": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": client_tmdb.cast_s}
                        }
                    ]
                },
                "Director": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": client_tmdb.director_s},
                        }
                    ]
                },
            }
        }
        print(data)
        data = json.dumps(data)
        requests.patch(url=edit_url, headers=self.headers, data=data)

