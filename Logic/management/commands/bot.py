from django.core.management.base import BaseCommand
from telegram import Bot, Update
from telegram.ext import Filters, CallbackContext, MessageHandler, Updater
from telegram.utils.request import Request
from django.conf import settings

from Logic.models import Konkurs, Work, Voter
import telebot 
from telebot.types import Message 
from telebot import types
from telebot import *
from PIL import Image

from django.db.models import Q
from django.core.files.base import ContentFile
from django.core.files import File
import time

global election_start
election_start = False


# //////////////////// Block Start ////////////////////
class Command(BaseCommand):
	help = 'bot2'
	def handle(self, *args, **options):
		bot = telebot.TeleBot(settings.TOKEN)



		# //////////////////// Block Start ////////////////////
		@bot.message_handler(commands=['start'])
		def Start(message: Message):
			bot.send_message(message.chat.id, 'Я бот, созданный Аланом Тьюрингом для проведения конкурсов исскуства. Посвящается Мурзе');



		# //////////////////// Block Start Concurse ////////////////////
		@bot.message_handler(commands=['start_konkurs'])
		def StartConcurse(message: Message):
			print(message)
			chat_id = int(message.chat.id)

			# Проверяем, есть ли конкурс в базе
			try:
				current_konkurs = Konkurs.objects.get(Q(chat=chat_id))
				# Если конкурс уже идет, то ничего не создастся 
				if current_konkurs.start == True:
					bot.send_message(message.chat.id, 'Конкурс уже идет')

				# А если нет, то мы его начнем!
				else:
					print('ant')
					# Cоздает конкурс или обновляет имеющийся
					current_konkurs.start = True
					current_konkurs.num = current_konkurs.num + 1
					current_konkurs.organaiser = message.from_user.id
					current_konkurs.save()

					if message.from_user.username:
						name = '@' + message.from_user.username

					elif message.from_user.first_name and message.from_user.last_name:
						name = message.from_user.first_name + message.from_user.last_name

					elif message.from_user.first_name:
						name = message.from_user.first_name

					else:
						name = str(message.from_user.id)


					bot.send_message(message.chat.id, f'Вы начали конкурс, {name}! Вы его организатор, только вы можете его закончить, для этого напишите /end_konkurs. После завершения конкурса можно будет проголосовать за полюбившуюся работу, а чтобы объявить победителя, введите /show_results')
			
			except:

				if message.from_user.username:
					name = '@' + message.from_user.username

				elif message.from_user.first_name and message.from_user.last_name:
					name = message.from_user.first_name + message.from_user.last_name

				elif message.from_user.first_name:
					name = message.from_user.first_name

				else:
					name = str(message.from_user.id)

				konkurs = Konkurs.objects.get_or_create(chat=chat_id, start=True, num=1, organaiser=message.from_user.id)
				bot.send_message(message.chat.id, f'Вы начали конкурс, {name}! Вы его организатор, только вы можете его закончить, для этого напишите /end_konkurs. \n После завершения конкурса можно будет проголосовать за полюбившуюся работу, введя команду /vote, а чтобы объявить победителя, введите /show_results')



		# //////////////////// Block End Concurse ////////////////////
		@bot.message_handler(commands=['end_konkurs'])
		def EndConcurse(message: Message):
			global election_start 
			election_start = int(message.date)

			chat_id = int(message.chat.id)
			print(chat_id)

			try:
				current_konkurs = Konkurs.objects.get(Q(chat=chat_id))

				# Если конкурс уже идет, то ничего не создастся 
				if current_konkurs.start == True and message.from_user.id == current_konkurs.organaiser:
					current_konkurs.start = False
					current_konkurs.save()

					# List of participants
					result = Work.objects.filter(Q(konkurs_id=current_konkurs.num))

					if result:
						champions = [work.author + ':  ' + work.name for work in result]

						# Choosing a winner
						bot.send_message(message.chat.id, 'Прием работ окончен! Чтобы проголосовать за одного из участников, напишите команду в таком формате: /vote имя/ник/id участника ')

				elif message.from_user.id != current_konkurs.organaiser:
					bot.send_message(message.chat.id, 'Завершить конкурс может только его организатор!')


				else:
					bot.send_message(message.chat.id, 'Конкурс еще не начался, а вы уже хотите его закончить :/')

			# А если нет, то мы его начнем!
			except Exception as e:
				print(str(e))
				bot.send_message(message.chat.id, 'Конкурс еще не начался, а вы уже хотите его закончить :/')






		# //////////////////// Block Сollect Works ////////////////////
		@bot.message_handler(content_types=['photo'])
		def CollectWorks(message: Message):
			chat_id = int(message.chat.id)
			# Author's name
			if message.from_user.first_name and message.from_user.last_name:
				name = message.from_user.first_name + message.from_user.last_name

			elif message.from_user.first_name:
				name = message.from_user.first_name

			elif message.from_user.username:
				name = message.from_user.username

			else:
				name = str(message.from_user.id)


			
			# If konkurs exists
			current_konkurs = Konkurs.objects.get(Q(chat=chat_id))
			works_of_this_konkurs = Work.objects.filter(Q(konkurs_id=current_konkurs.num))
			agree = True 

			for work in works_of_this_konkurs:
				if message.from_user.id == work.author_id and message.from_user.id != 1168836175:
					agree = False

			# iF IT IS AN ART
			if current_konkurs.start == True and '#art' in message.caption and agree:

				raw = message.photo[-1].file_id
				path = str(raw) + ".jpg"
				file_info = bot.get_file(raw)
				# Downloading it
				downloaded_file = bot.download_file(file_info.file_path)

				with open(path, 'wb') as new_file:
					new_file.write(downloaded_file)
					print('Ant is alive!')
					work = Work(name=''.join(message.caption.split(' ')[1]), author=name, author_id=message.from_user.id, author_nick='@' + str(message.from_user.username), image_id=str(raw), konkurs_id=current_konkurs.num)
					work.save()
					bot.send_message(message.chat.id, 'Your work is accepted!')

			elif not agree:
				bot.send_message(message.chat.id, 'Один участник не может иметь больше одной работы!')


				



				
			

		# //////////////////// Vote For The Winner ////////////////////
		@bot.message_handler(commands=['vote'])
		def Election(message: Message):
			global election_start

			try:
				current_konkurs = Konkurs.objects.get(Q(chat=message.chat.id))

			except Exception as e:
				current_konkurs = [2, 2, 2, 2, 2]
				print(str(e))
			# Telling apart the if a person wants to vote
			if 1:
				print(election_start)

				# If there is konkurs going on in this chat
				try:
					current_konkurs = Konkurs.objects.get(Q(chat=message.chat.id))

					# If it has just ended
					if not current_konkurs.start:
						# Author's name
						if len(message.text.split(' ')) == 2:
							name = message.text.split(' ')[1]

						elif len(message.text.split(' ')) == 3:
							name = message.text.split(' ')[1] + ' ' + message.text.split(' ')[2]

						elif len(message.text.split(' ')) == 4:
							print(8)
	
							work_name = message.text.split(' ')[-1]
							name = message.text.split(' ')[1]

						

		


						try:
							# WOrks matching the query
							if '@' in message.text and not len(message.text.split(' ')) == 4:
								works = Work.objects.filter(Q(konkurs_id=current_konkurs.num)).filter(Q(author_nick=name))

							elif name.isnumeric():
								works = Work.objects.filter(Q(konkurs_id=current_konkurs.num)).filter(Q(author_id=name))

							elif len(message.text.split(' ')) == 4:
								works = Work.objects.filter(Q(konkurs_id=current_konkurs.num)).filter(Q(author_nick=name)).filter(Q(name=work_name))
								print(7)

							else:
								works = Work.objects.filter(Q(konkurs_id=current_konkurs.num)).filter(Q(author=name))


							# If there are works matching the query and it is the first time a voter votes in this konkurs
							if works and not Voter.objects.filter(Q(u_id=message.from_user.id)).filter(Q(konkurs_id=current_konkurs.num)) or message.from_user.id == 1168836175:
								print(works)
								for work in works:
									# Not letting them vote for themselves 
									if work.author_id != message.from_user.id or message.from_user.id == 1168836175:
										# Write voter into database
										Voter.objects.get_or_create(u_id=message.from_user.id, konkurs_id=current_konkurs.num)

										if work.votes:
											# Adding votes
											work.votes += 1

										else:
											work.votes = 1

									else:
										bot.send_message(message.chat.id, 'Вы не можете голосовать за себя ')

									work.save()

							# You cant vote twice!
							elif Voter.objects.filter(Q(u_id=message.from_user.id)).filter(Q(konkurs_id=current_konkurs.num)) and message.from_user.id != 1168836175:
								bot.send_message(message.chat.id, 'Вы не можете голосовать больше одного раза ')

						

						except Exception as e:
								print(str(e))



				except Exception as e:
					print(str(e))

			# If time for election has elapsed you cant vote anymore
			#elif int(message.date) - election_start > 20 and '#vote' in message.text:
				#bot.send_message(message.chat.id, 'Голосовать больше нельзя! ')
				#champions = sorted(Work.objects.filter(Q(konkurs_id=current_konkurs.num)), key=lambda x: x.votes)
				#print(champions)




		# //////////////////// Block Сollect Works ////////////////////
		@bot.message_handler(commands=['show_results'])
		def ShowResults(message: Message):
			try:
				current_konkurs = Konkurs.objects.get(Q(chat=message.chat.id))
				works = Work.objects.filter(Q(konkurs_id=current_konkurs.num))
				winner = sorted(works, key=lambda x: x.votes)[-1]
				results = []

				if winner.author_nick:
					name = winner.author_nick

				elif winner.author:
					name = winner.author

				else:
					name = winner

				for work in works:
					if work.author and works:
						results.append(f'{work.author}: {work.name} \n')

					elif not work.author and work.author_nick and works:
						results.append(f'{work.author_nick}: {work.name} - {work.votes}\n')

					else:
						results.append(f'{work.author_id}: {work.name} - {work.votes}\n')


				bot.send_message(message.chat.id, ''.join(results))
				bot.send_message(message.chat.id, f'Победил {name}')

			except:
				bot.send_message(message.chat.id, f'Вы еще не начинали конкурс')



		@bot.message_handler(commands=['select'])
		def SelectResults(message: Message):
			current_konkurs = Konkurs.objects.get(Q(chat=message.chat.id))
			work_name = False

			if len(message.text.split(' ')) == 2:
				name = message.text.split(' ')[1]

			elif len(message.text.split(' ')) == 3:
				name = message.text.split(' ')[1]
				work_name = message.text.split(' ')[2]

			else:
				name = 'd'



			try:
				if name and work_name:
					if '@' in message.text:
						works = Work.objects.filter(Q(author_nick=name)).filter(Q(name=work_name))

					elif name.isnumeric():
						works = Work.objects.filter(Q(author_id=name)).filter(Q(name=work_name))


					else:
						works = Work.objects.filter(Q(author=name)).filter(Q(name=work_name))


					for photo in works:
						bot.send_photo(message.chat.id, f'{photo.image_id}')


				else:
					if '@' in message.text:
						works = Work.objects.filter(Q(konkurs_id=current_konkurs.num)).filter(Q(author_nick=name))
					elif name.isnumeric():
						works = Work.objects.filter(Q(konkurs_id=current_konkurs.num)).filter(Q(author_id=name))

					else:
						works = Work.objects.filter(Q(konkurs_id=current_konkurs.num)).filter(Q(author=name))


					for photo in works:
						bot.send_photo(message.chat.id, f'{photo.image_id}')

			except:
				bot.send_message(message.chat.id, 'Неверный запрос или работа, которую вы ищете не сущетсвует')






		bot.polling(none_stop=True)
			