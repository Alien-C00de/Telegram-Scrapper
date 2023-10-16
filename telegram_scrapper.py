import argparse
import asyncio
import csv
import os
import pathlib
import sys
import time
from configparser import ConfigParser

import requests
from bs4 import BeautifulSoup
import random
import time
import datetime
from const import user_agent

from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest, GetHistoryRequest
from telethon.tl.types import InputPeerEmpty
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.types import (PeerChannel, PeerChat)
from telethon.tl.functions.users import GetFullUserRequest

# Color class for print statement
class Color:
    re="\033[1;31m"         # Red
    gr="\033[1;32m"         # Green
    cy="\033[1;36m"         # Cyan
    yo="\033[1;33m"         # Yellow
    BGreen="\033[1;32m"     # Green
    Color_Off="\033[0m"     # Text Reset
    wt = "\033[0;37m"       # white

# Get connection to telegram using api_id, api_hash, phone
class get_authorization():
    def __init__(self) -> None:
        pass
    
    # Create client connection
    def get_client(self):
        color = Color()
        os.system('clear')
        try:
             # Reading Configs
            config = ConfigParser()
            config_path = pathlib.Path(__file__).parent.absolute() / "config.ini"
            config.read(config_path)
            
            'Telegram' in config
            api_id = config['Telegram']['api_id'] 
            api_hash =  config['Telegram']['api_hash'] 
            api_hash = str(api_hash)
            phone = config['Telegram']['phone'] 
            sfile = 'session_file'

            client = TelegramClient(phone, api_id, api_hash)
            client.connect()

            if not client.is_user_authorized():
                client.send_code_request(phone)
                os.system('clear')
                client.sign_in(phone, input(color.gr+'[+] Enter the verification code: '+color.yo))

            return client
        
        except KeyError:
            os.system('clear')
            print("\033[91m[-] Error: \033[92mPlease check required details are correct.\n")
            sys.exit(1)
        except Exception as EX:
            client.sign_in(password=input('Password: '))
            print("\033[91m[-] Error:", EX," \033[92m\n")

