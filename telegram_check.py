from telethon import TelegramClient

# بيانات API الخاصة بك
api_id = '###'  # استبدل YOUR_API_ID بمعرف API الخاص بك
api_hash = '###'  # استبدل YOUR_API_HASH بمفتاح API الخاص بك

# إنشاء الجلسة
client = TelegramClient('session_name', api_id, api_hash)

async def get_latest_post_number(channel_username):
    try:
        # الحصول على آخر رسالة في القناة
        message = await client.get_messages(channel_username, limit=1)
        if message:
            # رقم المنشور الأخير
            post_number = message[0].id
            print(f"تسلسل آخر بوست هو: {post_number}")
        else:
            print("لا توجد منشورات في القناة.")

        return post_number 
    
    except:
        return 0
    

