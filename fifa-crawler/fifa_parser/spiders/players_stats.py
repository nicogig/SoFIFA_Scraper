# -*- coding: utf-8 -*-
import scrapy
import json
import logging

class SofifaSpider(scrapy.Spider):
    name='players_stats'
    date = '200061' # FIFA 20

    def __init__(self):
        with open('../data/json/players_urls.json') as json_data:
            self.players = json.load(json_data)
        self.player_count = 1

    def start_requests(self):
        urls = [
            'https://sofifa.com/player/158023/{}?units=mks'.format(self.date) # ---> Messi example page
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for player in response.css('.info'):
            player_name = player.xpath('//div[@class="info"]/h1/text()').get() 
            player_teams = player.xpath('//div[@class="column col-3"]//h5//a/text()').getall() #Get the first team
            try:
                team = player_teams[0]
            except IndexError as indexError:
                team = None
            player_general_ratings = player.xpath('//div[@class="bp3-card player"]//div[@class="column col-3"]//span/text()').getall() # Overall Rating + Potential
            
            primary_stats = {'Overall Rating':player_general_ratings[0], 'Potential Rating':player_general_ratings[1]}
            
            ## Older FIFA games (09 for example) do not have all of this info, so for games that are not FIFA 21 I'm not scraping them.
            #player_ratings = []
            #player_ratings_names = ['Team Rating', 'Crossing', 'Dribbling', 'Acceleration', 'Shot Power', 'Aggression', 'Defensive Awareness', 'GK Diving', 'Finishing', 'Curve', 'Sprint Speed', 'Jumping', 'Interceptions', 'Standing Tackle', 'GK Kicking', 'Short Passing', 'Long Passing', 'Reactions', 'Strength', 'Vision', 'GK Positioning', 'Volleys', 'Ball Control', 'Balance', 'Long Shots', 'Penalties', 'GK Reflexes', 'Composure' ]

            #for i in range(1, 7):
            #    temp = player.xpath('//div[@class="column col-3"]//ul//li[{}]//span[1]/text()'.format(i)).re(r'\w+')
                #temp_names = player.xpath('//div[@class="column col-3"]//ul//li[{}]//span[2]/text()'.format(i)).getall()
            #    if len(player_teams) > 1 and i == 1:
            #        temp.pop(1) # We do not care about the national team
            #    player_ratings.extend([x for x in temp if x.isdigit()])

            #player_ratings_dict = {}
            #for i in range(len(player_ratings_names)):
            #    player_ratings_dict[player_ratings_names[i]] = player_ratings[i]

            player_info_dict = {
                'Name': player_name,
                'Team': team,
                'Primary Stats': primary_stats,
                #'Secondary Stats': player_ratings_dict
            }

            logging.info('*****************************************     ' + str(self.player_count) + '\n\n\n')
            yield player_info_dict

            if self.player_count < len(self.players):
                next_page_url = 'https://sofifa.com' + self.players[self.player_count]['player_url'] + '/{}'.format(self.date) + '?units=mks'
                self.player_count += 1
                yield scrapy.Request(url=next_page_url, callback=self.parse)