# Telegram scrapper for User details, Group details, Chat details
class Tele_MemberScarap(object):
    
    def __init__(self):
        pass
    
    # Get user details from subscribed group
    def Self_Group_Member_Finder(self):
        color  = Color()

        authoization = get_authorization()
        client = authoization.get_client()

        # os.system('clear')
        chats = []
        last_date = None
        chunk_size = 200
        groups=[]

        try:
            result = client(GetDialogsRequest(
                        offset_date=last_date,
                        offset_id=0,
                        offset_peer=  InputPeerEmpty(),
                        limit=chunk_size,
                        hash = 0
                    ))
            chats.extend(result.chats)

            for chat in chats:
                try:
                    if chat.megagroup == True or chat.gigagroup == True or chat.broadcast == True:
                        groups.append(chat)
                except:
                    continue

            print(color.gr+'[+] Choose a group to scrape members:'+color.re)
            for i, g in enumerate(groups):
                print(color.gr+'['+color.cy+str(i)+']' + ' - ' + g.title)
            print('')
            g_index = input(color.gr+"[+] Enter a Number: "+color.re)
            target_group = groups[int(g_index)]
            all_participants = []
            all_participants = client.iter_participants(target_group)

            print(color.gr+'[+] Fetching Members ...')
            time.sleep(1)
            
            tele_writer = Tele_Writer()
            tele_writer.Enter_User_Into_CSVFile(all_participants, target_group.title, target_group.id, target_group.title)
        
        except Exception as ex:
            print("\033[91m\n[-] Error:", ex , "\033[92m\n")
            pass

    # Get data from any group / channel 
    def Any_Group_Member_Finder(self, target_group):
        color  = Color()

        authoization = get_authorization()
        client = authoization.get_client()
        
        entity  = self.__retrieve_entity(client, target_group)
        if entity is None:
            print("\033[91m[-] Error: \033[92mCannot Find Any Entity Corresponding To {}. Either Use Group Id or User Name\n".format(target_group))
            sys.exit(1)

        self.get_basic_scan(client, entity, target_group)   # Display basic information about the group
        self.__get_user_details(client, entity)         # Get user details & store in CSV file
        self.__get_chat_details(client, entity)         # Get chat details & store in CSV file
    
    # Get information about group / channel
    def get_basic_scan(self, client = None, _entitydetails = None, target_group = ""):
        color  = Color()
        _entitydetails = None
        chat_type = ""
        web_req = None

        if client is None:
            authoization = get_authorization()
            client = authoization.get_client()
        
        if _entitydetails is None:
             _entitydetails = self.__retrieve_entity(client, target_group)
        print(" [!] ", "Performing basic scan")
        
        try:
            print(color.BGreen +"  ┬  Channel details " + color.wt)
            print(color.BGreen +"  ├  Title: "+ color.wt, _entitydetails.title)
            
            if _entitydetails.username:
                print(color.BGreen +"  ├  Username: " + color.wt, _entitydetails.username)
                url = "http://t.me/" + _entitydetails.username
                print(color.BGreen +"  ├  URL: " + color.wt, "http://t.me/" + _entitydetails.username)
                web_req = self.__parse_html_page(url)
            elif "https://t.me/" in target_group:
                print(color.BGreen +"  ├  Username: " + color.wt, "Private group")
                print(color.BGreen +"  ├  URL: " + color.wt, target_group)
                web_req = self.__parse_html_page(target_group)
            else:
                print(color.BGreen +"  ├  Username: " + color.wt, "Private group")
                print(color.BGreen +"  ├  URL: " + color.wt, "Private group")
            if _entitydetails.broadcast is True:
                chat_type = "Channel"
            elif _entitydetails.megagroup is True:
                _chat_type = "Megagroup"
            elif _entitydetails.gigagroup is True:
                chat_type = "Gigagroup"
            else:
                chat_type = "Chat"
            
            if web_req:
                print(color.BGreen +"  ├  Group Description: " + color.wt, web_req["group_description"])
                print(color.BGreen +"  ├  Total Participants: " + color.wt, web_req["total_participants"])
            print(color.BGreen +"  ├  Chat type: " + color.wt, chat_type)
            print(color.BGreen +"  ├  Chat id: " + color.wt, _entitydetails.username)
            print(color.BGreen +"  ├  Access hash: " + color.wt, _entitydetails.access_hash)
            print(color.BGreen +"  ├  Scam: " + color.wt, _entitydetails.scam)
            print(color.BGreen +"  ├  First post date: " + color.wt, _entitydetails.date)
            print(color.BGreen +"  ├  Restrictions: " + color.wt, _entitydetails.restriction_reason)

        except Exception as ex:
            print("\033[91m\n[-] Error:", ex , "\033[92m\n")
            pass
    
    def get_user_information(self, target_user):
        color  = Color()

        authoization = get_authorization()
        client = authoization.get_client()

        try:
            if '@' in target_user:
                my_user = client.get_entity(target_user)
            else:
                user  = int(target_user)
                my_user = client.get_entity(user)
                # result = client(GetFullUserRequest(user))
                # print(result.stringify())

            user_first_name = my_user.first_name
            user_last_name = my_user.last_name
            if user_last_name is not None:
                user_full_name = str(user_first_name) + " " + str(user_last_name)
            else:
                user_full_name = str(user_first_name)

            if my_user.photo is not None:
                user_photo = my_user.photo.photo_id
            else:
                user_photo = "None"

            user_status = "Not found"
            if my_user.status is not None:
                if "Empty" in str(my_user.status):
                    user_status = "Last seen over a month ago"
                elif "Month" in str(my_user.status):
                    user_status = "Between a week and a month"
                elif "Week" in str(my_user.status):
                    user_status = "Between three and seven days"
                elif "Offline" in str(my_user.status):
                    user_status = "Offline"
                elif "Online" in str(my_user.status):
                    user_status = "Online"
                elif "Recently" in str(my_user.status):
                    user_status = "Recently (within two days)"
            else:
                user_status = "Not found"

            if my_user.restriction_reason is not None:
                ios_restriction = my_user.restriction_reason[0]
                if 1 in my_user.restriction_reason:
                    android_restriction = my_user.restriction_reason[1]
                    user_restrictions = (
                        str(ios_restriction) + ", " + str(android_restriction)
                    )
                else:
                    user_restrictions = str(ios_restriction)
            else:
                user_restrictions = "None"
            
            print(color.BGreen +" [+] ", "User details for"+ color.wt, target_user)
            print(color.BGreen +"  ├  Id:" + color.wt, str(my_user.id))
            print(color.BGreen +"  ├  Username:" + color.wt, str(my_user.username))
            print(color.BGreen +"  ├  Name:" + color.wt, str(user_full_name))
            print(color.BGreen +"  ├  Verification:" + color.wt, str(my_user.verified))
            print(color.BGreen +"  ├  Photo ID:" + color.wt, str(user_photo))
            print(color.BGreen +"  ├  Phone number:" + color.wt, str(my_user.phone))
            print(color.BGreen +"  ├  Access hash:" + color.wt, str(my_user.access_hash))
            print(color.BGreen +"  ├  Language:" + color.wt, str(my_user.lang_code))
            print(color.BGreen +"  ├  Bot:" + color.wt, str(my_user.bot))
            print(color.BGreen +"  ├  Scam:" + color.wt, str(my_user.scam))
            print(color.BGreen +"  ├  Last seen:" + color.wt, str(user_status))
            print(color.BGreen +"  └  Restrictions:" + color.wt, str(user_restrictions))

            # result = client(GetFullUserRequest(my_user.id))
            # print(result.stringify())

        except Exception as exx:
            print("\033[91m[-] Error: \033[92m[-]", exx, "\n")
        
    # Get user details from any group / channel
    def __get_user_details(self, client, my_channel):
        offset = 0
        limit = 0
        all_participants = []

        try:
            participants = client(GetParticipantsRequest(
                my_channel, ChannelParticipantsSearch(''), offset= offset, limit = limit ,
                hash=0))
            
            all_participants.extend(participants.users)
            offset += len(participants.users)
            title  = my_channel.usename if my_channel.title is None else my_channel.title 

            writer = Tele_Writer()
            writer.Enter_User_Into_CSVFile(all_participants, my_channel.title, my_channel.id, title + "_"+ "UserList")
        except Exception as er:
            print("\033[91m\n[-] Error: Admin privileges are required to get paricipants list\033[92m\n")
            pass
    
    # Get chat details from any group / channel
    def __get_chat_details(self, client, my_channel):
        offset_id = 0
        limit = 100
        all_messages = []
        total_messages = 0
        total_count_limit = 0

        try:
            while True:
                print("[+] Current Offset ID is:", offset_id, "; Total Messages:", total_messages)
                history = client(GetHistoryRequest(
                    peer=my_channel,
                    offset_id=offset_id,
                    offset_date=None,
                    add_offset=0,
                    limit=limit,
                    max_id=0,
                    min_id=0,
                    hash=0
                ))
                if not history.messages:
                    break
                messages = history.messages
                all_messages.append(messages)
                offset_id = messages[len(messages) - 1].id
                total_messages = len(all_messages)
                
                if total_count_limit != 0 and total_messages >= total_count_limit:
                    break
                
            title  = my_channel.usename if my_channel.title is None else my_channel.title 

            writer = Tele_Writer()
            writer.Enter_Chat_Data_Into_CSVFile(all_messages, my_channel.title, my_channel.id, title + "_" + "Chats")
        except Exception as ex:
            print("\033[91m\n[-] Error: No chat retrive\033[92m\n")
            pass

    def __parse_html_page(self, url):   
        s = requests.Session()
        s.max_redirects = 10
        s.headers["User-Agent"] = random.choice(user_agent)
        URL = s.get(url)
        URL.encoding = "utf-8"
        html_content = URL.text
        soup = BeautifulSoup(html_content, "html.parser")
        name = ""
        group_description = ""
        total_participants = ""
        try:
            name = soup.find("div", {"class": ["tgme_page_title"]}).text
        except:
            name = "Not found"
        try:
            group_description = (
                soup.find("div", {"class": ["tgme_page_description"]})
                .getText(separator="\n")
                .replace("\n", " ")
            )
        except:
            group_description = "None"
        try:
            group_participants = soup.find("div", {"class": ["tgme_page_extra"]}).text
            sep = "members"
            stripped = group_participants.split(sep, 1)[0]
            total_participants = (
                stripped.replace(" ", "")
                .replace("members", "")
                .replace("subscribers", "")
                .replace("member", "")
            )
        except:
            total_participants = "Not found"
        return {
            "name": name,
            "group_description": group_description,
            "total_participants": total_participants,
        }

    def __retrieve_entity(self, client, _target):
        current_entity = None
        target = None
        try:
            current_entity = client.get_entity(_target)
            target = _target
        except Exception as exx:
            try:
                group  = int(_target)
                current_entity = client.get_entity(group)
                target = int(_target)
            except:
                pass
            pass
        if not current_entity:
            try:
                current_entity = client.get_entity(PeerChannel(_target))
                target = _target
            except Exception as exx:
                pass
        if not current_entity:
            try:
                current_entity = client.get_entity(PeerChat(_target))
                target = _target
            except Exception as exx:
                pass
        return current_entity
    
