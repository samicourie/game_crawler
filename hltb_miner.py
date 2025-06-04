from howlongtobeatpy import HowLongToBeat
import pandas as pd

def get_time(game_name):
    ## Returns a df [title_found, main, extra, completionist]. Returns tuple of 0 if not found.

    res = HowLongToBeat().search(game_name, similarity_case_sensitive=False)
    if res is None:
        pd.read_csv("none_times.csv").append({'id_game': game_name, 'reason': 'Not found on hl2b'},
                                             ignore_index=True).to_csv("none_times.csv")
        return pd.DataFrame(
            {'name': game_name, 'title_found': 'Not found on hl2b', 'main': 0, 'extra': 0, 'completionist': 0,
             'review_score': 0, 'review_count': 0, 'people_polled': 0}, index=[0])
    times = {'name': game_name, 'title_found': res[0].game_name, 'main': res[0].main_story, 'extra': res[0].main_extra,
             'completionist': res[0].completionist, 'review_score': res[0].review_score,
             # 'review_count': res[0].review_count, 
             # 'people_polled': res[0].people_polled
             } if len(res) > 0 else {
        'name': game_name, 'title_found': 'Not found on hl2b', 'main': 0, 'extra': 0, 'completionist': 0,
        'review_score': 0, # 'review_count': 0, 'people_polled': 0
        }

    times = pd.DataFrame(times, index=[0])
    return times


if __name__ == '__main__':
    print(get_time('The Legend of Zelda  Ocarina of Time'))
