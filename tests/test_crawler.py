from app.discovery.crawler import MainframeCrawler
from app.mainframe.screen_parser import ScreenParser


class FakeNavigator:
    def __init__(self):
        self.current = "root"
        self.stack = []
        self.screens = {
            "root": [
                "MAIN MENU                                                                       ",
                "1 Customer Search                                                                ",
                "2 Reports                                                                        ",
            ],
            "1": [
                "CUSTOMER SEARCH                                                                  ",
                "Customer ID: ________                                                            ",
            ],
            "2": [
                "REPORT MENU                                                                      ",
                "No fields                                                                        ",
            ],
        }

    def get_screen(self):
        return self.screens[self.current]

    def navigate_to_menu(self, option):
        self.stack.append(self.current)
        self.current = option

    def press_pf(self, number):
        if number == 3 and self.stack:
            self.current = self.stack.pop()


def test_crawler_builds_graph_without_revisiting():
    navigator = FakeNavigator()
    parser = ScreenParser()
    crawler = MainframeCrawler(navigator, parser)
    crawler.crawl(max_depth=2)

    assert len(crawler.graph) == 3
    titles = {node["title"] for node in crawler.graph.values()}
    assert "MAIN MENU" in titles
    assert "CUSTOMER SEARCH" in titles
