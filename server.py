import asyncio
import json
import os
from collections import defaultdict

MENU_FILE = "menu.json"

class FastFoodServer:
    def __init__(self):
        self.menu = defaultdict(dict)
        self.load_menu()

    def load_menu(self):
        if os.path.exists(MENU_FILE):
            with open(MENU_FILE, 'r') as f:
                try:
                    data = json.load(f)
                    for item_id, item_data in data.items():
                        self.menu[item_id] = item_data
                except json.JSONDecodeError:
                    self.menu = defaultdict(dict)

    def save_menu(self):
        with open(MENU_FILE, 'w') as f:
            json.dump(self.menu, f, indent=4)

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"Соединение с {addr}")

        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    break

                message = data.decode().strip()
                print(f"Получено от сервера {addr}: {message}")

                if message.startswith("GET_MENU"):
                    response = json.dumps(self.menu)
                    writer.write(response.encode())
                    await writer.drain()

                elif message.startswith("PLACE_ORDER"):
                    try:
                        order = json.loads(message[12:])
                        total = 0
                        receipt = {"items": [], "total": 0}

                        for item_id, quantity in order.items():
                            if item_id in self.menu:
                                item = self.menu[item_id]
                                price = item["price"]
                                item_total = price * quantity
                                receipt["items"].append({
                                    "name": item["name"],
                                    "quantity": quantity,
                                    "price": price,
                                    "item_total": item_total
                                })
                                total += item_total

                        receipt["total"] = total
                        response = json.dumps(receipt)
                        writer.write(response.encode())
                        await writer.drain()

                    except json.JSONDecodeError:
                        writer.write(b"Invalid order format")
                        await writer.drain()

                elif message.startswith("PAY"):
                    try:
                        parts = message.split()
                        amount = float(parts[1])
                        receipt = json.loads(" ".join(parts[2:]))
                        total = receipt["total"]

                        if amount >= total:
                            response = "Оплата прошла успешно."
                        else:
                            response = "Пойдешь мыть посуду."

                        writer.write(response.encode())
                        await writer.drain()

                    except (IndexError, ValueError):
                        writer.write(b"Invalid payment format")
                        await writer.drain()

                elif message.startswith("ADD_ITEM"):
                    try:
                        parts = message.split(maxsplit=1)
                        item_data = json.loads(parts[1])
                        item_id = str(len(self.menu) + 1)
                        self.menu[item_id] = {
                            "name": item_data["name"],
                            "price": item_data["price"]
                        }
                        self.save_menu()
                        writer.write(b"Item added successfully")
                        await writer.drain()

                    except (IndexError, json.JSONDecodeError):
                        writer.write(b"Invalid item format")
                        await writer.drain()

        except ConnectionResetError:
            print(f"Ошибка соединения с {addr}.")
        finally:
            writer.close()
            print(f"Соединение с {addr} завершено.")

async def main():
    server = FastFoodServer()
    server_instance = await asyncio.start_server(
        server.handle_client, '127.0.0.1', 8888)

    addr = server_instance.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server_instance:
        await server_instance.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())