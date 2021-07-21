import IDMDownloader
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as e_c


class AnimeScraper:

    PATH = "\chromedriver.exe"

    def __init__(self, path):
        self.PATH = path + self.PATH
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.page_load_strategy = "eager"
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        print("\nConnecting to virtual browser")
        self.driver = webdriver.Chrome(executable_path=self.PATH, options=options,
                                       service_log_path=path+r"\log.txt")
        print("Opening target website")
        self.driver.get("https://gogoanime.vc/")
        print("Setting up internal resources")
        self.animes = list()
        self.tot_ep = 0

    def search_anime(self, anime):
        print("Searching...")
        search_bar = self.driver.find_element_by_id("keyword")
        search_bar.clear()
        search_bar.send_keys(anime)
        search_bar.send_keys(Keys.RETURN)
        try:
            results = WebDriverWait(self.driver, 10).until(
                e_c.presence_of_element_located((By.CLASS_NAME, "items"))
            )
            self.animes = results.find_elements_by_tag_name("li")
            if len(self.animes) == 0:
                raise FileNotFoundError
            i = 1
            print("Matching animes found:")
            for anime in self.animes:
                name = anime.find_element_by_class_name("name")
                year = anime.find_element_by_class_name("released")
                print(str(i)+". "+name.text, year.text, sep=", ")
                i += 1
            return len(self.animes)
        except TimeoutException:
            print("Search operation failed")
            return -1
        except FileNotFoundError:
            print("No results found")
            return -2

    def select_anime(self, num):
        name = self.animes[num].find_element_by_class_name("name").text
        print(name, "selected")
        print("Finding episodes...")
        self.animes[num].click()

    def search_episodes(self, show=False):
        try:
            episodes = WebDriverWait(self.driver, 10).until(
                e_c.presence_of_element_located((By.ID, "episode_related"))
            )
            episodes = episodes.find_elements_by_tag_name("li")
            if len(episodes) == 0:
                raise FileNotFoundError
            return episodes
        except TimeoutException:
            if show:
                print("Could not search for episodes")
            return -1
        except FileNotFoundError:
            if show:
                print("No episodes found")
            return -2

    def get_episodes(self):
        episodes = self.search_episodes(show=True)
        if type(episodes) is list and len(episodes) > 0:
            print("Total episodes:", len(episodes))
            self.tot_ep = len(episodes)
            return len(episodes)
        return episodes

    def download_episodes(self, download_list, save_path, quality=1080):
        failed_list = set()
        selected_qualities = {"HDp": [], "360p": [], "480p": [], "720p": [], "1080p": []}
        for ep in download_list:
            print("Episode", ep+1)
            episodes = self.search_episodes()
            if type(episodes) is int:
                failed_list.add(ep)
                download_list.append(ep)
                if len(download_list) > (self.tot_ep + 10):
                    print("Retry limit exceeded")
                    print("Episodes that couldn't be downloaded:")
                    print(failed_list)
                    break
                else:
                    print("There was an error, will retry later")
                    continue
            elif ep in failed_list:
                failed_list.discard(ep)
            this_ep = episodes[len(episodes) - ep - 1]
            self.driver.execute_script("arguments[0].click();", this_ep.find_element_by_tag_name('a'))
            download_btn = self.driver.find_element_by_class_name("dowloads")
            download_btn.click()
            self.driver.switch_to.window(self.driver.window_handles[-1])
            file_name = self.driver.find_element_by_id("title").text + ".mp4"
            good_links = self.driver.find_element_by_class_name("mirror_link")
            links = good_links.find_elements_by_class_name("dowload")
            available_qualities = {'HD': None, 360: None, 480: None, 720: None, 1080: None}
            for link in links:
                url = link.find_element_by_tag_name('a').get_attribute("href")
                if "gogo-cdn" in url:
                    continue
                if link.text.find("HDP") != -1:
                    available_qualities['HD'] = link
                if link.text.find("360") != -1:
                    available_qualities[360] = link
                if link.text.find("480") != -1:
                    available_qualities[480] = link
                if link.text.find("720") != -1:
                    available_qualities[720] = link
                if link.text.find("1080") != -1:
                    available_qualities[1080] = link
            sel_link = None
            if available_qualities[quality] is not None:
                print("Selected quality found")
                sel_link = available_qualities[quality]
                selected_qualities[str(quality)+'p'].append(ep+1)
            else:
                print("Oops selected quality not available for this episode")
                for i in [1080, 720, 480, 360, "HD"]:
                    if available_qualities[i] is not None:
                        print("Switching to", str(i)+"p")
                        sel_link = available_qualities[i]
                        selected_qualities[str(i)+'p'].append(ep+1)
                        break
            url = sel_link.find_element_by_tag_name('a').get_attribute("href")
            IDMDownloader.download(url, save_path, file_name)
            print("Added to IDM queue")
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            self.driver.back()
        print("\nThe quality selected for each episode:")
        for i in selected_qualities.keys():
            if len(selected_qualities[i]) > 0:
                print(i+": ", end='')
                k = 1
                for j in range(len(selected_qualities[i])):
                    if j < len(selected_qualities[i]) - 1:
                        print(selected_qualities[i][j], end=', ')
                    else:
                        print(selected_qualities[i][j])
                    if k == 12:
                        print()
                        k = 0
                    k += 1

    def close_browser(self):
        self.driver.quit()
