import json
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


def get_shoes_by_type(shoe_type):
    """Функция для получения всех обуви определенного типа и их цен"""
    shoes = Shoe.objects.filter(name__icontains=shoe_type, available=True)
    shoe_list = [{"name": shoe.name, "price": shoe.price} for shoe in shoes]
    return shoe_list


def get_all_shoes():
    """Функция для получения всех доступных товаров в магазине"""
    shoes = Shoe.objects.filter(available=True)
    shoe_list = [{"name": shoe.name, "price": shoe.price} for shoe in shoes]
    return shoe_list


def shop_chat(request):
    if request.method == 'POST':
        user_message = request.POST.get('user_message', '')

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system",
                 "content": "Вы бот, отвечающий только на вопросы, "
                            "связанные с продажей обуви в магазине 'Тапки-лапки'. "
                            "Если вопрос не касается магазина или обуви или ухода за ней, вежливо откажите."},
                {"role": "user", "content": user_message}
            ],
            functions=[  # Настройка функций для получения данных
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
                },
                {
                    "name": "get_shoes_by_type",
                    "description": "Получает список обуви определенного типа",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "shoe_type": {"type": "string", "description": "Тип обуви, например, тапочки"}
                        },
                        "required": ["shoe_type"]
                    }
                },
                {
                    "name": "get_all_shoes",
                    "description": "Получает список всех обуви в магазине",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            ]
        )

        # Извлечение сообщения
        message = response.choices[0].message

        # Проверяем, если модель вызывает функцию
        if hasattr(message, 'function_call') and message.function_call:
            function_name = message.function_call.name  # Используем точечный доступ
            try:
                # Преобразуем строку JSON в словарь
                arguments = json.loads(message.function_call.arguments)
            except json.JSONDecodeError:
                arguments = {}

            if function_name == "get_shoe_price":
                shoe_name = arguments.get('shoe_name')
                if shoe_name:
                    price = get_shoe_price(shoe_name)
                    # Ответ с актуальной ценой
                    if price:
                        answer = f"Цена на {shoe_name} составляет {price} рублей."
                    else:
                        answer = f"К сожалению, мы не нашли информацию о {shoe_name}."
                else:
                    answer = "Ошибка при обработке запроса."
            elif function_name == "get_shoes_by_type":
                shoe_type = arguments.get('shoe_type')
                if shoe_type:
                    shoes = get_shoes_by_type(shoe_type)
                    if shoes:
                        shoes_list = "\n".join([f"{shoe['name']} - {shoe['price']} рублей" for shoe in shoes])
                        answer = f"Вот список {shoe_type}:\n{shoes_list}"
                    else:
                        answer = f"К сожалению, мы не нашли {shoe_type} в нашем магазине."
            elif function_name == "get_all_shoes":
                shoes = get_all_shoes()
                if shoes:
                    shoes_list = "\n".join([f"{shoe['name']} - {shoe['price']} рублей" for shoe in shoes])
                    answer = f"Вот все товары в нашем магазине:\n{shoes_list}"
                else:
                    answer = "К сожалению, у нас нет товаров в наличии."
        else:
            # Если нет вызова функции, возвращаем обычный ответ
            answer = message.content

        return JsonResponse({"answer": answer})

    return render(request, 'shop-chat.html')
