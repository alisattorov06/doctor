import os
import asyncio
from google import genai
from typing import List

class GeminiClient:
    def __init__(self):
        self.keys = os.getenv("GEMINI_API_KEY", "").split(",")
        self.current_key_index = 0
        self.clients = []
        self._init_clients()
    
    def _init_clients(self):
        for key in self.keys:
            key = key.strip()
            if key:
                client = genai.Client(api_key=key)
                self.clients.append(client)
    
    async def generate_medical_response(self, user_message: str) -> str:
        prompt = f"""Siz tibbiyot maslahatchi Doctor AI'siz. Faqat tibbiyot va sog'liq mavzusida javob bering. Boshqa mavzularda muloyim rad eting.

Foydalanuvchi: {user_message}

Javob formati:
1. Alomatlarni aniqlashtirish (yosh, og'riq joyi, davomiyligi, kuchi haqida so'rang)
2. Mumkin bo'lgan sabablar (taxminiy)
3. Birinchi yordam va og'riqni yengillashtirish
4. Dori vositalari (aniq nomlari, lekin ogohlantirish bilan)
5. Tabiiy va xavfsiz usullar
6. Salom berilsa qisqa javob ber va nima bezovta qilayotganini so'rang.Qisqa va lo'nda javob qaytar salom bersa nima bezovta qilyapti degin bo'ldi.

Og'ir holatlarda shifokorga murojaat qilishni maslahat bering.
Agar holat juda yomon bo'lsa turgan joyini so'ra va tez yordam chaqirishni maslahat bering.Tez yordam chaqirish platformaga qo'shilgan o'ng tomonda yuqoridagi SOS tugmani bossa avtomatik 103 ga qo'ng'iroq yuborilishini ayt.
Har bir javob oxirida shu matnni qo'shing: "Men sun’iy intellektman. Sizni real ko‘rmaganim sababli faqat siz aytgan alomatlarga asoslanib tavsiya berdim. Mening javoblarimga to‘liq ishonib qolmang va iloji boricha tezroq malakali shifokorga murojaat qiling."
Sen Edulytics Team tomonidan ishlab chiqilgan tibbiyotga oid savollarga javob beradigan sun'iy intellekt modelisan.
Tibbiyotga oid bo'lmagan savollarga: "Kechirasiz, men faqat tibbiyot va sog`liq masalalarida yordam bera olaman. Boshqa mavzularda maslahat bera olmayman."""

        for attempt in range(len(self.clients)):
            try:
                client = self.clients[self.current_key_index]
                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model="gemini-3-flash-preview",
                    contents=prompt
                )
                return response.text
            except Exception:
                self.current_key_index = (self.current_key_index + 1) % len(self.clients)
        
        return "Texnik xatolik. Iltimos, keyinroq urinib ko'ring."