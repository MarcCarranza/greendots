from bot_utils import *

API_KEY = open('../data/client_secret.txt', 'r').read().strip()

client_actions: List[List[Union[str, Callable]]] = None
ad_actions: List[List[Union[str, Callable]]] = None
mockup_advertisements_db = None
mockup_users_db = None

# region Helper Methods

# adds the callback handlers of the bot # this is actually the logic and brains 
# of the bot without handlers it cannot answer to any action done by the user
def add_dispatcher_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler('start', start))
    # this handler should be for the inline ad buttons
    dispatcher.add_handler(CallbackQueryHandler(button_pressed_handler))
    dispatcher.add_handler(MessageHandler(Filters.text, message_received_handler))

# endregion

# region Commands

# START Command - executed when the conversation starts
def start(update: Update, context: CallbackQuery):
    basic_callback_debug(update, context, command_name='start')
    mockup_users_db.add(update.message.from_user.id)

    kb_buttons = []
    for [action, _] in client_actions:
        kb_buttons.append(KeyboardButton(action)) 
    kb_buttons = build_menu(kb_buttons, 2)

    kb_markup = ReplyKeyboardMarkup(kb_buttons)
    context.bot.send_message(chat_id=update.message.chat_id, text='Selecciona una opció:',
                             reply_markup=kb_markup)

# ADS Command - return a list of ads of interest to the user
def get_ads_handler(update: Update, context: CallbackQuery):
    basic_callback_debug(update, context, command_name='get ads')
    # Get a list of relevant ads for the user and generete messages for it
    ads = mockup_advertisements_db.get_all()
    if (ads == []):
        update.message.reply_text(emojize("No hem pogut trobar cap anunci :( " + 
            "Apropa't al teu comerç més proper i anima’l a usar <b>Uepa!</b> :pear:"),
            parse_mode=ParseMode.HTML)
    else:
        for a in ads:
            send_ad(update, context, a)

# given an advertisement it will send the advertisement message with its own
# inline keyboard buttons
def send_ad(update, context, advertisement):
    ad_buttons = []
    for [action, _] in ad_actions:
        ad_buttons.append(InlineKeyboardButton(action, callback_data=action))

    reply_markup = InlineKeyboardMarkup(build_menu(ad_buttons, n_cols=2))
    message = '[id:' + str(advertisement.id) + '] ' + advertisement.message
    context.bot.send_message(update.message.chat_id,
                             text=message, reply_markup=reply_markup)


# SEARCH Command - asks for an input text and returns a list of shops who meet the
# desired searching criteria
# [currently unimplemented]
def search_handler(update: Update, context: CallbackQuery):
    basic_callback_debug(update, context, command_name='search')
    kb_buttons = []
    # Generate search buttons!
    for [action, _] in cercar_actions:
        kb_buttons.append(KeyboardButton(action)) 
    kb_buttons = build_menu(kb_buttons, 1)
    kb_markup = ReplyKeyboardMarkup(kb_buttons)
    context.bot.send_message(chat_id=update.message.chat_id, text="Com t' agradaria buscar el comerç?",
                             reply_markup=kb_markup)

    #update.message.reply_text("Cerca els comerços del teu barri! " + 
    #        "Pots filtrar per <b>Categoríes</b> o per <b>Nom</b>.",
    #        parse_mode=ParseMode.HTML)

def get_categories(update: Update, context: CallbackQuery):
    basic_callback_debug(update, context, command_name='categories_search')

    kb_buttons = []
    # Generate search buttons!
    for [action, _] in shop_categories:
    	kb_buttons.append(KeyboardButton(action)) 
    kb_buttons = build_menu(kb_buttons, 2)
    kb_markup = ReplyKeyboardMarkup(kb_buttons)
    context.bot.send_message(chat_id=update.message.chat_id, text="Selecciona una categoria!", reply_markup=kb_markup)


def get_shop_search(update: Update, context: CallbackQuery):
    basic_callback_debug(update, context, command_name='shop_name_search')
    update.message.reply_text(emojize("Escriu el nom del comerç " +
    	"O envian's un àudio! Aquest serà processat utilitzant <b>NLP</b> :microphone:"), parse_mode=ParseMode.HTML)


# HELP Command - returns a pretty-printed list of commands and useful information
# [currently unimplemented]
def help_handler(update: Update, context: CallbackQuery):
    basic_callback_debug(update, context, command_name='help')
    kb_buttons = []
    # Generate search buttons!
    for [action, _] in help_buttons:
        kb_buttons.append(KeyboardButton(action)) 
    kb_buttons = build_menu(kb_buttons, 1)
    kb_markup = ReplyKeyboardMarkup(kb_buttons)
    context.bot.send_message(chat_id=update.message.chat_id, text="En què necessites ajuda?", reply_markup=kb_markup)
    

