import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ClassroomConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        print("CONNECT METHOD TRIGGERED")

        self.classroom_id = self.scope['url_route']['kwargs']['classroom_id']
        self.group_name = f"classroom_{self.classroom_id}"
        self.user = self.scope.get("user")

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # async def receive(self, text_data):
    #     data = json.loads(text_data)
    #
    #
    #
    #     await self.channel_layer.group_send(
    #         self.group_name,
    #         {
    #             "type": "signal_message",
    #             "message": data,
    #             "sender_channel": self.channel_name
    #         }
    #     )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            sender = getattr(self.user, "username", None)

            if sender and not data.get("sender"):
                data["sender"] = sender

            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "signal_message",
                    "message": data,
                    "sender_channel": self.channel_name
                }
            )

        except Exception as e:
            print("❌ ERROR:", e)



    async def signal_message(self, event):
        if self.channel_name == event["sender_channel"]:
            return

        message = event["message"]
        target = message.get("target")
        current_user = getattr(self.user, "username", None)

        if target and target != current_user:
            return

        await self.send(text_data=json.dumps(message))
