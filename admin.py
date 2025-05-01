import asyncio
import json

async def admin_client():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

    try:
        while True:
            print("\n1 - Добавить позицию в меню")
            print("2 - Завершить")
            choice = input("Выберете действие (1 или 2): ")

            if choice == "1":
                name = input("Введите название позиции: ")
                try:
                    price = float(input("Введите стоимость позиции: "))
                    item_data = {"name": name, "price": price}
                    writer.write(f"ADD_ITEM {json.dumps(item_data)}".encode())
                    await writer.drain()
                    data = await reader.read(1024)
                    print("Ответ сервера:", data.decode())
                except ValueError:
                    print("Ошибка.")

            elif choice == "2":
                break
            else:
                print("Введите существующий номер действия (1 или 2).")
    finally:
        writer.close()
        await writer.wait_closed()

if __name__ == "__main__":
    asyncio.run(admin_client())