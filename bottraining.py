from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
bot = ChatBot("Chatterbot",storage_adapter="chatterbot.storage.SQLStorageAdapter")
trainer = ChatterBotCorpusTrainer(bot)
#training chatbot 
trainer.train(r"C:\Users\sushma\AppData\Local\Programs\Python\Python38\Scripts\Inframind\data\claimProcedure.yml")
trainer.train(r"C:\Users\sushma\AppData\Local\Programs\Python\Python38\Scripts\Inframind\data\modify.yml")
trainer.train(r"C:\Users\sushma\AppData\Local\Programs\Python\Python38\Scripts\Inframind\data\Transfer.yml")
trainer.train(r"C:\Users\sushma\AppData\Local\Programs\Python\Python38\Scripts\Inframind\data\greet.yml")
trainer.train(r"C:\Users\sushma\AppData\Local\Programs\Python\Python38\Scripts\Inframind\data\FAQ.yml")
trainer.train(r"C:\Users\sushma\AppData\Local\Programs\Python\Python38\Scripts\Inframind\data\Handoff.yml")
def bottrain(text):
  return str(bot.get_response(text))
