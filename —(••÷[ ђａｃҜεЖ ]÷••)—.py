import logging
import time
from collections import defaultdict
from typing import Optional, Tuple
from datetime import datetime, timedelta
import telegram
from telegram import Chat, ChatMember, ChatMemberUpdated, Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions, ChatMemberRestricted, Bot
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    ChatMemberHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackContext,
    ExtBot,
    Application, CallbackQueryHandler, ContextTypes, ConversationHandler
)

TOKEN = "Your Tocken"
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def extract_status_change(chat_member_update: ChatMemberUpdated) -> Optional[Tuple[bool, bool]]:
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("MEMBER", (None, None))

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

    return was_member, is_member

async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = extract_status_change(update.my_chat_member)
    if result is None:
        return
    was_member, is_member = result

    cause_name = update.effective_user.full_name
    chat = update.effective_chat
    if chat.type == Chat.PRIVATE:
        if not was_member and is_member:
            logger.info("%s  BOT Sbloccato", cause_name)
            context.bot_data.setdefault("user_ids", set()).add(chat.id)
        elif was_member and not is_member:
            logger.info("%s BOT Bloccato", cause_name)
            context.bot_data.setdefault("user_ids", set()).discard(chat.id)
    elif chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
        if not was_member and is_member:
            logger.info("%s è stato/a aggiunto/a al gruppo 🧑‍🤝‍🧑  %s", cause_name, chat.title)
            context.bot_data.setdefault("group_ids", set()).add(chat.id)
        elif was_member and not is_member:
            logger.info("%s è stato/a rimosso/a dal gruppo %s", cause_name, chat.title)
            context.bot_data.setdefault("group_ids", set()).discard(chat.id)
    elif not was_member and is_member:
        logger.info("%s è stato/a aggiunto/a %s", cause_name, chat.title)
        context.bot_data.setdefault("channel_ids", set()).add(chat.id)
    elif was_member and not is_member:
        logger.info("%s è stato/a rimosso/a %s", cause_name, chat.title)
        context.bot_data.setdefault("channel_ids", set()).discard(chat.id)

welcome_gif = "https://media4.giphy.com/media/yMWdlaSuPk7WkQaQBY/200.gif"
exit_gif = "https://media3.giphy.com/media/SefUpaLtGNLs9gtg4u/200.gif"

async def greet_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    result = extract_status_change(update.chat_member)
    if result is None:
        return

    was_member, is_member = result
    cause_name = update.chat_member.from_user.mention_html()
    member_name = update.chat_member.new_chat_member.user.mention_html()
    member_id = update.chat_member.new_chat_member.user.id

    if not was_member and is_member:
        await context.bot.send_animation(
            chat_id=chat_id,
            animation=welcome_gif,
            caption=(
                f"{member_name} [{member_id}] è stato/a aggiunto/a da {cause_name}. Benvenuto/a in questo gruppo! "
                "Si prega il gentile utente di rispettare il regolamento. "
                "Una presentazione è sempre ben gradita... Buona permanenza!"
            ),
            parse_mode=ParseMode.HTML
        )
    elif was_member and not is_member:
    
            await context.bot.send_animation(
            chat_id=chat_id,
            animation=exit_gif,
            caption=(
                f"{member_name} [{member_id}] è stato/a rimosso/a da {cause_name}, "
                "è stato breve ma intenso... RIP.."
            ),
            parse_mode=ParseMode.HTML
        )










fuoco = ['Fuoco', 'fuoco', 'tornado', 'Tornado', '1 a 0', 'uno a zero']
evocazione = ['Evoco', 'Evocazione', 'evocazione', 'evocazione', 'invocazione', 'Invocazione']
bestemmie = ['Dio', 'dio', 'DIO', 'madonna', 'Madonna', 'sant', 'Sant']
bad_words = ['compagnia?', 'compagnia ?', 'Compagnia?', 'Compagnia ?', 'Vendo', 'vendo', 'Offerta', 'offerta', 'Pubblicità', 'pubblicità', ]

