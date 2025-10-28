from howlongtobeatpy import HowLongToBeat
from crawlers.crawler import Crawler
from util.utility import get_best_match


class HLTBCrawler(Crawler):

    def __init__(self):
        super().__init__()
        self.hltb = HowLongToBeat()
        self.site = 'hltb'

    def get_api_info(self, title, year=0):
        main = '/'
        main_extra = '/'
        complete = '/'
        candidates = []
        candidates_years = []
        clean_title = title.replace('-', '')
        hltb_success = False
        try:
            hltb_games = self.hltb.search(clean_title, similarity_case_sensitive=False)
            for game in hltb_games:
                if game.similarity > 0.7:
                    candidates.append(game.game_name)
                    try:
                        candidates_years.append(game.release_world)
                    except Exception as _:
                        candidates_years.append(0)

            best_index, best_score, _ = get_best_match(candidates, title, year, candidates_years)
            if best_score > self.accepted_score:
                best_candidate = hltb_games[best_index]
                main = best_candidate.main_story
                main_extra = best_candidate.main_extra
                complete = best_candidate.completionist
                game_id = best_candidate.game_id
                game_url = best_candidate.game_web_link
                hltb_success = True
                return {'hltb-main': main, 'hltb-main+': main_extra, 'hltb-complete': complete, 
                'hltb-id': game_id, 'hltb-url': game_url, 'hltb-score': best_score, 'hltb-success': hltb_success}
        except Exception as _:
            pass
        return {'hltb-success': hltb_success}
    
    def get_url(self, title):
        return super().get_url(title)
    
    def get_info(self, url, score):

        if score >= self.accepted_score:
            main = '/'
            main_extra = '/'
            complete = '/'
            hltb_id = int(url.split('/')[-1])
            hltb_success = False
            try:
                hltb_game = self.hltb.search_from_id(hltb_id)
                main = hltb_game.main_story
                main_extra = hltb_game.main_extra
                complete = hltb_game.completionist
                game_id = hltb_game.game_id
                hltb_success = True
                return {'hltb-main': main, 'hltb-main+': main_extra, 'hltb-complete': complete, 
                        'hltb-id': game_id, 'hltb-url': url, 'hltb-success': hltb_success}
            except Exception as _:
                pass
        return {'hltb-success': hltb_success}

    def get_raw_info(self, url):
        return super().get_raw_info(url)
