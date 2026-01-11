import flet as ft
from supabase import create_client, Client
import time
import threading

# ==========================================
# 请把下面这两行换成你在 Supabase 网页上复制的内容
# ==========================================
SUPABASE_URL = "https://ecpyhdrhstemcfcozaab.supabase.co"
SUPABASE_KEY = "sb_publishable_d1vMvwvYaYzRmQ4V3m3trA_axDuv-SR"
# ==========================================

# 连接云端数据库
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def main(page: ft.Page):
    page.title = "zeyangshi聊天室 (云端同步版)"
    page.theme_mode = ft.ThemeMode.LIGHT

    # 你的名字（简单起见，我们随机生成或者是固定的）
    # 如果你想区分是谁，可以在发给朋友的代码里改成 "朋友"
    my_name = "shizeyng"

    # 聊天列表
    chat_list = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    # 发送消息的函数
    def send_message_click(e):
        if not new_message.value:
            return

        text_to_send = new_message.value
        new_message.value = ""  # 立刻清空输入框
        page.update()

        # 1. 往云端数据库插入一条数据
        try:
            supabase.table("messages").insert({
                "text": text_to_send,
                "sender": my_name
            }).execute()
        except Exception as err:
            print(f"发送失败: {err}")

    # 获取消息并更新界面的函数
    def check_new_messages():
        while True:
            try:
                # 1. 从云端拉取最新的 20 条消息
                response = supabase.table("messages").select("*").order("created_at", desc=True).limit(20).execute()
                data = response.data

                # 为了显示顺序正确，我们需要反转一下（因为刚才取的是最新的在前面）
                messages = list(reversed(data))

                # 2. 清空现在的屏幕，重新画一遍（简单粗暴但有效）
                chat_list.controls.clear()

                for msg in messages:
                    is_me = msg['sender'] == my_name

                    # 创建气泡
                    bubble = ft.Container(
                        content=ft.Column([
                            ft.Text(msg['sender'], size=10, color=ft.Colors.GREY),
                            ft.Text(msg['text'], size=16, color=ft.Colors.WHITE),
                        ]),
                        bgcolor=ft.Colors.BLUE_500 if is_me else ft.Colors.GREEN_500,
                        padding=10,
                        border_radius=10,
                        width=250,
                    )

                    # 放入行布局（如果是我发的靠右，别人发的靠左）
                    chat_list.controls.append(
                        ft.Row(
                            [bubble],
                            alignment=ft.MainAxisAlignment.END if is_me else ft.MainAxisAlignment.START
                        )
                    )

                # 3. 刷新界面
                page.update()

            except Exception as e:
                print(f"获取消息出错: {e}")

            # 每隔 1 秒去云端检查一次
            time.sleep(1)

    # 输入框
    new_message = ft.TextField(
        hint_text="输入消息...",
        autofocus=True,
        shift_enter=True,
        expand=True
    )

    # 发送按钮
    send_btn = ft.ElevatedButton(
        content=ft.Text("发送"),
        on_click=send_message_click
    )

    # 组装页面
    page.add(
        ft.Container(content=chat_list, expand=True, padding=10),
        ft.Container(
            content=ft.Row([new_message, send_btn]),
            padding=10,
            bgcolor=ft.Colors.GREY_100
        )
    )

    # 启动后台线程，自动去拉取新消息
    t = threading.Thread(target=check_new_messages, daemon=True)
    t.start()



ft.app(main)