def get_uepa_help(update: Update, context: CallbackQuery):
    basic_callback_debug(update, context, command_name='uepa')
    update.message.reply_text(emojize("<b>Hola!! Benvingut a Uepa!</b> \n:pear: El servei que t’apropa a la vida del teu barri :house_with_garden: . \nL’objectiu és crear" +
    	" un canal de comunicació directa entre veïnes i comerços locals :house:. \nSi vols conèixer les coses que estàn passant al teu voltant" +
    	" tens la opció <b>Anuncis</b> :newspaper:, on els comerciants podran fer publicacions i podràs establir converses amb ells. \nSi vols trobar algun" +
    	" negoci en concret, pots accedir a <b>Cercar</b> per buscar segons categoria o pel nom directament! " +
    	"\nFinalment, si vols fer una cerca amb el llistat de tots els establiments registrats al teu barri, " +
    	"pots accedir a <b>Llista</b> :memo:. \nMoltes gràcies per fer servir Uepa i esperem que gaudeixis aquesta plataforma!" +
    	"Comunica als teus comerciants de proximitat i fem barri junts! "), parse_mode=ParseMode.HTML)

    



def get_contact_help(update: Update, context: CallbackQuery):
    basic_callback_debug(update, context, command_name='help')
    update.message.reply_text(emojize("Si tens dubtes o suggerències no dubtes en escriure'ns :) Fem barri junts!\n" +
    	":envelope: Email: uepaapeu@gmail.com\n" +
    	"Tlf: 679598608"), parse_mode=ParseMode.HTML)

    
# MESSAGE RECEIVED - handler executed whenever a TEXT message is received from the user
def message_received_handler(update: Update, context: CallbackQuery): 
    for [action, handler] in client_actions:
        if (update.message.text == action):
            handler(update, context)
            return

    for [action, handler] in cercar_actions:
        if (update.message.text == action):
            handler(update, context)
            return

    for [action, handler] in help_buttons:
        if (update.message.text == action):
            handler(update, context)
            return


# ADVERTISEMENT INLINE BUTTONS - handler executed whenever an inlined button from an advertisement 
# is interacted with
def button_pressed_handler(update: Update, context: CallbackQuery):
    for [action, handler] in client_actions:
        if (update.message.text == action):
            handler(update, context)
            return
    query: CallbackQuery = update.callback_query
    print('user interacted with ' + query.message.text + ' and pressed ' + query.data +
          ' button pressed by user ' + str(query.from_user.username))

# PLACEHOLDER Command - unimplemented function
def placeholder_handler(update: Update, context: CallbackQuery):
    print("Unimplemented placeholder")
    unimplemented_function(update)

def contact_ad_owner(update: Update, context: CallbackQuery):
    return

def give_ad_feedback(update: Update, context: CallbackQuery):
    return

# endregion

# region Main Method

def main():
    # initialize the databases
    # in case the file already exists it will load the file
    # in case the file does not exists it will create an empty table

    global mockup_advertisements_db
    global mockup_users_db
    mockup_advertisements_db = AdvertisementDB('../data/advertisement_test.db')
    mockup_users_db = UsersDB("../data/users_test.db")


    global help_buttons
    help_buttons = [[emojize(':pear: Sobre Uepa', use_aliases=True), get_uepa_help], 
                    [emojize(':envelope: Contacte', use_aliases=True), get_contact_help], 
                    [emojize(':house: Start', use_aliases=True), start]]

    global client_actions
    client_actions = [[emojize(':newspaper: Què es cou?', use_aliases=True), get_ads_handler], 
                    [emojize(':mag: Cercar', use_aliases=True), search_handler], 
                    [emojize(':bulb: Ajuda', use_aliases=True), help_handler],
                    [emojize(':house_with_garden: El meu barri', use_aliases=True), start]]

    global cercar_actions
    cercar_actions = [[emojize(':rooster: Per Categoría', use_aliases=True), get_categories], 
                    [emojize(':abc: Per Nom', use_aliases=True), get_shop_search],
                    [emojize(':house: Start', use_aliases=True), start]]         

    global shop_categories
    shop_categories = [["Serveis generals", "1"], 
                    ["Alimentació", "2"],
                    ["Hosteleria", "3"],
                    ["Roba i Complements", "4"],
                    ["Llar", "5"],
                    ["Salut i benestar", "6"],
                    ["Altres", "7"],
                    ["Oci i Cultura", "8"],
                    [emojize(":house: Start"), start]]



    global ad_actions
    ad_actions = [[emojize('contactar'), contact_ad_owner],
                  [emojize('feedback'), give_ad_feedback]]

    # connect to the API with the key inside the secret.txt file
    updater = Updater(str(API_KEY),
                      use_context=True)
    dispatcher = updater.dispatcher
    add_dispatcher_handlers(dispatcher)

    # add a debugging/logging configuration to get a more granulated and
    # useful exception dump
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s' +
                        ' - %(message)s', level=logging.INFO)

    # start the application
    updater.start_polling()
    updater.idle()

# endregion

if __name__ == '__main__':
    main()
