import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
from collections import Counter
import itertools

print("=" * 60)
print("Анализ продаж зоомагазина")
print("=" * 60)

print("\nЗагрузка данных...")

try:
    df = pd.read_csv('pet_shop_sales.csv')
except:
    print("Файл не найден! Сначала запустите create_data.py")
    exit()

print(f"\nВсего продаж: {len(df)}")
print(f"Первые 3 записи:")
print(df.head(3))

print("\n" + "=" * 60)
print("Чистим данные...")
print("=" * 60)

print("\nПропуски до чистки:")
print(df.isnull().sum())

df = df.dropna()
print(f"\nПосле удаления пропусков осталось: {len(df)} записей")

df['date'] = pd.to_datetime(df['date'])
df['month'] = df['date'].dt.month
df['day_of_week'] = df['date'].dt.day_name()

print("\n" + "=" * 60)
print("Определяем тип животного...")
print("=" * 60)

def get_animal_type(product_name):
    product_lower = product_name.lower()
    
    if 'кошек' in product_lower or 'кошки' in product_lower:
        return 'Кошки'
    elif 'собак' in product_lower:
        return 'Собаки'
    elif 'для кошек' in product_lower:
        return 'Кошки'
    elif 'для собак' in product_lower:
        return 'Собаки'
    else:
        return 'Универсальное'

df['animal_type'] = df['product'].apply(get_animal_type)

print("\nРаспределение по типу животных:")
animal_counts = df['animal_type'].value_counts()
for animal, count in animal_counts.items():
    print(f"   {animal}: {count} продаж ({count/len(df)*100:.1f}%)")

print("\n" + "=" * 60)
print("Общие метрики")
print("=" * 60)

total_revenue = df['total'].sum()
total_orders = len(df)
avg_order = df['total'].mean()

print(f"\nОбщая выручка: {total_revenue:,.2f} руб.")
print(f"Количество продаж: {total_orders}")
print(f"Средний чек (общий): {avg_order:,.2f} руб.")

print("\n" + "=" * 60)
print("Анализ по типу животных")
print("=" * 60)

animal_stats = df.groupby('animal_type').agg({
    'total': ['sum', 'mean', 'count'],
    'price': 'mean'
}).round(2)

animal_stats.columns = ['Выручка', 'Средний чек', 'Количество продаж', 'Средняя цена товара']
animal_stats = animal_stats.sort_values('Выручка', ascending=False)

print("\nСтатистика по типу животных:")
print(animal_stats)

print("\n" + "=" * 60)
print("Анализ корзин покупок (что чаще всего покупают вместе)")
print("=" * 60)


daily_purchases = df.groupby('date')['product'].apply(list)

print(f"\nВсего дней с покупками: {len(daily_purchases)}")

all_pairs = []

for day, products in daily_purchases.items():
    if len(products) > 1:
        pairs = list(itertools.combinations(sorted(products), 2))
        all_pairs.extend(pairs)

pair_counts = Counter(all_pairs)

print("\nТоп-5 пар товаров, которые чаще всего покупают вместе:")
for i, (pair, count) in enumerate(pair_counts.most_common(5), 1):
    print(f"   {i}. {pair[0]} + {pair[1]} — {count} раз")

print("\n" + "=" * 60)
print("Анализ по категориям товаров")
print("=" * 60)

category_revenue = df.groupby('category')['total'].sum().sort_values(ascending=False)

print("\nТоп категорий по выручке:")
for cat, rev in category_revenue.head(5).items():
    print(f"   {cat}: {rev:,.2f} руб. ({rev/total_revenue*100:.1f}%)")

product_revenue = df.groupby('product')['total'].sum().sort_values(ascending=False)

print("\nТоп-5 товаров по выручке:")
for prod, rev in product_revenue.head(5).items():
    print(f"   {prod}: {rev:,.2f} руб.")

print("\n" + "=" * 60)
print("Создаю графики!")
print("=" * 60)

if not os.path.exists('pet_reports'):
    os.makedirs('pet_reports')
    print("Создана папка pet_reports/")

plt.figure(figsize=(8, 5))
animal_revenue = df.groupby('animal_type')['total'].sum()
colors = ['#FF9999', '#99CCFF', '#CCCCCC']  
plt.bar(animal_revenue.index, animal_revenue.values, color=colors)
plt.title('Выручка по типу животных', fontsize=14)
plt.ylabel('Выручка, руб.')
for i, v in enumerate(animal_revenue.values):
    plt.text(i, v + 500, f'{v/1000:.1f}K', ha='center')
plt.tight_layout()
plt.savefig('pet_reports/revenue_by_animal.png')
plt.show()
print("График 1 сохранён: revenue_by_animal.png")

plt.figure(figsize=(8, 5))
animal_avg = df.groupby('animal_type')['total'].mean()
plt.bar(animal_avg.index, animal_avg.values, color=colors)
plt.title('Средний чек по типу животных', fontsize=14)
plt.ylabel('Средний чек, руб.')
for i, v in enumerate(animal_avg.values):
    plt.text(i, v + 20, f'{v:.0f} руб.', ha='center')
plt.tight_layout()
plt.savefig('pet_reports/avg_check_by_animal.png')
plt.show()
print("График 2 сохранён: avg_check_by_animal.png")

plt.figure(figsize=(10, 6))
top_10 = product_revenue.head(10)
y_pos = range(len(top_10))
plt.barh(y_pos, top_10.values)
plt.yticks(y_pos, top_10.index)
plt.xlabel('Выручка, руб.')
plt.title('ТОП-10 товаров по выручке', fontsize=14)
plt.tight_layout()
plt.savefig('pet_reports/top_products.png')
plt.show()
print("График 3 сохранён: top_products.png")

print("\n" + "=" * 60)
print("Сохраняем отчёт в Excel")
print("=" * 60)

with pd.ExcelWriter('pet_reports/pet_shop_report.xlsx', engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Все продажи', index=False)
    
    animal_stats.to_excel(writer, sheet_name='По типу животных')
    
    product_stats = df.groupby('product').agg({
        'total': ['sum', 'mean', 'count'],
        'quantity': 'sum'
    }).round(2)
    product_stats.columns = ['Выручка', 'Средний чек', 'Кол-во продаж', 'Кол-во штук']
    product_stats = product_stats.sort_values(('Выручка'), ascending=False)
    product_stats.to_excel(writer, sheet_name='По товарам')
    
    print("Отчёт сохранён: pet_shop_report.xlsx")

print("\n" + "=" * 60)
print("Итоговые выводы")
print("=" * 60)

top_animal = animal_revenue.idxmax()
top_animal_revenue = animal_revenue.max()

print(f"\nСамые прибыльные покупатели: {top_animal}")
print(f" Выручка: {top_animal_revenue:,.2f} руб.")

if animal_avg['Кошки'] > animal_avg['Собаки']:
    print(f"\nВладельцы кошек тратят больше за один раз")
    print(f"   Кошки: {animal_avg['Кошки']:.0f} руб. vs Собаки: {animal_avg['Собаки']:.0f} руб.")
else:
    print(f"\nВладельцы собак тратят больше за один раз")

most_common_pair = pair_counts.most_common(1)[0]
print(f"\n🛒 Самая популярная комбинация:")
print(f"   {most_common_pair[0][0]} + {most_common_pair[0][1]}")
print(f"   (покупают вместе {most_common_pair[1]} раз)")

print("\n" + "=" * 60)
print("Анализ завершён!")
print(f"Все отчёты в папке: pet_reports/")
print("=" * 60)