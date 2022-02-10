from discord_components import DiscordComponents, ComponentsBot, Select, SelectOption, Button, ButtonStyle, ActionRow
import discord, sqlite3, datetime, os, setting
from discord_components.ext.filters import user_filter
import asyncio
from setting import admin_id
from datetime import timedelta
from discord_webhook import DiscordEmbed
from discord_buttons_plugin import ButtonType

client = discord.Client()

def nowstr():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

def now_hour():
    return str(datetime.datetime.now()).split(".")[0]

@client.event
async def on_ready():
    DiscordComponents(client)
    print(f"로그인 완료\n로그인완료 시간 : {now_hour()}\ndeveloped by Trexer#9279")
    
@client.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content == "!출퇴근":
        if message.author.id == int(admin_id) or message.author.guild_permissions.administrator:
            if (os.path.isfile("../db/" + str(message.guild.id) + ".db")):
                await message.delete()
                embed = discord.Embed(title="출퇴근봇", description='원하시는 버튼을 클릭해주세요.', color=0x5c6cdf) #color 부분에는 원하는 색깔 헥스코드 넣으셈
                await message.channel.send(
                embed=embed,
                components = [
                    ActionRow(
                        Button(style=ButtonStyle.blue,label = "출근",custom_id="출근"), #버튼 색깔 바꾸는거는 blue, green, red, gray 이렇게 있음
                        Button(style=ButtonStyle.blue,label = "퇴근",custom_id="퇴근"),
                        Button(style=ButtonStyle.blue,label = "로그채널 설정",custom_id="설정"),
                        Button(style=ButtonStyle.blue,label = "로그채널 아이디",custom_id="아이디"),
                    )
                ]
            )
    
    if message.content == "!도움말":
        await message.channel.send(embed=discord.Embed(title="도움말",description="!도움 : 도움말을 불러옵니다.\n!출퇴근 : 출근/퇴근 알림을 보내줄수있게하는 버튼이 나옵니다.\n!문의 : 문의하기\n!서버등록 : 서버를 등록합니다.",color=0x5c6cdf))
        
    if message.content == "!문의":
        await message.channel.send("Trexer#9279 여기로 ㄱ (귀찮은거면 안받음)")
        
    if message.content == "!서버등록":
        if message.author.guild_permissions.administrator or message.author.id == int(admin_id):
            if not (os.path.isfile("../db/" + str(message.guild.id) + ".db")):
                con = sqlite3.connect("../db/" + str(message.guild.id) + ".db")
                cur = con.cursor()
                cur.execute("CREATE TABLE serverinfo (serverid INTEGER, log_id INTEGER);")
                con.commit()
                cur.execute("INSERT INTO serverinfo VALUES (?, ?);",(str(message.guild.id), 0))
                con.commit()
                cur.execute("CREATE TABLE users (user_id INTEGER);")
                con.commit()
                con.close()
                await message.channel.send("등록완료")
            else:
                await message.channel.send("등록실패")
    

        
@client.event
async def on_button_click(button):
    if button.custom_id == "출근":
        if button.author.guild_permissions.administrator or button.author.id == int(admin_id):
            con = sqlite3.connect("../db/" + str(button.guild.id) + ".db")
            cur = con.cursor()
            cur.execute("SELECT * FROM serverinfo;")
            server_info = cur.fetchone()
            con.close()
            ts = await button.respond(embed=discord.Embed(title=":white_check_mark: 성공",description="출근알림 보내기 완료",color=0x5c6cdf))
            embed = discord.Embed(title=f"{button.author} 출근완료!",color=0x5c6cdf)
            embed.add_field(name="출근",value=f"{button.author.name}님이 출근을 하셨습니다." , inline=False)
            embed.add_field(name="출근날짜/시간",value=f"{nowstr()}")
            await client.get_channel(server_info[1]).send(embed=embed)
            
    if button.custom_id == "퇴근":
        if button.author.guild_permissions.administrator or button.author.id == int(admin_id):
            con = sqlite3.connect("../db/" + str(button.guild.id) + ".db")
            cur = con.cursor()
            cur.execute("SELECT * FROM serverinfo;")
            server_info = cur.fetchone()
            con.close()
            await button.respond(embed=discord.Embed(title=":white_check_mark: 성공",description="퇴근알림 보내기 완료",color=0x5c6cdf))
            embed = discord.Embed(title=f"{button.author} 퇴근!",color=0x5c6cdf)
            embed.add_field(name="퇴근",value=f"{button.author.name}님이 퇴근을 하셨습니다." , inline=False)
            embed.add_field(name="퇴근날짜/시간",value=f"{nowstr()}")
            await client.get_channel(server_info[1]).send(embed=embed)
            
    if button.custom_id == "설정":
        if button.author.guild_permissions.administrator or button.author.id == int(admin_id):
            if (os.path.isfile("../db/" + str(button.guild.id) + ".db")):
                ms = await button.channel.send(embed=discord.Embed(title="로그채널 설정",description="60초 안에 로그채널의 아이디를 입력해주세요.",color=0x5c6cdf))
                def check(ids):
                    return (ids.author.id == button.user.id)
                try:
                    ids = await client.wait_for("message",timeout=60,check=check)
                except asyncio.TimeoutError:
                    try:
                        await ms.edit(embed=discord.Embed(title=":no_entry: 시간초과",description="처음부터 다시 시작해주세요.",color=0x5c6cdf))
                    except:
                        pass
                    return None
                if ids.content.isdigit():
                    con = sqlite3.connect("../db/" + str(button.guild.id) + ".db")
                    cur = con.cursor()
                    cur.execute("UPDATE serverinfo SET log_id = ?;", (ids.content,))
                    con.commit()
                    con.close()
                    await ms.edit(embed=discord.Embed(title=":white_check_mark: 성공",description="설정된 값 : `" + ids.content + "`",color=0x5c6cdf))
                else:
                    await ms.edit(embed=discord.Embed(title=":no_entry: 실패",description="입력하신값이 정수인지 확인해주세요.",color=0x5c6cdf))
                    pass
                    
    if button.custom_id == "아이디":
        if button.author.guild_permissions.administrator or button.author.id == int(admin_id):
            if (os.path.isfile("../db/" + str(button.guild.id) + ".db")):
                con = sqlite3.connect("../db/" + str(button.guild.id) + ".db")
                cur = con.cursor()
                cur.execute("SELECT * FROM serverinfo;")
                server_info = cur.fetchone()
                con.close()
                await button.respond(embed=discord.Embed(title="로그채널 아이디",description=f"`{server_info[1]}`",color=0x5c6cdf))
                pass
            
        
        
            
            
            

client.run(setting.token)