tornado_gif = "https://media1.giphy.com/media/l0HlSGNW8OaNOLivK/200.gif"
evocazione_gif = "https://media1.giphy.com/media/55omzn8jo9Qld5L032/200.gif"
ban_gif_url = "https://media2.giphy.com/media/100QoSU9uTFU64/200.gif"
god_gif = "https://media4.giphy.com/media/NsCPVq6swx37Fq3GUm/200.gif"
mute_gif = "https://media3.giphy.com/media/tdkx9be2XuHAs/200.gif"

bestemmiometro = 0
user_bad_words_counter = {}
user_messages = defaultdict(list)






async def respond_to_group_words(update: Update, context: CallbackContext) -> None:
    global bestemmiometro
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    message_text = update.message.text.lower()
    user_name = update.effective_user.full_name

    if chat_type in [Chat.GROUP, Chat.SUPERGROUP]:
        if any(word in message_text for word in bestemmie):
            bestemmiometro += 1
            await context.bot.send_animation(
                chat_id=chat_id,
                animation=god_gif,
                caption=f"{user_name}, il bestemmiometro segna {bestemmiometro} bestemmie...",
                parse_mode=ParseMode.HTML
            )
        elif any(word in message_text for word in evocazione):
            await context.bot.send_animation(
                chat_id=chat_id,
                animation=evocazione_gif,
                caption=f"{user_name}",
                parse_mode=ParseMode.HTML
            )
        elif any(word in message_text for word in fuoco):
            await context.bot.send_animation(
                chat_id=chat_id,
                animation=tornado_gif,
                caption=f"{user_name}",
                parse_mode=ParseMode.HTML
            )

    if any(bad_word in message_text for bad_word in bad_words):
        if user_id not in user_bad_words_counter:
            user_bad_words_counter[user_id] = 0
        user_bad_words_counter[user_id] += 1

        await context.bot.send_message(chat_id=chat_id, text=f"WARN⚠️ {user_name}, [{user_id}], {user_bad_words_counter[user_id]}/3")

        if user_bad_words_counter[user_id] >= 3:
            await context.bot.send_animation(chat_id=chat_id, animation=ban_gif_url)
            await context.bot.send_message(chat_id=chat_id, text=f"BAN⚠️ {user_name}, [{user_id}], ed è così che si fa notizia...")
            ban_time = datetime.now() + timedelta(hours=24)
            ban_time_unix = int(ban_time.timestamp())

            try:
                context.chat_data["ban"] = True
                await context.bot.ban_chat_member(chat_id=chat_id, user_id=user_id, until_date=ban_time_unix)
                user_bad_words_counter[user_id] = 0
                del context.chat_data["ban"]
            except telegram.error.BadRequest as e:
                if 'Chat_admin_required' in str(e):
                    await context.bot.send_message(chat_id=chat_id, text="Non ho i permessi necessari per bannare membri. Assicurati che io abbia i permessi di amministratore.")
   
    current_time = time.time()
    user_messages[user_id].append(current_time)
    user_messages[user_id] = [timestamp for timestamp in user_messages[user_id] if current_time - timestamp < 30]

    logger.info(f"User {user_id} has sent {len(user_messages[user_id])} messages in the last minute.")

    if len(user_messages[user_id]) > 10:
        try:
            mute_time = 300
            mute_permissions = ChatPermissions(can_send_messages=False)
            until_date = int(time.time() + mute_time)

            context.chat_data["mute"] = True
            await context.bot.restrict_chat_member(chat_id=chat_id, user_id=user_id, permissions=mute_permissions, until_date=until_date)
            await context.bot.send_animation(
                animation=mute_gif,
                chat_id=chat_id,
                caption="Per favore, non spammare. Hai inviato più di 10 messaggi nell'ultimo minuto e sei stato temporaneamente mutato per 5 minuti.",
                parse_mode=ParseMode.HTML
            )
            user_messages[user_id] = []
            del context.chat_data["mute"]
        except Exception as e:
            if 'Chat_admin_required' in str(e):
                await context.bot.send_message(chat_id=chat_id, text="Non ho i permessi necessari per mutare membri. Assicurati che io abbia i permessi di amministratore.")








def main() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(ChatMemberHandler(greet_chat_members, ChatMemberHandler.CHAT_MEMBER))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, respond_to_group_words))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
