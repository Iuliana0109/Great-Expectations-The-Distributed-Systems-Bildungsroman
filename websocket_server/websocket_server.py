import asyncio
import websockets
import json
import redis

# Connect to Redis
redis_client = redis.StrictRedis(host='redis', port=6379, db=0)

connected_clients = {}

async def handler(websocket, path):
    try:
        async for message in websocket:
            data = json.loads(message)
            action = data.get("action")

            if action == "subscribe":
                competition_id = data.get("competition_id")
                if competition_id:
                    if competition_id not in connected_clients:
                        connected_clients[competition_id] = []
                    connected_clients[competition_id].append(websocket)
                    await websocket.send(json.dumps({"status": "subscribed", "competition_id": competition_id}))
            elif action == "new_submission":
                competition_id = data.get("competition_id")
                if competition_id in connected_clients:
                    # Notify all subscribers of the new submission
                    for client in connected_clients[competition_id]:
                        if client != websocket:
                            await client.send(json.dumps({"message": "New submission received", "data": data}))
    except websockets.ConnectionClosed:
        pass
    finally:
        # Remove disconnected clients from all rooms
        for subscribers in connected_clients.values():
            if websocket in subscribers:
                subscribers.remove(websocket)

start_server = websockets.serve(handler, "0.0.0.0", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
