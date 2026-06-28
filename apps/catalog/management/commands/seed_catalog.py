from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.catalog.models import Category, Product

CATEGORIES = [
    {"name": "Роллы", "slug": "rolls", "sort_order": 1},
    {"name": "Суши", "slug": "sushi", "sort_order": 2},
    {"name": "Сеты", "slug": "sets", "sort_order": 3},
    {"name": "Салаты", "slug": "salads", "sort_order": 4},
    {"name": "Супы", "slug": "soups", "sort_order": 5},
    {"name": "Напитки", "slug": "drinks", "sort_order": 6},
    {"name": "Десерты", "slug": "desserts", "sort_order": 7},
]

PRODUCTS = [
    {"category": "rolls", "name": "Филадельфия классик", "slug": "philadelphia-classic", "description": "Лосось, сливочный сыр, огурец, нори", "price": Decimal("12.90"), "weight_g": 280, "pieces": 8, "is_featured": True, "allergens": ["Рыба", "Молоко"]},
    {"category": "rolls", "name": "Калифорния", "slug": "california", "description": "Краб, авокадо, огурец, тобико, кунжут", "price": Decimal("11.50"), "weight_g": 260, "pieces": 8, "allergens": ["Рыба", "Кунжут"]},
    {"category": "rolls", "name": "Дракон ролл", "slug": "dragon-roll", "description": "Угорь, авокадо, огурец, унаги соус", "price": Decimal("14.90"), "weight_g": 300, "pieces": 8, "is_featured": True, "allergens": ["Рыба", "Соя"]},
    {"category": "rolls", "name": "Спайси лосось", "slug": "spicy-salmon", "description": "Лосось, спайси соус, зелёный лук, кунжут", "price": Decimal("10.50"), "weight_g": 240, "pieces": 8, "allergens": ["Рыба", "Кунжут"]},
    {"category": "rolls", "name": "Темпура ролл с креветкой", "slug": "tempura-shrimp-roll", "description": "Креветка в темпуре, авокадо, сливочный сыр", "price": Decimal("13.50"), "weight_g": 290, "pieces": 8, "allergens": ["Рыба", "Глютен", "Молоко"]},
    {"category": "sushi", "name": "Нигири лосось", "slug": "nigiri-salmon", "description": "Свежий лосось на рисе с васаби", "price": Decimal("6.90"), "weight_g": 160, "pieces": 4, "allergens": ["Рыба"]},
    {"category": "sushi", "name": "Нигири тунец", "slug": "nigiri-tuna", "description": "Тунец на рисе с васаби", "price": Decimal("7.50"), "weight_g": 160, "pieces": 4, "allergens": ["Рыба"]},
    {"category": "sushi", "name": "Нигири угорь", "slug": "nigiri-eel", "description": "Угорь с унаги соусом на рисе", "price": Decimal("8.90"), "weight_g": 170, "pieces": 4, "allergens": ["Рыба", "Соя"]},
    {"category": "sets", "name": "Сет «Для двоих»", "slug": "set-for-two", "description": "Филадельфия, Калифорния, 4 нигири лосось — 20 штук", "price": Decimal("26.90"), "weight_g": 500, "pieces": 20, "is_featured": True, "allergens": ["Рыба", "Молоко", "Кунжут"]},
    {"category": "sets", "name": "Сет «Мини»", "slug": "set-mini", "description": "Спайси лосось, 4 нигири тунец — 12 штук", "price": Decimal("17.90"), "weight_g": 350, "pieces": 12, "allergens": ["Рыба", "Кунжут"]},
    {"category": "salads", "name": "Чука салат", "slug": "chuka-salad", "description": "Маринованные водоросли чука, кунжут, ореховый соус", "price": Decimal("7.90"), "weight_g": 200, "pieces": None, "allergens": ["Кунжут", "Орехи"]},
    {"category": "salads", "name": "Салат с лососем", "slug": "salmon-salad", "description": "Микс салат, лосось, авокадо, помидоры черри, соус понзу", "price": Decimal("11.90"), "weight_g": 250, "pieces": None, "allergens": ["Рыба"]},
    {"category": "soups", "name": "Мисо суп", "slug": "miso-soup", "description": "Тофу, вакаме, зелёный лук, мисо паста", "price": Decimal("5.90"), "weight_g": 300, "pieces": None, "allergens": ["Соя"]},
    {"category": "soups", "name": "Том Ям с креветками", "slug": "tom-yum-shrimp", "description": "Креветки, грибы, лемонграсс, кокосовое молоко", "price": Decimal("9.90"), "weight_g": 350, "pieces": None, "is_featured": True, "allergens": ["Рыба", "Молоко"]},
    {"category": "drinks", "name": "Зелёный чай", "slug": "green-tea", "description": "Японский зелёный чай сенча", "price": Decimal("3.50"), "weight_g": 300, "pieces": None, "allergens": []},
    {"category": "drinks", "name": "Лимонад юдзу", "slug": "yuzu-lemonade", "description": "Домашний лимонад с японским цитрусом юдзу", "price": Decimal("4.90"), "weight_g": 350, "pieces": None, "allergens": []},
    {"category": "desserts", "name": "Моти", "slug": "mochi", "description": "Рисовые пирожные с начинкой — манго, клубника, матча", "price": Decimal("6.50"), "weight_g": 150, "pieces": 3, "allergens": ["Молоко"]},
]


class Command(BaseCommand):
    help = "Seed catalog categories and products"

    def handle(self, *args, **options):
        cats = {}
        for cat_data in CATEGORIES:
            obj, created = Category.objects.update_or_create(
                slug=cat_data["slug"],
                defaults=cat_data,
            )
            cats[cat_data["slug"]] = obj
            self.stdout.write(f"  {'created' if created else 'exists'}: {obj.name}")

        for prod_data in PRODUCTS:
            cat_slug = prod_data.pop("category")
            prod_data["category"] = cats[cat_slug]
            allergens = prod_data.pop("allergens", [])
            is_featured = prod_data.pop("is_featured", False)
            obj, created = Product.objects.update_or_create(
                slug=prod_data["slug"],
                defaults={**prod_data, "allergens": allergens, "is_featured": is_featured},
            )
            self.stdout.write(f"  {'created' if created else 'exists'}: {obj.name}")

        self.stdout.write(self.style.SUCCESS(
            f"Done — {len(CATEGORIES)} categories, {len(PRODUCTS)} products"
        ))
