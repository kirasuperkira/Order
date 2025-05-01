import asyncio
import json


async def customer_client():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

    try:
        writer.write(b"GET_MENU")
        await writer.drain()
        data = await reader.read(4096)
        menu = json.loads(data.decode())

        print("\nМеню:")
        for item_id, item in menu.items():
            print(f"{item_id}. {item['name']} - ${item['price']:.2f}")

        order = {}
        while True:
            item_id = input("\nВведите номер позиции для добавления в заказ ('0' для перехода к оплате заказа): ")
            if item_id.lower() == '0':
                break

            if item_id not in menu:
                print("Введите корректный номер позиции из меню.")
                continue

            try:
                quantity = int(input(f"Введите количество для следующей позиции: '{menu[item_id]['name']}': "))
                if quantity <= 0:
                    print("Количество должно быть > 0.")
                    continue
                order[item_id] = quantity
            except ValueError:
                print("Введите корректное количество (>0).")

        if not order:
            print("Позиции в заказе отсутствуют.")
            return

        writer.write(f"PLACE_ORDER {json.dumps(order)}".encode())
        await writer.drain()

        data = await reader.read(4096)
        receipt = json.loads(data.decode())
        print("\nЧек:")
        for item in receipt["items"]:
            print(f"{item['name']} x{item['quantity']} @ ${item['price']:.2f} = ${item['item_total']:.2f}")
        print(f"Стоимость вашего заказа: ${receipt['total']:.2f}")

        while True:
            try:
                payment = float(input(f"\nВведите сумму оплаты (стомость вашего заказа составляет ${receipt['total']:.2f}): "))
                if payment < receipt["total"]:
                    print("Оплата отклонена (недостаточное количество средств).")
                    continue
                break
            except ValueError:
                print("Введите корректное числовое значение.")

        writer.write(f"PAY {payment} {json.dumps(receipt)}".encode())
        await writer.drain()

        data = await reader.read(1024)
        print("\nОтвет: ", data.decode())

    finally:
        writer.close()
        await writer.wait_closed()

if __name__ == "__main__":
    asyncio.run(customer_client())