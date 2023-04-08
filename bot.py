import math

import telebot
import config
import apex
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

bot = telebot.TeleBot(config.BotToken)

platform_data = {'tg_id': None, 'alplatform': 'PC'}


@bot.message_handler(commands=['start'])
def start(m):
    markup = ReplyKeyboardMarkup(row_width=1)

    menu = KeyboardButton('Menu')

    markup.add(menu)

    text = f'Hi {m.from_user.full_name}'

    bot.send_message(m.chat.id, text, reply_markup=markup)


@bot.message_handler(regexp='Search')
def platform(m):
    markup = InlineKeyboardMarkup()

    # menu = KeyboardButton('Menu')
    # markup.add(menu)

    text = "Choose platform: "

    markup.add(InlineKeyboardButton(text='PC', callback_data=f'platform?PC'))
    markup.add(InlineKeyboardButton(text='Playstation', callback_data=f'platform?PS4'))
    markup.add(InlineKeyboardButton(text='Xbox', callback_data=f'platform?X1'))

    msg = bot.send_message(m.chat.id, text=text, reply_markup=markup)
    bot.register_next_step_handler(msg, player)
    # sg = bot.send_message(m.chat.id, text, reply_markup=markup)
    # ot.register_next_step_handler(msg, callback='platform')


def player(m):
    plyr = apex.alplayer(m.text, platform_data['alplatform'])

    inline_markup = InlineKeyboardMarkup()



    inline_markup.add(
            InlineKeyboardButton(text=f'Selected legend', callback_data=f'selected_legend?{m.text}')
        )

    text = f'Status: {plyr["realtime"]["currentStateAsText"]}\n' \
           f'Lobby status: {plyr["realtime"]["lobbyState"]}\n' \
           f'Player: {plyr["global"]["name"]}\n' \
           f'Platform: {plyr["global"]["platform"]}\n' \
           f'Level: {plyr["global"]["level"]} ({plyr["global"]["toNextLevelPercent"]}%)\n' \
           f'Rank: {plyr["global"]["rank"]["rankName"]} {plyr["global"]["rank"]["rankDiv"]} ({plyr["global"]["rank"]["rankScore"]} RP)\n' \
           f'Selected legend: {plyr["realtime"]["selectedLegend"]}'

    bot.send_message(m.chat.id, text=text, reply_markup=inline_markup)


@bot.message_handler(regexp='Store')
def store(m):
    inline_markup = InlineKeyboardMarkup()

    index = 4
    page = 1

    x = apex.req('store')
    keys = []

    for i in x:
        if i['shopType'] not in keys:
            keys.append(i['shopType'])

    for i in keys:
        inline_markup.add(
            InlineKeyboardButton(text=f'{str(i).capitalize()}', callback_data=f'store?{i}?{index}?{page}')
        )

    bot.send_message(m.chat.id, text='Current store items:', reply_markup=inline_markup)