# CSV file operation 
class Tele_Writer():

    def __init__(self):
        pass
    
    # Enter all the chat data into CSV file
    def Enter_Chat_Data_Into_CSVFile(self, all_chat, group_title = "", group_id = "", filename = ""):
        color = Color()

        print(color.gr+'\n[+] Saving Chat(s) in CSV file ...'+ color.wt)
        time.sleep(1)

        timestamp = int(datetime.datetime.now().timestamp())
        filename = '%s_%s.csv' % (filename.replace("/", "_"), timestamp)
        self.__create_dirs('output')
        completename = os.path.join('./output', filename)

        with open(completename, "w",encoding='UTF-8') as f:
            writer = csv.writer(f,delimiter=",",lineterminator="\n")
            writer.writerow(['Sender Id','Date', 'Chat Id','Message','Group', 'Group Id'])
            for chats in all_chat:
                for chat in chats:
                    senderid = chat.sender_id or ""
                    date = chat.date or ""
                    chat_id = chat.chat_id or ""
                    message = chat.message or ""
                    writer.writerow([senderid, date, chat_id, message, group_title, group_id])
        print(color.cy+'[+] {} Channel Chat scraped successfully!\n'.format(group_title) + color.wt)
        return True
        pass

    # Enter all the user data into CSV file    
    def Enter_User_Into_CSVFile(self, all_participants, group_title = "", group_id = "", filename = ""):
        color = Color()

        print(color.gr+'\n[+] Saving User(s) Details In CSV File ...'+ color.wt)
        time.sleep(1)

        timestamp = int(datetime.datetime.now().timestamp())
        filename = '%s_%s.csv' % (filename.replace("/", "_"), timestamp)
        self.__create_dirs('output')
        completename = os.path.join('./output', filename)

        with open(completename, "w",encoding='UTF-8') as f:
            writer = csv.writer(f,delimiter=",",lineterminator="\n")
            writer.writerow(['username','user id', 'access hash','name','group', 'group id'])
            for user in all_participants:
                username = user.username or ""
                first_name = user.first_name or ""
                last_name = user.last_name or ""
                name= (first_name + ' ' + last_name).strip()
                writer.writerow([username, user.id, user.access_hash, name, group_title, group_id])
        print(color.cy+'[+] {} Channel Members scraped successfully!\n'.format(group_title) + color.wt)
        return True

    # Create new folders
    def __create_dirs(self, root, subfolders=None):
        root = root if subfolders == None else f'{root}/{subfolders}/'
        if not os.path.exists(root):
            os.makedirs(f'{root}', exist_ok=True)

