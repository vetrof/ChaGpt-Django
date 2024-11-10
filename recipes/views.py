from openai import OpenAI
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse


def get_recipes(request):
    if request.method == 'POST':
        print("POST>>")
        products = request.POST.get('products', '')

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        print("WAIT OPENAI>>")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": f"Предложи рецепты в которых есть ТОЛЬКО эти продукты, "
                                            f"рецепты подробные и обширные, придумывать не нужно, "
                                            f"только те рецепты что есть в книгах рецептов, "
                                            f"учти что готовить будет непрофессионал: {products}"}
            ]
        )


        message = response.choices[0].message.content

        print(message)

        return JsonResponse({"recipes": message})
    return render(request, 'get_recipes.html')
