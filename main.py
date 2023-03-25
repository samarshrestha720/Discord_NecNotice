from bs4 import BeautifulSoup
import requests
import csv
import discord, os, asyncio, aiohttp
from io import BytesIO
from keep_alive import keep_alive
from time import sleep

client = discord.Client(intents=discord.Intents.default())


def wtofile(
  firstNotice_Title,
  firstNotice_url,
):  #write to file function
  with open('examNotices.csv', mode='a') as wfile:
    rows = [firstNotice_Title, firstNotice_url]
    writer = csv.writer(wfile)
    writer.writerow(rows)
    wfile.close()


def getImg(url):
  data = requests.get(url, verify=False)
  soup = BeautifulSoup(data.text, 'html.parser')
  imgBlock = soup.find('figure', {'class': 'aligncenter size-large'})
  imgUrl = imgBlock.find('a').get('href')
  return imgUrl


keep_alive()  #make script active


@client.event
async def on_ready():
  await client.wait_until_ready()
  channel = client.get_channel(int(os.environ['channel_id']))
  print(f"Logged in as {client.user}")
  count = 0
  while True:
    data = requests.get("https://nec.edu.np/exam/?cat=3", verify=False)
    soup = BeautifulSoup(data.text, 'html.parser')
    firstNotice = soup.find('div', {'class': 'col-sm-9 col-md-9'})
    firstNotice_url = firstNotice.find('a').get('href')
    firstNotice_Title = firstNotice.find('a').find('h4').text.strip()

    with open('examNotices.csv', mode='r') as file:
      csvFile = csv.reader(file)
      flag = 0
      for lines in csvFile:
        if (lines[0] == firstNotice_Title):
          print('NO NEW NOTICES!!')
          flag = 1
          break
      if (flag == 0):
        print('NEW NOTICE ALERT!!')
        print("Title: ", firstNotice_Title)
        try:
          imgUrl = getImg(firstNotice_url)  #get img url
        except:
          await channel.send(
            f"**_nec_ Exam Divison Notice:**\n{firstNotice_Title}\n{firstNotice_url}\n-NotifyNotice\nCould not get Img"
          )
          print("Discord Notice sent Sucessfully without img!!")
          wtofile(firstNotice_Title, firstNotice_url)
          sleep(1)
          os.system("kill 1")

        try:
          async with aiohttp.ClientSession() as session:  # creates session
            async with session.get(
                imgUrl, verify_ssl=False) as resp:  # gets image from url
              img = await resp.read()  # reads image from response
              with BytesIO(img) as file:  # converts to file-like object
                await channel.send(
                  f"**_nec_ Exam Divison Notice:**\n{firstNotice_Title}\n{firstNotice_url}\n-NotifyNotice\n",
                  file=discord.File(file, "testimage.png"))
                print("Discord Notice sent Sucessfully with img!!")
        except:
          os.system("kill 1")

        wtofile(firstNotice_Title, firstNotice_url)

      file.close()
    count += 1
    print(f"count: {count}")
    await asyncio.sleep(60)


try:
  client.run(os.environ['disToken'])
except:
  os.system("kill 1")