# Main function
def telegramMain():
    # Parser to take the arguments
    parser = argparse.ArgumentParser(description="Python Tool: Telegram Scrapper")
    parser.add_argument("-m", "--Self_Group_Members", help="Option To Scrap Self Group Members e.g. python Telegram_scrap.py -m self")
    parser.add_argument("-i", "--Any_Group_Members", help="Option To Scrap Any Groups e.g. python Telegram_scrap.py -i group_name")
    parser.add_argument("-b", "--Basic_Group_Scan", help="Option To get Group Details e.g. python Telegram_scrap.py -t group_name")
    parser.add_argument("-u", "--User_Details", help="Option To Get User Details e.g. python Telegram_scrap.py -u user_name")
    parser.add_argument("-v", "--version", help="show tool version", action="store_true")
    args = parser.parse_args()

    # Check for --single-entry or -s
    if args.Self_Group_Members:
        tele_members = Tele_MemberScarap()
        tele_members.Self_Group_Member_Finder()

    elif args.Any_Group_Members:
        tele_members = Tele_MemberScarap()
        tele_members.Any_Group_Member_Finder(args.Any_Group_Members.strip())

    elif args.Basic_Group_Scan:
        tele_members = Tele_MemberScarap()
        tele_members.get_basic_scan(target_group=args.Basic_Group_Scan.strip())

    elif args.User_Details:
        tele_members = Tele_MemberScarap()
        tele_members.get_user_information(target_user=args.User_Details.strip())

    elif args.version:
        print("\nPython Tool: Telegram Scrapping Tool ver:1.0.0\n--Alien.C00de--\n")
    else:
        print("usage: Telegram_scrap.py [-h] [-m Member_Scrap] [-V]")

if __name__ == '__main__':
    telegramMain()
