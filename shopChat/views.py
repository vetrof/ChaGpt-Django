from openai import OpenAI
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse

from .models import Shoe


def get_shoe_price(shoe_name):
    """Функция для получения цены обуви по названию"""
    try:
        shoe = Shoe.objects.get(name__icontains=shoe_name, available=True)
        return shoe.price
    except Shoe.DoesNotExist:
        return None  # Если обувь не найдена


def shop_chat(request):
    if request.method == 'POST':
        print("POST>>")
        user_message = request.POST.get('user_message', '')

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        print("WAIT OPENAI>>")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": "Вы бот, отвечающий только на вопросы, "
                            "связанные с продажей обуви в магазине 'Тапки-лапки'. "
                            "Если вопрос не касается магазина или обуви или ухода за ней, вежливо откажите."},
                {"role": "user", "content": user_message}
            ],
            functions=[  # Настройка функции для получения цены
                {
                    "name": "get_shoe_price",
                    "description": "Получает цену обуви по названию",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "shoe_name": {"type": "string", "description": "Название обуви"}
                        },
                        "required": ["shoe_name"]
                    }
                }
            ]
        )

        # Проверяем, если модель вызывает функцию
        message = response.choices[0].message
        answer = message.content
        # TODO разобраться с вызовом функции при получении цен
        # if message.get("function_call"):
        #     function_name = message["function_call"]["name"]
        #     shoe_name = message["function_call"]["arguments"]["shoe_name"]
        #
        #     if function_name == "get_shoe_price":
        #         price = get_shoe_price(shoe_name)
        #         # Ответ модели с актуальной ценой
        #         if price:
        #             answer = f"Цена на {shoe_name} составляет {price} рублей."
        #         else:
        #             answer = f"К сожалению, мы не нашли информацию о {shoe_name}."
        # else:
        #     answer = message.content

        return JsonResponse({"answer": answer})
    return render(request, 'shop-chat.html')



