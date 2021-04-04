import aiohttp
import asyncio
from bs4 import BeautifulSoup
from aiohttp import ClientSession
import json
import xlsxwriter 
import time



allCountryURl = []
countryTitle = []

allMainData = []

workbook = xlsxwriter.Workbook('Taxes.xlsx')




async def ConURL():

	async with aiohttp.ClientSession() as session:
		async with session.get('https://www.easyship.com/en-in/countries') as response:
			html = await response.text()
			soup =  BeautifulSoup(html,'html.parser')
			CountryList = soup.find_all("a", {"class": "country-card"})
			CountryName = soup.find_all("h2", {"class": "title"})

			for countryURL in CountryList:
				allCountryURl.append("https://www.easyship.com"+countryURL.attrs['href'])

			for CountryNames in CountryName:
				countryTitle.append(countryTitleValidation(CountryNames.string))



def countryTitleValidation(countryNames):
	if len(countryNames) >= 25:
		return countryNames[:24]
	else:
		return countryNames



async def mainPageParser(url, countryTitle):
	worksheet = workbook.add_worksheet(countryTitle)



	async with aiohttp.ClientSession() as session:
		async with session.get(url) as response:
			html2 = await response.text()
			soup1 =  BeautifulSoup(html2,'html.parser')
			mainData = soup1.find_all("h4", {"class": "second-title"},limit=5)
			duty_names = soup1.find_all("p", {"class": "duty-name"})
			duty_prices = soup1.find_all("p", {"class": "duty-value"})
			row = 0
			col = 0
			for mainDatas in mainData:
				split_data =  mainDatas.string.strip().split(':')
				worksheet.write(row, col, split_data[0])
				worksheet.write(row, col+1, split_data[1])
				row  += 1
			row = 0
			col = 0
			worksheet.write(row+5, col, 'country' )
			worksheet.write(row+5, col+1, countryTitle )
			row = 0
			col = 0

			for duty_name in duty_names:
				worksheet.write(row+6, col, duty_name.string.strip())
				row += 1
			row = 0
			col = 0

			for duty_price in duty_prices:
				worksheet.write(row+6, col+1, duty_price.string.strip())
				row += 1







				

async def main():
	start_time = time.time()
	await ConURL()
	tasks  = []
	async with ClientSession() as session:
		for i in range(len(allCountryURl)):
			print(allCountryURl[i],countryTitle[i])
			task = asyncio.ensure_future(mainPageParser(allCountryURl[i],countryTitle[i]))
			tasks.append(task)
			print('Tasks count: ', len(asyncio.Task.all_tasks()))
		responses = await asyncio.gather(*tasks)
		print('Tasks count: ', len(asyncio.Task.all_tasks()))
		print('Active tasks count: ', len(
		[task for task in asyncio.Task.all_tasks() if not task.done()])
		)
	workbook.close()

	end_time = time.time()

	print(end_time-start_time)




loop = asyncio.get_event_loop()
future = asyncio.ensure_future(main())
loop.run_until_complete(future)