@bot.message_handler(regexp='Replicator')
def replicators(m):
    inline_markup = InlineKeyboardMarkup()

    x = apex.req('crafting')

    page = 1
    for i in x[:4]:
        if i["bundleType"] != 'permanent':
            inline_markup.add(InlineKeyboardButton(text=f'{i["bundleType"]} rotation',
                                                   callback_data=f'replicator?{i["bundleType"]}?{page}'))
        else:
            inline_markup.add(
                InlineKeyboardButton(text=f'{i["bundle"]} rotation', callback_data=f'replicator?{i["bundle"]}?{page}'))

    bot.send_message(m.chat.id, text='Craft rotation: ', reply_markup=inline_markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    query = call.data.split('?')

    global platform_data

    if query[0] == 'replicator':
        bundle_type = query[1]
        inline_markup = InlineKeyboardMarkup()
        ALreplicator = apex.req('crafting')
        for i in ALreplicator[:4]:
            if i["bundleType"] == bundle_type or i['bundle'] == bundle_type:

                inline_markup.add(InlineKeyboardButton(text='Back', callback_data=f'replicators'))

                if len(i["bundleContent"]) > 1:  # с пагинацией
                    page = int(query[2])
                    if page == 1:
                        inline_markup.add(InlineKeyboardButton(text=f'{page}/2', callback_data=f' '),
                                          InlineKeyboardButton(text='-->',
                                                               callback_data=f'replicator?{i["bundleType"]}?{page + 1}'))
                    else:
                        inline_markup.add(
                            InlineKeyboardButton(text='<--', callback_data=f'replicator?{i["bundleType"]}?{page - 1}'),
                            InlineKeyboardButton(text=f'{page}/2', callback_data=f' ')
                            )
                    bot.edit_message_text(
                        f'Item: {i["bundleContent"][page - 1]["itemType"]["rarity"]} {i["bundleContent"][page - 1]["itemType"]["name"]}\n'
                        f'Cost: {i["bundleContent"][page - 1]["cost"]}\n'
                        f'StartDate: {i["startDate"]}\n'
                        f'EndDate: {i["endDate"]}\n'
                        f'{i["bundleContent"][page - 1]["itemType"]["asset"]}',
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=inline_markup
                    )
                    break
                elif len(i["bundleContent"]) == 1:  # без пагинации
                    bot.edit_message_text(
                        f'Weapon: {i["bundleContent"][0]["itemType"]["name"]}\n'
                        f'Cost: {i["bundleContent"][0]["cost"]}\n'
                        f'{i["bundleContent"][0]["itemType"]["asset"]}',
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=inline_markup)

                    break
    elif 'replicators' in query:  # список крафтящихся предметов через параметр "временности"
        page = 1
        ALreplicator = apex.req('crafting')
        inline_markup = InlineKeyboardMarkup()
        for i in ALreplicator[:4]:
            if i["bundleType"] != 'permanent':  # shows rotating crafting items
                inline_markup.add(InlineKeyboardButton(text=f'{i["bundleType"]} rotation',
                                                       callback_data=f'replicator?{i["bundleType"]}?{page}'))
            else:  # shows crafting guns
                inline_markup.add(InlineKeyboardButton(text=f'{i["bundle"]} rotation',
                                                       callback_data=f'replicator?{i["bundle"]}?{page}'))
        bot.edit_message_text(text='Craft rotation: ', chat_id=call.message.chat.id, message_id=call.message.message_id,
                              reply_markup=inline_markup)

    elif query[0] == 'map':
        mode = query[1]
        ALmap = apex.req('maprotation', 'version=2')
        inline_markup = InlineKeyboardMarkup()

        if query[2] == 'next':
            curnext = 'current'
        else:
            curnext = 'next'

        # Adds Back button( returns to game modes ) and 'next'/'current' buttons ( shows next/current game mode map )
        inline_markup.add(InlineKeyboardButton(text='Back', callback_data='MapRotation'),
                          InlineKeyboardButton(text=f'{curnext.capitalize()} map',
                                               callback_data=f'map?{mode}?{curnext}'))

        if int(ALmap[mode][query[2]]["DurationInMinutes"]) < 120:
            duration = f'{ALmap[mode][query[2]]["DurationInMinutes"]} minutes'
        else:
            duration = f"{int(ALmap[mode][query[2]]['DurationInMinutes'] / 60)} hours"

        text = ''

        keys = {"asset": '', "eventName": 'LTM: ', "map": "Map: ", "remainingTimer": "Remaining Time: "}

        for i, c in keys.items():
            if i == 'asset' and 'eventName' in ALmap[mode][query[2]]:
                continue
            elif i in ALmap[mode][query[2]]:
                text += f'{c}{ALmap[mode][query[2]][i]}\n'
        text += f'Duration: {duration}'

        bot.edit_message_text(
            text=text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=inline_markup
        )

    elif query[0] == 'MapRotation':
        inline_markup = InlineKeyboardMarkup()

        current = apex.req('maprotation', y='version=2')

        for i in current:
            if 'arenas' not in i:
                inline_markup.add(InlineKeyboardButton(text=f'{i}', callback_data=f'map?{i}?current'))

        bot.edit_message_text(
            text="Which mode: ",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=inline_markup
        )

    elif query[0] == 'store':
        ALshop = apex.req('store')
        inline_markup = InlineKeyboardMarkup()
        page = int(query[3])
        index = int(query[2])
        pages = math.ceil(len(ALshop) / 4)

        inline_markup.add(InlineKeyboardButton(text='___________________________', callback_data=' '))

        for i in ALshop[index - 4:index]:  # Showing items in the shop page by page
            if i['shopType'] == query[1]:
                inline_markup.add(
                    InlineKeyboardButton(text=f'{i["title"]}',
                                         callback_data=f'shopItem?{i["title"]}?{query[1]}?{index}?{page}')
                )

        inline_markup.add(InlineKeyboardButton(text='___________________________', callback_data=' '))

        if page == 1:  # Page 1
            inline_markup.add(
                InlineKeyboardButton(text=f'{page}/{pages}', callback_data=' '),
                InlineKeyboardButton(text='-->', callback_data=f'store?{query[1]}?{index + 4}?{page + 1}')
            )

        elif page == pages:  # Any page
            inline_markup.add(
                InlineKeyboardButton(text='<--', callback_data=f'store?{query[1]}?{index - 4}?{page - 1}'),
                InlineKeyboardButton(text=f'{page}/{pages}', callback_data=' ')
            )

        else:  # Last page
            inline_markup.add(
                InlineKeyboardButton(text='<--', callback_data=f'store?{query[1]}?{index - 4}?{page - 1}'),
                InlineKeyboardButton(text=f'{page}/{pages}', callback_data=' '),
                InlineKeyboardButton(text='-->', callback_data=f'store?{query[1]}?{index + 4}?{page + 1}')
            )

        # Back Button
        inline_markup.add(InlineKeyboardButton(text='Back', callback_data=f'shopType?{query[1]}?{index}?{page}'))

        bot.edit_message_text(
            text=f'{query[1].capitalize()}',
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=inline_markup
        )

    elif query[0] == 'shopType':  # shop Back button
        inline_markup = InlineKeyboardMarkup()

        x = apex.req('store')
        keys = []

        for i in x:
            if i['shopType'] not in keys:
                keys.append(i['shopType'])

        for i in keys:  # Choose which type of shop (specials/basic shop)
            inline_markup.add(
                InlineKeyboardButton(text=f'{str(i).capitalize()}', callback_data=f'store?{i}?{query[2]}?{query[3]}')
            )

        bot.edit_message_text(
            text=f'Store: ',
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=inline_markup
        )


    elif query[0] == 'shopItem':
        ALshop = apex.req('store')
        inline_markup = InlineKeyboardMarkup()
        # Back button( returns to all items in shop )
        inline_markup.add(
            InlineKeyboardButton(text='Back', callback_data=f'store?{query[2]}?{query[3]}?{query[4]}')
        )

        for i in ALshop:
            if i['title'] == query[1]:
                bot.edit_message_text(
                    text=f'Title: {i["title"]}\n'
                         f'Price: {i["pricing"][0]["quantity"]} {i["pricing"][0]["ref"]}\n'
                         f'{i["asset"]}',
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=inline_markup
                )
                break


    elif query[0] == 'platform':

        platform_data['alplatform'] = query[1]

        bot.edit_message_text(text="Type player's nickname: ", chat_id=call.message.chat.id,
                              message_id=call.message.message_id)

    elif query[0] == 'player':


        plyr = apex.alplayer(query[2],platform_data['alplatform'])

        if query[1] == 'global':
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(text='Selected legend', callback_data=f'selected_legend?{query[2]}'))


            text = f'Status: {plyr["realtime"]["currentStateAsText"]}\n' \
                   f'Lobby status: {plyr["realtime"]["lobbyState"]}\n' \
                   f'Player: {plyr["global"]["name"]}\n' \
                   f'Platform: {plyr["global"]["platform"]}\n' \
                   f'Level: {plyr["global"]["level"]} ({plyr["global"]["toNextLevelPercent"]}%)\n' \
                   f'Rank: {plyr["global"]["rank"]["rankName"]} {plyr["global"]["rank"]["rankDiv"]} ({plyr["global"]["rank"]["rankScore"]} RP)\n' \
                   f'Selected legend: {plyr["realtime"]["selectedLegend"]}'

            if plyr['global']['bans']['isActive']:
                text += f'Ban:\n' \
                        f'  Remaining time: {plyr["global"]["bans"]["remainingSeconds"]} seconds\n' \
                        f'  Ban reason: {plyr["global"]["bans"]["last_banReason"]}'

            bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=markup)

    elif query[0] == 'selected_legend':

        markup = InlineKeyboardMarkup()

        markup.add(InlineKeyboardButton(text='Back', callback_data=f'player?global?{query[1]}'))

        plyr = apex.alplayer(query[1], platform_data['alplatform'])

        legend = plyr["legends"]["selected"]

        text = f'{legend["ImgAssets"]["icon"]}\n' \
               f'Selected legend: {legend["LegendName"]}\n' \
               f'{legend["data"][0]["name"]}: {legend["data"][0]["value"]}\n' \
               f'{legend["data"][2]["name"]}: {legend["data"][2]["value"]}'

        bot.edit_message_text(
            text=text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )



@bot.message_handler(regexp='Current map')
def current_map(m):
    inline_markup = InlineKeyboardMarkup()

    current = apex.req('maprotation', y='version=2')

    for i in current:
        if 'arenas' not in i:
            inline_markup.add(InlineKeyboardButton(text=f'{i}', callback_data=f'map?{i}?current'))

    bot.send_message(m.chat.id, text='Which mode:', reply_markup=inline_markup)


@bot.message_handler(regexp='Menu')
def menu(m):
    markup = ReplyKeyboardMarkup(row_width=1)

    search_player = KeyboardButton('Search')
    store_rotation = KeyboardButton('Store')
    craft_rotation = KeyboardButton('Replicator')
    current_map = KeyboardButton('Current map')

    markup.add(search_player, store_rotation, craft_rotation, current_map)

    text = 'Menu'

    bot.send_message(m.chat.id, text, reply_markup=markup)


bot.infinity_polling()
