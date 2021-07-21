import os
import time
import WebHandler


def clear():
    _ = os.system("cls")
    return


def main():
    clear()
    print("Initializing...")
    handler = WebHandler.AnimeScraper(os.getcwd())
    time.sleep(1)
    print("\nDone")
    time.sleep(2)
    trying_again = False
    name = str()
    while True:
        clear()
        if not trying_again:
            name = input("Enter name of the anime: ")
        results = handler.search_anime(name)
        if results > 0:
            choice = int(input("Select anime from the results or 0 to search again: "))
            clear()
            if choice == 0:
                continue
            handler.select_anime(choice-1)
            download_list = list()
            while True:
                episodes = handler.get_episodes()
                if episodes == -1:
                    choice = input("Try again? (y/n): ")
                    if choice == 'y' or choice == 'Y':
                        print("Finding episodes...")
                        continue
                    else:
                        flag = -2
                        break
                elif episodes == -2:
                    flag = -2
                    break
                else:
                    temp = input("Enter ep. number to download (0 for all): ")
                    temp = temp.split(sep=",")
                    for i in temp:
                        i = i.strip()
                        if '-' in i:
                            r = i.split(sep='-')
                            for k in range(int(r[0]), int(r[1])+1):
                                download_list.append(k-1)
                        elif i.isnumeric() and i != '0':
                            download_list.append(int(i)-1)
                        elif i == '0':
                            download_list = [x for x in range(episodes)]
                            break
                    i = 0
                    while i < len(download_list):
                        if download_list[i] > (episodes-1):
                            download_list.pop(i)
                        else:
                            i += 1
                    flag = 1
                    break
            if flag == 1:
                clear()
                print("Episodes selected to be downloaded:")
                k = 1
                for i in range(len(download_list)):
                    if i < len(download_list) - 1:
                        print(download_list[i]+1, end=', ')
                    else:
                        print(download_list[i]+1)
                    if k == 12:
                        print()
                        k = 0
                    k += 1
                print("Choose a preferred download quality:")
                print("1. 360p")
                print("2. 480p")
                print("3. 720p")
                print("4. 1080p")
                print("If selected quality is not found highest available will be selected")
                choice = int(input("Your choice (1-4): "))
                if choice == 1:
                    quality = 360
                elif choice == 2:
                    quality = 480
                elif choice == 3:
                    quality = 720
                else:
                    quality = 1080
                print(str(quality)+'p selected')
                print("Enter location to save files (blank for default):")
                save_path = input()
                if len(save_path) == 0:
                    save_path = os.getcwd() + "\Downloads"
                    os.makedirs(save_path, exist_ok=True)
                    print("Will be saving to", save_path)
                elif os.path.exists(save_path):
                    pass
                else:
                    save_path = os.getcwd() + "\Downloads"
                    os.makedirs(save_path, exist_ok=True)
                    print("Location does not exists")
                    print("Default location will be selected")
                    print("Will be saving to", save_path)
                time.sleep(5)
                clear()
                print("Downloads will start in a moment")
                print("-----------------------------------\n")
                time.sleep(3)
                handler.download_episodes(download_list, save_path, quality)
                print("\nDon't forget to start the queue in IDM")
            elif flag == -2:
                choice = input("Search for another anime? (y/n): ")
                if choice == 'y' or choice == 'Y':
                    clear()
                    continue
            break
        elif results == -1:
            choice = input("Try again? (y/n): ")
            if choice == 'y' or choice == 'Y':
                trying_again = True
                clear()
                continue
            break
        else:
            choice = input("Search again? (y/n): ")
            if choice == 'y' or choice == 'Y':
                trying_again = False
                clear()
                continue
            break
    time.sleep(2)
    print("\n-----------------------------------")
    print("Closing connections, please wait...")
    handler.close_browser()
    print("Finished, you can now terminate this script")


if __name__ == '__main__':
    main()
    input("\n\nPress enter to exit ")
